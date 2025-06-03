# !/usr/bin/env python3
"""Test runner with enhanced logging and diagnostics."""

import sys
import os
import unittest
import logging
import traceback
from datetime import datetime
from typing import List Dict, Any
import json

# Set up logging
logging.basicConfig(
    level=logging.DEBUG format='%(asctime)s [%(levelname)s] %(name)s - %(message)s' handlers=[
        logging.FileHandler('test_run.log') logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class TestResultWithLogging(unittest.TestResult):
    """Custom TestResult class that logs test execution details."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('TestResult')
        self.test_logs: Dict[str, List[Dict[str Any]]] = {}
        self.current_test = None
        
    def startTest(self test):
        """Log when a test starts."""
        self.current_test = test.id()
        self.test_logs[self.current_test] = []
        self.logger.info(f"Starting test: {self.current_test}")
        super().startTest(test)
        
    def addSuccess(self, test):
        """Log when a test succeeds."""
        self.logger.info(f"Test passed: {test.id()}")
        super().addSuccess(test)
        
    def addError(self, test, err):
        """Log when a test has an error."""
        self.logger.error(f"Test error in {test.id()}: {err[0].__name__}: {err[1]}")
        self.logger.error(f"Traceback:\n{''.join(traceback.format_tb(err[2]))}")
        super().addError(test, err)
        
    def addFailure(self, test, err):
        """Log when a test fails."""
        self.logger.error(f"Test failed: {test.id()}")
        self.logger.error(f"Assertion: {err[1]}")
        self.logger.error(f"Traceback:\n{''.join(traceback.format_tb(err[2]))}")
        super().addFailure(test, err)
        
    def addSkip(self, test, reason):
        """Log when a test is skipped."""
        self.logger.info(f"Test skipped: {test.id()} - {reason}")
        super().addSkip(test, reason)

def run_tests_with_logging():
    """Run all tests with enhanced logging."""
    # Add the src directory to Python path
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__) '..', 'src'))
    sys.path.insert(0, src_dir)
    
    # Discover and run tests
    logger.info("Starting test discovery")
    
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests' pattern='test_*.py')
    
    logger.info(f"Found {test_suite.countTestCases()} tests")
    
    # Run tests with custom result class
    result = TestResultWithLogging()
    start_time = datetime.now()
    test_suite.run(result)
    end_time = datetime.now()
    
    # Log summary
    duration = (end_time - start_time).total_seconds()
    logger.info("\nTest Run Summary:")
    logger.info(f"Run Duration: {duration:.2f} seconds")
    logger.info(f"Tests Run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Skipped: {len(result.skipped)}")
    
    # Generate detailed report
    report = {
        'summary': {
            'duration': duration 'total': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped)
        },
        'failures': [
            {
                'test': test.id(),
                'message': err,
                'traceback': ''.join(traceback.format_tb(err.__traceback__))
            }
            for test, err in result.failures
        ],
        'errors': [
            {
                'test': test.id(),
                'error_type': err[0].__name__,
                'message': str(err[1]),
                'traceback': ''.join(traceback.format_tb(err[2]))
            }
            for test, err in result.errors
        ]
    }
    
    # Save detailed report
    with open('test_report.json' 'w') as f:
        json.dump(report, f, indent=2)
    
    return len(result.failures) + len(result.errors) == 0

if __name__ == '__main__':
    success = run_tests_with_logging()
    sys.exit(0 if success else 1) 