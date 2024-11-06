import os
import re
import logging
from functools import lru_cache

import google.generativeai as genai
from nltk.stem import PorterStemmer
from neo4j import GraphDatabase
from SPARQLWrapper import SPARQLWrapper, JSON

from .relevancy_scorer import RelevancyScorer
scorer = RelevancyScorer()

logging.getLogger("neo4j").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

ps = PorterStemmer()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_session(self):
        return self.driver.session()

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

db = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)

def clean_skill_name(skill):
    """Remove brackets and standardize skill names"""
    cleaned = re.sub(r'\s*\([^)]*\)', '', skill)
    cleaned = re.sub(r'\s*\[[^\]]*\]', '', cleaned)
    return ' '.join(cleaned.split())

def standardize_matric_number(matric_number):
    """Standardize matric number format to uppercase and remove all whitespaces"""
    if not matric_number:
        return None
    return ''.join(matric_number.split()).upper()

def preprocess_title(title):
    title = re.sub(r'[^\w\s]', '', title.lower())
    return ' '.join(ps.stem(word) for word in title.split())

@lru_cache(maxsize=100)
def extract_job_title(user_input):
    prompt = f"""
    Given the user input, please identify the most relevant job title:
    User input: "{user_input}"
    The output should be a single job title only, based on the input. Be specific and try to match common industry job titles.
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text.strip() if response else "Unknown"

def get_student_data(matric_number):
    """Get student's completed modules and their preclusions"""
    matric_number = standardize_matric_number(matric_number)
    query = """
    MATCH (s:Student {matricNumber: $matric_number})-[:COMPLETED]->(m:Module)
    WITH collect(DISTINCT m.moduleCode) as completed_modules
    OPTIONAL MATCH (m:Module)
    WHERE m.moduleCode IN completed_modules
    OPTIONAL MATCH (m)-[:MUST_NOT_HAVE_TAKEN_ONE_OF]->(pg:PreclusionGroup)-[:INCLUDED_AS_PRECLUSION]->(precluded:Module)
    RETURN completed_modules, collect(DISTINCT precluded.moduleCode) as precluded_modules
    """
    with db.get_session() as session:
        result = session.run(query, matric_number=matric_number)
        record = result.single()
        if record:
            completed = record["completed_modules"]
            precluded = [p for p in record["precluded_modules"] if p]
            return completed, completed + precluded
        return [], []

def can_take_module(module_code, completed_modules):
    """Check if student can take a module based on prerequisites"""
    query = """
    MATCH (m:Module {moduleCode: $module_code})
    OPTIONAL MATCH (m)-[:MUST_HAVE_TAKEN_ONE_OF]->(pg:PrerequisiteGroup)
    OPTIONAL MATCH (pg)-[:INCLUDED_AS_PREREQUISITE]->(prereq:Module)
    RETURN m.moduleCode as code,
           COLLECT(DISTINCT prereq.moduleCode) as prerequisites
    """
    with db.get_session() as session:
        result = session.run(query, module_code=module_code)
        record = result.single()
        if not record:
            return False
        
        prerequisites = record["prerequisites"]
        if not prerequisites: 
            return True
            
        return any(prereq in completed_modules for prereq in prerequisites)

def get_completed_modules_by_skill(matric_number, skill):
    """Get completed modules that teach a specific skill"""
    cleaned_skill = clean_skill_name(skill)
    matric_number = standardize_matric_number(matric_number)
    
    if len(cleaned_skill) == 1:
        query = """
        MATCH (s:Student {matricNumber: $matric_number})-[:COMPLETED]->(m:Module)-[:SKILL_TAUGHT]->(sk:Skill)
        WHERE toLower(trim(sk.name)) = toLower(trim($skill))
        RETURN DISTINCT m.moduleCode as code, m.title as title, collect(sk.name) as skills
        """
    else:
        query = """
        MATCH (s:Student {matricNumber: $matric_number})-[:COMPLETED]->(m:Module)-[:SKILL_TAUGHT]->(sk:Skill)
        WHERE toLower(trim(sk.name)) CONTAINS toLower(trim($skill))
        RETURN DISTINCT m.moduleCode as code, m.title as title, collect(sk.name) as skills
        """
    
    with db.get_session() as session:
        result = session.run(query, matric_number=matric_number, skill=cleaned_skill)
        return [(record["code"], record["title"], 
                [clean_skill_name(s) for s in record["skills"]])
               for record in result]

def get_relevant_modules(skills, matric_number=None):
    """Get relevant modules for given skills with relevancy scores"""
    modules_by_skill = {}
    
    with db.get_session() as session:
        excluded_modules = []
        completed_modules = []
        if matric_number:
            completed_modules, excluded_modules = get_student_data(matric_number)

        for skill in skills:
            cleaned_skill = clean_skill_name(skill)
            
            # Different queries for single letter skills vs regular skills
            if len(cleaned_skill) == 1:
                query = """
                MATCH (s:Skill)
                WHERE toLower(trim(s.name)) = toLower(trim($skill))
                MATCH (m:Module)-[:SKILL_TAUGHT]->(s)
                WHERE NOT m.moduleCode IN $excluded_modules
                RETURN DISTINCT m.moduleCode AS code, m.title AS title,
                       m.description AS description, collect(s.name) AS skills
                """
            else:
                query = """
                MATCH (s:Skill)
                WHERE toLower(trim(s.name)) CONTAINS toLower(trim($skill))
                MATCH (m:Module)-[:SKILL_TAUGHT]->(s)
                WHERE NOT m.moduleCode IN $excluded_modules
                RETURN DISTINCT m.moduleCode AS code, m.title AS title,
                       m.description AS description, collect(s.name) AS skills
                """

            result = session.run(query, skill=cleaned_skill, excluded_modules=excluded_modules)
            
            valid_modules = []
            skill_desc_pairs = []
            
            for record in result:
                if not matric_number or can_take_module(record["code"], completed_modules):
                    valid_modules.append({
                        'code': record["code"],
                        'title': record["title"],
                        'skills': record["skills"],
                        'description': record["description"] or ''
                    })
                    skill_desc_pairs.append((skill, record["description"] or ''))
            
            if valid_modules:
                relevance_scores = scorer.calculate_batch_relevance_scores(skill_desc_pairs)
                
                modules = []
                for module, score in zip(valid_modules, relevance_scores):
                    modules.append({
                        'code': module['code'],
                        'title': module['title'],
                        'skills': module['skills'],
                        'relevance_score': score
                    })
                
                # Sort by relevance score and get top 5
                modules.sort(key=lambda x: x['relevance_score'], reverse=True)
                modules_by_skill[skill] = modules[:5]

    return modules_by_skill

def job_title_exists(job_title):
    query = """
    MATCH (j:Job)
    WHERE trim(toLower(j.jobTitle)) = trim(toLower($job_title))
    RETURN j
    """
    with db.get_session() as session:
        result = session.run(query, job_title=job_title)
        return result.single() is not None

def get_skills_for_job(job_title):
    query = """
    MATCH (j:Job {jobTitle: $job_title})-[:REQUIRES]->(s:Skill)
    RETURN s.name AS skill
    """
    with db.get_session() as session:
        result = session.run(query, job_title=job_title)
        return [clean_skill_name(record["skill"]) for record in result]

def get_job_recommendations(job_description, matric_number=None):
    """Main function to get job recommendations"""
    try:
        matric_number = standardize_matric_number(matric_number)
        job_title = extract_job_title(job_description)
        logger.info(f"Extracted job title: {job_title}")

        if job_title_exists(job_title):
            skills = get_skills_for_job(job_title)
            if skills:
                response_data = {
                    "success": True,
                    "job": {
                        "title": job_title,
                        "skills": skills
                    },
                    "student": {
                        "matricNumber": matric_number
                    },
                    "skillBreakdown": {}
                }

                completed_modules_by_skill = {}
                if matric_number:
                    for skill in skills:
                        completed = get_completed_modules_by_skill(matric_number, skill)
                        if completed:
                            completed_modules_by_skill[skill] = completed

                modules_by_skill = get_relevant_modules(skills, matric_number)

                # Structure skill breakdown
                for skill in skills:
                    skill_data = {
                        "name": skill,
                        "completed": [],
                        "recommended": []
                    }

                    # Add completed modules
                    if skill in completed_modules_by_skill:
                        skill_data["completed"] = [
                            {
                                "code": code,
                                "title": title,
                                "skills": skill_list
                            }
                            for code, title, skill_list in completed_modules_by_skill[skill]
                        ]

                    # Add recommended modules
                    if skill in modules_by_skill:
                        skill_data["recommended"] = modules_by_skill[skill]

                    response_data["skillBreakdown"][skill] = skill_data

                return response_data

            else:
                return {
                    "success": False,
                    "error": f"Job title '{job_title}' found, but no skills are associated with it."
                }
        else:
            return {
                "success": False,
                "error": f"Job title '{job_title}' not found."
            }

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }
    
def get_job_description_from_wikidata(job_description):
    """
    Queries Wikidata to get a description for a given job title.
    
    Parameters:
    job_title (str): The job title to query
    
    Returns:
    str: A description of the job from Wikidata, or an error message if not found
    """
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f"""
    SELECT ?description WHERE {{
      ?job wdt:P31 wd:Q28640;  # Instance of profession or occupation
           rdfs:label "{job_description}"@en;
           schema:description ?description.
      FILTER (lang(?description) = "en")
    }}
    LIMIT 1
    """
    
    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["description"]["value"]
        return "No description available for this job title."
    except Exception as e:
        return "Error retrieving job description."