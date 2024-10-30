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

def create_entity(tx, row):
    entity_columns = row.filter(regex='entities').index 
    representative_entities = ontology['representative_entities']
    for entity_column in entity_columns:
        for entity in ast.literal_eval(row[entity_column]):
            entity_type = entity[1]
            config = ontology["entities"].get(entity_type)
            if not config:
                raise ValueError(f"Entity type {entity_type} not found in ontology.")

            if entity_type in representative_entities:
              if entity_type == 'MODULE' and 'moduleCode' in row.index:
                unique_key = config["unique"][0]
                unique_value = row.get(unique_key)
                if not unique_value:
                    raise ValueError(f"Missing unique identifier {unique_key} for {entity_type}.")

                attributes = {k: v for k, v in row.items() if k in config["attributes"]}
                query = f"""
                MERGE (e:{entity_type} {{{unique_key}: $unique_value}})
                SET e += $attributes
                """
                tx.run(query, unique_value=unique_value, attributes=attributes)
              elif entity_type in ['STUDENT','STAFF']:
                unique_key = config["unique"][0]
                unique_value = row.get(unique_key) 
                if not unique_value:
                    raise ValueError(f"Missing unique identifier {unique_key} for {entity_type}.")
                attributes = {k: v for k, v in row.items() if k in config["attributes"]}
                query = f"""
                MERGE (e:{entity_type} {{{unique_key}: $unique_value}}) 
                SET e += $attributes
                """
                tx.run(query, unique_value=unique_value, attributes=attributes)

            else:
              unique_value = entity[0]
              query = f"""
              MERGE (e:{entity_type} {{name: $unique_value}}) 
              """
              tx.run(query, unique_value=unique_value)

def create_relationship(tx, from_type, from_id, to_type, to_id, relationship_type):
    relationship_config = ontology["relationships"].get(relationship_type)
    if not relationship_config or relationship_config["from"] != from_type or relationship_config["to"] != to_type:
        raise ValueError(f"Invalid relationship {relationship_type} between {from_type} and {to_type}.")

    unique_from_entity_identifier = ontology['entities'][from_type]['unique'][0]
    unique_to_entity_identifier = ontology['entities'][to_type]['unique'][0]

    query = f"""
    MATCH (a:{from_type} {{{unique_from_entity_identifier}: $from_id}})
    MATCH (b:{to_type} {{{unique_to_entity_identifier}: $to_id}})
    MERGE (a)-[r:{relationship_type}]->(b)
    """
    tx.run(query, from_id=from_id, to_id=to_id)

def batch_create_entities_and_relationships(driver, df):
    ontology = json.load(open('/content/ontology_config.json'))
    with driver.session() as session:
        for index, row in df.iterrows():  
            session.execute_write(create_entity, row)

            if pd.notna(row['Relationships']):
              relationships = ast.literal_eval(row['Relationships'])
              for relationship in relationships:
                  session.execute_write(
                      create_relationship,
                      relationship["from_type"],
                      relationship["from_id"],
                      relationship["to_type"],
                      relationship["to_id"],
                      relationship["type"]
              )

def serialize_neo4j_value(value):
    if isinstance(value, Node):
        return {
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
        onotology_data = json.load(file)
        ontology = json.dumps(onotology_data)
    system_prompt = f"""
    this is how my neo4j database ontology looks like: {ontology}.
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

    cypher_query = ast.literal_eval(completion.choices[0].message.content)['query']

    result = tx.run(cypher_query).value()
    serialized_result = serialize_neo4j_value(result)
    return cypher_query, serialized_result

def evaluate_prompt(prompt):
    with driver.session() as session:
      cypher_query, result = session.execute_read(generate_cypher_query,prompt)
    return cypher_query,result