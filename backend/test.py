from py2neo import Graph

uri = "neo4j+s://67203e25.databases.neo4j.io"
user = "neo4j"
password = "KUKTrqvpgw9FLuAam0cCauBnsdQsTC3CW1lCboUWhaA"

try:
    graph = Graph(uri, auth=(user, password))
    print("Successfully connected to Neo4j")
except Exception as e:
    print(f"Connection failed: {e}")