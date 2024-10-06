def create_staff_node_and_relationships(tx, employee_name, employee_id, nric, birth_date, join_date, department, modules_taught):
    tx.run("""
        MERGE (st:Staff {employeeId: $employee_id})
        ON CREATE SET st.employeeName = $employee_name, st.nric = $nric, st.birthDate = $birth_date, st.joinDate = $join_date
        ON MATCH SET st.employeeName = $employee_name, st.nric = $nric, st.birthDate = $birth_date, st.joinDate = $join_date
    """, employee_id = employee_id, employee_name = employee_name, nric = nric, birth_date = birth_date, join_date = join_date)

    tx.run("""
        MERGE (d:Department {name: $department})
        WITH d
        MATCH (st:Staff {employeeId: $employee_id})
        MERGE (st)-[:employed_under]->(d)
    """, department=department, employee_id=employee_id)

    tx.run("""
        MERGE (c:Course {moduleCode: $module_code})
        WITH c
        MATCH (st:Staff {employeeId: $employee_id})
        MERGE (c)-[:taught_by]->(st)
    """, employee_id=employee_id, module_code=modules_taught)

def create_staffs(data):
    driver = GraphDatabase.driver("neo4j+s://67203e25.databases.neo4j.io", auth=("neo4j", "KUKTrqvpgw9FLuAam0cCauBnsdQsTC3CW1lCboUWhaA"))
    session = driver.session()

    with driver.session() as session:
        for _, row in staff.iterrows():
            employee_name = row['Employee Name']
            employee_id = row['Employee ID']
            nric = row['NRIC']
            birth_date = row['DOB']
            join_date = row['DOJ']
            department = row['Department_ID']
            modules_taught = row['Modules Taught']

            session.execute_write(create_staff_node_and_relationships, employee_name, employee_id, nric, birth_date, join_date, department, modules_taught)