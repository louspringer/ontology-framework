#!/usr/bin/env python3
"""
Tests for namespace recovery project.
"""

import pytest
from src.ontology_framework.namespace_recovery import create_namespace_recovery_project, get_project_status
from src.ontology_framework.github_project_manager import TaskStatus

def test_create_namespace_recovery_project():
    """Test creation of namespace recovery project."""
    manager = create_namespace_recovery_project()
    
    # Verify all tasks were created
    assert len(manager.tasks) == 10
    
    # Verify task dependencies
    audit_task = manager.get_task("NSR-001")
    assert audit_task.title == "🕵️‍♂️ Audit Current Namespace Usage"
    assert audit_task.depends_on == []
    
    analysis_task = manager.get_task("NSR-002")
    assert analysis_task.title == "📊 Analyze Namespace Patterns"
    assert analysis_task.depends_on == ["NSR-001"]
    
    # Verify priorities
    high_priority_tasks = manager.list_tasks(priority=1)
    assert len(high_priority_tasks) == 3  # Analysis phase tasks
    
    medium_priority_tasks = manager.list_tasks(priority=2)
    assert len(medium_priority_tasks) == 3  # Implementation phase tasks
    
    low_priority_tasks = manager.list_tasks(priority=3)
    assert len(low_priority_tasks) == 4  # Validation and completion tasks

def test_project_status():
    """Test project status reporting."""
    manager = create_namespace_recovery_project()
    
    # Initial status
    status = get_project_status(manager)
    assert "0/10 tasks completed" in status
    assert "In Progress: 0 tasks" in status
    
    # Complete some tasks
    manager.update_task_status("NSR-001", TaskStatus.COMPLETED)
    manager.update_task_status("NSR-002", TaskStatus.IN_PROGRESS)
    
    status = get_project_status(manager)
    assert "1/10 tasks completed" in status
    assert "In Progress: 1 tasks" in status 