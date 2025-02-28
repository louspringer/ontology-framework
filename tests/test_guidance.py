import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import OWL, RDF, RDFS, Graph, Literal, Namespace, URIRef


class TestGuidanceOntology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up paths
        cls.base_path = Path(__file__).parent.parent
        cls.test_file = cls.base_path / "tests" / "guidance_test.ttl"
        cls.guidance_file = cls.base_path / "guidance.ttl"
        cls.modules_path = cls.base_path / "guidance" / "modules"

        # Load all ontologies
        cls.g = Graph()
        cls.g.parse(cls.test_file, format="turtle")
        cls.g.parse(cls.guidance_file, format="turtle")

        # Load all modules
        for module in [
            "core.ttl",
            "model.ttl",
            "security.ttl",
            "validation.ttl",
            "collaboration.ttl",
        ]:
            module_path = cls.modules_path / module
            print(f"Loading module: {module_path}")
            cls.g.parse(module_path, format="turtle")

        # Define namespaces
        cls.GUIDANCE = Namespace("guidance#")
        cls.TEST = Namespace("guidance_test#")
        cls.CORE = Namespace(str(cls.modules_path / "core#"))

    def test_module_registry_completeness(self):
        """Test that all modules are properly registered"""
        query = """
        SELECT (COUNT(?module) as ?count) WHERE {
            ?registry rdf:type guidance:ModuleRegistry ;
                     guidance:registeredModule ?module .
        }
        """
        results = list(self.g.query(query))
        if not results:
            self.fail("No results from module registry query")
        result = results[0]
        if not isinstance(result[0], Literal):
            self.fail("Count result is not a Literal")
        count = int(result[0])
        self.assertEqual(count, 5, "Should have exactly 5 registered modules")

    def test_module_imports(self):
        """Test that each module has proper imports"""
        query = """
        SELECT ?module WHERE {
            ?module rdf:type owl:Ontology .
            FILTER NOT EXISTS { ?module owl:imports ?import }
        }
        """
        result = list(self.g.query(query))
        self.assertEqual(len(result), 0, "All modules should have imports")

    def test_legacy_support(self):
        """Test legacy support mappings"""
        query = """
        SELECT (COUNT(?mapping) as ?count) WHERE {
            ?support rdf:type guidance:LegacySupport ;
                    guidance:hasLegacyMapping ?mapping .
        }
        """
        results = list(self.g.query(query))
        if not results:
            self.fail("No results from legacy support query")
        result = results[0]
        if not isinstance(result[0], Literal):
            self.fail("Count result is not a Literal")
        count = int(result[0])
        self.assertEqual(count, 5, "Should have legacy mappings for all modules")

    def test_version_consistency(self):
        """Test version information consistency"""
        query = """
        SELECT ?module WHERE {
            ?module rdf:type owl:Ontology .
            FILTER NOT EXISTS { ?module owl:versionInfo ?version }
        }
        """
        result = list(self.g.query(query))
        self.assertEqual(len(result), 0, "All modules should have version info")

    def test_shacl_constraints(self):
        """Test SHACL constraints"""
        # Load test shapes
        shapes_graph = Graph()
        shapes_graph.parse(self.test_file, format="turtle")

        # Validate against SHACL shapes
        conforms, results_graph, results_text = validate(
            self.g,
            shacl_graph=shapes_graph,
            inference="rdfs",
            abort_on_first=True,
        )

        self.assertTrue(conforms, f"SHACL validation failed:\n{results_text}")

    def test_module_class_definitions(self):
        """Test that each module defines its required classes"""
        required_classes = {
            "core": ["Interpretation", "Action", "DomainAnalogy", "BestPractice"],
            "model": ["ModelFirstPrinciple", "ModelQualityPrecedence"],
            "security": ["SecurityPattern", "AuthenticationPattern"],
            "validation": ["ValidationPattern", "TestCase"],
            "collaboration": ["PRManagementPattern", "PRTemplate"],
        }

        # Debug: Print all classes and their labels
        print("\nDebug: All Classes and Labels:")
        for s, p, o in self.g.triples((None, RDF.type, OWL.Class)):
            label = self.g.value(s, RDFS.label)
            print(f"Class: {s} Label: {label}")

            # Special debug for BestPractice class
            if isinstance(label, Literal) and str(label) == "BestPractice":
                print(f"\nFound BestPractice class at {s}")
                for p2, o2 in self.g.predicate_objects(s):
                    print(f"  {p2} -> {o2}")

        for module, classes in required_classes.items():
            for class_name in classes:
                query = f"""
                SELECT ?class ?label WHERE {{
                    ?class rdf:type owl:Class ;
                           rdfs:label ?label .
                    FILTER(str(?label) = "{class_name}")
                }}
                """
                results = list(self.g.query(query))
                if not results:
                    print(f"\nDebug: Missing class {class_name} in {module} module")
                    print("Current classes with similar labels:")
                    similar_query = f"""
                    SELECT ?class ?label WHERE {{
                        ?class rdf:type owl:Class ;
                               rdfs:label ?label .
                        FILTER(contains(str(?label), "{class_name}"))
                    }}
                    """
                    similar_results = list(self.g.query(similar_query))
                    for row in similar_results:
                        class_uri = (
                            row[0]
                            if isinstance(row[0], (URIRef, Literal))
                            else str(row[0])
                        )
                        label = row[1] if isinstance(row[1], Literal) else str(row[1])
                        print(f"Found similar: {class_uri} with label {label}")

                    # Special debug for BestPractice
                    if class_name == "BestPractice":
                        bp_uri = self.CORE["BestPractice"]
                        print(f"\nLooking for BestPractice at {bp_uri}")
                        for p, o in self.g.predicate_objects(bp_uri):
                            print(f"  {p} -> {o}")

                    self.fail(f"Missing class {class_name} in {module} module")


if __name__ == "__main__":
    unittest.main()
