from flask import Flask, request, jsonify
from flask_cors import CORS
from neo4j import GraphDatabase
from main_functions.students import create_student_node_and_relationships, create_student, create_students, delete_student_node_and_relationships, delete_student, get_students_all_connections
from visualize_algo import visualize_student_and_relationships
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