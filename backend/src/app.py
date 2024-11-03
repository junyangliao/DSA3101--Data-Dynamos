from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from neo4j import GraphDatabase
from main_functions.students import create_student, create_students, delete_student
from main_functions.modules import create_module, create_modules, delete_module
from main_functions.job_skills import create_jobs_and_skills, delete_job
from main_functions.staffs import create_staff, create_staffs, delete_staff
from main_functions.job_recommendations import get_job_recommendations
from utils import evaluate_prompt, capitalize_name
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
@app.route('/create-student', methods=['POST'])
def create_new_student():
    student_data = request.json

    if not student_data:
        return jsonify({'message': f"No Student Data Found"}),400
    
    matric_number = student_data.get('matric_number')

    create_student(student_data)

    return jsonify({'message': f"Student with Matric Number {matric_number} created successfully"}), 201

# Function to create a new module individually
@app.route('/create-module', methods=['POST'])
def create_new_module():
    module_data = request.json

    if not module_data:
        return jsonify({'message': f"No Module Data Found"}),400
    
    module_code = module_data.get('module_code')
    
    create_module(module_data)

    return jsonify({'message': f"Module with module code {module_code} created successfully"}), 201

# Function to create a new staff individually
@app.route('/create-staff', methods=['POST'])
def create_new_staff():
    staff_data = request.json

    if not staff_data:
        return jsonify({'message': f"No Staff Data Found"}),400
    
    staff_name = staff_data.get('employee_name')
    
    create_staff(staff_data)

    return jsonify({'message': f"Staff with name {staff_name} created successfully"}), 201

# Function to create a new job individually
@app.route('/create-job', methods=['POST'])
def create_new_job():
    job_data = request.json

    if not job_data:
        return jsonify({'message': f"No Job Data Found"}),400
    
    create_jobs_and_skills(job_data)

    return jsonify({'message': 'Job created successfully'}), 201

# Function to upload student data as a csv
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

# Function to upload modules data as a csv
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

# Function to upload jobs data as a csv
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

# Function to upload staffs data as a csv
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

# Function to delete individual module 
@app.route('/delete-module', methods=['POST'])
def delete_module_node():
    data = request.json
    module_code = data.get('module_code')

    if not module_code:
        return jsonify({'error': 'Module Code is required'}), 400
    
    delete_module(module_code)

    return jsonify({'message': f"Module with Module Code {module_code} deleted successfully"}), 201

# Function to delete individual student
@app.route('/delete-student', methods=['POST'])
def delete_student_node():
    data = request.json
    matric_number = data.get('matric_number')

    if not matric_number:
        return jsonify({'error': 'Student Matric Number is required'}), 400
    
    delete_student(matric_number)

    return jsonify({'message': f"Student with Matric Number {matric_number} deleted successfully"}), 201

# Function to delete individual staff 
@app.route('/delete-staff', methods=['POST'])
def delete_staff_node():
    data = request.json
    employee_id = data.get('employee_id')

    if not employee_id:
        return jsonify({'error': 'Employee ID is required'}), 400
    
    delete_staff(employee_id)

    return jsonify({'message': f"Employee with ID {employee_id} deleted successfully"}), 201

# Function to delete individual job
@app.route('/delete-job', methods=['POST'])
def delete_job_node():
    data = request.json
    job_title = data.get('job_title')

    if not job_title:
        return jsonify({'error': 'Job Title is required'}), 400
    
    delete_job(job_title)

    return jsonify({'message': f"Job with Job Title {job_title} deleted successfully"}), 201

# Function to create dashboard component for student distribution among faculties
@app.route('/student-distribution-faculty', methods=['GET'])
def student_faculty_distribution():
    with driver.session() as session:
        query = """
        MATCH (f:Faculty)<-[:STUDYING_UNDER]-(s:Student)
        RETURN f.name AS faculty, COUNT(s) AS student_count
        """
        results = session.run(query,timeout = 120).data() 

    return jsonify(results)

# Function to create dashboard component for student distribution among majors
@app.route('/student-distribution-major', methods=['GET'])
def student_major_distribution():
    with driver.session() as session:
        query = """
        MATCH (m:Major)<-[:MAJOR_IN]-(s:Student)
        RETURN m.name AS major, COUNT(s) AS student_count
        """
        results = session.run(query,timeout = 120).data()
    print(f"Results: {results}")

    return jsonify(results)

# Function to create module visualization on modules page
@app.route('/visualize-module', methods=['POST'])
def visualize_module():
    user_input = request.get_json().get('module_code')
    module_code = user_input.upper()
    with driver.session() as session:
        query = """
        MATCH (m:Module {moduleCode: $module_code})
        OPTIONAL MATCH (m)-[:BELONGS_TO]->(d:Department)
        OPTIONAL MATCH (d)-[:PART_OF]->(f:Faculty)
        OPTIONAL MATCH (m)-[:MUST_NOT_HAVE_TAKEN_ONE_OF]->(preclu:PreclusionGroup)
        OPTIONAL MATCH (m)-[:MUST_HAVE_TAKEN_ONE_OF]->(prereq:PrerequisiteGroup)
        OPTIONAL MATCH (m)-[:OFFERED_IN]->(s:Semester)
        OPTIONAL MATCH (m)-[:TAUGHT_BY]->(st:Staff)
        RETURN m, d, f, preclu, prereq, s, st;
        """
        data = session.run(query, module_code=module_code).data()

        print(f"Data fetched for module_code '{module_code}':", data)

        # Initialize the network graph visualization
        net = Network(cdn_resources='in_line')

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
            prof = record.get('st')

            # Add module node
            module_code = module['moduleCode']
            module_data = {
                'moduleCode': module.get('moduleCode',''),
                'title': module.get('title', ''),
                'moduleCredit': module.get('moduleCredit', ''),
                'description': module.get('description', '')
            }
            net.add_node(module_code, label=f"Module: {module_code}", color='lightblue', data=module_data )

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
            
            if prof:
                prof_name = prof['employeeName']
                net.add_node(prof_name, label=f"Professor: {prof_name}", color='darkgreen')
                net.add_edge(module_code, prof_name, label='TAUGHT_BY', length=300, font={'size': 14})

    # Display the graph
    html_filename = f"{module_code}_graph.html"
    net.write_html(html_filename)
    with open(html_filename, "a") as f:
        f.write("""
        <style>
        #nodeModal {
            display: none;
            position: fixed;
            z-index: 1;
            right: 0;
            top: 0;
            width: 400px;
            height: 100vh;
            background-color: white;
            box-shadow: -2px 0px 5px rgba(0, 0, 0, 0.3);
            padding: 20px;
            overflow-y: auto;
            margin-top: 10px;
            margin-bottom: 10px;
            border-radius: 5px 0 0 5px; 
        }
        #modalContent {
            max-width: 100%;
        }
        #closeModal {
            position: absolute;
            top: 15px;
            left: 15px;
            font-size: 24px;
            cursor: pointer;
            color: #555;
        }
        #overlay {
            display: none;
            position: fixed;
            z-index: 0;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }
        #modalTitle {
        margin-left: 10px; 
        padding-left: 10px;
        }
        </style>

        <div id="overlay"></div>
        <div id="nodeModal">
            <span id="closeModal">&times;</span>
            <div id="modalContent">
                <h2 id="modalTitle">Node Details</h2>
                <p id="modalData"></p>
            </div>
        </div>

        <script type="text/javascript">
        document.getElementById("closeModal").onclick = function() {
            document.getElementById("nodeModal").style.display = "none";
            document.getElementById("overlay").style.display = "none";
        }

        network.on("click", function(params) {
            if (params.nodes.length > 0) {
                var nodeId = params.nodes[0];
                var node = network.body.data.nodes.get(nodeId);

                if (node.label.startsWith("Module:")) {
                    var moduleData = node.data || {};
                    var title = moduleData.title || "No Title";
                    var moduleCode = moduleData.moduleCode || "No Module Code";
                    var moduleCredit = moduleData.moduleCredit || "N/A";
                    var description = moduleData.description || "No Description available.";

                    document.getElementById("modalTitle").innerText = node.label;
                    document.getElementById("modalData").innerHTML = `
                        <strong>Module Code:</strong> ${moduleCode} <br>
                        <strong>Module Credit:</strong> ${moduleCredit} <br>
                        <strong>Description:</strong> ${description}
                    `;
                    document.getElementById("nodeModal").style.display = "flex";
                }
            }
        });
        </script>
        """)

    return {"file_url": f"/visualizations/{html_filename}"}

# Function to create student visualization on students page
@app.route('/visualize-student', methods=['POST'])
def visualize_student():
    user_input = request.get_json().get('matric_number')
    matric_number = user_input.upper()
    with driver.session() as session:
        query = """
        MATCH (s:Student {matricNumber: $matric_number})
        OPTIONAL MATCH (s)-[:STUDYING_UNDER]->(f:Faculty)
        OPTIONAL MATCH (d:Department)-[:PART_OF]->(f:Faculty)
        OPTIONAL MATCH (s)-[:MAJOR_IN]->(m:Major)
        OPTIONAL MATCH (s)-[:SECOND_MAJOR_IN]->(sm:secondMajor)
        OPTIONAL MATCH (s)-[:COMPLETED]->(mod:Module)
        RETURN s, d, f, m, sm, COLLECT(mod) AS completedModules;
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
            completed_modules = record.get('completedModules', [])

            matric_number = student['matricNumber']
            student_data = {
                'studentName': student.get('studentName',''),
                'matricNumber': student.get('matricNumber', ''),
                'grades': student.get('grades', ''),
                'nric': student.get('nric', ''),
                'completedModules': [module['moduleCode'] for module in completed_modules]
            }
            net.add_node(matric_number, label=f"Student: {matric_number}", color='lightblue', data=student_data)

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

    # Display the graph
    html_filename = f"{matric_number}_graph.html"
    net.write_html(html_filename)
    with open(html_filename, "a") as f:
        f.write("""
        <style>
        #nodeModal {
            display: none;
            position: fixed;
            z-index: 1;
            right: 0;
            top: 0;
            width: 400px;
            height: 100vh;
            background-color: white;
            box-shadow: -2px 0px 5px rgba(0, 0, 0, 0.3);
            padding: 20px;
            overflow-y: auto;
            margin-top: 10px;
            margin-bottom: 10px;
            border-radius: 5px 0 0 5px; 
        }
        #modalContent {
            max-width: 100%;
        }
        #closeModal {
            position: absolute;
            top: 15px;
            left: 15px;
            font-size: 24px;
            cursor: pointer;
            color: #555;
        }
        #overlay {
            display: none;
            position: fixed;
            z-index: 0;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }
        #modalTitle {
        margin-left: 10px; 
        padding-left: 10px;
        }
        </style>

        <div id="overlay"></div>
        <div id="nodeModal">
            <span id="closeModal">&times;</span>
            <div id="modalContent">
                <h2 id="modalTitle">Node Details</h2>
                <p id="modalData"></p>
            </div>
        </div>

        <script type="text/javascript">
        document.getElementById("closeModal").onclick = function() {
            document.getElementById("nodeModal").style.display = "none";
            document.getElementById("overlay").style.display = "none";
        }

        network.on("click", function(params) {
            if (params.nodes.length > 0) {
                var nodeId = params.nodes[0];
                var node = network.body.data.nodes.get(nodeId);

                if (node.label.startsWith("Student:")) {
                    var studentData = node.data || {};
                    var title = studentData.title || "No Title";
                    var studentName = studentData.studentName || "No Student Found";
                    var matricNumber = studentData.matricNumber || "N/A";
                    var grades = studentData.grades || "N/A";
                    var nric = studentData.nric || "N/A";
                    var completedModules = studentData.completedModules.join(', ') || "N/A";

                    document.getElementById("modalTitle").innerText = node.label;
                    document.getElementById("modalData").innerHTML = `
                        <strong>Student Name:</strong> ${studentName} <br>
                        <strong>Matric Number:</strong> ${matricNumber} <br>
                        <strong>Grades:</strong> ${grades} <br>
                        <strong>NRIC:</strong> ${nric} <br>
                        <strong>Modules Completed:</strong> ${completedModules}
                    `;
                    document.getElementById("nodeModal").style.display = "flex";
                }
            }
        });
        </script>
        """)
    return {"file_url": f"/visualizations/{html_filename}"}

# Function to create staff visualization on staff page
@app.route('/visualize-staff', methods=['POST'])
def visualize_staff():
    user_input = request.get_json().get('employee_name')
    employee_name = capitalize_name(user_input)
    with driver.session() as session:
        query = """
        MATCH (st:Staff {employeeName: $employee_name})
        OPTIONAL MATCH (st)-[:EMPLOYED_UNDER]->(d:Department)
        OPTIONAL MATCH (d:Department)-[:PART_OF]->(f:Faculty)
        OPTIONAL MATCH (m:Module)-[:TAUGHT_BY]->(st)
        RETURN st,d,f,m
        """
        data = session.run(query, employee_name=employee_name).data()

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
            employee_data = {
                'employeeName': staff.get('employeeName',''),
                'employeeId': staff.get('employeeId', ''),
                'joinDate': staff.get('joinDate', ''),
                'nric': staff.get('nric', ''),
                'birthDate': staff.get('birthDate', '')
            }
            net.add_node(employee_name, label=f"Employee Name: {employee_name}", color='lightblue', data=employee_data)

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
    net.write_html(html_filename)
    with open(html_filename, "a") as f:
        f.write("""
        <style>
        #nodeModal {
            display: none;
            position: fixed;
            z-index: 1;
            right: 0;
            top: 0;
            width: 400px;
            height: 100vh;
            background-color: white;
            box-shadow: -2px 0px 5px rgba(0, 0, 0, 0.3);
            padding: 20px;
            overflow-y: auto;
            margin-top: 10px;
            margin-bottom: 10px;
            border-radius: 5px 0 0 5px; 
        }
        #modalContent {
            max-width: 100%;
        }
        #closeModal {
            position: absolute;
            top: 15px;
            left: 15px;
            font-size: 24px;
            cursor: pointer;
            color: #555;
        }
        #overlay {
            display: none;
            position: fixed;
            z-index: 0;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }
        #modalTitle {
        margin-left: 10px; 
        padding-left: 10px;
        }
        </style>

        <div id="overlay"></div>
        <div id="nodeModal">
            <span id="closeModal">&times;</span>
            <div id="modalContent">
                <h2 id="modalTitle">Node Details</h2>
                <p id="modalData"></p>
            </div>
        </div>

        <script type="text/javascript">
        document.getElementById("closeModal").onclick = function() {
            document.getElementById("nodeModal").style.display = "none";
            document.getElementById("overlay").style.display = "none";
        }

        network.on("click", function(params) {
            if (params.nodes.length > 0) {
                var nodeId = params.nodes[0];
                var node = network.body.data.nodes.get(nodeId);

                if (node.label.startsWith("Employee Name:")) {
                    var staffData = node.data || {};
                    var employeeName = staffData.employeeName || "No Staff Found";
                    var employeeId = staffData.employeeId || "N/A";
                    var joinDate = staffData.joinDate || "N/A";
                    var nric = staffData.nric || "N/A";
                    var birthDate = staffData.birthDate || "N/A";

                    document.getElementById("modalTitle").innerText = node.label;
                    document.getElementById("modalData").innerHTML = `
                        <strong>Staff Name:</strong> ${employeeName} <br>
                        <strong>Staff ID:</strong> ${employeeId} <br>
                        <strong>Date Joined:</strong> ${joinDate} <br>
                        <strong>NRIC:</strong> ${nric} <br>
                        <strong>Date of Birth:</strong> ${birthDate}
                    `;
                    document.getElementById("nodeModal").style.display = "flex";
                }
            }
        });
        </script>
        """)
    return {"file_url": f"/visualizations/{html_filename}"}

# Function to serve visualization on webpage
@app.route('/visualizations/<path:filename>')
def serve_visualization(filename):
    file_path = os.path.join(os.getcwd(), filename)
    response = send_from_directory(os.getcwd(), filename)
    os.remove(file_path)
    return response

# Function for prompt answer generation for query bot 
@app.route('/process_query', methods=['POST'])
def process_query():
    query = request.get_json().get('query')

    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        result = evaluate_prompt(query)
        
        return jsonify(result), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Function for testing connection to neo4j
@app.route('/test-neo4j', methods=['GET'])
def test_neo4j():
    with driver.session() as session:
        try:
            session.run("MATCH (n) RETURN n LIMIT 1")
            return jsonify({"status": "Neo4j connection successful!"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Function for recommending jobs in jobs page
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

if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 5000)