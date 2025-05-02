import unittest
import logging
from tests.test_module_constraints import TestModuleConstraints

def run_tests():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestModuleConstraints)
    
    # Run tests
    logger.info("Starting module constraints tests...")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Log results
    if result.wasSuccessful():
        logger.info("All tests passed successfully!")
    else:
        logger.error("Some tests failed:")
        for failure in result.failures:
            logger.error(f"Failure: {failure[0]}")
            logger.error(f"Error: {failure[1]}")
        for error in result.errors:
            logger.error(f"Error: {error[0]}")
            logger.error(f"Error: {error[1]}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_tests() 