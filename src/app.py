from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# Function to create a new student individually
@app.route('/students', methods=['POST'])
def create_new_student():
    student_data = request.json
    s = create_student(student_data)
    return jsonify({'message': 'Student created successfully'}), 201