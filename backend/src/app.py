from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from neo4j import GraphDatabase
from main_functions.students import create_student_node_and_relationships, create_student, create_students, delete_student_node_and_relationships, delete_student, get_students_all_connections
from pyvis.network import Network
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password),max_connection_pool_size=10)

# Function to create a new student individually
@app.route('/student', methods=['POST'])
def create_new_student():
    student_data = request.json
    s = create_student(student_data)
    return jsonify({'message': 'Student created successfully'}), 201

# Function to create graph showing the staff distribution by department
@app.route('/staff-distribution', methods=['GET'])
def staff_distribution():
    with driver.session() as session:
        print("Received a request at /staff-distribution")  # Debug log
        query = """
        MATCH (d:Department)<-[:employed_under]-(s:Staff)
        RETURN d.name AS department, COUNT(s) AS staff_count
        """
        results = session.run(query,timeout = 120).data()
        print(f"Results: {results}")  # Debug log

    return jsonify(results)

@app.route('/student-distribution-faculty', methods=['GET'])
def student_faculty_distribution():
    with driver.session() as session:
        print("Received a request at /staff-distribution-faculty")  # Debug log
        query = """
        MATCH (f:Faculty)<-[:studying_under]-(s:Student)
        RETURN f.name AS faculty, COUNT(s) AS student_count
        """
        results = session.run(query,timeout = 120).data()
    print(f"Results: {results}")  # Debug log

    return jsonify(results)

@app.route('/student-distribution-major', methods=['GET'])
def student_major_distribution():
    with driver.session() as session:
        print("Received a request at /staff-distribution-major")  # Debug log
        query = """
        MATCH (m:Major)<-[:major_in]-(s:Student)
        RETURN m.name AS major, COUNT(s) AS student_count
        """
        results = session.run(query,timeout = 120).data()
    print(f"Results: {results}")  # Debug log

    return jsonify(results)

@app.route('/visualize-module', methods=['POST'])
def visualize_module():
    module_code = request.get_json().get('module_code')
    with driver.session() as session:
        query = """
        MATCH (m:Module {moduleCode: $module_code})
        OPTIONAL MATCH (m)-[:BELONGS_TO]->(d:Department)
        OPTIONAL MATCH (d)-[:PART_OF]->(f:Faculty)
        OPTIONAL MATCH (m)-[:HAS_PREREQUISITE]->(p:Module)
        OPTIONAL MATCH (m)-[:HAS_PRECLUSION]->(pr:Module)
        OPTIONAL MATCH (m)-[:OFFERED_IN]->(s:Semester)
        RETURN m, d, f, p, pr, s;
        """
        data = session.run(query, module_code=module_code).data()

        print(f"Data fetched for module_code '{module_code}':", data)

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
    html_filename = f"{module_code}_graph.html"
    net.show(html_filename)
    return {"file_url": f"/visualizations/{html_filename}"}

@app.route('/visualize-student', methods=['POST'])
def visualize_student():
    matric_number = request.get_json().get('matric_number')
    with driver.session() as session:
        query = """
        MATCH (s:Student {matricNumber: $matric_number})
        OPTIONAL MATCH (s)-[:studying_under]->(f:Faculty)
        OPTIONAL MATCH (d:Department)-[:PART_OF]->(f:Faculty)
        OPTIONAL MATCH (s)-[:major_in]->(m:Major)
        OPTIONAL MATCH (s)-[:SECOND_MAJOR_IN]->(sm:secondMajor)
        OPTIONAL MATCH (s)-[:completed]->(mod:Module)
        RETURN s, d, f, m, sm, mod;
        """
        data = session.run(query, matric_number=matric_number).data()

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
    html_filename = f"{matric_number}_graph.html"
    net.show(html_filename)
    return {"file_url": f"/visualizations/{html_filename}"}

@app.route('/visualizations/<path:filename>')
def serve_visualization(filename):
    file_path = os.path.join(os.getcwd(), filename)
    response = send_from_directory(os.getcwd(), filename)
    os.remove(file_path)
    return response

@app.route('/test-neo4j', methods=['GET'])
def test_neo4j():
    with driver.session() as session:
        try:
            session.run("MATCH (n) RETURN n LIMIT 1")
            return jsonify({"status": "Neo4j connection successful!"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 5000)