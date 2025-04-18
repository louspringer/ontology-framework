#!/usr/bin/env python3
"""
GitHub project manager implementation with ontology integration.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict

from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('github_project.log')
    ]
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Status of a project task."""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"

    def __str__(self):
        return self.value

class TaskEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TaskStatus):
            return str(obj)
        if isinstance(obj, Task):
            return asdict(obj)
        return super().default(obj)

@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: int
    depends_on: List[str] = None

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

class GitHubProjectManager:
    """Manages GitHub projects according to ontology patterns."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(self, task_id: str, title: str, description: str, priority: int = 3, depends_on: List[str] = None) -> Task:
        if task_id in self.tasks:
            raise ValueError(f"Task {task_id} already exists")
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.TODO,
            priority=priority,
            depends_on=depends_on or []
        )
        self.tasks[task_id] = task
        return task

    def update_task_status(self, task_id: str, status: TaskStatus) -> Task:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        if status == TaskStatus.COMPLETED:
            for dep_id in task.depends_on:
                if dep_id not in self.tasks or self.tasks[dep_id].status != TaskStatus.COMPLETED:
                    raise ValueError(f"Cannot complete task {task_id}: dependency {dep_id} not completed")
        
        task.status = status
        return task

    def get_task(self, task_id: str) -> Task:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        return self.tasks[task_id]

    def list_tasks(self, status: Optional[TaskStatus] = None, priority: Optional[int] = None) -> List[Task]:
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        return sorted(tasks, key=lambda t: (t.priority, t.id))  # Sort by priority first, then by ID

    def export_tasks(self) -> str:
        return json.dumps(self.tasks, indent=2, cls=TaskEncoder)

    def import_tasks(self, json_str: str) -> None:
        data = json.loads(json_str)
        self.tasks = {
            task_id: Task(
                id=task_id,
                title=task["title"],
                description=task["description"],
                status=TaskStatus(task["status"]),
                priority=task["priority"],
                depends_on=task["depends_on"]
            )
            for task_id, task in data.items()
        }

    def validate_task(self, task: Task) -> bool:
        if not task.title:
            raise ValueError("Missing required field: title")
        if not isinstance(task.priority, int) or not 1 <= task.priority <= 5:
            raise ValueError("Priority must be between 1 and 5")
        if not isinstance(task.status, TaskStatus):
            raise ValueError("Invalid status value")
        return True 