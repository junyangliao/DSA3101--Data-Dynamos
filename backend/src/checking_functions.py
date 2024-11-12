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
        duplicates = [
            {"value": record["value"], "count": record["count"]} for record in results
        ]
        if duplicates:
            unique_issues.append(
                {f"{entity}_unique_constraint_violation_on_{attr}": duplicates}
            )
    return unique_issues


def check_required_relationships(tx, entity, relationships):
    relationship_issues = []
    for relationship, details in relationships.items():
        target = details["to"]
        is_optional = details.get("optional", False)

        # Skip check if relationship is optional
        if is_optional:
            continue

        # Query to find nodes missing the required relationship
        query = f"""
        MATCH (n:{entity})
        WHERE NOT (n)-[:{relationship}]->(:{target})
        RETURN n
        """
        results = tx.run(query)
        missing_relationships = [record["n"] for record in results]
        if missing_relationships:
            relationship_issues.append(
                {f"{entity}_missing_{relationship}": missing_relationships}
            )
    return relationship_issues


def check_orphaned_relationships(tx, relationship, source, target):
    query = f"""
    MATCH (n:{source})-[r:{relationship}]->(m)
    WHERE NOT (m:{target})
    RETURN n, m
    """
    results = tx.run(query)
    orphans = [{"source": record["n"], "target": record["m"]} for record in results]
    return orphans if orphans else None


def check_attributes(tx, entity, attributes):
    attribute_issues = []
    for attr in attributes:
        query = f"""
        MATCH (n:{entity})
        WHERE n.{attr} IS NULL
        RETURN n
        """
        results = tx.run(query)
        missing_attrs = [record["n"] for record in results]
        if missing_attrs:
            attribute_issues.append({f"{entity}_missing_{attr}": missing_attrs})
    return attribute_issues


def ontology_consistency_check(driver, ontology):
    with driver.session() as session:
        issues = []

        # 1. Check unique constraints for each entity
        for entity, data in ontology["entities"].items():
            unique_attrs = data.get("unique", [])
            unique_issues = session.execute_read(
                check_unique_constraints, entity, unique_attrs
            )
            issues.extend(unique_issues)

        # 2. Check required relationships
        required_relationships = {
            rel: details
            for rel, details in ontology["relationships"].items()
            if not details.get("optional", False)
        }
        for relationship, details in required_relationships.items():
            source, target = details["from"], details["to"]
            relationship_issues = session.execute_read(
                check_required_relationships, source, {relationship: details}
            )
            issues.extend(relationship_issues)

        # 3. Check orphaned relationships
        for relationship, details in ontology["relationships"].items():
            source, target = details["from"], details["to"]
            orphan_issues = session.execute_read(
                check_orphaned_relationships, relationship, source, target
            )
            if orphan_issues:
                issues.append({f"orphaned_{relationship}": orphan_issues})

        # 4. Check attributes for each entity
        for entity, data in ontology["entities"].items():
            attributes = data.get("attributes", [])
            attribute_issues = session.execute_read(
                check_attributes, entity, attributes
            )
            issues.extend(attribute_issues)

        # Return all issues found or a success message
        return (
            {"status": "inconsistencies_found", "issues": issues}
            if issues
            else {"status": "consistent", "message": "No inconsistencies found"}
        )
