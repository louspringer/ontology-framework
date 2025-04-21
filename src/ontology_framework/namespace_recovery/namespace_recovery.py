"""
Namespace recovery module for handling namespace recovery projects.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Status of a recovery task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    """A namespace recovery task."""
    id: int
    name: str
    status: TaskStatus
    dependencies: List[int]
    
@dataclass
class Project:
    """A namespace recovery project."""
    id: int
    name: str
    tasks: List[Task]
    
def create_namespace_recovery_project(name: str) -> Project:
    """Create a namespace recovery project with 10 tasks.
    
    Args:
        name: Name of the project
        
    Returns:
        Project: The created project
    """
    logger.info(f"Creating namespace recovery project: {name}")
    
    # Create 10 tasks with dependencies
    tasks = []
    for i in range(1, 11):
        # Each task depends on the previous task
        dependencies = [i-1] if i > 1 else []
        task = Task(
            id=i,
            name=f"Task {i}",
            status=TaskStatus.PENDING,
            dependencies=dependencies
        )
        tasks.append(task)
    
    project = Project(
        id=1,  # Simple ID for now
        name=name,
        tasks=tasks
    )
    
    return project

def get_project_status(project: Project) -> Dict[str, int]:
    """Get the status of a project.
    
    Args:
        project: The project to check
        
    Returns:
        Dict[str, int]: Status counts by task status
    """
    status_counts = {
        "pending": 0,
        "in_progress": 0,
        "completed": 0,
        "failed": 0
    }
    
    for task in project.tasks:
        status_counts[task.status.value] += 1
        
    return status_counts 