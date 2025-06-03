"""
Test cases for validation telemetry collection and analysis.
"""
import pytest
from datetime import datetime
from typing import Dict, List, Any

from ontology_framework.mcp.validation_telemetry import (
    ValidationTelemetry,
    ValidationMetrics,
    PatternMetrics
)
from ontology_framework.mcp.hypercube_analysis import HypercubeAnalyzer
from ontology_framework.mcp.bfg9k_targeting import BFG9KTargeter

@pytest.fixture
def hypercube_analyzer():
    """Fixture for hypercube analyzer instance"""
    analyzer = HypercubeAnalyzer()
    # Update dimensions with test values
    analyzer.dimensions["semantic_accuracy"].update(0.95)
    analyzer.dimensions["response_time"].update(0.5)
    analyzer.dimensions["confidence"].update(0.9)
    analyzer.dimensions["validation_success"].update(1.0)
    return analyzer

@pytest.fixture
def bfg9k_targeter(hypercube_analyzer):
    """Fixture for BFG9K targeter instance"""
    return BFG9KTargeter(hypercube_analyzer=hypercube_analyzer)

@pytest.fixture
def validation_telemetry(hypercube_analyzer, bfg9k_targeter):
    """Fixture for validation telemetry instance"""
    return ValidationTelemetry(hypercube_analyzer, bfg9k_targeter)

@pytest.fixture
def sample_validation_result() -> Dict[str, Any]:
    """Fixture for sample validation result"""
    return {
        "target": "test_target",
        "ordinance": {
            "rules": ["hierarchy", "semantics", "shacl"],
            "config": {
                "precision": 0.95,
                "recall": 0.90,
                "timeout": 30
            }
        },
        "telemetry": {
            "semantic_accuracy": 0.95,
            "response_time": 0.5,
            "confidence": 0.9,
            "validation_success": True,
            "error_rate": 0.05,
            "throughput": 10.0,
            "resource_usage": 0.7
        }
    }

def test_collect_metrics(validation_telemetry, sample_validation_result):
    """Test metrics collection from validation result"""
    # Collect metrics
    validation_telemetry.collect_metrics(sample_validation_result)
    
    # Verify metrics were collected
    assert len(validation_telemetry.metrics_history) == 1
    metrics = validation_telemetry.metrics_history[0]
    
    # Verify metric values
    assert metrics.semantic_accuracy == 0.95
    assert metrics.response_time == 0.5
    assert metrics.confidence == 0.9
    assert metrics.validation_success is True
    assert metrics.error_rate == 0.05
    assert metrics.throughput == 10.0
    assert metrics.resource_usage == 0.7
    assert isinstance(metrics.timestamp, datetime)

def test_detect_patterns(validation_telemetry, sample_validation_result):
    """Test pattern detection in validation metrics"""
    # Collect multiple metrics to detect patterns
    for _ in range(5):
        validation_telemetry.collect_metrics(sample_validation_result)
    
    # Detect patterns
    patterns = validation_telemetry.detect_patterns()
    
    # Verify patterns were detected
    assert len(patterns) > 0
    for pattern in patterns:
        assert isinstance(pattern, PatternMetrics)
        assert pattern.pattern_type in ["error_rate", "response_time", "resource_usage"]
        assert 0 <= pattern.frequency <= 1
        assert 0 <= pattern.confidence <= 1
        assert isinstance(pattern.impact, str)
        assert isinstance(pattern.timestamp, datetime)

def test_analyze_performance(validation_telemetry, sample_validation_result):
    """Test performance analysis"""
    # Collect metrics
    for _ in range(3):
        validation_telemetry.collect_metrics(sample_validation_result)
    
    # Analyze performance
    performance = validation_telemetry.analyze_performance()
    
    # Verify performance metrics
    assert "accuracy" in performance
    assert "response_time" in performance
    assert "confidence" in performance
    assert "success_rate" in performance
    assert "trends" in performance
    
    # Verify trend calculations
    trends = performance["trends"]
    assert "accuracy_trend" in trends
    assert "response_time_trend" in trends
    assert "confidence_trend" in trends
    assert "success_rate_trend" in trends

def test_analyze_errors(validation_telemetry, sample_validation_result):
    """Test error analysis"""
    # Collect metrics
    for _ in range(3):
        validation_telemetry.collect_metrics(sample_validation_result)
    
    # Analyze errors
    errors = validation_telemetry.analyze_errors()
    
    # Verify error metrics
    assert "error_rate" in errors
    assert "error_patterns" in errors
    assert "error_distribution" in errors
    
    # Verify error distribution
    distribution = errors["error_distribution"]
    assert "by_rule" in distribution
    assert "by_severity" in distribution
    assert "by_type" in distribution

def test_update_telemetry(validation_telemetry, sample_validation_result):
    """Test telemetry update"""
    # Update telemetry
    validation_telemetry.update_telemetry(sample_validation_result)
    
    # Verify telemetry was updated
    telemetry = validation_telemetry.get_telemetry()
    assert "metrics" in telemetry
    assert "patterns" in telemetry
    assert "performance" in telemetry
    assert "errors" in telemetry
    assert "timestamp" in telemetry

def test_get_telemetry(validation_telemetry, sample_validation_result):
    """Test telemetry retrieval"""
    # Update telemetry
    validation_telemetry.update_telemetry(sample_validation_result)
    
    # Get telemetry
    telemetry = validation_telemetry.get_telemetry()
    
    # Verify telemetry structure
    assert isinstance(telemetry, dict)
    assert "metrics" in telemetry
    assert "patterns" in telemetry
    assert "performance" in telemetry
    assert "errors" in telemetry
    assert "timestamp" in telemetry
    
    # Verify metrics
    metrics = telemetry["metrics"]
    assert isinstance(metrics, list)
    assert len(metrics) > 0
    assert all(isinstance(m, ValidationMetrics) for m in metrics)
    
    # Verify patterns
    patterns = telemetry["patterns"]
    assert isinstance(patterns, list)
    assert all(isinstance(p, PatternMetrics) for p in patterns)
    
    # Verify performance
    performance = telemetry["performance"]
    assert isinstance(performance, dict)
    assert "accuracy" in performance
    assert "response_time" in performance
    assert "confidence" in performance
    assert "success_rate" in performance
    
    # Verify errors
    errors = telemetry["errors"]
    assert isinstance(errors, dict)
    assert "error_rate" in errors
    assert "error_patterns" in errors
    assert "error_distribution" in errors
