"""
Configuration management for the Ontology Framework.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import yaml

def load_environment() -> None:
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")

def get_api_token() -> Optional[str]:
    """Get the Boldo API token from environment variables.
    
    Returns:
        Optional[str]: The API token if found, None otherwise.
    """
    return os.environ.get("BOLDO_API_TOKEN")

# Load environment variables when module is imported
load_environment()

class Config:
    """CLI configuration manager."""
    
    def __init__(self):
        self.config_path = Path(os.getenv("ONTOLOGY_CONFIG", "~/.config/ontology/config.yaml"))
        self.config_path = self.config_path.expanduser()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()
        
    @property
    def config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self._config
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            return self._default_config()
            
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or self._default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._default_config()
            
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "graphdb": {
                "url": os.getenv("GRAPHDB_URL", "http://localhost:7200"),
                "username": os.getenv("GRAPHDB_USERNAME", "admin"),
                "password": os.getenv("GRAPHDB_PASSWORD", "root"),
            },
            "guidance": {
                "directory": os.getenv("GUIDANCE_DIR", "guidance"),
                "auto_sync": True,
                "sync_threshold": 300,  # seconds
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }
        
    def save(self):
        """Save configuration to file."""
        with open(self.config_path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False)
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
        
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save() 