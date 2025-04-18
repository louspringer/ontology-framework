"""
Configuration management for the Ontology Framework.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

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