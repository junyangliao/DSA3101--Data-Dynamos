from neo4j import GraphDatabase

def check_unique_constraints(tx, entity, unique_attributes):
    unique_issues = []
    for attr in unique_attributes:
        query = f"""
        MATCH (n:{entity})
        WITH n.{attr} AS value, COUNT(n) AS count
        WHERE count > 1
        RETURN value, count
        """
        results = tx.run(query)
        duplicates = [{"value": record["value"], "count": record["count"]} for record in results]
        if duplicates:
            unique_issues.append({f"{entity}_unique_constraint_violation_on_{attr}": duplicates})
    return unique_issues

def check_required_relationships(tx, entity, relationships):
    """Check for missing required relationships"""
    relationship_issues = []
    for relationship, details in relationships.items():
        target = details["to"]
        query = f"""
        MATCH (n:{entity})
        WHERE NOT (n)-[:{relationship}]->(:{target})
        RETURN CASE
            WHEN n.degree IS NOT NULL THEN n.degree
            WHEN n.moduleCode IS NOT NULL THEN n.moduleCode + ': ' + n.title
            WHEN n.name IS NOT NULL THEN n.name
            ELSE 'Unknown'
        END as display_value
        """
        results = tx.run(query)
        missing_relationships = [record["display_value"] for record in results]
        if missing_relationships:
            relationship_issues.append({f"{entity}_missing_{relationship}": missing_relationships})
    return relationship_issues

def check_orphaned_relationships(tx, relationship, source, target):
    query = f"""
    MATCH (n:{source})-[r:{relationship}]->(m)
    WHERE NOT (m:{target})
    RETURN CASE
        WHEN n.degree IS NOT NULL THEN n.degree
        WHEN n.moduleCode IS NOT NULL THEN n.moduleCode + ': ' + n.title
        WHEN n.name IS NOT NULL THEN n.name
        ELSE 'Unknown'
    END as display_value
    """
    results = tx.run(query)
    orphans = [record["display_value"] for record in results]
    return orphans if orphans else None

def check_attributes(tx, entity, attributes, ontology):
    """Check for missing required attributes"""
    attribute_issues = []
    
    # Get list of attributes that correspond to optional relationships
    optional_attributes = set()
    for rel_name, rel_details in ontology["relationships"].items():
        if rel_details.get("optional", False) and rel_details["from"] == entity:
            attr_name = rel_name.replace("_IN", "").title().replace("_", " ").replace(" ", "_")
            optional_attributes.add(attr_name)
    
    # Only check required attributes
    required_attrs = [attr for attr in attributes if attr not in optional_attributes]
    
    for attr in required_attrs:
        query = f"""
        MATCH (n:{entity})
        WHERE n.{attr} IS NULL
        RETURN CASE
            WHEN n.degree IS NOT NULL THEN n.degree
            WHEN n.moduleCode IS NOT NULL THEN n.moduleCode + ': ' + n.title
            WHEN n.name IS NOT NULL THEN n.name
            ELSE 'Unknown'
        END as display_value
        """
        results = tx.run(query)
        missing_attrs = [record["display_value"] for record in results]
        if missing_attrs:
            attribute_issues.append({f"{entity}_missing_{attr}": missing_attrs})
    return attribute_issues

def get_existing_entities(driver):
    """Get list of entities that actually exist in the database"""
    with driver.session() as session:
        query = """
        CALL db.labels() YIELD label
        RETURN collect(label) as labels
        """
        result = session.run(query)
        return result.single()["labels"]

def get_existing_relationships(driver):
    """Get list of relationships that actually exist in the database"""
    with driver.session() as session:
        query = """
        CALL db.relationshipTypes() YIELD relationshipType
        RETURN collect(relationshipType) as types
        """
        result = session.run(query)
        return result.single()["types"]

def filter_ontology(ontology, existing_entities, existing_relationships):
    """Filter ontology to only include existing elements"""
    return {
        "entities": {
            k: v for k, v in ontology["entities"].items() 
            if k in existing_entities
        },
        "relationships": {
            k: v for k, v in ontology["relationships"].items()
            if k in existing_relationships and 
            v["from"] in existing_entities and 
            v["to"] in existing_entities
        }
    }

def format_results_for_api(results):
    """Format consistency check results for API response"""
    if results["status"] == "inconsistencies_found":
        formatted_issues = {}
        
        # Group issues by entity type
        for issue in results["issues"]:
            for check_type, details in issue.items():
                entity = check_type.split('_')[0]
                if entity not in formatted_issues:
                    formatted_issues[entity] = []
                
                issue_type = check_type.replace(f"{entity}_", "").replace("_", " ").title()
                
                if isinstance(details, list):
                    formatted_issues[entity].append({
                        "type": issue_type,
                        "details": details
                    })
        
        return {
            "status": "inconsistencies_found",
            "issues": formatted_issues,
            "message": None
        }
    else:
        return {
            "status": "consistent",
            "issues": {},
            "message": "No inconsistencies found"
        }

def ontology_consistency_check(driver, ontology):
    """Main function to run all consistency checks"""
    existing_entities = get_existing_entities(driver)
    existing_relationships = get_existing_relationships(driver)
    filtered_ontology = filter_ontology(ontology, existing_entities, existing_relationships)
    
    with driver.session() as session:
        issues = []
        
        # Run all checks
        for entity, data in filtered_ontology["entities"].items():
            # Check unique constraints
            unique_attrs = data.get("unique", [])
            unique_issues = session.execute_read(check_unique_constraints, entity, unique_attrs)
            issues.extend(unique_issues)
            
            # Check attributes
            attributes = data.get("attributes", [])
            attribute_issues = session.execute_read(
                check_attributes, 
                entity, 
                attributes,
                ontology
            )
            issues.extend(attribute_issues)
        
        # Check relationships
        for relationship, details in filtered_ontology["relationships"].items():
            if not details.get("optional", False):
                relationship_issues = session.execute_read(
                    check_required_relationships,
                    details["from"],
                    {relationship: details}
                )
                issues.extend(relationship_issues)
        
        return {
            "status": "inconsistencies_found" if issues else "consistent",
            "issues": issues,
            "message": "No inconsistencies found" if not issues else None
        }

def run_consistency_check(driver, ontology):
    """Wrapper function to run consistency check and format results for API"""
    try:
        results = ontology_consistency_check(driver, ontology)
        return format_results_for_api(results)
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "issues": {}
        }