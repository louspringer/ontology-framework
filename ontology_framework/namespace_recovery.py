#!/usr/bin/env python3
"""
Namespace Recovery Project Plan
"""

from typing import List
from .github_project_manager import GitHubProjectManager, TaskStatus

def create_namespace_recovery_project() -> GitHubProjectManager:
    """Create the Namespace Recovery project with emojified tasks."""
    manager = GitHubProjectManager()
    
    # Phase 1: Analysis and Planning 🕵️‍♂️
    manager.create_task(
        task_id="NSR-001",
        title="🕵️‍♂️ Audit Current Namespace Usage",
        description="Identify all files using example.org and relative paths",
        priority=1
    )
    
    manager.create_task(
        task_id="NSR-002",
        title="📊 Analyze Namespace Patterns",
        description="Document current namespace patterns and inconsistencies",
        priority=1,
        depends_on=["NSR-001"]
    )
    
    manager.create_task(
        task_id="NSR-003",
        title="📝 Create Recovery Plan",
        description="Document step-by-step recovery process",
        priority=1,
        depends_on=["NSR-002"]
    )
    
    # Phase 2: Implementation 🛠️
    manager.create_task(
        task_id="NSR-004",
        title="🛠️ Update Core Ontologies",
        description="Fix namespace references in core ontology files",
        priority=2,
        depends_on=["NSR-003"]
    )
    
    manager.create_task(
        task_id="NSR-005",
        title="🔧 Update Implementation Files",
        description="Update namespace references in Python implementation files",
        priority=2,
        depends_on=["NSR-004"]
    )
    
    manager.create_task(
        task_id="NSR-006",
        title="🧪 Update Test Files",
        description="Update namespace references in test files",
        priority=2,
        depends_on=["NSR-005"]
    )
    
    # Phase 3: Validation and Documentation 📚
    manager.create_task(
        task_id="NSR-007",
        title="✅ Validate Changes",
        description="Run full test suite and validate all changes",
        priority=3,
        depends_on=["NSR-006"]
    )
    
    manager.create_task(
        task_id="NSR-008",
        title="📚 Update Documentation",
        description="Update documentation with new namespace standards",
        priority=3,
        depends_on=["NSR-007"]
    )
    
    manager.create_task(
        task_id="NSR-009",
        title="🛡️ Add Prevention Measures",
        description="Implement CI/CD checks for namespace compliance",
        priority=3,
        depends_on=["NSR-008"]
    )
    
    manager.create_task(
        task_id="NSR-010",
        title="🎉 Project Completion",
        description="Final review and project sign-off",
        priority=3,
        depends_on=["NSR-009"]
    )
    
    return manager

def get_project_status(manager: GitHubProjectManager) -> str:
    """Get a friendly status report of the project."""
    total_tasks = len(manager.tasks)
    completed_tasks = len(manager.list_tasks(status=TaskStatus.COMPLETED))
    in_progress = len(manager.list_tasks(status=TaskStatus.IN_PROGRESS))
    
    return f"""
    🎯 Namespace Recovery Project Status
    ===================================
    📊 Progress: {completed_tasks}/{total_tasks} tasks completed
    🚧 In Progress: {in_progress} tasks
    📅 Next Steps: {[t.title for t in manager.list_tasks(status=TaskStatus.TODO)][:2]}
    """ 