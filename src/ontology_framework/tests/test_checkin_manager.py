"""
Tests for the check-in manager module.
"""

import unittest
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.modules.checkin_manager import CheckinManager, StepStatus

# Define namespaces used in the sample plan
CHECKIN = Namespace("http://example.org/checkin#")
PLAN = Namespace("http://example.org/plan#")

class TestCheckinManager(unittest.TestCase):
    """Test suite for the check-in manager module."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.manager = CheckinManager()
        self.test_graph = Graph()
        
    def test_plan_creation(self) -> None:
        """Test plan creation phase."""
        # Test creating a new plan
        plan_id = "test_plan"
        plan_uri = self.manager.create_checkin_plan(plan_id)
        
        # Verify plan properties
        self.assertIsInstance(plan_uri, URIRef)
        self.assertTrue(self.manager.graph.triples((plan_uri, RDF.type, None)))
        self.assertTrue(self.manager.graph.triples((plan_uri, RDFS.label, Literal(plan_id))))
        
    def test_step_management(self) -> None:
        """Test step management phase."""
        # Add test steps
        self.manager.add_step("step1", "First test step")
        self.manager.add_step("step2", "Second test step")
        
        # Test starting a step
        self.manager.start_step("step1")
        step1 = next(s for s in self.manager.steps if s.name == "step1")
        self.assertEqual(step1.status, StepStatus.IN_PROGRESS)
        self.assertIsNotNone(step1.started_at)
        
        # Test completing a step
        self.manager.complete_step("step1")
        self.assertEqual(step1.status, StepStatus.COMPLETED)
        self.assertIsNotNone(step1.completed_at)
        
        # Test failing a step
        self.manager.fail_step("step2", "Test error")
        step2 = next(s for s in self.manager.steps if s.name == "step2")
        self.assertEqual(step2.status, StepStatus.FAILED)
        self.assertEqual(step2.error, "Test error")
        
    def test_validation(self) -> None:
        """Test validation phase."""
        # Create a test ontology
        test_class = URIRef("http://example.org/TestClass")
        self.test_graph.add((test_class, RDF.type, OWL.Class))
        
        # Test basic validation
        messages = self.manager.validate_ontology(self.test_graph)
        self.assertIsInstance(messages, list)
        
        # Test validation with missing labels
        messages = self.manager._validate_basic(self.test_graph)
        self.assertTrue(any("has no label" in msg for msg in messages))
        
    def test_plan_structure(self) -> None:
        """Test check-in plan structure validation."""
        # Load sample plan
        self.manager.load_plan("src/ontology_framework/examples/sample_checkin_plan.ttl")
        
        # Verify plan type
        plan_uri = PLAN.SampleCheckinPlan
        self.assertTrue(self.manager.graph.triples((plan_uri, RDF.type, CHECKIN.CheckinPlan)))
        
        # Verify steps
        step1 = PLAN.Step1
        self.assertTrue(self.manager.graph.triples((step1, RDF.type, CHECKIN.IntegrationStep)))
        self.assertTrue(self.manager.graph.triples((step1, RDFS.label, None)))
        self.assertTrue(self.manager.graph.triples((step1, RDFS.comment, None)))
        
        # Verify step order
        step_order = next(self.manager.graph.objects(step1, CHECKIN.stepOrder))
        self.assertEqual(str(step_order), "1")

if __name__ == '__main__':
    unittest.main() 