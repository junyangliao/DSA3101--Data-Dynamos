import os
import pandas as pd
import ast
from neo4j import GraphDatabase
from utils import format_node,format_relationship

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
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
          MERGE (m:Major {name: $major})
          WITH m
          MATCH (s:Student {matricNumber: $matric_number})
          MERGE (s)-[:SECOND_MAJOR_IN]->(m)
      """, major=second_major, matric_number=matric_number)

    if modules_completed:
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
        faculty = data.get('faculty')
        major = data.get('major')
        second_major = data.get('second major')
        modules_completed = data.get('modules completed')
        grades = data.get('grades')

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
            modules_completed = ast.literal_eval(row['Modules_Completed'])
            grades = row['Grades']

            session.execute_write(create_student_node_and_relationships, student_name, matric_number, nric, year, faculty, major, second_major, modules_completed, grades)

def delete_student_node_and_relationships(tx, matric_number):
    tx.run("""
        MATCH (s:Student {matricNumber: $matric_number})
        DETACH DELETE s;
    """, matric_number=matric_number)

def delete_student(data):
    with driver.session() as session:
        matric_number = data
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
    query_data = session.run(query).data()
    
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



