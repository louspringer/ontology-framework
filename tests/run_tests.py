#!/usr/bin/env python3
import sys
import unittest
from datetime import datetime
from pathlib import Path

from test_guidance import TestGuidanceOntology


def generate_test_report(test_results, runtime):
    """Generate a markdown report of test results"""
    report = f"""# Guidance Ontology Test Report
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
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGuidanceOntology)

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
