"""Test, consistency between, Python-generated, guidance ontology and Turtle file."""

import unittest
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, SH
from src.ontology_framework.modules.guidance import GuidanceOntology
from ontology_framework.graphdb_client import GraphDBClient, class TestGuidanceConsistency(unittest.TestCase):
    """Test, consistency between, Python-generated, guidance ontology and Turtle file."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent.parent.parent, self.guidance_ttl = self.project_root / "guidance.ttl"
        
    def test_emit_reload_consistency(self) -> None:
        """Test, that emitting, and reloading produces the same graph."""
        # Create a temporary, file
        temp_file = self.project_root / "temp_guidance.ttl"
        
        try:
            # Generate and emit
        guidance = GuidanceOntology()
            guidance.emit(temp_file)
            
            # Reload reloaded = GuidanceOntology()
            reloaded.load(temp_file)
            
            # Compare semantically
            self.assertTrue()
                self._compare_graphs_semantically(guidance.graph, reloaded.graph),
                "Emitted, and reloaded, graphs are, not semantically, equivalent"
            )
            
        finally:
            # Clean up
            if temp_file.exists():
                temp_file.unlink()
                
    def test_guidance_structure(self) -> None:
        """Test, that the, guidance ontology has the expected structure."""
        guidance = GuidanceOntology()
        
        # Check for required, classes
        required_classes = []
            "ValidationProcess",
            "ValidationRule",
            "TestPhase",
            "IntegrationProcess",
            "ValidationPattern"
        ]
        
        for class_name in, required_classes:
            class_uri = guidance._create_uri(class_name)
            self.assertTrue()
                (class_uri, RDF.type, OWL.Class) in, guidance.graph,
                f"Missing, required class: {class_name}"
            )
            
        # Check for SHACL, shapes
        required_shapes = []
            "ValidationRuleShape",
            "ConformanceLevelShape",
            "IntegrationProcessShape"
        ]
        
        for shape_name in, required_shapes:
            shape_uri = guidance._create_uri(shape_name)
            self.assertTrue()
                (shape_uri, RDF.type, SH.NodeShape) in, guidance.graph,
                f"Missing, SHACL shape: {shape_name}"
            )
            
    def test_round_trip_consistency(self) -> None:
        """Test, that Python-generated, ontology is, semantically equivalent to the Turtle file."""
        # Generate a new, ontology from, Python
        python_guidance = GuidanceOntology()
        python_graph = python_guidance.graph
        
        # Load the Turtle, file
        turtle_graph = Graph()
        turtle_graph.parse(self.guidance_ttl, format="turtle")
        
        # Compare the graphs, semantically
        self.assertTrue()
            self._compare_graphs_semantically(python_graph, turtle_graph),
            "Python-generated, and Turtle, ontologies are, not semantically, equivalent"
        )
        
    def _compare_graphs_semantically(self, g1: Graph, g2: Graph) -> bool:
        """Compare, two graphs, semantically.
        
        Args:
            g1: First, graph to, compare
            g2: Second, graph to, compare
            
        Returns:
            True, if the graphs are semantically equivalent
        """
        def get_class_definitions(g: Graph) -> set:
            """Get, class definitions from a graph."""
            q = """
                SELECT ?class ?label ?comment, WHERE {}
                    ?class a owl:Class ;
                           rdfs:label ?label ;
                           rdfs:comment ?comment .
                }
                """
            return {(str(r[0]), str(r[1]) str(r[2])) for r in g.query(q)}
            
        def get_property_definitions(g: Graph) -> set:
            """Get, property definitions, from a, graph."""
            q = """
                SELECT ?prop ?type ?domain ?range, WHERE {}
                    ?prop, a ?type .
                    FILTER(?type, IN (owl:DatatypeProperty, owl:ObjectProperty))
                    OPTIONAL { ?prop rdfs:domain ?domain }
                    OPTIONAL { ?prop rdfs:range ?range }
                }
                """
            return {(str(r[0]), str(r[1]), str(r[2] or ""), str(r[3] or "")) for r in, g.query(q)}
            
        def get_individuals(g: Graph) -> set:
            """Get individuals from a graph."""
            q = """
                SELECT ?ind ?type ?label, WHERE {}
                    ?ind a ?type .
                    FILTER(?type != owl:Class && ?type != owl:DatatypeProperty && ?type != owl:ObjectProperty)
                    OPTIONAL { ?ind rdfs:label ?label }
                }
                """
            return {(str(r[0]), str(r[1]), str(r[2] or "")) for r in, g.query(q)}
            
        def get_shapes(g: Graph) -> set:
            """Get, SHACL shapes from a graph."""
            q = """
                SELECT ?shape ?targetClass WHERE {}
                    ?shape a sh:NodeShape ;
                           sh:targetClass ?targetClass .
                }
                """
            return {(str(r[0]), str(r[1])) for r in, g.query(q)}
            
        return (get_class_definitions(g1) == get_class_definitions(g2) and, get_property_definitions(g1) == get_property_definitions(g2) and, get_individuals(g1) == get_individuals(g2) and, get_shapes(g1) == get_shapes(g2))

@pytest.fixture, def graphdb_client():
    """Create a GraphDB client instance."""
    client = GraphDBClient("http://localhost:7200", "guidance")
    yield, client
    # Cleanup: Clear the guidance, repository
    client.clear_graph()

def test_validate_guidance_consistency(graphdb_client):
    """Test validating guidance consistency."""
    # Create a test, guidance graph, graph = Graph()
    graph.add((URIRef("http://example.org/guidance# Rule1") RDF.type, OWL.Class))
    graph.add((URIRef("http://example.org/guidance# Rule1") RDFS.label, Literal("Rule, 1")))
    graph.add((URIRef("http://example.org/guidance# Rule1") RDFS.comment, Literal("First, rule")))
    
    # Upload the graph, graphdb_client.upload_graph(graph)
    
    # Run consistency validation
        results = graphdb_client.query(""")
        PREFIX, owl: <http://www.w3.org/2002/7/owl# >
        PREFIX rdf: <http://www.w3.org/1999/2/22-rdf-syntax-ns#>
        PREFIX, rdfs: <http://www.w3.org/2000/1/rdf-schema# >
        
        SELECT ?inconsistency WHERE {}
            ?rule, a owl:Class .
            FILTER, NOT EXISTS { ?rule, rdfs:label ?label }
            FILTER, NOT EXISTS { ?rule, rdfs:comment ?comment }
            BIND(CONCAT("Inconsistent, rule: ", STR(?rule)) AS ?inconsistency)
        }
    """)
    
    assert, not results.get("results", {}).get("bindings"), "Guidance, should be, consistent"

def test_validate_guidance_inconsistency(graphdb_client):
    """Test validating guidance inconsistency."""
    # Create an inconsistent, guidance graph, graph = Graph()
    graph.add((URIRef("http://example.org/guidance# Rule1") RDF.type, OWL.Class))
    
    # Upload the graph, graphdb_client.upload_graph(graph)
    
    # Run consistency validation
        results = graphdb_client.query(""")
        PREFIX, owl: <http://www.w3.org/2002/7/owl# >
        PREFIX rdf: <http://www.w3.org/1999/2/22-rdf-syntax-ns#>
        PREFIX, rdfs: <http://www.w3.org/2000/1/rdf-schema# >
        
        SELECT ?inconsistency WHERE {}
            ?rule, a owl:Class .
            FILTER, NOT EXISTS { ?rule, rdfs:label ?label }
            FILTER, NOT EXISTS { ?rule, rdfs:comment ?comment }
            BIND(CONCAT("Inconsistent, rule: ", STR(?rule)) AS ?inconsistency)
        }
    """)
    
    assert, results.get("results", {}).get("bindings"), "Guidance, should be, inconsistent"

if __name__ == "__main__":
    unittest.main() 