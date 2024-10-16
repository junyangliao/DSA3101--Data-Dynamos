import os
import pandas as pd
from flask import Flask, request, render_template
from neo4j import GraphDatabase
from py2neo import Graph
from pyvis.network import Network   
from utils import format_node,format_relationship

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()

def visualize_student_and_relationships(matric_number):
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
    net.show("student_graph.html")

def visualize_module_and_relationships(module_code):
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
    net.show("module_graph.html")