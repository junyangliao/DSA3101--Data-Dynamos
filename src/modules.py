def create_module_node_and_relationships(tx, module_code, title, description, module_credit, department, faculty, prerequisites, preclusions, semesters):
    # Create course node
    tx.run("""
        MERGE (c:Course {moduleCode: $module_code})
        ON CREATE SET c.title = $title, c.description = $description, c.moduleCredit = $module_credit
        ON MATCH SET c.title = $title, c.description = $description, c.moduleCredit = $module_credit
    """, module_code=module_code, title=title, description=description, module_credit=module_credit)

    # Create department and faculty nodes and their relationships
    tx.run("""
        MERGE (d:Department {name: $department})
        MERGE (f:Faculty {name: $faculty})
        MERGE (d)-[:PART_OF]->(f)
        WITH d
        MATCH (c:Course {moduleCode: $module_code}) 
        MERGE (c)-[:BELONGS_TO]->(d)
    """, department=department, faculty=faculty, module_code=module_code)

    # Create relationships for prerequisites
    if isinstance(prerequisites, list) and len(prerequisites) > 0:
      for prerequisite in prerequisites:
          tx.run("""
              MERGE (p:Course {moduleCode: $prerequisite})
              WITH p
              MATCH (c:Course {moduleCode: $module_code})
              MERGE (c)-[:HAS_PREREQUISITE]->(p)
          """, module_code=module_code, prerequisite=prerequisite)

    # Create relationships for preclusions
    if isinstance(preclusions, list) and len(preclusions) > 0:
      for preclusion in preclusions:
          tx.run("""
              MERGE (p:Course {moduleCode: $preclusion})
              WITH p
              MATCH (c:Course {moduleCode: $module_code})
              MERGE (c)-[:HAS_PRECLUSION]->(p)
          """, module_code=module_code, preclusion = preclusion)

    # Create relationships for semesters
    for semester in semesters:
        tx.run("""
            MERGE (s:Semester {number: $semester})
            WITH s
            MATCH (c:Course {moduleCode: $module_code})
            MERGE (c)-[:OFFERED_IN]->(s)
        """, semester=semester, module_code=module_code)

def create_modules(data):
    driver = GraphDatabase.driver("neo4j+s://67203e25.databases.neo4j.io", auth=("neo4j", "KUKTrqvpgw9FLuAam0cCauBnsdQsTC3CW1lCboUWhaA"))
    session = driver.session()

    with driver.session() as session:
        for _, row in data.iterrows():
            module_code = row['moduleCode']
            title = row['title']
            description = row['description']
            module_credit = row['moduleCredit']
            department = row['department']
            faculty = row['faculty']
            prerequisites = row['prerequisite']  # Assuming this is a list
            preclusions = row['preclusion']
            semesters = []
            if row['semester_01'] > 0: semesters.append(1)
            if row['semester_02'] > 0: semesters.append(2)
            if row['semester_03'] > 0: semesters.append(3)
            if row['semester_04'] > 0: semesters.append(4)
            
            session.execute_write(create_module_node_and_relationships, module_code, title, description, module_credit, department, faculty, prerequisites, preclusions, semesters)

# (Unfinished)
# def get_default_modules(tx, n = 25):
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


    
