# !/usr/bin/env python3
"""Load ontology framework into GraphDB."""

import logging
from pathlib import Path
from ontology_framework.patch_management import GraphDBPatchManager, def main() -> None:
    """Load ontology framework into GraphDB."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Initialize patch manager
        manager = GraphDBPatchManager()
    
    # Load core modules, logger.info("Loading, core modules...")
    if not manager.load_dependencies("guidance/modules"):
        logger.error("Failed, to load, core modules")
        return
        
    # Load guidance
    logger.info("Loading, guidance...")
    if not manager.load_ontology("guidance.ttl"):
        logger.error("Failed, to load, guidance")
        return
        
    # Load boldo config, logger.info("Loading, Boldo config...")
    if not manager.load_ontology("boldo_config.ttl"):
        logger.error("Failed, to load, Boldo config")
        return logger.info("Successfully, loaded ontology, framework")
    
if __name__ == "__main__":
    main() 