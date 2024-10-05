def create_jobs_and_skills_nodes_and_relationships(tx, job_title, skills):

    tx.run("""
        MERGE (j:Job {jobTitle: $job_title})
        WITH j
        UNWIND $skills AS skill_name
        MERGE (s:Skill {name: skill_name})
        MERGE (j)-[:REQUIRES]->(s)
    """, job_title=job_title, skills=skills)

def create_jobs_and_skills(data):
    driver = GraphDatabase.driver("neo4j+s://67203e25.databases.neo4j.io", auth=("neo4j", "KUKTrqvpgw9FLuAam0cCauBnsdQsTC3CW1lCboUWhaA"))
    session = driver.session()
    data['Skills'] = data['Skills'].str.split(',')

    with driver.session() as session:
        for _, row in data.iterrows():
            job_title = row['Job Title']
            skills = row['Skills']

            session.execute_write(create_jobs_and_skills, job_title, skills)