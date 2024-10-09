import os
from neo4j import GraphDatabase

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()

def create_jobs_and_skills_nodes_and_relationships(tx, job_title, skills):

    tx.run("""
        MERGE (j:Job {jobTitle: $job_title})
        WITH j
        UNWIND $skills AS skill_name
        MERGE (s:Skill {name: skill_name})
        MERGE (j)-[:REQUIRES]->(s)
    """, job_title=job_title, skills=skills)

def create_jobs_and_skills(data):
    data['Skills'] = data['Skills'].str.split(',')

    with driver.session() as session:
        for _, row in data.iterrows():
            job_title = row['Job Title']
            skills = row['Skills']

            session.execute_write(create_jobs_and_skills, job_title, skills)