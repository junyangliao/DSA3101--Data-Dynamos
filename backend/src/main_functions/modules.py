import os
from neo4j import GraphDatabase

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
session = driver.session()

def create_module_node_and_relationships(
    tx,
    module_code,
    title,
    description,
    module_credit,
    department,
    faculty,
    prerequisites,
    preclusions,
    semesters,
    skills,
):
    tx.run(
        """
        MERGE (m:Module {moduleCode: $module_code})
        ON CREATE SET m.title = $title, m.description = $description, m.moduleCredit = $module_credit
        ON MATCH SET m.title = $title, m.description = $description, m.moduleCredit = $module_credit
    """,
        module_code=module_code,
        title=title,
        description=description,
        module_credit=module_credit,
    )

    tx.run(
        """
        MERGE (d:Department {name: $department})
        MERGE (f:Faculty {name: $faculty})
        MERGE (d)-[:PART_OF]->(f)
        WITH d
        MATCH (m:Module {moduleCode: $module_code})
        MERGE (m)-[:BELONGS_TO]->(d)
    """,
        department=department,
        faculty=faculty,
        module_code=module_code,
    )

    if prerequisites:
        for prereq_list in prerequisites:
            if len(prereq_list) >= 1:  # Check if it's a valid list
                # Create a group node for the alternatives
                group_name = f"{prereq_list}"
                tx.run(
                    """
                    MERGE (g:PrerequisiteGroup {name: $group_name})
                """,
                    group_name=group_name,
                )

                # Connect group to each prerequisite module
                for prereq in prereq_list:
                    tx.run(
                        """
                        MATCH (p:Module {moduleCode: $prereq}), (g:PrerequisiteGroup {name: $group_name})
                        MERGE (p)-[:INCLUDED_AS_PREREQUISITE]->(g)
                    """,
                        prereq=prereq,
                        group_name=group_name,
                    )

                # Connect main module to the group
                tx.run(
                    """
                    MATCH (m:Module {moduleCode: $module_code}), (g:PrerequisiteGroup {name: $group_name})
                    MERGE (m)-[:MUST_HAVE_TAKEN_ONE_OF]->(g)
                """,
                    module_code=module_code,
                    group_name=group_name,
                )

    if preclusions:
        group_name = f"{preclusions}"
        tx.run(
            """
                MERGE (g:PreclusionGroup {name: $group_name})
            """,
            group_name=group_name,
        )

        for preclusion in preclusions:
            tx.run(
                """
                MATCH (p:Module {moduleCode: $preclusion}), (g:PreclusionGroup {name: $group_name})
                MERGE (p)-[:INCLUDED_AS_PRECLUSION]->(g)
            """,
                preclusion=preclusion,
                group_name=group_name,
            )

        tx.run(
            """
            MATCH (m:Module {moduleCode: $module_code}), (g:PreclusionGroup {name: $group_name})
            MERGE (m)-[:MUST_NOT_HAVE_TAKEN_ONE_OF]->(g)
        """,
            module_code=module_code,
            group_name=group_name,
        )

    for semester in semesters:
        tx.run(
            """
            MERGE (s:Semester {number: $semester})
            WITH s
            MATCH (m:Module {moduleCode: $module_code})
            MERGE (m)-[:OFFERED_IN]->(s)
        """,
            semester=semester,
            module_code=module_code,
        )

    if skills:
        for skill in skills:
            tx.run(
                """
                MERGE (m:Module {moduleCode: $module_code})
                WITH m
                MATCH (s:Skill {name: $skill})
                MERGE (m)-[:SKILL_TAUGHT]->(s)
            """,
                module_code=module_code,
                skill=skill,
            )


def create_module(data):
    with driver.session() as session:
        module_code = data.get("module_code")
        title = data.get("title")
        description = data.get("description")
        module_credit = data.get("module_credit")
        department = data.get("department")
        faculty = data.get("faculty")
        prerequisites = data.get("prerequisites",[])
        preclusions = data.get("preclusions",[])
        semesters = data.get("semesters",[])
        skills = data.get("skills", [])


        session.execute_write(
            create_module_node_and_relationships,
            module_code,
            title,
            description,
            module_credit,
            department,
            faculty,
            prerequisites,
            preclusions,
            semesters,
            skills
        )

def delete_module_node_and_relationships(tx, module_code):
    tx.run(
        """
        MATCH (m:Module {moduleCode: $module_code})
        DETACH DELETE m;
    """,
        module_code=module_code,
    )


def delete_module(data):
    with driver.session() as session:
        module_code = data
        session.execute_write(delete_module_node_and_relationships, module_code)
