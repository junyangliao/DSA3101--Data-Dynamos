import os
import pandas as pd
import ast
from neo4j import GraphDatabase
from pyvis.network import Network   
from utils import batch_create_entities_and_relationships

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()

def create_module_node_and_relationships(tx, module_code, title, description, module_credit, department, faculty, prerequisites, preclusions, semesters, skills):
    tx.run("""
        MERGE (m:Module {moduleCode: $module_code})
        ON CREATE SET m.title = $title, m.description = $description, m.moduleCredit = $module_credit
        ON MATCH SET m.title = $title, m.description = $description, m.moduleCredit = $module_credit
    """, module_code=module_code, title=title, description=description, module_credit=module_credit)

    tx.run("""
        MERGE (d:Department {name: $department})
        MERGE (f:Faculty {name: $faculty})
        MERGE (d)-[:PART_OF]->(f)
        WITH d
        MATCH (m:Module {moduleCode: $module_code})
        MERGE (m)-[:BELONGS_TO]->(d)
    """, department=department, faculty=faculty, module_code=module_code)

    if prerequisites:
        for prereq_list in prerequisites:
            if len(prereq_list)>=1:  # Check if it's a valid list
                # Create a group node for the alternatives
                group_name = f"{prereq_list}"
                tx.run("""
                    MERGE (g:PrerequisiteGroup {name: $group_name})
                """, group_name=group_name)
                
                # Connect group to each prerequisite module
                for prereq in prereq_list:
                    tx.run("""
                        MATCH (p:Module {moduleCode: $prereq}), (g:PrerequisiteGroup {name: $group_name})
                        MERGE (p)-[:INCLUDED_AS_PREREQUISITE]->(g)
                    """, prereq=prereq, group_name=group_name)
                
                # Connect main module to the group
                tx.run("""
                    MATCH (m:Module {moduleCode: $module_code}), (g:PrerequisiteGroup {name: $group_name})
                    MERGE (m)-[:MUST_HAVE_TAKEN_ONE_OF]->(g)
                """, module_code=module_code, group_name=group_name)

    if preclusions:
        group_name = f"{preclusions}"
        tx.run("""
                MERGE (g:PreclusionGroup {name: $group_name})
            """, group_name=group_name)
        
        for preclusion in preclusions:
            tx.run("""
                MATCH (p:Module {moduleCode: $preclusion}), (g:PreclusionGroup {name: $group_name})
                MERGE (p)-[:INCLUDED_AS_PRECLUSION]->(g)
            """, preclusion=preclusion, group_name=group_name)

        tx.run("""
            MATCH (m:Module {moduleCode: $module_code}), (g:PreclusionGroup {name: $group_name})
            MERGE (m)-[:MUST_NOT_HAVE_TAKEN_ONE_OF]->(g)
        """, module_code=module_code, group_name = group_name)

    for semester in semesters:
        tx.run("""
            MERGE (s:Semester {number: $semester})
            WITH s
            MATCH (m:Module {moduleCode: $module_code})
            MERGE (m)-[:OFFERED_IN]->(s)
        """, semester=semester, module_code=module_code)
    
    if skills:
        for skill in skills:
            tx.run("""
                MERGE (m:Module {moduleCode: $module_code})
                WITH m
                MATCH (s:Skill {name: $skill})
                MERGE (m)-[:SKILL_TAUGHT]->(s)
            """, module_code=module_code, skill = skill)

# May throw an error
def create_module(data):
    with driver.session() as session:
        module_code = data.get('module code')
        title = data.get('title')
        description = data.get('description')
        module_credit = data.get('module credit')
        department = data.get('department')
        faculty = data.get('faculty')
        prerequisites = list(data.get('prerequisites'))
        preclusions = list(data.get('preclusions'))
        semesters = list(data.get('semesters'))

        session.execute_write(create_module_node_and_relationships, module_code, title, description, module_credit, department, faculty, prerequisites, preclusions, semesters)

def create_modules(data):
    with driver.session() as session:
        for _, row in data.iterrows():
            module_code = row['moduleCode']
            title = row['title']
            description = row['description']
            module_credit = row['moduleCredit']
            department = row['department']
            faculty = row['faculty']
            prerequisites = ast.literal_eval(row['prerequisite'])
            preclusions = ast.literal_eval(row['preclusion'])
            skills = ast.literal_eval(row['Description_entities']).get('Skill')
            semesters = []
            if row['semester_01'] > 0: semesters.append(1)
            if row['semester_02'] > 0: semesters.append(2)
            if row['semester_03'] > 0: semesters.append(3)
            if row['semester_04'] > 0: semesters.append(4)
            
            session.execute_write(create_module_node_and_relationships, module_code, title, description, module_credit, department, faculty, prerequisites, preclusions, semesters,skills)

def delcaring_constraints_for_modules(tx):
    # Enforce constraint on moduleCode
    tx.run("""
        CREATE CONSTRAINT IF NOT EXISTS
        FOR (m:Module) REQUIRE m.moduleCode IS UNIQUE;
    """)
    
    tx.run("""
        CREATE CONSTRAINT IF NOT EXISTS
        FOR (f:Faculty) REQUIRE f.name IS UNIQUE;
    """)

    tx.run("""
        CREATE CONSTRAINT IF NOT EXISTS
        FOR (d:Department) REQUIRE d.name IS UNIQUE;
    """)

def delete_module_node_and_relationships(tx, module_code):
    tx.run("""
        MATCH (m:Module {moduleCode: $module_code})
        DETACH DELETE m;
    """, module_code=module_code)   

def delete_module(data):
    with driver.session() as session:
        module_code = data
        session.execute_write(delete_module_node_and_relationships, module_code)
    

# def get_job_recommendations(query):
    

# def get_modules(tx, n = 25):
#     graph = Graph("neo4j+s://67203e25.databases.neo4j.io", auth=("neo4j", "KUKTrqvpgw9FLuAam0cCauBnsdQsTC3CW1lCboUWhaA"))

#     query = """
#         MATCH p=()-[]->() RETURN p LIMIT 25;
#     """ 
#     data = graph.run(query).data()
#     net = Network(notebook=True, cdn_resources='in_line')

#     # Add nodes and edges from the data
#     for record in data:
#         course_code = record['moduleCode']
#         course_title = record['title']
#         description = record['description']
#         module_credit = record['moduleCredit']
#         semester = record['semester']

#         # Add course node with description and modular credits as tooltip
#         net.add_node(course_code, label=course_code, title=tooltip_text, color='lightblue')

#         # Add semester node
#         net.add_node(f"Semester {semester}", label=f"Semester {semester}", color='lightgreen')

#         # Add edge (relationship)
#         net.add_edge(course_code, f"Semester {semester}", label='OFFERED_IN')

#     # Step 5: Generate the graph as an HTML file
#     net.show("/content/course_graph.html")


    
