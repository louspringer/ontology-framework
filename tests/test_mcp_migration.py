"""
Test suite for MCP configuration migration.
"""
import json
import pytest
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from ontology_framework.mcp.migrate import migrate_config, migrate_file

@pytest.fixture
def old_config() -> Dict[str, Any]:
    """Sample old configuration format."""
    return {
        "validation": {
            "enabled": True,
            "requirePhaseOrder": True,
            "requireContext": True,
            "requireServerConfig": True,
            "dryRun": False,
            "backupEnabled": True,
            "rules": {
                "phaseOrder": ["discovery", "plan", "do", "check", "act"],
                "requiredPhases": ["discovery", "plan", "do", "check"],
                "optionalPhases": ["act"]
            }
        },
        "validationRules": {
            "ontologyStructure": {
                "requiredClasses": ["ValidationProcess", "ValidationRule"],
                "requiredProperties": ["hasStringRepresentation", "hasValidationRules"],
                "requiredShapes": ["ValidationRuleShape"]
            },
            "phaseExecution": {
                "discoveryRequirements": {
                    "ontologyPath": "guidance.ttl",
                    "targetFiles": ["src/ontology_framework/modules/guidance.py"]
                },
                "planRequirements": {
                    "discoveryResults": {
                        "classes": ["ValidationPattern", "TestPhase"],
                        "individuals": ["UnitTestPhase", "IntegrationTestPhase"],
                        "shapes": ["ValidationRuleShape"]
                    }
                }
            }
        },
        "mcpServers": {
            "bfg9k": {
                "url": "http://localhost:7700/sse",
                "type": "sse"
            }
        },
        "metadata": {
            "project": "test-project",
            "version": "0.1.0",
            "author": "test-author"
        },
        "logging": {
            "level": "INFO",
            "format": "%(message)s",
            "file": "test.log"
        }
    }

@pytest.fixture
def temp_config_file(tmp_path: Path, old_config: Dict[str, Any]) -> Path:
    """Create a temporary configuration file."""
    config_path = tmp_path / "mcp.json"
    with open(config_path, 'w') as f:
        json.dump(old_config, f, indent=2)
    return config_path

def test_migrate_config(old_config: Dict[str, Any]):
    """Test configuration migration function."""
    new_config = migrate_config(old_config)
    
    # Test core structure
    assert "core" in new_config
    assert "adapters" in new_config
    assert "metadata" in new_config
    assert "logging" in new_config
    
    # Test validation settings
    assert new_config["core"]["validation"]["enabled"] == old_config["validation"]["enabled"]
    assert new_config["core"]["validation"]["requirePhaseOrder"] == old_config["validation"]["requirePhaseOrder"]
    assert new_config["core"]["validation"]["rules"] == old_config["validation"]["rules"]
    
    # Test validation rules
    assert new_config["core"]["validationRules"]["ontologyStructure"] == old_config["validationRules"]["ontologyStructure"]
    assert new_config["core"]["validationRules"]["phaseExecution"]["discoveryRequirements"] == old_config["validationRules"]["phaseExecution"]["discoveryRequirements"]
    
    # Test adapters
    assert new_config["adapters"]["ide"]["servers"] == old_config["mcpServers"]
    
    # Test metadata
    assert new_config["metadata"]["project"] == old_config["metadata"]["project"]
    assert new_config["metadata"]["version"] == old_config["metadata"]["version"]
    assert new_config["metadata"]["author"] == old_config["metadata"]["author"]
    assert "timestamp" in new_config["metadata"]
    
    # Test logging
    assert new_config["logging"]["level"] == old_config["logging"]["level"]
    assert new_config["logging"]["format"] == old_config["logging"]["format"]
    assert new_config["logging"]["file"] == old_config["logging"]["file"]

def test_migrate_file(temp_config_file: Path):
    """Test file migration function."""
    # Run migration
    result = migrate_file(temp_config_file)
    
    # Check result
    assert result == temp_config_file
    
    # Check backup
    backup_path = temp_config_file.with_suffix('.json.bak')
    assert backup_path.exists()
    
    # Check new format
    with open(temp_config_file, 'r') as f:
        new_config = json.load(f)
    
    assert "core" in new_config
    assert "adapters" in new_config
    assert "metadata" in new_config
    assert "logging" in new_config

def test_migrate_file_no_backup(temp_config_file: Path):
    """Test file migration without backup."""
    # Run migration without backup
    result = migrate_file(temp_config_file, backup=False)
    
    # Check result
    assert result == temp_config_file
    
    # Check no backup created
    backup_path = temp_config_file.with_suffix('.json.bak')
    assert not backup_path.exists()

def test_migrate_file_error(tmp_path: Path):
    """Test migration with invalid file."""
    # Try to migrate non-existent file
    result = migrate_file(tmp_path / "nonexistent.json")
    assert result is None 