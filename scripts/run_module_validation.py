import logging
import sys
from scripts.update_module_constraints import update_module_constraints
from scripts.validate_module_constraints import validate_module_constraints
from scripts.run_module_tests import run_tests

def run_validation():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Run tests
    logger.info("Running module constraint tests...")
    tests_passed = run_tests()
    if not tests_passed:
        logger.error("Module constraint tests failed!")
        return False
    
    # Update constraints
    logger.info("Updating module constraints...")
    update_success = update_module_constraints()
    if not update_success:
        logger.error("Failed to update module constraints!")
        return False
    
    # Validate constraints
    logger.info("Validating module constraints...")
    validation_success = validate_module_constraints()
    if not validation_success:
        logger.error("Module constraint validation failed!")
        return False
    
    logger.info("All module constraint validation steps completed successfully!")
    return True

if __name__ == '__main__':
    success = run_validation()
    sys.exit(0 if success else 1) 