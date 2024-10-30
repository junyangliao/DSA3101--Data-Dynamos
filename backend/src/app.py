from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from neo4j import GraphDatabase
from main_functions.students import create_student, create_students, delete_student
from main_functions.modules import create_module, create_modules, delete_module
from main_functions.job_skills import create_job_and_skills, create_jobs_and_skills, delete_job
from main_functions.staffs import create_staffs, delete_staff
from main_functions.job_recommendations import get_job_recommendations
from utils import evaluate_prompt, serialize_neo4j_value
from pyvis.network import Network
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password),max_connection_pool_size=10)

# Function to create a new student individually
@app.route('/student', methods=['POST'])
def create_new_student():
    student_data = request.json
    create_student(student_data)
    return jsonify({'message': 'Student created successfully'}), 201

# Function to create a new student individually
@app.route('/module', methods=['POST'])
def create_new_module():
    module_data = request.json
    create_module(module_data)
    return jsonify({'message': 'Module created successfully'}), 201

# Function to create a new student individually
@app.route('/job', methods=['POST'])
def create_new_job():
    job_data = request.json
    create_job_and_skills(job_data)
    return jsonify({'message': 'Job created successfully'}), 201

@app.route('/upload-student-csv', methods=['POST'])
def upload_student_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_csv(file)
        create_students(df)
        return jsonify({'message': 'CSV data integrated successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/upload-modules-csv', methods=['POST'])
def upload_modules_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_csv(file)
        create_modules(df)
        return jsonify({'message': 'CSV data integrated successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/upload-jobs-csv', methods=['POST'])
def upload_jobs_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_csv(file)
        create_jobs_and_skills(df)
        return jsonify({'message': 'CSV data integrated successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/upload-staffs-csv', methods=['POST'])
def upload_staffs_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_csv(file)
        create_staffs(df)
        return jsonify({'message': 'CSV data integrated successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete-module', methods=['POST'])
def delete_module_node():
    data = request.json
    module_code = data.get('module_code')

    if not module_code:
        return jsonify({'error': 'Module Code is required'}), 400
    
    delete_module(module_code)

    return jsonify({'message': f"Module with Module Code {module_code} deleted successfully"}), 201

@app.route('/delete-student', methods=['POST'])
def delete_student_node():
    data = request.json
    matric_number = data.get('matric_number')

    if not matric_number:
        return jsonify({'error': 'Student Matric Number is required'}), 400
    
    delete_student(matric_number)

    return jsonify({'message': f"Student with Matric Number {matric_number} deleted successfully"}), 201

@app.route('/delete-staff', methods=['POST'])
def delete_staff_node():
    data = request.json
    employee_id = data.get('employee_id')

    if not employee_id:
        return jsonify({'error': 'Employee ID is required'}), 400
    
    delete_staff(employee_id)

    return jsonify({'message': f"Employee with ID {employee_id} deleted successfully"}), 201

@app.route('/delete-job', methods=['POST'])
def delete_job_node():
    data = request.json
    job_title = data.get('job_title')

    if not job_title:
        return jsonify({'error': 'Job Title is required'}), 400
    
    delete_job(job_title)

    return jsonify({'message': f"Job with Job Title {job_title} deleted successfully"}), 201

# Function to create graph showing the staff distribution by department
@app.route('/staff-distribution', methods=['GET'])
def staff_distribution():
    with driver.session() as session:
        print("Received a request at /staff-distribution")  # Debug log
        query = """
        MATCH (d:Department)<-[:EMPLOYED_UNDER]-(s:Staff)
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
        MATCH (f:Faculty)<-[:STUDYING_UNDER]-(s:Student)
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
        MATCH (m:Major)<-[:MAJOR_IN]-(s:Student)
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
        OPTIONAL MATCH (m)-[:MUST_NOT_HAVE_TAKEN_ONE_OF]->(preclu:PreclusionGroup)
        OPTIONAL MATCH (m)-[:MUST_HAVE_TAKEN_ONE_OF]->(prereq:PrerequisiteGroup)
        OPTIONAL MATCH (m)-[:OFFERED_IN]->(s:Semester)
        RETURN m, d, f, preclu, prereq, s;
        """
        data = session.run(query, module_code=module_code).data()

        print(f"Data fetched for module_code '{module_code}':", data)

        # Initialize the network graph visualization
        net = Network(notebook=True, cdn_resources='in_line')

        # Update physics settings to improve readability
        net.toggle_physics(True)  # Enable physics

        net.set_options("""
        {
            "nodes": {
                "shape": "dot",
                "size": 30,
                "font": {
                    "size": 16
                }
            },
            "edges": {
                "length": 500,
                "font": {
                    "size": 14
                }
            },
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -150,
                    "centralGravity": 0.01,
                    "springLength": 400,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based",
                "timestep": 0.35
            }
        }
        """)

        # Add nodes and edges to the visualization
        for record in data:
            module = record['m']
            department = record.get('d')
            faculty = record.get('f')
            preclusion_group = record.get('preclu')
            prereq_group = record.get('prereq')
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

            if prereq_group:
                prereq_grouped = prereq_group['name']
                net.add_node(prereq_grouped, label= f"Prerequisite Group: {prereq_grouped}", color = 'grey')
                net.add_edge(module_code, prereq_grouped, label='MUST_HAVE_TAKEN_ONE_OF', length=300, font={'size':14})

            # Add preclusions
            if preclusion_group:
                preclusion_group_codes = preclusion_group['name']
                net.add_node(preclusion_group_codes, label=f"Preclusion Group: {preclusion_group_codes}", color='orange')
                net.add_edge(module_code, preclusion_group_codes, label='MUST_NOT_HAVE_TAKEN_ONE_OF', length=300, font={'size': 14})

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
        OPTIONAL MATCH (s)-[:STUDYING_UNDER]->(f:Faculty)
        OPTIONAL MATCH (d:Department)-[:PART_OF]->(f:Faculty)
        OPTIONAL MATCH (s)-[:MAJOR_IN]->(m:Major)
        OPTIONAL MATCH (s)-[:SECOND_MAJOR_IN]->(sm:secondMajor)
        OPTIONAL MATCH (s)-[:COMPLETED]->(mod:Module)
        RETURN s, d, f, m, sm, mod;
        """
        data = session.run(query, matric_number=matric_number).data()

        # Initialize the network graph visualization
        net = Network(notebook=True, cdn_resources='in_line')

                # Update physics settings to improve readability
        net.toggle_physics(True)  # Enable physics

        # Modify the physics options to make the graph more readable
        net.set_options("""
        {
            "nodes": {
                "shape": "dot",
                "size": 30,
                "font": {
                    "size": 16
                }
            },
            "edges": {
                "length": 300,
                "font": {
                    "size": 14
                }
            },
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -150,
                    "centralGravity": 0.01,
                    "springLength": 400,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based",
                "timestep": 0.35
            }
        }
        """)

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

@app.route('/visualize-staff', methods=['POST'])
def visualize_staff():
    employee_id = request.get_json().get('employee_id')
    with driver.session() as session:
        query = """
        MATCH (st:Staff {employeeId: $employee_id})
        OPTIONAL MATCH (st)-[:EMPLOYED_UNDER]->(d:Department)
        OPTIONAL MATCH (d:Department)-[:PART_OF]->(f:Faculty)
        OPTIONAL MATCH (m:Module)-[:TAUGHT_BY]->(st)
        RETURN st,d,f,m
        """
        data = session.run(query, employee_id=employee_id).data()

        # Initialize the network graph visualization
        net = Network(notebook=True, cdn_resources='in_line')

                # Update physics settings to improve readability
        net.toggle_physics(True)  # Enable physics

        # Modify the physics options to make the graph more readable
        net.set_options("""
        {
            "nodes": {
                "shape": "dot",
                "size": 30,
                "font": {
                    "size": 16
                }
            },
            "edges": {
                "length": 300,
                "font": {
                    "size": 14
                }
            },
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -150,
                    "centralGravity": 0.01,
                    "springLength": 400,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based",
                "timestep": 0.35
            }
        }
        """)

        # Add nodes and edges to the visualization
        for record in data:
            staff = record['st']
            department = record.get('d')
            faculty = record.get('f')
            module = record.get('m')

            employee_name = staff['employeeName']
            net.add_node(employee_name, label=f"Employee Name: {employee_name}", color='lightblue')

            if department:
                dept_name = department['name']
                net.add_node(dept_name, label=f"Department: {dept_name}", color='lightgreen')
                net.add_edge(dept_name, employee_name, label='EMPLOYED_UNDER', length=300, font={'size': 14})

            if faculty:
                fac_name = faculty['name']
                net.add_node(fac_name, label=f"Faculty: {fac_name}", color='lightcoral')
                net.add_edge(dept_name, fac_name, label='STUDYING_UNDER', length=300, font={'size': 14})
            
            if module:
                module_code = module['moduleCode']
                net.add_node(module_code, label=f"Module: {module_code}", color='lightblue')
                net.add_edge(employee_name, module_code, label='TAUGHT_BY', length=300, font={'size': 14})

    # Display the graph
    html_filename = f"{employee_name}_graph.html"
    net.show(html_filename)
    return {"file_url": f"/visualizations/{html_filename}"}

@app.route('/visualizations/<path:filename>')
def serve_visualization(filename):
    file_path = os.path.join(os.getcwd(), filename)
    response = send_from_directory(os.getcwd(), filename)
    os.remove(file_path)
    return response

@app.route('/process_query', methods=['POST'])
def process_query():
    query = request.get_json().get('query')

    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        cypher_query, result = evaluate_prompt(query)
        if isinstance(result,list):
            serialized_result = result
        elif isinstance(result[0],list):
            serialized_result = result
        else:
            serialized_result = [serialize_neo4j_value(record) for record in result][0]['properties']
        
        return jsonify({
            'cypher_query': cypher_query,
            'result': serialized_result
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/job-recommendations', methods=['POST'])
def job_recommendations():
    data = request.get_json()
    job_description = data.get('jobDescription')
    matric_number = data.get('matricNumber')
    
    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400
    
    try:
        recommendations = get_job_recommendations(job_description, matric_number)
        return jsonify({'recommendations': recommendations}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500