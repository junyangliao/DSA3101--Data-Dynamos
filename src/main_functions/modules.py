import os
import pandas as pd
from flask import Flask, request, render_template
from neo4j import GraphDatabase
from py2neo import Graph
from pyvis.network import Network   
from utils import format_node,format_relationship

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()

def create_module_node_and_relationships(tx, module_code, title, description, module_credit, department, faculty, prerequisites, preclusions, semesters):
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

    if isinstance(prerequisites, list) and len(prerequisites) > 0:
      for prerequisite in prerequisites:
          tx.run("""
              MERGE (p:Module {moduleCode: $prerequisite})
              WITH p
              MATCH (m:Module {moduleCode: $module_code})
              MERGE (m)-[:HAS_PREREQUISITE]->(p) 
          """, module_code=module_code, prerequisite=prerequisite)

    if isinstance(preclusions, list) and len(preclusions) > 0:
      for preclusion in preclusions:
          tx.run("""
              MERGE (p:Module {moduleCode: $preclusion})
              WITH p
              MATCH (m:Module {moduleCode: $module_code})
              MERGE (m)-[:HAS_PRECLUSION]->(p)
          """, module_code=module_code, preclusion = preclusion)

    for semester in semesters:
        tx.run("""
            MERGE (s:Semester {number: $semester})
            WITH s
            MATCH (m:Module {moduleCode: $module_code})
            MERGE (m)-[:OFFERED_IN]->(s)
        """, semester=semester, module_code=module_code)

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
            prerequisites = row['prerequisite']
            preclusions = row['preclusion']
            semesters = []
            if row['semester_01'] > 0: semesters.append(1)
            if row['semester_02'] > 0: semesters.append(2)
            if row['semester_03'] > 0: semesters.append(3)
            if row['semester_04'] > 0: semesters.append(4)
            
            session.execute_write(create_module_node_and_relationships, module_code, title, description, module_credit, department, faculty, prerequisites, preclusions, semesters)

def delete_module_node_and_relationships(tx, module_code):
    tx.run("""
        MATCH (m:Module {moduleCode: $module_code})
        DETACH DELETE m;
    """, module_code=module_code)   

def delete_module(data):
    with driver.session() as session:
        module_code = data.get('module code')
        session.execute_write(delete_module_node_and_relationships, module_code)

def get_modules_all_connections():
    output = []
    query = """
        MATCH (m:Module)
        WITH m
        LIMIT 15
        MATCH (m)-[r]-(connectedNode)
        RETURN m, r, connectedNode;
        """
    query_data = graph.run(query).data()
    
    for result in query_data:
        module_node = result['m']  
        relationship = result['r']  
        connected_node = result['connectedNode']  

        formatted_module = format_node(module_node)
        formatted_connected_node = format_node(connected_node)
        formatted_relationship = format_relationship(relationship)
        
        connection = f"{formatted_module}{formatted_relationship}{formatted_connected_node}"
        output.append(connection)

    output_df = pd.DataFrame({'results':output})
    return output_df

def visualize_module_and_relationships(module_code):
    query = """
    MATCH (m:Module {moduleCode: $module_code})
    OPTIONAL MATCH (m)-[:BELONGS_TO]->(d:Department)
    OPTIONAL MATCH (d)-[:PART_OF]->(f:Faculty)
    OPTIONAL MATCH (m)-[:HAS_PREREQUISITE]->(p:Module)
    OPTIONAL MATCH (m)-[:HAS_PRECLUSION]->(pr:Module)
    OPTIONAL MATCH (m)-[:OFFERED_IN]->(s:Semester)
    RETURN m, d, f, p, pr, s;
    """
    data = graph.run(query, module_code=module_code).data()

    # Initialize the network graph visualization
    net = Network(notebook=True, cdn_resources='in_line')

    # Add nodes and edges to the visualization
    for record in data:
        module = record['m']
        department = record.get('d')
        faculty = record.get('f')
        prerequisite = record.get('p')
        preclusion = record.get('pr')
        semester = record.get('s')

        # Add module node
        module_code = module['moduleCode']
        net.add_node(module_code, label=f"Module: {module_code}", color='lightblue')

        # Add department and faculty
        if department:
            dept_name = department['name']
            net.add_node(dept_name, label=f"Department: {dept_name}", color='lightgreen')
            net.add_edge(module_code, dept_name, label='BELONGS_TO', length=300, font={'size': 14})

            if faculty:
                fac_name = faculty['name']
                net.add_node(fac_name, label=f"Faculty: {fac_name}", color='lightcoral')
                net.add_edge(dept_name, fac_name, label='PART_OF', length=300, font={'size': 14})

        # Add prerequisites
        if prerequisite:
            prereq_code = prerequisite['moduleCode']
            net.add_node(prereq_code, label=f"Prerequisite: {prereq_code}", color='yellow')
            net.add_edge(module_code, prereq_code, label='HAS_PREREQUISITE', length=300, font={'size': 14})

        # Add preclusions
        if preclusion:
            preclusion_code = preclusion['moduleCode']
            net.add_node(preclusion_code, label=f"Preclusion: {preclusion_code}", color='orange')
            net.add_edge(module_code, preclusion_code, label='HAS_PRECLUSION', length=300, font={'size': 14})

        # Add semesters
        if semester:
            sem_number = semester['number']
            sem_label = f"Semester {sem_number}"
            net.add_node(sem_label, label=sem_label, color='purple')
            net.add_edge(module_code, sem_label, label='OFFERED_IN', length=300, font={'size': 14})

    # Display the graph
    net.show("module_graph.html")
    

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


    
