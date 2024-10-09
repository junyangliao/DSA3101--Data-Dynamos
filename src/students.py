import os
from neo4j import GraphDatabase

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
        MERGE (s)-[:studying_under]->(f)
    """, faculty=faculty, matric_number=matric_number)

    tx.run("""
        MERGE (m:Major {name: $major})
        WITH m
        MATCH (s:Student {matricNumber: $matric_number})
        MERGE (s)-[:major_in]->(m)
    """, major=major, matric_number=matric_number)
    
    if isinstance(second_major,str):
      tx.run("""
          MERGE (sm:secondMajor {name: $second_major})
          WITH sm
          MATCH (s:Student {matricNumber: $matric_number})
          MERGE (s)-[:second_major_in]->(sm)
      """, second_major=second_major, matric_number=matric_number)

    if isinstance(modules_completed, list) and len(modules_completed) > 0:
      for module in modules_completed:
          tx.run("""
              MERGE (c:Course {moduleCode: $module_code})
              WITH c
              MATCH (s:Student {matricNumber: $matric_number})
              MERGE (s)-[:completed]->(c)
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

def create_students(data):
    with driver.session() as session:
        for _, row in data.iterrows():
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

