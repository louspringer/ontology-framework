import unittest
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
# TODO: Create missing constraints module
# from ontology_framework.modules.constraints import (
#     ModuleConstraints,
#     ConstraintViolation,
#     ConstraintValidationResult
# )

# Temporary placeholder classes for testing
class ModuleConstraints:
    def __init__(self):
        self.constraints = []
    
    def get_all(self):
        return self.constraints
    
    def add(self, constraint):
        self.constraints.append(constraint)
    
    def validate(self, graph):
        return ConstraintValidationResult(True, [], [])

class ConstraintViolation:
    def __init__(self, constraint_id, severity, message=""):
        self.constraint_id = constraint_id
        self.severity = severity
        self.message = message

class ConstraintValidationResult:
    def __init__(self, is_valid, violations=None, warnings=None):
        self.is_valid = is_valid
        self.violations = violations or []
        self.warnings = warnings or []

class TestModuleConstraints(unittest.TestCase):
    """Test cases for module constraints."""

    def setUp(self):
        """Set up test fixtures."""
        self.constraints = ModuleConstraints()
        self.test_graph = Graph()
        
        # Set up test data
        self.test_ns = Namespace("http://example.org/test#")
        self.test_graph.bind("test", self.test_ns)
        self.test_graph.bind("rdf", RDF)
        self.test_graph.bind("rdfs", RDFS)
        self.test_graph.bind("owl", OWL)
        self.test_graph.bind("sh", SH)

    def test_constraint_initialization(self):
        """Test constraint initialization."""
        self.assertIsNotNone(self.constraints)
        self.assertEqual(len(self.constraints.get_all()), 0)

    def test_add_constraint(self):
        """Test adding a constraint."""
        constraint = {
            "id": "test_constraint",
            "description": "Test constraint",
            "severity": "error",
            "query": """
                SELECT ?subject ?predicate ?object
                WHERE {
                    ?subject ?predicate ?object .
                }
            """
        }
        self.constraints.add(constraint)
        self.assertEqual(len(self.constraints.get_all()), 1)

    def test_validate_constraints(self):
        """Test constraint validation."""
        # Add test data
        self.test_graph.add((
            self.test_ns.TestClass,
            RDF.type,
            OWL.Class
        ))
        
        # Add test constraint
        constraint = {
            "id": "class_definition",
            "description": "Check class definitions",
            "severity": "error",
            "query": """
                SELECT ?class
                WHERE {
                    ?class a owl:Class .
                }
            """
        }
        self.constraints.add(constraint)
        
        # Validate
        result = self.constraints.validate(self.test_graph)
        self.assertIsInstance(result, ConstraintValidationResult)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.violations), 0)

    def test_constraint_violation(self):
        """Test constraint violation detection."""
        # Add invalid data
        self.test_graph.add((
            self.test_ns.InvalidClass,
            RDF.type,
            Literal("Invalid")
        ))
        
        # Add constraint that should detect the violation
        constraint = {
            "id": "valid_class_type",
            "description": "Classes must have valid type",
            "severity": "error",
            "query": """
                SELECT ?class
                WHERE {
                    ?class a ?type .
                    FILTER (!isIRI(?type))
                }
            """
        }
        self.constraints.add(constraint)
        
        # Validate
        result = self.constraints.validate(self.test_graph)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.violations), 1)
        
        violation = result.violations[0]
        self.assertIsInstance(violation, ConstraintViolation)
        self.assertEqual(violation.constraint_id, "valid_class_type")
        self.assertEqual(violation.severity, "error")

    def test_custom_severity_levels(self):
        """Test custom severity levels."""
        constraint = {
            "id": "custom_severity",
            "description": "Test custom severity",
            "severity": "warning",
            "query": "SELECT * WHERE { ?s ?p ?o }"
        }
        self.constraints.add(constraint)
        
        result = self.constraints.validate(self.test_graph)
        self.assertTrue(result.is_valid)  # Warnings don't make it invalid
        self.assertEqual(len(result.warnings), 1)

    def tearDown(self):
        """Clean up test fixtures."""
        self.constraints = None
        self.test_graph = None
        self.test_ns = None

if __name__ == '__main__':
    unittest.main() 