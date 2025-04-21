"""Test consistency between Python-generated base ontology and Turtle file."""

import unittest
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, SH, URIRef, Literal
from src.ontology_framework.modules.ontology import Ontology

class TestOntologyConsistency(unittest.TestCase):
    """Test consistency between Python-generated base ontology and Turtle file."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.ontology_ttl = self.project_root / "ontology.ttl"
        
    @staticmethod
    def check_class_definitions(g1: Graph, g2: Graph) -> bool:
        """Check if two graphs have the same class definitions."""
        q = """
            SELECT ?class ?label ?comment
            WHERE {
                ?class a owl:Class ;
                       rdfs:label ?label ;
                       rdfs:comment ?comment .
            }
            ORDER BY ?class
            """
        results1 = set(map(str, g1.query(q)))
        results2 = set(map(str, g2.query(q)))
        if results1 != results2:
            print("\nClass definitions in Python-generated ontology:")
            for r in sorted(results1):
                print(f"  {r}")
            print("\nClass definitions in Turtle file:")
            for r in sorted(results2):
                print(f"  {r}")
            print("\nIn Python but not in Turtle:")
            for r in sorted(results1 - results2):
                print(f"  {r}")
            print("\nIn Turtle but not in Python:")
            for r in sorted(results2 - results1):
                print(f"  {r}")
        return results1 == results2
        
    @staticmethod
    def check_properties(g1: Graph, g2: Graph) -> bool:
        """Check if two graphs have the same property definitions."""
        q = """
            SELECT ?prop ?domain ?range
            WHERE {
                ?prop a ?type .
                FILTER(?type IN (owl:DatatypeProperty, owl:ObjectProperty))
                OPTIONAL { ?prop rdfs:domain ?domain }
                OPTIONAL { ?prop rdfs:range ?range }
            }
            ORDER BY ?prop
            """
        results1 = set(map(str, g1.query(q)))
        results2 = set(map(str, g2.query(q)))
        if results1 != results2:
            print("\nProperty definitions in Python-generated ontology:")
            for r in sorted(results1):
                print(f"  {r}")
            print("\nProperty definitions in Turtle file:")
            for r in sorted(results2):
                print(f"  {r}")
        return results1 == results2
        
    @staticmethod
    def check_individuals(g1: Graph, g2: Graph) -> bool:
        """Check if two graphs have the same individuals."""
        q = """
            SELECT ?ind ?type
            WHERE {
                ?ind a ?type .
                FILTER(?type != owl:Class && ?type != owl:DatatypeProperty && ?type != owl:ObjectProperty)
            }
            ORDER BY ?ind
            """
        results1 = set(map(str, g1.query(q)))
        results2 = set(map(str, g2.query(q)))
        if results1 != results2:
            print("\nIndividuals in Python-generated ontology:")
            for r in sorted(results1):
                print(f"  {r}")
            print("\nIndividuals in Turtle file:")
            for r in sorted(results2):
                print(f"  {r}")
        return results1 == results2
        
    @staticmethod
    def check_shapes(g1: Graph, g2: Graph) -> bool:
        """Check if two graphs have the same SHACL shapes."""
        q = """
            SELECT ?shape ?targetClass
            WHERE {
                ?shape a sh:NodeShape ;
                       sh:targetClass ?targetClass .
            }
            ORDER BY ?shape
            """
        results1 = set(map(str, g1.query(q)))
        results2 = set(map(str, g2.query(q)))
        if results1 != results2:
            print("\nSHACL shapes in Python-generated ontology:")
            for r in sorted(results1):
                print(f"  {r}")
            print("\nSHACL shapes in Turtle file:")
            for r in sorted(results2):
                print(f"  {r}")
        return results1 == results2
        
    def test_round_trip_consistency(self) -> None:
        """Test that Python-generated base ontology is semantically equivalent to the Turtle file."""
        # Generate a new ontology from Python
        python_ontology = Ontology("https://raw.githubusercontent.com/louspringer/ontology-framework/main/ontology#")
        python_graph = python_ontology.graph
        
        # Add ontology metadata
        base_uri = URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/ontology#")
        python_graph.add((base_uri, RDF.type, OWL.Ontology))
        python_graph.add((base_uri, RDFS.label, Literal("Base Ontology", lang="en")))
        python_graph.add((base_uri, RDFS.comment, Literal("Core ontology for the ontology framework", lang="en")))
        python_graph.add((base_uri, OWL.versionInfo, Literal("0.1.0")))
        
        # Load the Turtle file
        turtle_graph = Graph()
        turtle_graph.parse(self.ontology_ttl, format="turtle")
        
        # Run all semantic checks
        self.assertTrue(
            self.check_class_definitions(python_graph, turtle_graph),
            "Class definitions differ between Python-generated and Turtle ontologies"
        )
        self.assertTrue(
            self.check_properties(python_graph, turtle_graph),
            "Property definitions differ between Python-generated and Turtle ontologies"
        )
        self.assertTrue(
            self.check_individuals(python_graph, turtle_graph),
            "Individuals differ between Python-generated and Turtle ontologies"
        )
        self.assertTrue(
            self.check_shapes(python_graph, turtle_graph),
            "SHACL shapes differ between Python-generated and Turtle ontologies"
        )
        
    def test_emit_reload_consistency(self) -> None:
        """Test that emitting and reloading produces the same graph."""
        # Create a temporary file
        temp_file = self.project_root / "temp_ontology.ttl"
        
        try:
            # Generate and emit
            ontology = Ontology("https://raw.githubusercontent.com/louspringer/ontology-framework/main/ontology#")
            ontology.emit_ontology(temp_file)
            
            # Reload
            reloaded = Ontology("https://raw.githubusercontent.com/louspringer/ontology-framework/main/ontology#")
            reloaded.load(temp_file)
            
            # Compare
            self.assertTrue(
                self.check_class_definitions(ontology.graph, reloaded.graph),
                "Emitted and reloaded graphs have different class definitions"
            )
            
        finally:
            # Clean up
            if temp_file.exists():
                temp_file.unlink()

    def test_guidance_modules_loaded(self) -> None:
        """Test that guidance modules are loaded correctly."""
        ontology = Ontology("https://raw.githubusercontent.com/louspringer/ontology-framework/main/ontology#")
        
        # Check if compliance module is loaded by verifying its triples
        q = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?s ?label ?comment
            WHERE {
                ?s rdfs:label ?label ;
                   rdfs:comment ?comment .
                FILTER(str(?s) IN ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", 
                                 "http://www.w3.org/2000/01/rdf-schema#subClassOf"))
            }
            ORDER BY ?s
            """
        results = list(ontology.graph.query(q))
        
        # Verify that core RDF/RDFS properties are loaded with metadata
        self.assertTrue(len(results) >= 2, "Core RDF/RDFS properties not found in loaded modules")
        
        # Check specific properties from compliance.ttl
        found_type = False
        found_subclass = False
        
        for row in results:
            s, label, comment = map(str, row)
            if "rdf-syntax-ns#type" in s:
                found_type = True
                self.assertEqual(label, "22-rdf-syntax-ns#type")
                self.assertEqual(comment, "Description of 22-rdf-syntax-ns#type")
            elif "rdf-schema#subClassOf" in s:
                found_subclass = True
                self.assertEqual(label, "rdf-schema#subClassOf")
                self.assertEqual(comment, "Description of rdf-schema#subClassOf")
                
        self.assertTrue(found_type, "rdf:type metadata not found")
        self.assertTrue(found_subclass, "rdfs:subClassOf metadata not found")

if __name__ == "__main__":
    unittest.main() 