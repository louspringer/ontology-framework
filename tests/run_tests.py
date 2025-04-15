#!/usr/bin/env python3
import sys
import unittest
import os
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def discover_tests():
    """Discover all test files in the tests directory"""
    test_dir = Path(__file__).parent
    test_files = []
    
    # Files to exclude (Oracle-dependent tests)
    exclude_files = {
        'test_oracle_rdf.py',
        'test_semantic_equivalence.py'  # Also Oracle-dependent
    }
    
    for file in test_dir.glob('test_*.py'):
        if file.name != 'run_tests.py' and file.name not in exclude_files:
            test_files.append(file.stem)
            
    return test_files

def import_test_modules(test_files):
    """Import all test modules"""
    test_modules = []
    for test_file in test_files:
        try:
            module = __import__(f'tests.{test_file}', fromlist=['*'])
            test_modules.append(module)
        except ImportError as e:
            print(f"Warning: Could not import {test_file}: {e}")
    return test_modules

def generate_test_report(test_results, runtime):
    """Generate a markdown report of test results"""
    report = f"""# Ontology Framework Test Report
Generated: {datetime.now().isoformat()}
Runtime: {runtime:.2f} seconds

## Summary
- Tests Run: {test_results.testsRun}
- Failures: {len(test_results.failures)}
- Errors: {len(test_results.errors)}
- Skipped: {len(test_results.skipped)}

## Details\n"""

    if test_results.wasSuccessful():
        report += "\n✅ All tests passed successfully!\n"
    else:
        if test_results.failures:
            report += "\n### Failures\n"
            for failure in test_results.failures:
                test_case, traceback = failure
                report += f"\n#### {test_case.id()}\n```\n{traceback}\n```\n"

        if test_results.errors:
            report += "\n### Errors\n"
            for error in test_results.errors:
                test_case, traceback = error
                report += f"\n#### {test_case.id()}\n```\n{traceback}\n```\n"

    return report

def main():
    # Discover and import all test modules
    test_files = discover_tests()
    print(f"Running tests from: {', '.join(test_files)}")
    
    test_modules = import_test_modules(test_files)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for module in test_modules:
        # Find all test classes in the module
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                suite.addTests(loader.loadTestsFromTestCase(obj))
    
    # Run tests and time execution
    start_time = datetime.now()
    test_results = unittest.TextTestRunner(verbosity=2).run(suite)
    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    
    # Generate report
    report = generate_test_report(test_results, runtime)
    
    # Save report
    report_path = Path(__file__).parent / "test_report.md"
    report_path.write_text(report)
    print(f"\nTest report saved to: {report_path}")
    
    # Return appropriate exit code
    return 0 if test_results.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())
