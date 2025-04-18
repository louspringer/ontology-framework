#!/usr/bin/env python3
"""Test namespace recovery with patch management."""

from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS
from .patch_management import PatchManager, PatchNotFoundError
from .namespace_recovery import create_namespace_recovery_project
from .github_project_manager import TaskStatus, Task
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define our recovery namespace using relative URI
RECOVERY = Namespace("./recovery#")

def test_namespace_recovery_patching() -> None:
    """Test namespace recovery with patch management."""
    # Initialize patch manager with relative namespace
    patch_manager = PatchManager()
    patch_manager.graph.bind("recovery", RECOVERY)
    
    # Create namespace recovery project
    manager = create_namespace_recovery_project()
    
    # Get the first task (NSR-001)
    tasks: List[Task] = manager.list_tasks()
    if not tasks:
        logger.error("No tasks found in project")
        return
        
    task = tasks[0]  # NSR-001: Audit Current Namespace Usage
    logger.info(f"Processing task: {task.title}")
    
    # Document the example.org finding
    finding = {
        "file": "src/ontology_framework/patch_management.py",
        "issue": "Using absolute URIs with example.org instead of relative URIs",
        "impact": "Non-portable, externally dependent namespace usage",
        "fix": "Replace with relative URIs (./patches/...)"
    }
    logger.info(f"Found absolute URI usage: {finding}")
    
    # Create a patch for the task with relative URI
    patch_data: Dict[str, Any] = {
        RDFS.label: Literal(task.title),
        RDFS.comment: Literal(task.description),
        RECOVERY.status: Literal(task.status.name),
        RECOVERY.priority: Literal(task.priority),
        RECOVERY.finding: Literal(str(finding))
    }
    
    # Add and validate patch using relative URI
    patch_uri = URIRef(f"./patches/{task.id}")
    patch_manager.add_patch(patch_uri, patch_data)
    
    try:
        # Validate patch
        if patch_manager.validate_patch(patch_uri):
            logger.info("Patch validated successfully")
            
            # Apply patch
            if patch_manager.apply_patch(patch_uri):
                logger.info("Patch applied successfully")
                
                # Get change history
                history = patch_manager.get_change_history(str(patch_uri))
                logger.info(f"Change history: {history}")
                
                # Update task status
                task.status = TaskStatus.IN_PROGRESS
                logger.info(f"Updated task status to: {task.status.name}")
                logger.info(f"First absolute URI instance documented in {finding['file']}")
                
            else:
                logger.error("Failed to apply patch")
        else:
            logger.error("Patch validation failed")
            
    except PatchNotFoundError as e:
        logger.error(f"Patch not found: {e}")
    except ValueError as e:
        logger.error(f"Validation error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_namespace_recovery_patching() 