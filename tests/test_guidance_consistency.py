"""Test consistency between Python-generated guidance ontology and Turtle file."""

import unittest
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, SH
from rdflib.query import ResultRow
from typing import List, Set, Tuple, cast
from src.ontology_framework.modules.guidance import GuidanceOntology

class TestGuidanceConsistency(unittest.TestCase):
    """Test consistency between Python-generated guidance ontology and Turtle file."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.guidance_ttl = self.project_root / "guidance.ttl"
        
    def test_emit_reload_consistency(self) -> None:
        """Test that emitting and reloading produces the same graph."""
        # Create a temporary file
        temp_file = self.project_root / "temp_guidance.ttl"
        
        try:
            # Generate and emit
            guidance = GuidanceOntology()
            guidance.emit(temp_file)
            
            # Reload
            reloaded = GuidanceOntology(str(temp_file))
            
            # Compare semantically
            self.assertTrue(
                self._compare_graphs_semantically(guidance.graph, reloaded.graph),
                "Emitted and reloaded graphs are not semantically equivalent"
            )
            
        finally:
            # Clean up
            if temp_file.exists():
                temp_file.unlink()
                
    def test_guidance_structure(self) -> None:
        """Test that the guidance ontology has the expected structure."""
        guidance = GuidanceOntology()
        
        # Check for required classes
        required_classes: List[str] = ['IntegrationRequirement', 'SHACLValidation', 'TODO', 'ValidationPattern', 'ConformanceLevel', 'IntegrationProcess', 'IntegrationStep', 'ModelConformance', 'TestProtocol', 'TestPhase', 'TestCoverage']
        
        for class_name in required_classes:
            class_uri = guidance.base[class_name]
            self.assertTrue(
                (class_uri, RDF.type, OWL.Class) in guidance.graph,
                f"Missing required class: {class_name}"
            )
            
        # Check for conformance levels
        conformance_levels: List[str] = ['STRICT', 'MODERATE', 'RELAXED']
        for level in conformance_levels:
            level_uri = guidance.base[level]
            self.assertTrue(
                (level_uri, RDF.type, guidance.base.ConformanceLevel) in guidance.graph,
                f"Missing conformance level: {level}"
            )
            
        # Check for SHACL shapes
        required_shapes: List[str] = []
        
        for shape_name in required_shapes:
            shape_uri = guidance.base[shape_name]
            self.assertTrue(
                (shape_uri, RDF.type, SH.NodeShape) in guidance.graph,
                f"Missing SHACL shape: {shape_name}"
            )
            
    def test_round_trip_consistency(self) -> None:
        """Test that Python-generated ontology is semantically equivalent to the Turtle file."""
        # Generate a new ontology from Python
        python_guidance = GuidanceOntology()
        python_graph = python_guidance.graph
        
        # Load the Turtle file
        turtle_graph = Graph()
        turtle_graph.parse(self.guidance_ttl, format="turtle")
        
        # Compare the graphs semantically
        self.assertTrue(
            self._compare_graphs_semantically(python_graph, turtle_graph),
            "Python-generated and Turtle ontologies are not semantically equivalent"
        )
        
    def _compare_graphs_semantically(self, g1: Graph, g2: Graph) -> bool:
        """Compare two graphs semantically using DAG-informed recursive descent.
        
        Args:
            g1: First graph to compare
            g2: Second graph to compare
            
        Returns:
            True if the graphs are semantically equivalent
        """
        from rdflib import URIRef, Literal, BNode
        from typing import Set, Tuple, Dict, Any, cast
        from rdflib.query import ResultRow
        
        def get_top_level_structure(g: Graph) -> Dict[str, Set[Tuple[str, str]]]:
            """Get top-level structure of the graph.
            
            Returns:
                Dictionary containing sets of (subject, predicate) pairs for each type
            """
            structure: Dict[str, Set[Tuple[str, str]]] = {
                'classes': set(),
                'properties': set(),
                'shapes': set(),
                'individuals': set()
            }
            
            # Get all class definitions
            q = """
                SELECT ?s ?p
                WHERE {
                    ?s a owl:Class .
                    ?s ?p ?o .
                    FILTER(?p IN (rdfs:label, rdfs:comment, owl:versionInfo))
                }
            """
            for row in g.query(q):
                row = cast(ResultRow, row)
                structure['classes'].add((str(row[0]), str(row[1])))
                
            # Get all property definitions
            q = """
                SELECT ?s ?p
                WHERE {
                    ?s a ?type .
                    FILTER(?type IN (owl:DatatypeProperty, owl:ObjectProperty))
                    ?s ?p ?o .
                    FILTER(?p IN (rdfs:label, rdfs:comment, rdfs:domain, rdfs:range))
                }
            """
            for row in g.query(q):
                row = cast(ResultRow, row)
                structure['properties'].add((str(row[0]), str(row[1])))
                
            # Get all SHACL shapes
            q = """
                SELECT ?s ?p
                WHERE {
                    ?s a sh:NodeShape .
                    ?s ?p ?o .
                    FILTER(?p IN (sh:targetClass, sh:property))
                }
            """
            for row in g.query(q):
                row = cast(ResultRow, row)
                structure['shapes'].add((str(row[0]), str(row[1])))
                
            # Get all individuals
            q = """
                SELECT ?s ?p
                WHERE {
                    ?s a ?type .
                    FILTER(?type != owl:Class && ?type != owl:DatatypeProperty && ?type != owl:ObjectProperty)
                    ?s ?p ?o .
                    FILTER(?p IN (rdfs:label, rdfs:comment))
                }
            """
            for row in g.query(q):
                row = cast(ResultRow, row)
                structure['individuals'].add((str(row[0]), str(row[1])))
                
            return structure
            
        def compare_property_values(g1: Graph, g2: Graph, subject: URIRef, predicate: URIRef) -> bool:
            """Compare property values between two graphs.
            
            Args:
                g1: First graph
                g2: Second graph
                subject: Subject URI
                predicate: Predicate URI
                
            Returns:
                True if property values are equivalent
            """
            values1 = set(str(o) for o in g1.objects(subject, predicate))
            values2 = set(str(o) for o in g2.objects(subject, predicate))
            if values1 != values2:
                print(f"Property values differ for {subject} {predicate}:")
                print(f"  Graph 1: {values1}")
                print(f"  Graph 2: {values2}")
                return False
            return True
            
        def compare_shacl_properties(g1: Graph, g2: Graph, shape: URIRef) -> bool:
            """Compare SHACL property shapes between two graphs.
            
            Args:
                g1: First graph
                g2: Second graph
                shape: Shape URI
                
            Returns:
                True if property shapes are equivalent
            """
            # Get all property shapes
            q = """
                SELECT ?path ?minCount ?maxCount ?datatype
                WHERE {
                    ?shape sh:property ?prop .
                    ?prop sh:path ?path .
                    OPTIONAL { ?prop sh:minCount ?minCount }
                    OPTIONAL { ?prop sh:maxCount ?maxCount }
                    OPTIONAL { ?prop sh:datatype ?datatype }
                }
            """
            props1: Set[Tuple[str, str, str, str]] = set()
            props2: Set[Tuple[str, str, str, str]] = set()
            
            for row in g1.query(q, initBindings={'shape': shape}):
                row = cast(ResultRow, row)
                props1.add((str(row[0]), str(row[1] or ""), str(row[2] or ""), str(row[3] or "")))
            for row in g2.query(q, initBindings={'shape': shape}):
                row = cast(ResultRow, row)
                props2.add((str(row[0]), str(row[1] or ""), str(row[2] or ""), str(row[3] or "")))
                
            if props1 != props2:
                print(f"SHACL properties differ for shape {shape}:")
                print(f"  Graph 1: {props1}")
                print(f"  Graph 2: {props2}")
                return False
            return True
            
        # First, compare top-level structure
        structure1 = get_top_level_structure(g1)
        structure2 = get_top_level_structure(g2)
        
        if structure1 != structure2:
            print("Top-level structure differs:")
            for category in structure1:
                if structure1[category] != structure2[category]:
                    print(f"  {category}:")
                    print(f"    Graph 1: {structure1[category]}")
                    print(f"    Graph 2: {structure2[category]}")
            return False
            
        # Then, recursively compare property values
        for category, pairs in structure1.items():
            for subject, predicate in pairs:
                subject_uri = URIRef(subject)
                predicate_uri = URIRef(predicate)
                
                if not compare_property_values(g1, g2, subject_uri, predicate_uri):
                    return False
                    
                # For SHACL shapes, compare property shapes
                if category == 'shapes':
                    if not compare_shacl_properties(g1, g2, subject_uri):
                        return False
                        
        return True

if __name__ == "__main__":
    unittest.main()