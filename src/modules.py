import os
from neo4j import GraphDatabase

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()

def create_module_node_and_relationships(tx, module_code, title, description, module_credit, department, faculty, prerequisites, preclusions, semesters):
    # Create course node
    tx.run("""
        MERGE (m:Module {moduleCode: $module_code})
        ON CREATE SET m.title = $title, m.description = $description, m.moduleCredit = $module_credit
        ON MATCH SET m.title = $title, m.description = $description, m.moduleCredit = $module_credit
    """, module_code=module_code, title=title, description=description, module_credit=module_credit)

    # Create department and faculty nodes and their relationships
    tx.run("""
        MERGE (d:Department {name: $department})
        MERGE (f:Faculty {name: $faculty})
        MERGE (d)-[:PART_OF]->(f)
        WITH d
        MATCH (m:Module {moduleCode: $module_code}) 
        MERGE (m)-[:BELONGS_TO]->(d)
    """, department=department, faculty=faculty, module_code=module_code)

    # Create relationships for prerequisites
    if isinstance(prerequisites, list) and len(prerequisites) > 0:
      for prerequisite in prerequisites:
          tx.run("""
              MERGE (p:Module {moduleCode: $prerequisite})
              WITH p
              MATCH (m:Module {moduleCode: $module_code})
              MERGE (m)-[:HAS_PREREQUISITE]->(p) 
          """, module_code=module_code, prerequisite=prerequisite)

    # Create relationships for preclusions
    if isinstance(preclusions, list) and len(preclusions) > 0:
      for preclusion in preclusions:
          tx.run("""
              MERGE (p:Module {moduleCode: $preclusion})
              WITH p
              MATCH (m:Module {moduleCode: $module_code})
              MERGE (m)-[:HAS_PRECLUSION]->(p)
          """, module_code=module_code, preclusion = preclusion)

    # Create relationships for semesters
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


    
