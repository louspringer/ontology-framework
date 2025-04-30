"""Script to validate test coverage against requirements."""

import sys
from pathlib import Path
import logging
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
TEST = Namespace("http://example.org/test#")
IMPL = Namespace("http://example.org/implementation#")
BASE = Namespace("http://example.org/ontology-framework#")

def load_test_dependencies() -> Graph:
    """Load test dependencies from Turtle file."""
    try:
        test_dir = Path(__file__).parent
        g = Graph()
        g.parse(test_dir / "test_dependencies.ttl", format="turtle")
        return g
    except Exception as e:
        raise RuntimeError(f"Error loading test dependencies: {str(e)}")

def get_test_suites(g: Graph) -> dict:
    """Get test suites and their tests."""
    suites = {}
    
    # Query to get all test suites
    suite_query = """
    SELECT ?suite ?label
    WHERE {
        ?suite a test:TestSuite ;
               rdfs:label ?label .
    }
    """
    
    for row in g.query(suite_query, initNs={"test": TEST, "rdfs": RDFS}):
        suite_uri = str(row.suite)
        suite_name = str(row.label).replace(" Test Suite", "")
        
        # Get all tests for this suite
        test_query = """
        SELECT ?test
        WHERE {
            <%s> test:hasTest ?test .
        }
        """ % suite_uri
        
        tests = [str(r.test) for r in g.query(test_query)]
        
        suites[suite_uri] = {
            "name": suite_name,
            "tests": tests,
            "test_count": len(tests),
            "dependencies": defaultdict(set)
        }
    
    return suites

def get_test_dependencies(g: Graph, suites: dict):
    """Get implementation dependencies for each test."""
    dep_query = """
    SELECT ?test ?impl ?depType
    WHERE {
        ?test test:dependsOn ?impl .
        ?impl test:dependencyType ?depType .
    }
    """
    
    for row in g.query(dep_query, initNs={"test": TEST}):
        test_uri = str(row.test)
        impl_uri = str(row.impl)
        dep_type = str(row.depType)
        
        # Find which suite this test belongs to
        for suite_info in suites.values():
            if test_uri in suite_info["tests"]:
                suite_info["dependencies"][dep_type].add(impl_uri)

def validate_coverage(g: Graph):
    """Validate test coverage against requirements."""
    logger.info("Test Coverage Validation Results:")
    logger.info("--------------------------------")
    
    try:
        # Get test suites and their tests
        suites = get_test_suites(g)
        
        # Get implementation dependencies
        get_test_dependencies(g, suites)
        
        # Report results
        total_tests = 0
        total_deps = 0
        total_impl_classes = set()
        
        for suite_uri, suite_info in sorted(suites.items(), key=lambda x: x[1]["name"]):
            name = suite_info["name"]
            tests = suite_info["test_count"]
            total_tests += tests
            
            # Count unique implementation dependencies
            all_deps = set()
            for dep_type, deps in suite_info["dependencies"].items():
                all_deps.update(deps)
                total_impl_classes.update(deps)
            
            deps = len(all_deps)
            total_deps += deps
            
            logger.info(f"\nSuite: {name}")
            logger.info(f"  Tests: {tests}")
            logger.info(f"  Implementation Dependencies: {deps}")
            
            if deps > 0:
                logger.info("  Dependencies by Type:")
                for dep_type, deps in sorted(suite_info["dependencies"].items()):
                    logger.info(f"    {dep_type}:")
                    for impl_uri in sorted(deps):
                        impl_name = impl_uri.split("#")[-1]
                        logger.info(f"      - {impl_name}")
        
        logger.info("\nSummary:")
        logger.info(f"Total Test Suites: {len(suites)}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Total Implementation Dependencies: {len(total_impl_classes)}")
        
        # Calculate coverage metrics
        if total_tests > 0:
            test_ratio = total_deps / total_tests
            logger.info(f"Test-to-Dependency Ratio: {test_ratio:.2f}")
            
            impl_ratio = len(total_impl_classes) / total_tests
            logger.info(f"Implementation Coverage Ratio: {impl_ratio:.2f}")
            
            # Analyze coverage distribution
            covered_suites = sum(1 for s in suites.values() if len(s["dependencies"]) > 0)
            coverage_percent = (covered_suites / len(suites)) * 100
            logger.info(f"Suite Coverage: {coverage_percent:.1f}% ({covered_suites}/{len(suites)} suites)")
        
    except Exception as e:
        raise RuntimeError(f"Error validating test coverage: {str(e)}")

def main():
    """Main entry point."""
    try:
        g = load_test_dependencies()
        validate_coverage(g)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main() 