#!/usr/bin/env python3
"""Test suite for MCP prompt implementation."""

from typing import Dict, List, Any
import pytest
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from src.ontology_framework.modules.mcp_prompt import (
    MCPPrompt,
    PromptContext,
    PromptError,
    DiscoveryPhase,
    PlanPhase,
    DoPhase,
    CheckPhase,
    ActPhase,
    AdjustPhase
)
from rdflib import Graph, URIRef

class TestPromptContext(unittest.TestCase):
    """Test cases for PromptContext."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.valid_ontology = Path("models/mcp_prompt.ttl")
        self.valid_target = Path("src/ontology_framework/modules/ontology.py")
        self.invalid_path = Path("nonexistent.ttl")
    
    def test_valid_context(self) -> None:
        """Test valid context configuration."""
        context = PromptContext(
            ontology_path=self.valid_ontology,
            target_files=[self.valid_target]
        )
        context.validate()  # Should not raise
    
    def test_invalid_ontology_path(self) -> None:
        """Test invalid ontology path."""
        context = PromptContext(
            ontology_path=self.invalid_path,
            target_files=[self.valid_target]
        )
        with self.assertRaises(PromptError) as cm:
            context.validate()
        self.assertIn("Ontology path does not exist", str(cm.exception))
    
    def test_invalid_target_file(self) -> None:
        """Test invalid target file."""
        context = PromptContext(
            ontology_path=self.valid_ontology,
            target_files=[self.invalid_path]
        )
        with self.assertRaises(PromptError) as cm:
            context.validate()
        self.assertIn("Target file does not exist", str(cm.exception))

class TestPlanPhase(unittest.TestCase):
    """Test cases for PlanPhase."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.phase = PlanPhase()
        self.context = PromptContext(
            ontology_path=Path("models/mcp_prompt.ttl"),
            target_files=[Path("src/ontology_framework/modules/ontology.py")]
        )
    
    def test_successful_execution(self) -> None:
        """Test successful plan phase execution."""
        results = self.phase.execute(self.context)
        self.assertEqual(self.phase.status, "COMPLETED")
        self.assertIn("classes", results)
        self.assertIn("properties", results)
        self.assertIn("validation_rules", results)
        self.assertIn("metadata", results)
    
    def test_invalid_context(self) -> None:
        """Test execution with invalid context."""
        invalid_context = PromptContext(
            ontology_path=Path("nonexistent.ttl"),
            target_files=[Path("nonexistent.py")]
        )
        with self.assertRaises(PromptError):
            self.phase.execute(invalid_context)
        self.assertEqual(self.phase.status, "ERROR")

class TestDoPhase(unittest.TestCase):
    """Test cases for DoPhase."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.phase = DoPhase()
        self.context = {
            'plan': {
                'validation_rules': {'rule1': 'value1'},
                'file_changes': {
                    'file1.ttl': {'action': 'create'},
                    'file2.ttl': {'action': 'modify'}
                }
            }
        }
    
    def test_successful_execution(self) -> None:
        """Test successful do phase execution."""
        results = self.phase.execute(self.context)
        self.assertEqual(results['status'], 'COMPLETED')
        self.assertIn('file1.ttl', results['generated_files'])
        self.assertIn('file2.ttl', results['modified_files'])
        self.assertEqual(results['validation_rules'], {'rule1': 'value1'})
    
    def test_error_handling(self) -> None:
        """Test error handling in do phase."""
        # Create context that should cause an error
        error_context = {'plan': {'file_changes': {'invalid': None}}}
        results = self.phase.execute(error_context)
        self.assertEqual(results['status'], 'ERROR')
        self.assertIn('error', results)

class TestCheckPhase(unittest.TestCase):
    """Test cases for CheckPhase."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.phase = CheckPhase()
        self.context = PromptContext(
            ontology_path=Path("models/mcp_prompt.ttl"),
            target_files=[Path("src/ontology_framework/modules/ontology.py")]
        )
        self.do_results = {
            "modified_files": ["test.py"],
            "status": "COMPLETED"
        }
    
    def test_successful_execution(self) -> None:
        """Test successful check phase execution."""
        results = self.phase.execute(self.context, self.do_results)
        self.assertEqual(self.phase.status, "COMPLETED")
        self.assertIn("validation_results", results)
        self.assertIn("test_results", results)
        self.assertIn("do_results", results)
    
    def test_failed_do_phase(self) -> None:
        """Test execution with failed do phase."""
        failed_do = {"status": "ERROR"}
        with self.assertRaises(PromptError) as cm:
            self.phase.execute(self.context, failed_do)
        self.assertIn("Cannot execute Check phase with failed Do phase", str(cm.exception))
        self.assertEqual(self.phase.status, "ERROR")

class TestActPhase(unittest.TestCase):
    """Test cases for ActPhase."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.phase = ActPhase()
        self.context = PromptContext(
            ontology_path=Path("models/mcp_prompt.ttl"),
            target_files=[Path("src/ontology_framework/modules/ontology.py")]
        )
        self.check_results = {
            "validation_results": [
                {"file": "test.py", "status": "PASSED", "details": "OK"}
            ],
            "status": "COMPLETED"
        }
    
    def test_successful_execution(self) -> None:
        """Test successful act phase execution."""
        results = self.phase.execute(self.context, self.check_results)
        self.assertEqual(self.phase.status, "COMPLETED")
        self.assertIn("adjustments", results)
        self.assertIn("recommendations", results)
        self.assertIn("check_results", results)
    
    def test_failed_check_phase(self) -> None:
        """Test execution with failed check phase."""
        failed_check = {"status": "ERROR"}
        with self.assertRaises(PromptError) as cm:
            self.phase.execute(self.context, failed_check)
        self.assertIn("Cannot execute Act phase with failed Check phase", str(cm.exception))
        self.assertEqual(self.phase.status, "ERROR")

class TestDiscoveryPhase(unittest.TestCase):
    """Test cases for DiscoveryPhase."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.phase = DiscoveryPhase()
        self.context = PromptContext(
            ontology_path=Path("models/mcp_prompt.ttl"),
            target_files=[Path("src/ontology_framework/modules/ontology.py")]
        )
    
    def test_successful_execution(self) -> None:
        """Test successful discovery phase execution."""
        results = self.phase.execute(self.context)
        self.assertEqual(self.phase.status, "COMPLETED")
        
        # Verify ontology analysis structure
        self.assertIn("ontology_analysis", results)
        ontology_analysis = results["ontology_analysis"]
        self.assertIn("classes", ontology_analysis)
        self.assertIn("properties", ontology_analysis)
        self.assertIn("data_properties", ontology_analysis)
        self.assertIn("individuals", ontology_analysis)
        self.assertIn("class_hierarchy", ontology_analysis)
        self.assertIn("shapes", ontology_analysis)
        
        # Verify file analysis structure
        self.assertIn("file_analysis", results)
        self.assertTrue(isinstance(results["file_analysis"], list))
        if results["file_analysis"]:
            file_info = results["file_analysis"][0]
            self.assertIn("file", file_info)
            self.assertIn("exists", file_info)
            self.assertIn("size", file_info)
            self.assertIn("modified", file_info)
        
        # Verify metadata structure
        self.assertIn("metadata", results)
        metadata = results["metadata"]
        self.assertIn("ontology_path", metadata)
        self.assertIn("ontology_format", metadata)
        self.assertIn("discovery_timestamp", metadata)
        
        # Verify data types
        self.assertTrue(all(isinstance(cls, URIRef) for cls in ontology_analysis["classes"]))
        self.assertTrue(all(isinstance(prop, URIRef) for prop in ontology_analysis["properties"]))
        self.assertTrue(isinstance(ontology_analysis["class_hierarchy"], dict))
        self.assertTrue(isinstance(ontology_analysis["shapes"], dict))
    
    def test_invalid_context(self) -> None:
        """Test execution with invalid context."""
        invalid_context = PromptContext(
            ontology_path=Path("nonexistent.ttl"),
            target_files=[Path("nonexistent.py")]
        )
        with self.assertRaises(PromptError) as cm:
            self.phase.execute(invalid_context)
        self.assertEqual(self.phase.status, "ERROR")
        self.assertIn("Ontology path does not exist", str(cm.exception))

class TestMCPPrompt(unittest.TestCase):
    """Test cases for MCPPrompt."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.context = PromptContext(
            ontology_path=Path("models/mcp_prompt.ttl"),
            target_files=[Path("src/ontology_framework/modules/ontology.py")]
        )
    
    def test_successful_execution(self) -> None:
        """Test successful MCP prompt execution."""
        prompt = MCPPrompt(self.context)
        results = prompt.execute()
        
        # Check for phase results
        self.assertIn("discovery", results)
        self.assertIn("plan", results)
        self.assertIn("do", results)
        self.assertIn("check", results)
        self.assertIn("act", results)
        
        # Verify discovery phase structure
        discovery_results = results["discovery"]
        self.assertIn("ontology_analysis", discovery_results)
        self.assertIn("file_analysis", discovery_results)
        self.assertIn("metadata", discovery_results)
        
        # Verify plan phase structure
        plan_results = results["plan"]
        self.assertIn("classes", plan_results)
        self.assertIn("properties", plan_results)
        self.assertIn("validation_rules", plan_results)
        self.assertIn("metadata", plan_results)
        
        # Verify do phase structure
        do_results = results["do"]
        self.assertIn("generated_files", do_results)
        self.assertIn("modified_files", do_results)
        self.assertIn("plan_results", do_results)
        
        # Verify check phase structure
        check_results = results["check"]
        self.assertIn("validation_results", check_results)
        self.assertIn("test_results", check_results)
        self.assertIn("do_results", check_results)
        
        # Verify act phase structure
        act_results = results["act"]
        self.assertIn("adjustments", act_results)
        self.assertIn("recommendations", act_results)
        self.assertIn("check_results", act_results)
        
        # Verify that classes and properties contain URIRefs
        self.assertTrue(all(isinstance(cls, URIRef) for cls in plan_results["classes"]))
        self.assertTrue(all(isinstance(prop, URIRef) for prop in plan_results["properties"]))
        
        # Verify that validation_rules and metadata are dictionaries
        self.assertIsInstance(plan_results["validation_rules"], dict)
        self.assertIsInstance(plan_results["metadata"], dict)
        
        # Verify that file lists are lists
        self.assertIsInstance(do_results["generated_files"], list)
        self.assertIsInstance(do_results["modified_files"], list)
        
        # Verify that validation and test results are lists
        self.assertIsInstance(check_results["validation_results"], list)
        self.assertIsInstance(check_results["test_results"], list)
        
        # Verify that adjustments and recommendations are lists
        self.assertIsInstance(act_results["adjustments"], list)
        self.assertIsInstance(act_results["recommendations"], list)
    
    def test_error_handling(self) -> None:
        """Test error handling in MCP prompt execution."""
        invalid_context = PromptContext(
            ontology_path=Path("nonexistent.ttl"),
            target_files=[Path("nonexistent.py")]
        )
        prompt = MCPPrompt(invalid_context)
        results = prompt.execute()
        
        self.assertIn("error", results)
        self.assertIn("phases", results)
        self.assertEqual(results["phases"]["plan"], "ERROR")

class TestAdjustPhase(unittest.TestCase):
    """Test cases for AdjustPhase."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.phase = AdjustPhase()
        self.context = {
            'check': {
                'validation_results': [
                    {'file': 'test.ttl', 'status': 'FAILED', 'rule': 'rule1', 'details': 'Error message'},
                    {'file': 'test2.ttl', 'status': 'PASSED', 'rule': 'rule2', 'details': 'OK'}
                ]
            }
        }
    
    def test_successful_execution(self) -> None:
        """Test successful adjust phase execution."""
        results = self.phase.execute(self.context)
        self.assertIn('check_results', results)
        self.assertEqual(len(results['adjustments']), 1)
        self.assertEqual(results['adjustments'][0]['file'], 'test.ttl')
        self.assertEqual(results['adjustments'][0]['rule'], 'rule1')
        self.assertIn('Error message', results['adjustments'][0]['action'])
    
    def test_no_adjustments_needed(self) -> None:
        """Test adjust phase with no adjustments needed."""
        context = {
            'check': {
                'validation_results': [
                    {'file': 'test.ttl', 'status': 'PASSED', 'rule': 'rule1', 'details': 'OK'}
                ]
            }
        }
        results = self.phase.execute(context)
        self.assertEqual(len(results['adjustments']), 0)
        self.assertEqual(len(results['recommendations']), 0)

if __name__ == "__main__":
    unittest.main() 