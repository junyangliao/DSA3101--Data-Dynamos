import os
from neo4j import GraphDatabase

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()


def create_staff_node_and_relationships(
    tx,
    employee_name,
    employee_id,
    nric,
    birth_date,
    join_date,
    department,
    modules_taught,
):
    tx.run(
        """
        MERGE (st:Staff {Employee_ID: $employee_id})
        ON CREATE SET st.Employee_Name = $employee_name, st.NRIC = $nric, st.DOB = $birth_date, st.DOJ = $join_date
        ON MATCH SET st.Employee_Name = $employee_name, st.NRIC = $nric, st.DOB = $birth_date, st.DOJ = $join_date
    """,
        employee_id=employee_id,
        employee_name=employee_name,
        nric=nric,
        birth_date=birth_date,
        join_date=join_date,
    )

    tx.run(
        """
        MERGE (d:Department {name: $department})
        WITH d
        MATCH (st:Staff {Employee_ID: $employee_id})
        MERGE (st)-[:EMPLOYED_UNDER]->(d)
    """,
        department=department,
        employee_id=employee_id,
    )

    tx.run(
        """
        MERGE (m:Module {moduleCode: $module_code})
        WITH m
        MATCH (st:Staff {Employee_ID: $employee_id})
        MERGE (m)-[:TAUGHT_BY]->(st)
    """,
        employee_id=employee_id,
        module_code=modules_taught,
    )


def create_staff(data):
    with driver.session() as session:
        employee_name = data.get("employee_name")
        employee_id = data.get("employee_id")
        nric = data.get("nric")
        birth_date = data.get("dob")
        join_date = data.get("doj")
        department = data.get("department")
        modules_taught = data.get("modules_taught")

        session.execute_write(
            create_staff_node_and_relationships,
            employee_name,
            employee_id,
            nric,
            birth_date,
            join_date,
            department,
            modules_taught,
        )

def modify_staff_node_and_relationships(
    tx,
    employee_name = None,
    employee_id = None,
    nric = None,
    birth_date = None,
    join_date = None,
    department = None,
    modules_taught = None,
):
    # Update basic student info
    tx.run(
        """
        MATCH (s:Staff {Employee_Name: $employee_name})
        SET s.Employee_ID = coalesce($employee_id, s.Employee_ID),
            s.NRIC = coalesce($nric, s.NRIC),
            s.DOB = coalesce($birth_date, s.DOB),
            s.DOJ = coalesce($join_date, s.DOJ)
        """,
        employee_id=employee_id,
        employee_name=employee_name,
        nric=nric,
        birth_date=birth_date,
        join_date=join_date,
    )

    # Update faculty relationship
    if department:
        tx.run(
            """
            MATCH (s:Staff {Employee_Name: $employee_name})
            OPTIONAL MATCH (s)-[r:EMPLOYED_UNDER]->(:Department)
            DELETE r
            WITH s
            MERGE (d:Department {name: $department})
            MERGE (s)-[:EMPLOYED_UNDER]->(d)
            """,
            employee_name=employee_name,
            department=department,
        )

    # Update major relationship
    if modules_taught:
        tx.run(
            """
            MATCH (s:Staff {Employee_Name: $employee_name})
            OPTIONAL MATCH (:Module)-[r:TAUGHT_BY]->(s)
            DELETE r
            WITH s
            MERGE (m:Module {moduleCode: $module_code})
            MERGE (m)-[:TAUGHT_BY]->(s)
            """,
            employee_name=employee_name,
            module_code=modules_taught,
        )

def modify_staff(data):
    with driver.session() as session:
        employee_name = data.get("employee_name")
        employee_id = data.get("employee_id")
        nric = data.get("nric")
        birth_date = data.get("dob")
        join_date = data.get("doj")
        department = data.get("department")
        modules_taught = data.get("modules_taught")

        session.execute_write(
            modify_staff_node_and_relationships,
            employee_name,
            employee_id,
            nric,
            birth_date,
            join_date,
            department,
            modules_taught,
        )

def delete_staff_node_and_relationships(tx, employee_name):
    tx.run(
        """
        MATCH (st:Staff {Employee_Name: $employee_name})
        DETACH DELETE st;
    """,
        employee_name=employee_name,
    )


def delete_staff(data):
    with driver.session() as session:
        employee_name = data
        session.execute_write(delete_staff_node_and_relationships, employee_name)
