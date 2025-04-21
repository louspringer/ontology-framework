"""GitHub project management functionality for the ontology framework.

This module provides functionality for managing GitHub projects, including repository
creation, issue tracking, and project board management.
"""

from typing import Dict, List, Optional, Union
import os
import logging
from github import Github, Repository, Project, ProjectColumn
from .exceptions import GitHubError
from enum import Enum
import json

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task status enumeration."""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"

class Task:
    """Task model for project management."""
    
    def __init__(self, task_id: str, title: str, description: str = "", 
                 priority: int = 3, status: TaskStatus = TaskStatus.TODO,
                 depends_on: List[str] = None):
        """Initialize a task.
        
        Args:
            task_id: Unique task identifier
            title: Task title
            description: Task description
            priority: Task priority (1-5)
            status: Task status
            depends_on: List of task IDs this task depends on
        """
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.depends_on = depends_on or []
        
    def to_dict(self) -> Dict:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status.value,
            "depends_on": self.depends_on
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create task from dictionary."""
        return cls(
            task_id=data["id"],
            title=data["title"],
            description=data["description"],
            priority=data["priority"],
            status=TaskStatus(data["status"]),
            depends_on=data["depends_on"]
        )

class GitHubProjectManager:
    """Manages GitHub projects and repositories for ontology framework."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub project manager.
        
        Args:
            token: GitHub access token. If not provided, will try to get from environment.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise GitHubError("GitHub token not provided and not found in environment")
        self.github = Github(self.token)
        self.tasks: Dict[str, Task] = {}
        
    def create_task(self, task_id: str, title: str, description: str = "", 
                   priority: int = 3, depends_on: List[str] = None) -> Task:
        """Create a new task.
        
        Args:
            task_id: Unique task identifier
            title: Task title
            description: Task description
            priority: Task priority (1-5)
            depends_on: List of task IDs this task depends on
            
        Returns:
            Created task
            
        Raises:
            ValueError: If task ID already exists or priority is invalid
        """
        if task_id in self.tasks:
            raise ValueError(f"Task {task_id} already exists")
            
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")
            
        task = Task(task_id, title, description, priority, TaskStatus.TODO, depends_on)
        self.tasks[task_id] = task
        return task
        
    def get_task(self, task_id: str) -> Task:
        """Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object
            
        Raises:
            KeyError: If task not found
        """
        return self.tasks[task_id]
        
    def update_task_status(self, task_id: str, status: TaskStatus) -> Task:
        """Update task status.
        
        Args:
            task_id: Task ID
            status: New status
            
        Returns:
            Updated task
            
        Raises:
            KeyError: If task not found
            ValueError: If task dependencies are not completed
        """
        task = self.tasks[task_id]
        
        if status == TaskStatus.COMPLETED:
            for dep_id in task.depends_on:
                dep_task = self.tasks[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    raise ValueError(f"Cannot complete task {task_id}: dependency {dep_id} not completed")
                    
        task.status = status
        return task
        
    def list_tasks(self, status: Optional[TaskStatus] = None, 
                  priority: Optional[int] = None) -> List[Task]:
        """List tasks with optional filters.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            
        Returns:
            List of tasks matching filters
        """
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
            
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
            
        return sorted(tasks, key=lambda t: t.priority)
        
    def export_tasks(self) -> str:
        """Export tasks to JSON.
        
        Returns:
            JSON string of tasks
        """
        tasks_data = [task.to_dict() for task in self.tasks.values()]
        return json.dumps(tasks_data)
        
    def import_tasks(self, json_data: str) -> None:
        """Import tasks from JSON.
        
        Args:
            json_data: JSON string of tasks
        """
        tasks_data = json.loads(json_data)
        self.tasks = {task["id"]: Task.from_dict(task) for task in tasks_data}
        
    def validate_task(self, task: Task) -> bool:
        """Validate task data.
        
        Args:
            task: Task to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If task data is invalid
        """
        if not task.title:
            raise ValueError("Missing required field: title")
            
        if not 1 <= task.priority <= 5:
            raise ValueError("Priority must be between 1 and 5")
            
        return True
        
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Repository.Repository:
        """Create a new GitHub repository.
        
        Args:
            name: Repository name
            description: Repository description
            private: Whether repository should be private
            
        Returns:
            Created repository object
            
        Raises:
            GitHubError: If repository creation fails
        """
        try:
            repo = self.github.get_user().create_repo(
                name=name,
                description=description,
                private=private
            )
            logger.info(f"Created repository {name}")
            return repo
        except Exception as e:
            raise GitHubError(f"Failed to create repository: {str(e)}")
            
    def create_project(self, repo: Repository.Repository, name: str, body: str = "") -> Project.Project:
        """Create a new project in a repository.
        
        Args:
            repo: Repository to create project in
            name: Project name
            body: Project description
            
        Returns:
            Created project object
            
        Raises:
            GitHubError: If project creation fails
        """
        try:
            project = repo.create_project(
                name=name,
                body=body
            )
            logger.info(f"Created project {name} in repository {repo.name}")
            return project
        except Exception as e:
            raise GitHubError(f"Failed to create project: {str(e)}")
            
    def create_project_columns(self, project: Project.Project, columns: List[str]) -> List[ProjectColumn.ProjectColumn]:
        """Create columns in a project.
        
        Args:
            project: Project to create columns in
            columns: List of column names
            
        Returns:
            List of created column objects
            
        Raises:
            GitHubError: If column creation fails
        """
        try:
            created_columns = []
            for column_name in columns:
                column = project.create_column(column_name)
                created_columns.append(column)
                logger.info(f"Created column {column_name} in project {project.name}")
            return created_columns
        except Exception as e:
            raise GitHubError(f"Failed to create project columns: {str(e)}") 