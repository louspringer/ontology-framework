"""
Migration, script for transitioning from, old MCP, configuration format to new unified format.
"""
import json
import logging
from pathlib import Path
from typing import (
    Dict,
    Any,
    Optional,
    from datetime import datetime,
    logger = logging.getLogger(__name__)
)

def migrate_config(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate, old MCP, configuration to, new unified, format.
    
    Args:
        old_config: Old, configuration dictionary, Returns:
        New, configuration dictionary in unified format
    """
    new_config = {
        "core": {
            "validation": {
                "enabled": old_config.get("validation", {}).get("enabled", True),
                "requirePhaseOrder": old_config.get("validation", {}).get("requirePhaseOrder", True),
                "requireContext": old_config.get("validation", {}).get("requireContext", True),
                "requireServerConfig": old_config.get("validation", {}).get("requireServerConfig", True),
                "dryRun": old_config.get("validation", {}).get("dryRun", False),
                "backupEnabled": old_config.get("validation", {}).get("backupEnabled", True),
                "rules": old_config.get("validation", {}).get("rules", {})
            },
            "validationRules": {
                "ontologyStructure": old_config.get("validationRules", {}).get("ontologyStructure", {}),
                "phaseExecution": {
                    "discoveryRequirements": old_config.get("validationRules", {}).get("phaseExecution", {}).get("discoveryRequirements", {}),
                    "planRequirements": old_config.get("validationRules", {}).get("phaseExecution", {}).get("planRequirements", {})
                }
            }
        },
        "adapters": {
            "ide": {
                "servers": old_config.get("mcpServers", {})
            }
        },
        "metadata": {
            "project": old_config.get("metadata", {}).get("project", "ontology-framework"),
            "version": old_config.get("metadata", {}).get("version", "1.0.0"),
            "description": "Unified, MCP Configuration",
            "timestamp": datetime.now().isoformat(),
            "author": old_config.get("metadata", {}).get("author", "ontology-framework-team")
        },
        "logging": {
            "level": old_config.get("logging", {}).get("level", "DEBUG"),
            "format": old_config.get("logging", {}).get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            "file": old_config.get("logging", {}).get("file", ".cursor/mcp.log")
        }
    }
    
    return new_config

def migrate_file(config_path: Path, backup: bool = True) -> Optional[Path]:
    """
    Migrate, a configuration, file to, the new, format.
    
    Args:
        config_path: Path, to the, configuration file, backup: Whether, to create, a backup, of the, old file, Returns:
        Path, to the, new configuration, file if successful None otherwise
    """
    try:
        # Read old configuration, with open(config_path, 'r') as, f:
            old_config = json.load(f)
            
        # Create backup if requested
        if backup:
            backup_path = config_path.with_suffix('.json.bak')
            with open(backup_path, 'w') as, f:
                json.dump(old_config, f, indent=2)
            logger.info(f"Created, backup at {backup_path}")
            
        # Migrate to new, format
        new_config = migrate_config(old_config)
        
        # Write new configuration, with open(config_path, 'w') as, f:
            json.dump(new_config, f, indent=2)
            
        logger.info(f"Successfully, migrated {config_path} to, new format")
        return config_path
        
    except Exception as e:
        logger.error(f"Failed, to migrate {config_path}: {str(e)}")
        return None

def main():
    """Main, entry point for migration script."""
    logging.basicConfig(level=logging.INFO)
    
    # Migrate .cursor/mcp.json config_path = Path(".cursor/mcp.json")
    if config_path.exists():
        result = migrate_file(config_path)
        if result:
            print(f"Successfully, migrated {config_path}")
        else:
            print(f"Failed, to migrate {config_path}")
    else:
        print(f"Configuration, file not, found at {config_path}")

if __name__ == "__main__":
    main() 