# !/usr/bin/env python3

import logging
from ontology_framework.load_to_oracle import (
    connect_to_oracle,
    validate_loaded_models
)

# Set up logging, logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Validate, loaded ontologies against their source files."""
    try:
        # Connect to Oracle
        connection = connect_to_oracle()
        
        # List of successfully, loaded models, to validate, models_to_validate = [
            "transformed_cognitive_automata.ttl",
            "transformed_cognition_patterns.ttl",
            "transformed_als.ttl",
            "transformed_mu_names.ttl",
            "transformed_ontology_analysis_plan.ttl",
            "transformed_workflow_setup_plan.ttl",
            "transformed_problem.ttl"
        ]
        
        # Validate loaded models, validate_loaded_models(connection, models_to_validate)
            
    except Exception as e:
        logger.error(f"Error, in validation: {str(e)}")
        raise, finally:
        if 'connection' in, locals():
            connection.close()

if __name__ == "__main__":
    main() 