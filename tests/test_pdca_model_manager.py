"""Tests for the PDCA model manager."""

import unittest
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from src.ontology_framework.model.pdca_model_manager import PDCAModelManager

# Define namespaces
PDCA = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/pdca#")

class TestPDCAModelManager(unittest.TestCase):
    """Test cases for PDCAModelManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PDCAModelManager()
        
    def test_pdca_loop_creation(self):
        """Test that a PDCA loop is created correctly."""
        loop = self.manager.start_pdca_loop()
        
        # Check loop instance
        self.assertTrue((loop, RDF.type, PDCA.PDCALoop) in self.manager.graph)
        self.assertTrue((loop, PDCA.hasStatus, Literal("ACTIVE")) in self.manager.graph)
        
    def test_plan_phase(self):
        """Test that the Plan phase is created correctly."""
        # Start a loop
        loop = self.manager.start_pdca_loop()
        
        # Define objectives
        objectives = {
            "obj1": {
                "label": "Test Objective 1",
                "description": "Test description",
                "tasks": [
                    {
                        "label": "Task 1",
                        "description": "Task description",
                        "priority": "HIGH"
                    }
                ]
            }
        }
        
        # Create plan phase
        plan_phase = self.manager.plan_phase(objectives)
        
        # Check plan phase instance
        self.assertTrue((plan_phase, RDF.type, PDCA.PlanPhase) in self.manager.graph)
        self.assertTrue((plan_phase, PDCA.hasStatus, Literal("IN_PROGRESS")) in self.manager.graph)
        
        # Check objectives
        self.assertTrue((PDCA.obj1, RDF.type, PDCA.Objective) in self.manager.graph)
        self.assertTrue((PDCA.obj1, RDFS.label, Literal("Test Objective 1")) in self.manager.graph)
        
    def test_do_phase(self):
        """Test that the Do phase is created correctly."""
        # Start a loop and create plan phase
        loop = self.manager.start_pdca_loop()
        plan_phase = self.manager.plan_phase({})
        
        # Create do phase
        do_phase = self.manager.do_phase(plan_phase)
        
        # Check do phase instance
        self.assertTrue((do_phase, RDF.type, PDCA.DoPhase) in self.manager.graph)
        self.assertTrue((do_phase, PDCA.hasStatus, Literal("IN_PROGRESS")) in self.manager.graph)
        self.assertTrue((do_phase, PDCA.implementsPlan, plan_phase) in self.manager.graph)
        
    def test_check_phase(self):
        """Test that the Check phase is created correctly."""
        # Start a loop and create plan and do phases
        loop = self.manager.start_pdca_loop()
        plan_phase = self.manager.plan_phase({})
        do_phase = self.manager.do_phase(plan_phase)
        
        # Create check phase
        check_phase = self.manager.check_phase(do_phase)
        
        # Check check phase instance
        self.assertTrue((check_phase, RDF.type, PDCA.CheckPhase) in self.manager.graph)
        self.assertTrue((check_phase, PDCA.hasStatus, Literal("IN_PROGRESS")) in self.manager.graph)
        self.assertTrue((check_phase, PDCA.evaluatesDoPhase, do_phase) in self.manager.graph)
        
    def test_act_phase(self):
        """Test that the Act phase is created correctly."""
        # Start a loop and create plan, do, and check phases
        loop = self.manager.start_pdca_loop()
        plan_phase = self.manager.plan_phase({})
        do_phase = self.manager.do_phase(plan_phase)
        check_phase = self.manager.check_phase(do_phase)
        
        # Create act phase
        act_phase = self.manager.act_phase(check_phase)
        
        # Check act phase instance
        self.assertTrue((act_phase, RDF.type, PDCA.ActPhase) in self.manager.graph)
        self.assertTrue((act_phase, PDCA.hasStatus, Literal("IN_PROGRESS")) in self.manager.graph)
        self.assertTrue((act_phase, PDCA.basedOnCheckPhase, check_phase) in self.manager.graph)
        
    def test_validation(self):
        """Test that the model validates correctly."""
        # Create a complete PDCA cycle
        loop = self.manager.start_pdca_loop()
        plan_phase = self.manager.plan_phase({})
        do_phase = self.manager.do_phase(plan_phase)
        check_phase = self.manager.check_phase(do_phase)
        act_phase = self.manager.act_phase(check_phase)
        
        # Validate the model
        result = self.manager.validate_model()
        self.assertTrue(result["conforms"])
        
    def test_save_load(self):
        """Test saving and loading the model."""
        # Create a complete PDCA cycle
        loop = self.manager.start_pdca_loop()
        plan_phase = self.manager.plan_phase({})
        do_phase = self.manager.do_phase(plan_phase)
        check_phase = self.manager.check_phase(do_phase)
        act_phase = self.manager.act_phase(check_phase)
        
        # Save in RDF/XML format
        self.manager.save_model(format="xml")
        
        # Create new manager and load
        new_manager = PDCAModelManager()
        new_manager.load_model(format="xml")
        
        # Check that loaded model matches original
        self.assertEqual(len(self.manager.graph), len(new_manager.graph))
        
    def test_query(self):
        """Test querying the model."""
        # Create a complete PDCA cycle
        loop = self.manager.start_pdca_loop()
        plan_phase = self.manager.plan_phase({})
        do_phase = self.manager.do_phase(plan_phase)
        check_phase = self.manager.check_phase(do_phase)
        act_phase = self.manager.act_phase(check_phase)
        
        # Query for all phases
        query = """
        SELECT ?phase ?type
        WHERE {
            ?phase a ?type .
            FILTER (?type IN (pdca:PlanPhase, pdca:DoPhase, pdca:CheckPhase, pdca:ActPhase))
        }
        """
        results = self.manager.query_model(query)
        self.assertIsNotNone(results)
        self.assertEqual(len(list(results)), 4)  # Should find all four phases
        
if __name__ == "__main__":
    unittest.main() 