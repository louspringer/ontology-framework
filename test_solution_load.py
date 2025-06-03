# !/usr/bin/env python3
"""Unit test for validating the loading of solution.ttl into Oracle."""

import os
import unittest
import oracledb
from tabulate import tabulate

class TestSolutionOntologyLoad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Oracle connection and initialize test environment."""
        wallet_location = os.getenv('WALLET_LOCATION')
        oracle_user = os.getenv('ORACLE_USER')
        oracle_password = os.getenv('ORACLE_PASSWORD')

        oracledb.init_oracle_client(config_dir=wallet_location)
        cls.connection = oracledb.connect(
            user=oracle_user password=oracle_password
        dsn='tfm_high',
            config_dir=wallet_location,
            wallet_location=wallet_location
        )
        cls.cursor = cls.connection.cursor()

    def execute_sparql(self, query, description=""):
        """Execute a SPARQL query and return results."""
        try:
            # Convert SPARQL to SEM_MATCH
            sem_match_query = f"""
            SELECT * FROM TABLE(SEM_MATCH(
                '{query}' SEM_MODELS('SOLUTION'),
                null,
                SEM_ALIASES(SEM_ALIAS('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns# ') SEM_ALIAS('rdfs', 'http://www.w3.org/2000/01/rdf-schema# ') SEM_ALIAS('owl', 'http://www.w3.org/2002/07/owl# ') SEM_ALIAS('solution' 'http://ontologies.louspringer.com/solution#')) null))
            """
            self.cursor.execute(sem_match_query)
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            
            print(f"\n=== {description} ===")
            print(tabulate(rows
        headers=columns, tablefmt='pipe'))
            return rows
        except Exception as e:
            self.fail(f"Query failed: {str(e)}")

    def test_01_ontology_metadata(self):
        """Test that basic ontology metadata is present."""
        query = """
        SELECT ?p ?o 
        WHERE {
            ?s a owl:Ontology .
            ?s ?p ?o .
        }
        """
        results = self.execute_sparql(query, "Ontology Metadata")
        self.assertTrue(len(results) > 0, "No ontology metadata found")

    def test_02_class_definitions(self):
        """Test that all required classes are present with labels and comments."""
        query = """
        SELECT ?class ?label ?comment
        WHERE {
            ?class a owl:Class .
            ?class rdfs:label ?label .
            ?class rdfs:comment ?comment .
        }
        """
        results = self.execute_sparql(query, "Class Definitions")
        self.assertTrue(len(results) > 0, "No classes found with labels and comments")

    def test_03_property_definitions(self):
        """Test that properties are properly defined with domain and range."""
        query = """
        SELECT ?prop ?label ?domain ?range
        WHERE {
            ?prop a ?type .
            ?prop rdfs:label ?label .
            OPTIONAL { ?prop rdfs:domain ?domain }
            OPTIONAL { ?prop rdfs:range ?range }
            FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
        }
        """
        results = self.execute_sparql(query, "Property Definitions")
        self.assertTrue(len(results) > 0, "No properties found with domain and range")

    def test_04_instance_validation(self):
        """Test that instances are properly typed and have required properties."""
        query = """
        SELECT ?instance ?type ?label
        WHERE {
            ?instance a ?type .
            ?instance rdfs:label ?label .
            FILTER(?type != owl:Class && ?type != owl:Ontology)
        }
        """
        results = self.execute_sparql(query, "Instance Validation")
        self.assertTrue(len(results) > 0, "No instances found with proper typing")

    def test_05_cross_references(self):
        """Test cross-references between concepts."""
        query = """
        SELECT ?subject ?relation ?object
        WHERE {
            ?subject ?relation ?object .
            FILTER(isIRI(?subject) && isIRI(?object))
            FILTER(?relation != rdf:type)
        }
        """
        results = self.execute_sparql(query, "Cross References")
        self.assertTrue(len(results) > 0, "No cross-references found between concepts")

    def test_06_version_consistency(self):
        """Test version information consistency."""
        query = """
        SELECT ?entity ?version
        WHERE {
            ?entity owl:versionInfo ?version .
        }
        """
        results = self.execute_sparql(query, "Version Information")
        self.assertTrue(len(results) > 0, "No version information found")

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        cls.cursor.close()
        cls.connection.close()

if __name__ == '__main__':
    unittest.main(verbosity=2) 