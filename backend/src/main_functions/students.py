import os
from neo4j import GraphDatabase

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()


def create_student_node_and_relationships(
    tx,
    student_name,
    matric_number,
    nric,
    year,
    faculty,
    major,
    second_major,
    modules_completed,
    grades,
):
    tx.run(
        """
        MERGE (s:Student {Matric_Number: $matric_number})
        ON CREATE SET s.Student_Name = $student_name, s.NRIC = $nric, s.Year = $year, s.Grades = $grades
        ON MATCH SET s.Student_Name = $student_name, s.NRIC = $nric, s.Year = $year, s.Grades = $grades
    """,
        matric_number=matric_number,
        student_name=student_name,
        nric=nric,
        year=year,
        grades=grades,
    )

    tx.run(
        """
        MERGE (f:Faculty {name: $faculty})
        WITH f
        MATCH (s:Student {Matric_Number: $matric_number})
        MERGE (s)-[:STUDYING_UNDER]->(f)
    """,
        faculty=faculty,
        matric_number=matric_number,
    )

    tx.run(
        """
        MERGE (m:Major {name: $major})
        WITH m
        MATCH (s:Student {Matric_Number: $matric_number})
        MERGE (s)-[:MAJOR_IN]->(m)
    """,
        major=major,
        matric_number=matric_number,
    )

    if isinstance(second_major, str):
        tx.run(
            """
          MERGE (m:Major {name: $major})
          WITH m
          MATCH (s:Student {Matric_Number: $matric_number})
          MERGE (s)-[:SECOND_MAJOR_IN]->(m)
      """,
            major=second_major,
            matric_number=matric_number,
        )

    if modules_completed:
        for module in modules_completed:
            tx.run(
                """
              MERGE (m:Module {moduleCode: $module_code})
              WITH m
              MATCH (s:Student {Matric_Number: $matric_number})
              MERGE (s)-[:COMPLETED]->(m)
          """,
                matric_number=matric_number,
                module_code=module,
            )


def create_student(data):
    with driver.session() as session:
        student_name = data.get("name")
        matric_number = data.get("matric_number")
        nric = data.get("nric")
        year = data.get("year")
        faculty = data.get("faculty")
        major = data.get("major")
        second_major = data.get("second_major")
        modules_completed = data.get("modules_completed")
        grades = data.get("grades")

        session.execute_write(
            create_student_node_and_relationships,
            student_name,
            matric_number,
            nric,
            year,
            faculty,
            major,
            second_major,
            modules_completed,
            grades,
        )


def modify_student_node_and_relationships(
    tx,
    matric_number,
    student_name=None,
    nric=None,
    year=None,
    faculty=None,
    major=None,
    second_major=None,
    modules_completed=None,
    grades=None,
):
    # Update basic student info
    tx.run(
        """
        MATCH (s:Student {Matric_Number: $matric_number})
        SET s.Student_Name = coalesce($student_name, s.Student_Name),
            s.NRIC = coalesce($nric, s.NRIC),
            s.Year = coalesce($year, s.Year),
            s.Grades = coalesce($grades, s.Grades)
        """,
        matric_number=matric_number,
        student_name=student_name,
        nric=nric,
        year=year,
        grades=grades,
    )

    # Update faculty relationship
    if faculty:
        tx.run(
            """
            MATCH (s:Student {Matric_Number: $matric_number})
            OPTIONAL MATCH (s)-[r:STUDYING_UNDER]->(:Faculty)
            DELETE r
            WITH s
            MERGE (f:Faculty {name: $faculty})
            MERGE (s)-[:STUDYING_UNDER]->(f)
            """,
            matric_number=matric_number,
            faculty=faculty,
        )

    # Update major relationship
    if major:
        tx.run(
            """
            MATCH (s:Student {Matric_Number: $matric_number})
            OPTIONAL MATCH (s)-[r:MAJOR_IN]->(:Major)
            DELETE r
            WITH s
            MERGE (m:Major {name: $major})
            MERGE (s)-[:MAJOR_IN]->(m)
            """,
            matric_number=matric_number,
            major=major,
        )

    # Update second major relationship if provided
    if second_major:
        tx.run(
            """
            MATCH (s:Student {Matric_Number: $matric_number})
            OPTIONAL MATCH (s)-[r:SECOND_MAJOR_IN]->(:Major)
            DELETE r
            WITH s
            MERGE (m:Major {name: $second_major})
            MERGE (s)-[:SECOND_MAJOR_IN]->(m)
            """,
            matric_number=matric_number,
            second_major=second_major,
        )

    # Update completed modules relationships
    if modules_completed:
        # Remove existing COMPLETED relationships
        tx.run(
            """
            MATCH (s:Student {Matric_Number: $matric_number})-[r:COMPLETED]->(:Module)
            DELETE r
            """,
            matric_number=matric_number,
        )
        # Create new COMPLETED relationships
        for module in modules_completed:
            tx.run(
                """
                MATCH (s:Student {Matric_Number: $matric_number})
                MERGE (m:Module {moduleCode: $module_code})
                MERGE (s)-[:COMPLETED]->(m)
                """,
                matric_number=matric_number,
                module_code=module,
            )


def modify_student(data):
    with driver.session() as session:
        matric_number = data.get("matric_number")
        student_name = data.get("name")
        nric = data.get("nric")
        year = data.get("year")
        faculty = data.get("faculty")
        major = data.get("major")
        second_major = data.get("second_major")
        modules_completed = data.get("modules_completed")
        grades = data.get("grades")

        session.execute_write(
            modify_student_node_and_relationships,
            matric_number,
            student_name,
            nric,
            year,
            faculty,
            major,
            second_major,
            modules_completed,
            grades,
        )


def delete_student_node_and_relationships(tx, matric_number):
    tx.run(
        """
        MATCH (s:Student {Matric_Number: $matric_number})
        DETACH DELETE s;
    """,
        matric_number=matric_number,
    )


def delete_student(data):
    with driver.session() as session:
        matric_number = data
        session.execute_write(delete_student_node_and_relationships, matric_number)
