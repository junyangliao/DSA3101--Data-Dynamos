import os
import pandas as pd
from neo4j import GraphDatabase
from utils import format_node, format_relationship

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()


def create_jobs_and_skills_nodes_and_relationships(tx, job_title, skills):

    tx.run(
        """
        MERGE (j:Job {name: $job_title})
        WITH j
        UNWIND $skills AS skill_name
        MERGE (s:Skill {name: skill_name})
        MERGE (j)-[:REQUIRES]->(s)
    """,
        job_title=job_title,
        skills=skills,
    )


def create_job_and_skills(data):
    with driver.session() as session:
        job_title = data.get("job_title")
        skills = data.get("Skills")

        session.execute_write(
            create_jobs_and_skills_nodes_and_relationships, job_title, skills
        )

def delete_job_node_and_relationships(tx, job_title):
    tx.run(
        """
        MATCH (j:Job {name: $job_title})
        DETACH DELETE j;
    """,
        job_title=job_title,
    )


def delete_job(data):
    with driver.session() as session:
        job_title = data
        session.execute_write(delete_job_node_and_relationships, job_title)
