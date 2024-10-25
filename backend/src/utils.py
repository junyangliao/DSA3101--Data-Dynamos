import json
import ast
import pandas as pd
from openai import OpenAI
import os
from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")
openai_api_key = os.getenv("OPENAI_API_KEY")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()

def format_node(node):
    node_type = list(node.labels)[0]  
    properties = node.items()  
    formatted_props = ", ".join([f'{k}: "{v}"' for k, v in properties])
    return f"(:{node_type} {{{formatted_props}}})"

def format_relationship(rel):
    rel_type = rel.__class__.__name__  
    return f"-[:{rel_type}]->"

def create_entity(tx, row, ontology):
    # Extract attributes that don't contain 'entities' in the column name
    attributes = {k: v for k, v in row.items() if 'entities' not in k.lower()}
    
    # List of entity columns to handle dynamically
    entity_columns = ['Module_entities', 'Department_entities', 'Faculty_entities', 'Description_entities', 'Student_entities', 'Major_entities', 'Staff_entities', 'Job_entities']
    
    for entity_column in entity_columns:
        # Check if the entity column exists in the row
        if entity_column in row and pd.notna(row[entity_column]):
            # Safely evaluate the entity data
            entity_data = ast.literal_eval(row[entity_column])
            
            if entity_data:
                entity_type = entity_data[0][1]  # Extract entity type (e.g., MODULE, DEPARTMENT, etc.)
                entity_name = entity_data[0][0]  # Extract entity name (e.g., ABM5001 for modules)
                
                # Fetch entity configuration from the ontology
                entity_config = ontology['entities'].get(entity_type)
                if not entity_config:
                    raise ValueError(f"Unknown entity type: {entity_type}")
                
                # For 'Module_entities', use the dynamically generated attributes
                if entity_column in ['Module_entities','Student_entities', 'Staff_entities', ]:
                    attributes_str = ', '.join([f"{k}: ${k}" for k in attributes])
                    query = f"""
                        MERGE (n:{entity_type} {{{attributes_str}}})
                    """
                    tx.run(query, attributes)
                
                # For other entities like department or faculty, use 'name' as a unique identifier
                else:
                    query = f"""
                        MERGE (n:{entity_type} {{name: $name}})
                    """
                    parameters = {'name': entity_name}
                    tx.run(query, parameters)

                # Log or print the action for debugging
                print(f"Entity of type {entity_type} created with name: {entity_name}")

# # Apply the function to each row in the DataFrame
# def handle_csv():
#   for _, row in modules.iterrows():
#       session.execute_write(create_entity, row, ontology)

def serialize_neo4j_value(value):
    if isinstance(value, Node):
        return {
            'id': value.id,
            'labels': list(value.labels),
            'properties': dict(value)
        }
    elif isinstance(value, Relationship):
        return {
            'id': value.id,
            'type': value.type,
            'start_node_id': value.start_node.id,
            'end_node_id': value.end_node.id,
            'properties': dict(value)
        }
    elif isinstance(value, list):  
        return [serialize_neo4j_value(v) for v in value]
    else:
        return value  

def generate_cypher_query(tx,prompt):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", openai_api_key))
    json_file_path = os.path.join(os.path.dirname(__file__), 'ontology_config_test.json')
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    system_prompt = f"""
    This is how my neo4j database ontology looks like: {data}.
    keep in mind these rules : Mixing label expression symbols ('|', '&', '!', and '%') with colon (':') between labels is not allowed. Please only use one set of symbols. This expression could be expressed as :PrerequisiteGroup|(pg&PreclusionGroup)
    """
    model="gpt-4-1106-preview"
    completion = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={
            "type": "json_object"
        },
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Answer the following question in JSON format: {prompt}" # Added instruction to format in JSON
            }
        ]
    )

    try:
        cypher_query = ast.literal_eval(completion.choices[0].message.content)['query']
        
        # Run the generated Cypher query
        result = tx.run(cypher_query).value()
        
        return cypher_query, result
    
    except (KeyError, ValueError) as e:
        raise Exception(f"Failed to generate Cypher query: {str(e)}")

def evaluate_prompt(prompt):
    with driver.session() as session:
      cypher_query, result = session.execute_read(generate_cypher_query,prompt)
    return cypher_query,result