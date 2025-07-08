#!/usr/bin/env python3
"""
Validation Performance Test Script

This script measures SHACL validation performance to compare with property graph targets.
Focuses on validation operations that would benefit from < 1ms response times.
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

# Validation imports
try:
    from pyshacl import validate as pyshacl_validate
    PYSHACL_AVAILABLE = True
except ImportError:
    PYSHACL_AVAILABLE = False
    print("Warning: pyshacl not available. Install with: pip install pyshacl")

@dataclass
class ValidationMetric:
    """Represents a single validation performance measurement."""
    operation: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    triple_count: Optional[int] = None
    validation_result: Optional[bool] = None
    error_count: Optional[int] = None
    warning_count: Optional[int] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class ValidationPerformanceTester:
    """Tests validation performance for comparison with property graphs."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.process = psutil.Process()
        self.results = []
        
    def log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{datetime.now().isoformat()}] {message}")
    
    def measure_validation(self, operation_name: str, validation_func, *args, **kwargs) -> ValidationMetric:
        """Measure performance of a validation operation."""
        self.log(f"Measuring {operation_name}")
        
        # Force garbage collection before measurement
        gc.collect()
        
        # Get initial memory and CPU
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        initial_cpu = self.process.cpu_percent()
        
        # Measure operation
        start_time = time.time()
        try:
            result = validation_func(*args, **kwargs)
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
        
        # Extract validation result details
        validation_result = None
        error_count = None
        warning_count = None
        
        if isinstance(result, dict):
            validation_result = result.get('conforms', None)
            if 'results' in result and isinstance(result['results'], list):
                error_count = len([r for r in result['results'] if 'error' in r.lower()])
                warning_count = len([r for r in result['results'] if 'warning' in r.lower()])
        
        metric = ValidationMetric(
            operation=operation_name,
            duration_ms=duration_ms,
            memory_mb=memory_delta,
            cpu_percent=final_cpu,
            validation_result=validation_result,
            error_count=error_count,
            warning_count=warning_count,
            error=error
        )
        
        self.results.append(metric)
        self.log(f"  Duration: {duration_ms:.2f}ms, Memory: {memory_delta:.2f}MB, Valid: {validation_result}")
        
        return metric
    
    def load_test_ontologies(self) -> List[Graph]:
        """Load test ontologies for validation."""
        ontologies = []
        
        # Find ontology files
        ttl_files = list(Path(".").rglob("*.ttl"))
        self.log(f"Found {len(ttl_files)} TTL files")
        
        # Load a subset for testing (first 10 files)
        for ttl_file in ttl_files[:10]:
            try:
                graph = Graph()
                graph.parse(str(ttl_file), format="turtle")
                ontologies.append(graph)
                self.log(f"  Loaded {ttl_file}: {len(graph)} triples")
            except Exception as e:
                self.log(f"  Failed to load {ttl_file}: {e}")
        
        return ontologies
    
    def test_shacl_validation(self, graphs: List[Graph]) -> List[ValidationMetric]:
        """Test SHACL validation performance."""
        metrics = []
        
        if not PYSHACL_AVAILABLE:
            self.log("pyshacl not available, skipping SHACL tests")
            return metrics
        
        # Create basic SHACL shapes for testing
        shapes_graph = Graph()
        shapes_graph.parse(data="""
            @prefix sh: <http://www.w3.org/ns/shacl#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            
            # Basic class shape
            [] a sh:NodeShape ;
                sh:targetClass owl:Class ;
                sh:property [
                    sh:path rdfs:label ;
                    sh:minCount 1 ;
                    sh:datatype xsd:string ;
                    sh:message "Class must have a label" ;
                ] ;
                sh:property [
                    sh:path rdfs:comment ;
                    sh:minCount 1 ;
                    sh:datatype xsd:string ;
                    sh:message "Class must have a comment" ;
                ] .
            
            # Basic property shape
            [] a sh:NodeShape ;
                sh:targetClass owl:ObjectProperty ;
                sh:property [
                    sh:path rdfs:label ;
                    sh:minCount 1 ;
                    sh:datatype xsd:string ;
                    sh:message "Property must have a label" ;
                ] .
        """, format="turtle")
        
        for i, graph in enumerate(graphs):
            # Test SHACL validation
            def shacl_validation():
                return pyshacl_validate(
                    graph,
                    shacl_graph=shapes_graph,
                    inference='rdfs',
                    abort_on_first=False
                )
            
            metric = self.measure_validation(f"shacl_validation_{i}", shacl_validation)
            metric.triple_count = len(graph)
            metrics.append(metric)
        
        return metrics
    
    def test_sparql_validation(self, graphs: List[Graph]) -> List[ValidationMetric]:
        """Test SPARQL-based validation performance."""
        metrics = []
        
        # Define validation queries
        validation_queries = [
            ("class_labels", """
                SELECT ?class WHERE {
                    ?class a owl:Class .
                    FILTER NOT EXISTS { ?class rdfs:label ?label }
                }
            """),
            ("property_labels", """
                SELECT ?property WHERE {
                    ?property a ?type .
                    FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
                    FILTER NOT EXISTS { ?property rdfs:label ?label }
                }
            """),
            ("class_comments", """
                SELECT ?class WHERE {
                    ?class a owl:Class .
                    FILTER NOT EXISTS { ?class rdfs:comment ?comment }
                }
            """),
            ("namespace_consistency", """
                SELECT ?entity WHERE {
                    ?entity a ?type .
                    FILTER(?type IN (owl:Class, owl:ObjectProperty, owl:DatatypeProperty))
                    FILTER NOT EXISTS { ?entity owl:versionInfo ?version }
                }
            """)
        ]
        
        for query_name, query_text in validation_queries:
            for i, graph in enumerate(graphs):
                def sparql_validation():
                    results = list(graph.query(query_text))
                    return {
                        'conforms': len(results) == 0,
                        'results': [str(r[0]) for r in results],
                        'error_count': len(results)
                    }
                
                metric = self.measure_validation(f"sparql_{query_name}_{i}", sparql_validation)
                metric.triple_count = len(graph)
                metrics.append(metric)
        
        return metrics
    
    def test_bfg9k_validation(self, graphs: List[Graph]) -> List[ValidationMetric]:
        """Test BFG9K pattern validation performance."""
        metrics = []
        
        # BFG9K validation involves multiple steps
        for i, graph in enumerate(graphs):
            # Step 1: Exact match validation
            def exact_match_validation():
                query = """
                SELECT ?rule WHERE {
                    ?rule a <http://example.org/guidance#ValidationRule> .
                    FILTER NOT EXISTS { ?rule rdfs:label ?label }
                }
                """
                results = list(graph.query(query))
                return {
                    'conforms': len(results) == 0,
                    'results': [str(r[0]) for r in results],
                    'error_count': len(results)
                }
            
            metric = self.measure_validation(f"bfg9k_exact_match_{i}", exact_match_validation)
            metric.triple_count = len(graph)
            metrics.append(metric)
            
            # Step 2: Similarity validation
            def similarity_validation():
                query = """
                SELECT ?component WHERE {
                    ?component a <http://example.org/guidance#ValidationComponent> .
                    FILTER NOT EXISTS {
                        ?path a <http://example.org/guidance#ValidationPath> ;
                              <http://example.org/guidance#hasStartNode> ?component .
                    }
                }
                """
                results = list(graph.query(query))
                return {
                    'conforms': len(results) == 0,
                    'results': [str(r[0]) for r in results],
                    'error_count': len(results)
                }
            
            metric = self.measure_validation(f"bfg9k_similarity_{i}", similarity_validation)
            metric.triple_count = len(graph)
            metrics.append(metric)
        
        return metrics
    
    def test_real_time_validation_scenarios(self, graphs: List[Graph]) -> List[ValidationMetric]:
        """Test validation scenarios that would benefit from < 1ms response."""
        metrics = []
        
        # Scenario 1: Real-time class validation
        for i, graph in enumerate(graphs):
            def real_time_class_validation():
                query = """
                ASK {
                    ?class a owl:Class .
                    ?class rdfs:label ?label .
                    ?class rdfs:comment ?comment .
                }
                """
                return {
                    'conforms': graph.query(query).askAnswer,
                    'results': [],
                    'error_count': 0 if graph.query(query).askAnswer else 1
                }
            
            metric = self.measure_validation(f"realtime_class_{i}", real_time_class_validation)
            metric.triple_count = len(graph)
            metrics.append(metric)
        
        # Scenario 2: Real-time property validation
        for i, graph in enumerate(graphs):
            def real_time_property_validation():
                query = """
                ASK {
                    ?property a owl:ObjectProperty .
                    ?property rdfs:label ?label .
                    ?property rdfs:domain ?domain .
                    ?property rdfs:range ?range .
                }
                """
                return {
                    'conforms': graph.query(query).askAnswer,
                    'results': [],
                    'error_count': 0 if graph.query(query).askAnswer else 1
                }
            
            metric = self.measure_validation(f"realtime_property_{i}", real_time_property_validation)
            metric.triple_count = len(graph)
            metrics.append(metric)
        
        # Scenario 3: Real-time namespace validation
        for i, graph in enumerate(graphs):
            def real_time_namespace_validation():
                query = """
                ASK {
                    ?entity a ?type .
                    FILTER(?type IN (owl:Class, owl:ObjectProperty))
                    FILTER(STRSTARTS(STR(?entity), "http://"))
                }
                """
                return {
                    'conforms': graph.query(query).askAnswer,
                    'results': [],
                    'error_count': 0 if graph.query(query).askAnswer else 1
                }
            
            metric = self.measure_validation(f"realtime_namespace_{i}", real_time_namespace_validation)
            metric.triple_count = len(graph)
            metrics.append(metric)
        
        return metrics
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate validation performance summary."""
        if not self.results:
            return {}
        
        # Calculate statistics
        durations = [m.duration_ms for m in self.results if m.error is None]
        memory_deltas = [m.memory_mb for m in self.results if m.error is None]
        
        # Categorize by operation type
        shacl_times = [m.duration_ms for m in self.results if 'shacl' in m.operation and m.error is None]
        sparql_times = [m.duration_ms for m in self.results if 'sparql' in m.operation and m.error is None]
        bfg9k_times = [m.duration_ms for m in self.results if 'bfg9k' in m.operation and m.error is None]
        realtime_times = [m.duration_ms for m in self.results if 'realtime' in m.operation and m.error is None]
        
        summary = {
            "total_operations": len(self.results),
            "successful_operations": len([m for m in self.results if m.error is None]),
            "failed_operations": len([m for m in self.results if m.error is not None]),
            "overall_stats": {
                "mean_ms": sum(durations) / len(durations) if durations else 0,
                "median_ms": sorted(durations)[len(durations)//2] if durations else 0,
                "min_ms": min(durations) if durations else 0,
                "max_ms": max(durations) if durations else 0,
                "p95_ms": sorted(durations)[int(len(durations)*0.95)] if durations else 0
            },
            "validation_types": {
                "shacl": {
                    "count": len(shacl_times),
                    "mean_ms": sum(shacl_times) / len(shacl_times) if shacl_times else 0,
                    "min_ms": min(shacl_times) if shacl_times else 0,
                    "max_ms": max(shacl_times) if shacl_times else 0
                },
                "sparql": {
                    "count": len(sparql_times),
                    "mean_ms": sum(sparql_times) / len(sparql_times) if sparql_times else 0,
                    "min_ms": min(sparql_times) if sparql_times else 0,
                    "max_ms": max(sparql_times) if sparql_times else 0
                },
                "bfg9k": {
                    "count": len(bfg9k_times),
                    "mean_ms": sum(bfg9k_times) / len(bfg9k_times) if bfg9k_times else 0,
                    "min_ms": min(bfg9k_times) if bfg9k_times else 0,
                    "max_ms": max(bfg9k_times) if bfg9k_times else 0
                },
                "realtime": {
                    "count": len(realtime_times),
                    "mean_ms": sum(realtime_times) / len(realtime_times) if realtime_times else 0,
                    "min_ms": min(realtime_times) if realtime_times else 0,
                    "max_ms": max(realtime_times) if realtime_times else 0
                }
            },
            "property_graph_target": {
                "target_ms": 1.0,
                "achievable_operations": [m.operation for m in self.results if m.duration_ms < 1.0 and m.error is None],
                "needs_optimization": [m.operation for m in self.results if m.duration_ms >= 1.0 and m.error is None]
            }
        }
        
        return summary
    
    def run_validation_tests(self) -> Dict[str, Any]:
        """Run the complete validation performance test."""
        self.log("Starting validation performance tests")
        
        # Load test ontologies
        graphs = self.load_test_ontologies()
        if not graphs:
            raise ValueError("No ontology files found")
        
        # Run validation tests
        self.test_shacl_validation(graphs)
        self.test_sparql_validation(graphs)
        self.test_bfg9k_validation(graphs)
        self.test_real_time_validation_scenarios(graphs)
        
        # Generate summary
        summary = self.generate_summary()
        
        self.log("Validation performance tests completed")
        return {
            "metrics": [asdict(m) for m in self.results],
            "summary": summary
        }

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test validation performance for property graph comparison")
    parser.add_argument("--output", default="validation_performance.json", 
                       help="Output file for results")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    try:
        # Run validation tests
        tester = ValidationPerformanceTester(verbose=args.verbose)
        results = tester.run_validation_tests()
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        summary = results["summary"]
        print(f"\nValidation Performance Summary:")
        print(f"Total operations: {summary['total_operations']}")
        print(f"Successful: {summary['successful_operations']}")
        print(f"Failed: {summary['failed_operations']}")
        print(f"Overall average: {summary['overall_stats']['mean_ms']:.2f}ms")
        print(f"95th percentile: {summary['overall_stats']['p95_ms']:.2f}ms")
        
        print(f"\nValidation Type Performance:")
        for vtype, stats in summary['validation_types'].items():
            if stats['count'] > 0:
                print(f"  {vtype}: {stats['mean_ms']:.2f}ms avg ({stats['min_ms']:.2f}-{stats['max_ms']:.2f}ms)")
        
        print(f"\nProperty Graph Target Analysis:")
        target = summary['property_graph_target']
        print(f"  Target: < {target['target_ms']}ms")
        print(f"  Already < 1ms: {len(target['achievable_operations'])} operations")
        print(f"  Need optimization: {len(target['needs_optimization'])} operations")
        
        if target['needs_optimization']:
            print(f"  Operations needing optimization:")
            for op in target['needs_optimization'][:5]:  # Show first 5
                print(f"    - {op}")
        
        print(f"\nResults saved to: {args.output}")
        
    except Exception as e:
        print(f"Error running validation performance tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 