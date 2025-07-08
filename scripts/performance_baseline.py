#!/usr/bin/env python3
"""
Performance Baseline Script for Ontology Framework

This script establishes performance baselines for the current RDF/SPARQL-based
ontology framework to compare against potential property graph implementations.

Usage:
    python scripts/performance_baseline.py [--output results.json] [--verbose]
"""

import sys
import time
import json
import psutil
import gc
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# RDF imports
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, OWL, XSD, SH
from rdflib.namespace import NamespaceManager
from rdflib.plugins.sparql import prepareQuery

# Ontology framework imports
try:
    from src.ontology_framework.validation_handler import ValidationHandler
    from src.ontology_framework.modules.validator import MCPValidator
    from src.ontology_framework.model.graphdb_model_manager import GraphDBModelManager
except ImportError:
    print("Warning: Could not import ontology framework modules. Running basic tests only.")
    ValidationHandler = None
    MCPValidator = None
    GraphDBModelManager = None

@dataclass
class PerformanceMetric:
    """Represents a single performance measurement."""
    operation: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    triple_count: Optional[int] = None
    result_count: Optional[int] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class PerformanceBaseline:
    """Collection of performance metrics."""
    system_info: Dict[str, Any]
    metrics: List[PerformanceMetric]
    summary: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class PerformanceBaselineRunner:
    """Runs performance baseline tests for the ontology framework."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.process = psutil.Process()
        self.results = []
        
    def log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{datetime.now().isoformat()}] {message}")
    
    def measure_operation(self, operation_name: str, func, *args, **kwargs) -> PerformanceMetric:
        """Measure performance of an operation."""
        self.log(f"Measuring {operation_name}")
        
        # Force garbage collection before measurement
        gc.collect()
        
        # Get initial memory and CPU
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        initial_cpu = self.process.cpu_percent()
        
        # Measure operation
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            error = None
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = None
            error = str(e)
        
        # Get final memory and CPU
        final_memory = self.process.memory_info().rss / 1024 / 1024
        memory_delta = final_memory - initial_memory
        final_cpu = self.process.cpu_percent()
        
        # Extract result count if available
        result_count = None
        if hasattr(result, '__len__'):
            result_count = len(result)
        elif isinstance(result, (list, tuple)):
            result_count = len(result)
        
        metric = PerformanceMetric(
            operation=operation_name,
            duration_ms=duration_ms,
            memory_mb=memory_delta,
            cpu_percent=final_cpu,
            result_count=result_count,
            error=error
        )
        
        self.results.append(metric)
        self.log(f"  Duration: {duration_ms:.2f}ms, Memory: {memory_delta:.2f}MB")
        
        return metric
    
    def load_ontology_files(self) -> List[Graph]:
        """Load all ontology files from the project."""
        ontology_files = []
        
        # Find all .ttl files
        ttl_files = list(Path(".").rglob("*.ttl"))
        self.log(f"Found {len(ttl_files)} TTL files")
        
        for ttl_file in ttl_files:
            try:
                graph = Graph()
                graph.parse(str(ttl_file), format="turtle")
                ontology_files.append(graph)
                self.log(f"  Loaded {ttl_file}: {len(graph)} triples")
            except Exception as e:
                self.log(f"  Failed to load {ttl_file}: {e}")
        
        return ontology_files
    
    def test_basic_queries(self, graphs: List[Graph]) -> List[PerformanceMetric]:
        """Test basic SPARQL query performance."""
        metrics = []
        
        for i, graph in enumerate(graphs):
            # Test 1: Basic triple pattern
            def basic_query():
                return list(graph.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 1000"))
            
            metric = self.measure_operation(f"basic_query_{i}", basic_query)
            metric.triple_count = len(graph)
            metrics.append(metric)
            
            # Test 2: Class query
            def class_query():
                return list(graph.query("""
                    SELECT ?class WHERE {
                        ?class a owl:Class .
                    }
                """))
            
            metric = self.measure_operation(f"class_query_{i}", class_query)
            metric.triple_count = len(graph)
            metrics.append(metric)
            
            # Test 3: Property query
            def property_query():
                return list(graph.query("""
                    SELECT ?property WHERE {
                        ?property a ?type .
                        FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
                    }
                """))
            
            metric = self.measure_operation(f"property_query_{i}", property_query)
            metric.triple_count = len(graph)
            metrics.append(metric)
        
        return metrics
    
    def test_validation_performance(self, graphs: List[Graph]) -> List[PerformanceMetric]:
        """Test validation performance if validation modules are available."""
        metrics = []
        
        if ValidationHandler is None:
            self.log("ValidationHandler not available, skipping validation tests")
            return metrics
        
        try:
            handler = ValidationHandler()
            
            for i, graph in enumerate(graphs):
                # Test basic validation
                def basic_validation():
                    return handler.validate(graph)
                
                metric = self.measure_operation(f"basic_validation_{i}", basic_validation)
                metric.triple_count = len(graph)
                metrics.append(metric)
                
                # Test SHACL validation if available
                def shacl_validation():
                    return handler.validate_shacl(graph)
                
                metric = self.measure_operation(f"shacl_validation_{i}", shacl_validation)
                metric.triple_count = len(graph)
                metrics.append(metric)
                
        except Exception as e:
            self.log(f"Validation tests failed: {e}")
        
        return metrics
    
    def test_dependency_analysis(self, graphs: List[Graph]) -> List[PerformanceMetric]:
        """Test dependency analysis performance."""
        metrics = []
        
        # Combine all graphs for dependency analysis
        combined_graph = Graph()
        for graph in graphs:
            combined_graph += graph
        
        # Test dependency queries
        dependency_queries = [
            ("depends_on", """
                SELECT ?source ?target WHERE {
                    ?source <http://example.org/dependsOn> ?target .
                }
            """),
            ("imports", """
                SELECT ?source ?target WHERE {
                    ?source <http://www.w3.org/2002/07/owl#imports> ?target .
                }
            """),
            ("subclass", """
                SELECT ?parent ?child WHERE {
                    ?child rdfs:subClassOf ?parent .
                }
            """),
            ("subproperty", """
                SELECT ?parent ?child WHERE {
                    ?child rdfs:subPropertyOf ?parent .
                }
            """)
        ]
        
        for query_name, query_text in dependency_queries:
            def dependency_query():
                return list(combined_graph.query(query_text))
            
            metric = self.measure_operation(f"dependency_{query_name}", dependency_query)
            metric.triple_count = len(combined_graph)
            metrics.append(metric)
        
        return metrics
    
    def test_pattern_matching(self, graphs: List[Graph]) -> List[PerformanceMetric]:
        """Test pattern matching performance."""
        metrics = []
        
        # Combine all graphs
        combined_graph = Graph()
        for graph in graphs:
            combined_graph += graph
        
        # Test various pattern matching queries
        pattern_queries = [
            ("validation_rule", """
                SELECT ?rule ?target WHERE {
                    ?rule a <http://example.org/ValidationRule> .
                    ?rule <http://example.org/hasTarget> ?target .
                }
            """),
            ("namespace_conflict", """
                SELECT ?ns1 ?ns2 WHERE {
                    ?ns1 a <http://example.org/Namespace> .
                    ?ns2 a <http://example.org/Namespace> .
                    FILTER(?ns1 != ?ns2)
                }
            """),
            ("circular_dependency", """
                SELECT ?entity WHERE {
                    ?entity <http://example.org/dependsOn> ?entity .
                }
            """)
        ]
        
        for pattern_name, query_text in pattern_queries:
            def pattern_query():
                return list(combined_graph.query(query_text))
            
            metric = self.measure_operation(f"pattern_{pattern_name}", pattern_query)
            metric.triple_count = len(combined_graph)
            metrics.append(metric)
        
        return metrics
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "memory_available_gb": psutil.virtual_memory().available / 1024 / 1024 / 1024,
            "disk_usage_percent": psutil.disk_usage('.').percent
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary."""
        if not self.results:
            return {}
        
        # Calculate statistics
        durations = [m.duration_ms for m in self.results if m.error is None]
        memory_deltas = [m.memory_mb for m in self.results if m.error is None]
        
        summary = {
            "total_operations": len(self.results),
            "successful_operations": len([m for m in self.results if m.error is None]),
            "failed_operations": len([m for m in self.results if m.error is not None]),
            "duration_stats": {
                "mean_ms": sum(durations) / len(durations) if durations else 0,
                "median_ms": sorted(durations)[len(durations)//2] if durations else 0,
                "min_ms": min(durations) if durations else 0,
                "max_ms": max(durations) if durations else 0,
                "p95_ms": sorted(durations)[int(len(durations)*0.95)] if durations else 0
            },
            "memory_stats": {
                "mean_mb": sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0,
                "max_mb": max(memory_deltas) if memory_deltas else 0,
                "total_mb": sum(memory_deltas) if memory_deltas else 0
            },
            "slowest_operations": sorted(
                [m for m in self.results if m.error is None],
                key=lambda x: x.duration_ms,
                reverse=True
            )[:5],
            "largest_memory_operations": sorted(
                [m for m in self.results if m.error is None],
                key=lambda x: x.memory_mb,
                reverse=True
            )[:5]
        }
        
        return summary
    
    def run_baseline(self) -> PerformanceBaseline:
        """Run the complete performance baseline."""
        self.log("Starting performance baseline")
        
        # Get system info
        system_info = self.get_system_info()
        self.log(f"System: {system_info}")
        
        # Load ontology files
        graphs = self.load_ontology_files()
        if not graphs:
            raise ValueError("No ontology files found")
        
        # Run performance tests
        self.test_basic_queries(graphs)
        self.test_validation_performance(graphs)
        self.test_dependency_analysis(graphs)
        self.test_pattern_matching(graphs)
        
        # Generate summary
        summary = self.generate_summary()
        
        baseline = PerformanceBaseline(
            system_info=system_info,
            metrics=self.results,
            summary=summary
        )
        
        self.log("Performance baseline completed")
        return baseline

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run performance baseline for ontology framework")
    parser.add_argument("--output", default="performance_baseline.json", 
                       help="Output file for results")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    try:
        # Run baseline
        runner = PerformanceBaselineRunner(verbose=args.verbose)
        baseline = runner.run_baseline()
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(asdict(baseline), f, indent=2, default=str)
        
        # Print summary
        print(f"\nPerformance Baseline Summary:")
        print(f"Total operations: {baseline.summary['total_operations']}")
        print(f"Successful: {baseline.summary['successful_operations']}")
        print(f"Failed: {baseline.summary['failed_operations']}")
        print(f"Average duration: {baseline.summary['duration_stats']['mean_ms']:.2f}ms")
        print(f"95th percentile: {baseline.summary['duration_stats']['p95_ms']:.2f}ms")
        print(f"Total memory usage: {baseline.summary['memory_stats']['total_mb']:.2f}MB")
        
        print(f"\nSlowest operations:")
        for op in baseline.summary['slowest_operations']:
            print(f"  {op.operation}: {op.duration_ms:.2f}ms")
        
        print(f"\nResults saved to: {args.output}")
        
    except Exception as e:
        print(f"Error running performance baseline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 