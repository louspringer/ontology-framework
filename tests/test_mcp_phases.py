#!/usr/bin/env python3
"""Test suite for MCP phases."""

from typing import Dict, List, Any
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from ontology_framework.modules.phases import (
    PromptPhase,
    PlanPhase,
    DoPhase,
    CheckPhase,
    AdjustPhase,
    PhaseError,
    PhaseResult
)
from rdflib import Graph, URIRef

@pytest.fixture
def sample_ontology_path(tmp_path) -> Path:
    """Create a sample ontology file for testing."""
    ontology_path = tmp_path / "test_ontology.ttl"
    ontology_path.write_text("""
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix ex: <http://example.org/> .
    
    ex:TestClass a owl:Class .
    ex:TestProperty a owl:ObjectProperty .
    ex:TestIndividual a ex:TestClass .
    """)
    return ontology_path

@pytest.fixture
def discovery_context(sample_ontology_path) -> Dict[str, Any]:
    """Create a context for discovery phase."""
    return {
        'ontologyPath': str(sample_ontology_path),
        'targetFiles': ['test1.ttl', 'test2.ttl'],
        'metadata': {'author': 'Test Author'},
        'validationRules': {
            'rule1': {
                'sparql': 'SELECT ?s WHERE { ?s a owl:Class }'
            }
        }
    }

@pytest.fixture
def plan_context() -> Dict[str, Any]:
    """Create a context for plan phase."""
    return {
        'discovery': {
            'results': {
                'ontology_analysis': {
                    'classes': ['ex:TestClass'],
                    'properties': ['ex:TestProperty']
                },
                'file_analysis': [
                    {'file': 'test1.ttl', 'exists': False},
                    {'file': 'test2.ttl', 'exists': True}
                ]
            }
        },
        'improvements': {
            'add_class': 'ex:NewClass'
        }
    }

@pytest.fixture
def do_context() -> Dict[str, Any]:
    """Create a context for do phase."""
    return {
        'plan': {
            'results': {
                'file_changes': {
                    'test1.ttl': {'action': 'create'},
                    'test2.ttl': {'action': 'modify'}
                }
            }
        }
    }

@pytest.fixture
def check_context(sample_ontology_path) -> Dict[str, Any]:
    """Create a context for check phase."""
    return {
        'do': {
            'results': {
                'generated_files': ['test1.ttl'],
                'modified_files': ['test2.ttl']
            }
        },
        'ontologyPath': str(sample_ontology_path),
        'validationRules': {
            'rule1': {
                'sparql': 'SELECT ?s WHERE { ?s a owl:Class }'
            }
        }
    }

@pytest.fixture
def adjust_context() -> Dict[str, Any]:
    """Create a context for adjust phase."""
    return {
        'check': {
            'results': {
                'validation_results': [
                    {
                        'status': 'FAILED',
                        'file': 'test1.ttl',
                        'rule': 'rule1',
                        'details': 'Missing required class'
                    }
                ]
            }
        }
    }

class TestDiscoveryPhase:
    """Test suite for DiscoveryPhase."""
    
    def test_successful_execution(self, discovery_context):
        """Test successful discovery phase execution."""
        phase = PromptPhase()
        result = phase.execute(discovery_context)
        
        assert result.status == "COMPLETED"
        assert result.error is None
        assert result.results is not None
        assert 'ontology_analysis' in result.results
        assert 'file_analysis' in result.results
        assert 'validation_rules' in result.results
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.end_time > result.start_time
    
    def test_invalid_context(self):
        """Test discovery phase with invalid context."""
        phase = PromptPhase()
        with pytest.raises(PhaseError):
            phase.execute({})
    
    def test_missing_ontology(self, discovery_context):
        """Test discovery phase with missing ontology file."""
        discovery_context['ontologyPath'] = 'nonexistent.ttl'
        phase = PromptPhase()
        with pytest.raises(PhaseError):
            phase.execute(discovery_context)

class TestPlanPhase:
    """Test suite for PlanPhase."""
    
    def test_successful_execution(self, plan_context):
        """Test successful plan phase execution."""
        phase = PlanPhase()
        result = phase.execute(plan_context)
        
        assert result.status == "COMPLETED"
        assert result.error is None
        assert result.results is not None
        assert 'classes' in result.results
        assert 'properties' in result.results
        assert 'file_changes' in result.results
        assert result.start_time is not None
        assert result.end_time is not None
    
    def test_invalid_context(self):
        """Test plan phase with invalid context."""
        phase = PlanPhase()
        with pytest.raises(PhaseError):
            phase.execute({})
    
    def test_missing_discovery(self, plan_context):
        """Test plan phase with missing discovery results."""
        del plan_context['discovery']
        phase = PlanPhase()
        with pytest.raises(PhaseError):
            phase.execute(plan_context)

class TestDoPhase:
    """Test suite for DoPhase."""
    
    def test_successful_execution(self, do_context):
        """Test successful do phase execution."""
        phase = DoPhase()
        result = phase.execute(do_context)
        
        assert result.status == "COMPLETED"
        assert result.error is None
        assert result.results is not None
        assert 'generated_files' in result.results
        assert 'modified_files' in result.results
        assert result.start_time is not None
        assert result.end_time is not None
    
    def test_invalid_context(self):
        """Test do phase with invalid context."""
        phase = DoPhase()
        with pytest.raises(PhaseError):
            phase.execute({})
    
    def test_missing_plan(self, do_context):
        """Test do phase with missing plan results."""
        del do_context['plan']
        phase = DoPhase()
        with pytest.raises(PhaseError):
            phase.execute(do_context)

class TestCheckPhase:
    """Test suite for CheckPhase."""
    
    def test_successful_execution(self, check_context):
        """Test successful check phase execution."""
        phase = CheckPhase()
        result = phase.execute(check_context)
        
        assert result.status == "COMPLETED"
        assert result.error is None
        assert result.results is not None
        assert 'validation_results' in result.results
        assert 'do_results' in result.results
        assert result.start_time is not None
        assert result.end_time is not None
    
    def test_invalid_context(self):
        """Test check phase with invalid context."""
        phase = CheckPhase()
        with pytest.raises(PhaseError):
            phase.execute({})
    
    def test_missing_do_results(self, check_context):
        """Test check phase with missing do results."""
        del check_context['do']
        phase = CheckPhase()
        with pytest.raises(PhaseError):
            phase.execute(check_context)
    
    def test_validation_error(self, check_context):
        """Test check phase with validation error."""
        check_context['validationRules']['rule1']['sparql'] = 'INVALID SPARQL'
        phase = CheckPhase()
        result = phase.execute(check_context)
        
        assert result.status == "COMPLETED"
        assert any(r['status'] == 'ERROR' for r in result.results['validation_results'])

class TestAdjustPhase:
    """Test suite for AdjustPhase."""
    
    def test_successful_execution(self, adjust_context):
        """Test successful adjust phase execution."""
        phase = AdjustPhase()
        result = phase.execute(adjust_context)
        
        assert result.status == "COMPLETED"
        assert result.error is None
        assert result.results is not None
        assert 'adjustments' in result.results
        assert 'recommendations' in result.results
        assert len(result.results['adjustments']) > 0
        assert result.start_time is not None
        assert result.end_time is not None
    
    def test_invalid_context(self):
        """Test adjust phase with invalid context."""
        phase = AdjustPhase()
        with pytest.raises(PhaseError):
            phase.execute({})
    
    def test_missing_check_results(self, adjust_context):
        """Test adjust phase with missing check results."""
        del adjust_context['check']
        phase = AdjustPhase()
        with pytest.raises(PhaseError):
            phase.execute(adjust_context)
    
    def test_no_adjustments_needed(self, adjust_context):
        """Test adjust phase when no adjustments are needed."""
        adjust_context['check']['results']['validation_results'][0]['status'] = 'PASSED'
        phase = AdjustPhase()
        result = phase.execute(adjust_context)
        
        assert result.status == "COMPLETED"
        assert len(result.results['adjustments']) == 0 