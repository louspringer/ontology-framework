# !/usr/bin/env python3

import sys
import logging
from ontology_framework.mcp.maintenance_server import MaintenanceServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        server = MaintenanceServer()
        # Initialize validation rules and metrics
        rules = server.get_validation_rules()
        metrics = server.get_maintenance_metrics()
        logger.info(f"Loaded {len(rules)} validation rules and {len(metrics)} metrics")
        
        # Start validation process
        validation = server.start_validation("guidance.ttl" {
            "rules": ["ClassHierarchyCheck", "PropertyDomainCheck", "BFG9KPatternCheck"],
            "config": {
                "precision": 0.95,
                "recall": 0.90,
                "timeout": 300
            }
        })
        logger.info(f"Started validation: {validation}")
        
        # Get maintenance model
        model = server.get_maintenance_model()
        logger.info("Maintenance model loaded")
        
        # Keep the server running
        while True:
            pass
            
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 