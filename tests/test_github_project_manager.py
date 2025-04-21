#!/usr/bin/env python3
"""
Tests for GitHub project manager implementation.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from ontology_framework.github_project_manager import (
    GitHubProjectManager,
    TaskStatus,
    Task
)

@pytest.fixture
def project_manager():
    return GitHubProjectManager()

def test_create_task(project_manager):
    """Test creating a new task."""
    task = project_manager.create_task(
        task_id="TEST-001",
        title="Test Task",
        description="Test Description",
        priority=3
    )
    
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.priority == 3
    assert task.status == TaskStatus.TODO
    assert task.depends_on == []

def test_create_duplicate_task(project_manager):
    """Test creating a task with an existing ID."""
    project_manager.create_task(
        task_id="TEST-001",
        title="Test Task",
        description="Test Description"
    )
    
    with pytest.raises(ValueError, match="Task TEST-001 already exists"):
        project_manager.create_task(
            task_id="TEST-001",
            title="Duplicate Task",
            description="Should Fail"
        )

def test_update_task_status(project_manager):
    """Test updating task status."""
    task = project_manager.create_task(
        task_id="TEST-001",
        title="Test Task",
        description="Test Description"
    )
    
    task = project_manager.update_task_status(task.id, TaskStatus.IN_PROGRESS)
    assert task.status == TaskStatus.IN_PROGRESS

def test_task_dependencies(project_manager):
    """Test task dependency validation."""
    parent_task = project_manager.create_task(
        task_id="TEST-001",
        title="Parent Task",
        description="Parent Description"
    )
    
    child_task = project_manager.create_task(
        task_id="TEST-002",
        title="Child Task",
        description="Child Description",
        depends_on=["TEST-001"]
    )
    
    # Should not be able to complete child task before parent
    with pytest.raises(ValueError, match="Cannot complete task TEST-002: dependency TEST-001 not completed"):
        project_manager.update_task_status(child_task.id, TaskStatus.COMPLETED)
    
    # Complete parent task first
    task = project_manager.update_task_status(parent_task.id, TaskStatus.COMPLETED)
    assert task.status == TaskStatus.COMPLETED
    
    # Now child task can be completed
    task = project_manager.update_task_status(child_task.id, TaskStatus.COMPLETED)
    assert task.status == TaskStatus.COMPLETED

def test_list_tasks(project_manager):
    """Test listing tasks with filters."""
    project_manager.create_task(
        task_id="TEST-001",
        title="High Priority Task",
        description="High Priority",
        priority=1
    )
    
    project_manager.create_task(
        task_id="TEST-002",
        title="Low Priority Task",
        description="Low Priority",
        priority=5
    )
    
    tasks = project_manager.list_tasks()
    assert len(tasks) == 2
    assert tasks[0].priority == 1  # Higher priority first
    assert tasks[1].priority == 5
    
    # Filter by priority
    tasks = project_manager.list_tasks(priority=1)
    assert len(tasks) == 1
    assert tasks[0].priority == 1
    
    # Filter by status
    tasks = project_manager.list_tasks(status=TaskStatus.TODO)
    assert len(tasks) == 2

def test_export_import_tasks(project_manager):
    """Test exporting and importing tasks."""
    original_task = project_manager.create_task(
        task_id="TEST-001",
        title="Test Task",
        description="Test Description",
        priority=3
    )
    
    # Export tasks
    exported_json = project_manager.export_tasks()
    
    # Create new project manager and import tasks
    new_manager = GitHubProjectManager()
    new_manager.import_tasks(exported_json)
    
    # Verify imported task matches original
    imported_task = new_manager.get_task("TEST-001")
    assert imported_task.title == original_task.title
    assert imported_task.description == original_task.description
    assert imported_task.priority == original_task.priority
    assert imported_task.status == original_task.status
    assert imported_task.depends_on == original_task.depends_on

def test_validate_task(project_manager):
    """Test task validation."""
    task = project_manager.create_task(
        task_id="TEST-001",
        title="Test Task",
        description="Test Description",
        priority=3
    )
    
    assert project_manager.validate_task(task)
    
    # Test invalid priority
    with pytest.raises(ValueError, match="Priority must be between 1 and 5"):
        task.priority = 0
        project_manager.validate_task(task)
    
    # Test missing title
    with pytest.raises(ValueError, match="Missing required field: title"):
        task.title = ""
        project_manager.validate_task(task) 