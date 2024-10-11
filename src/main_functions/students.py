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

def create_student_node_and_relationships(tx, student_name, matric_number, nric, year, faculty, major, second_major, modules_completed, grades):
    tx.run("""
        MERGE (s:Student {matricNumber: $matric_number})
        ON CREATE SET s.studentName = $student_name, s.nric = $nric, s.year = $year, s.grades = $grades
        ON MATCH SET s.studentName = $student_name, s.nric = $nric, s.year = $year, s.grades = $grades
    """, matric_number = matric_number, student_name = student_name, nric = nric, year = year, grades = grades)

    tx.run("""
        MERGE (f:Faculty {name: $faculty})
        WITH f
        MATCH (s:Student {matricNumber: $matric_number})
        MERGE (s)-[:STUDYING_UNDER]->(f)
    """, faculty=faculty, matric_number=matric_number)

    tx.run("""
        MERGE (m:Major {name: $major})
        WITH m
        MATCH (s:Student {matricNumber: $matric_number})
        MERGE (s)-[:MAJOR_IN]->(m)
    """, major=major, matric_number=matric_number)
    
    if isinstance(second_major,str):
      tx.run("""
          MERGE (sm:secondMajor {name: $second_major})
          WITH sm
          MATCH (s:Student {matricNumber: $matric_number})
          MERGE (s)-[:SECOND_MAJOR_IN]->(sm)
      """, second_major=second_major, matric_number=matric_number)

    if isinstance(modules_completed, list) and len(modules_completed) > 0:
      for module in modules_completed:
          tx.run("""
              MERGE (m:Module {moduleCode: $module_code})
              WITH m
              MATCH (s:Student {matricNumber: $matric_number})
              MERGE (s)-[:COMPLETED]->(m)
          """, matric_number=matric_number, module_code=module)

def create_student(data):
    with driver.session() as session:
        student_name = data.get('name')
        matric_number = data.get('matric number')
        nric = data.get('nric')
        year = data.get('year')
        faculty = data.get('major')
        major = row['Major']
        second_major = data.get('second major')
        modules_completed = data.get('modules_completed')
        grades = data.get['grades']

        session.execute_write(create_student_node_and_relationships, student_name, matric_number, nric, year, faculty, major, second_major, modules_completed, grades)

def create_students(student_data_list):
    with driver.session() as session:
        for _, row in student_data_list.iterrows():
            student_name = row['Student_Name']
            matric_number = row['Matric_Number']
            nric = row['NRIC']
            year = row['Year']
            faculty = row['Faculties']
            major = row['Major']
            second_major = row['Second Major']
            modules_completed = row['Modules_Completed']
            grades = row['Grades']

            session.execute_write(create_student_node_and_relationships, student_name, matric_number, nric, year, faculty, major, second_major, modules_completed, grades)

def delete_student_node_and_relationships(tx, matric_number):
    tx.run("""
        MATCH (s:Student {matricNumber: $matric_number})
        DETACH DELETE s;
    """, matric_number=matric_number)

def delete_student(data):
    with driver.session() as session:
        matric_number = data.get('matric number')
        session.execute_write(delete_student_node_and_relationships, matric_number)

def get_students_all_connections():
    output = []
    query = """
        MATCH (s:Student)
        WITH s
        LIMIT 5
        MATCH (s)-[r]-(connectedNode)
        RETURN s, r, connectedNode;
        """
    query_data = graph.run(query).data()
    
    for result in query_data:
        student_node = result['s']  
        relationship = result['r']  
        connected_node = result['connectedNode']  

        formatted_student = format_node(student_node)
        formatted_connected_node = format_node(connected_node)
        formatted_relationship = format_relationship(relationship)
        
        connection = f"{formatted_student}{formatted_relationship}{formatted_connected_node}"
        output.append(connection)

    output_df = pd.DataFrame({'results':output})
    return output_df

def visualize_student_and_relationships(matric_number):
    query = """
    MATCH (s:Student {matricNumber: $matric_number})
    OPTIONAL MATCH (s)-[:studying_under]->(f:Faculty)
    OPTIONAL MATCH (d:Department)-[:PART_OF]->(f:Faculty)
    OPTIONAL MATCH (s)-[:major_in]->(m:Major)
    OPTIONAL MATCH (s)-[:SECOND_MAJOR_IN]->(sm:secondMajor)
    OPTIONAL MATCH (s)-[:completed]->(mod:Module)
    RETURN s, d, f, m, sm, mod;
    """
    data = graph.run(query, matric_number=matric_number).data()

    # Initialize the network graph visualization
    net = Network(notebook=True, cdn_resources='in_line')

    # Add nodes and edges to the visualization
    for record in data:
        student = record['s']
        department = record.get('d')
        faculty = record.get('f')
        major = record.get('m')
        second_major = record.get('sm')
        module = record.get('mod')

        matric_number = student['matricNumber']
        net.add_node(matric_number, label=f"Student: {matric_number}", color='lightblue')

        if faculty:
            fac_name = faculty['name']
            net.add_node(fac_name, label=f"Faculty: {fac_name}", color='lightcoral')
            net.add_edge(matric_number, fac_name, label='STUDYING_UNDER', length=300, font={'size': 14})

            if department:
                dept_name = department['name']
                net.add_node(dept_name, label=f"Department: {dept_name}", color='lightgreen')
                net.add_edge(module_code, dept_name, label='BELONGS_TO', length=300, font={'size': 14})
                net.add_edge(dept_name, fac_name, label='PART_OF', length=300, font={'size': 14})

        if major:
            major_name = major['name']
            net.add_node(major_name, label=f"Major: {major_name}", color='yellow')
            net.add_edge(matric_number, major_name, label='MAJOR_IN', length=300, font={'size': 14})

        if second_major:
            second_major = second_major['name']
            net.add_node(second_major, label=f"Second Major: {second_major}", color='yellow')
            net.add_edge(matric_number, second_major, label='SECOND_MAJOR_IN', length=300, font={'size': 14})

        if module:
          module_code = module['moduleCode']
          net.add_node(module_code, label=f"Module: {module_code}", color='lightblue')
          net.add_edge(matric_number, module_code, label='COMPLETED', length=300, font={'size': 14})
          net.add_edge(module_code, dept_name, label='BELONGS_TO', length=300, font={'size': 14})

    # Display the graph
    net.show("student_graph.html")



