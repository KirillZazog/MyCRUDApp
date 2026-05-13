import os
from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv

load_dotenv()

class Neo4jConnection:
    def __init__(self):
        host = os.getenv("NEO4J_HOST", "localhost")
        port = os.getenv("NEO4J_PORT", "7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "neo4j")
        uri = f"bolt://{host}:{port}"
        self._driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))

    def get_driver(self):
        return self._driver

    def test_connection(self) -> bool:
        try:
            with self._driver.session() as session:
                result = session.run("RETURN 1 AS test")
                _ = result.single()["test"]
            return True
        except Exception as e:
            print("Neo4j connection test failed:", e)
            return False

    def close(self):
        """Close the driver and free resources."""
        self._driver.close()

    def create_node(self, label: str, properties: dict) -> bool:
        """Create a node with the given label and properties.

        Returns True on success, False otherwise.
        """
        try:
            with self._driver.session() as session:
                cypher = f"CREATE (n:{label} $props) RETURN n"
                session.run(cypher, props=properties)
            return True
        except Exception as e:
            print("Error creating node:", e)
            return False

    def get_all_nodes(self, label: str):
        """Retrieve all nodes with the specified label.

        Returns a list of node objects or an empty list on failure.
        """
        try:
            with self._driver.session() as session:
                result = session.run(f"MATCH (n:{label}) RETURN n")
                return [record["n"] for record in result]
        except Exception as e:
            print("Error fetching nodes:", e)
            return []

    def update_node_property(self, label: str, match_props: dict, update_props: dict) -> bool:
        """Update properties of nodes matching `match_props`.

        Returns True on success, False otherwise.
        """
        try:
            with self._driver.session() as session:
                match_clause = ' AND '.join([f"n.{k} = ${{k}}" for k in match_props.keys()])
                set_clause = ', '.join([f"n.{k} = ${{new_{k}}}" for k in update_props.keys()])
                params = {**match_props, **{f"new_{k}": v for k, v in update_props.items()}}
                cypher = f"MATCH (n:{label}) WHERE {match_clause} SET {set_clause}"
                session.run(cypher, **params)
            return True
        except Exception as e:
            print("Error updating node:", e)
            return False

    def delete_node(self, label: str, match_props: dict) -> bool:
        """Delete nodes with the given label that match `match_props`.

        Returns True on success, False otherwise.
        """
        try:
            with self._driver.session() as session:
                match_clause = ' AND '.join([f"n.{k} = ${{k}}" for k in match_props.keys()])
                cypher = f"MATCH (n:{label}) WHERE {match_clause} DETACH DELETE n"
                session.run(cypher, **match_props)
            return True
        except Exception as e:
            print("Error deleting node:", e)
            return False

if __name__ == "__main__":
    conn = Neo4jConnection()
    if conn.test_connection():
        print("Successfully connected to Neo4j container.")
    else:
        print("Failed to connect to Neo4j container.")
    conn.close()
