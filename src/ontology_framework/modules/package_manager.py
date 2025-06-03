# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

"""Module for managing ontology packages."""

from typing import Dict, List, Optional
from pathlib import Path
import yaml

class PackageManager:
    """Class for managing ontology packages."""
    
    def __init__(self, package_dir: Optional[Path] = None) -> None:
        """Initialize the package manager.
        
        Args:
            package_dir: Optional path to package directory
        """
        self.package_dir = package_dir or Path("packages")
        self.package_dir.mkdir(exist_ok=True)
        self.packages: Dict[str, Dict] = {}
        self.load_packages()
        
    def load_packages(self) -> None:
        """Load package configurations."""
        for package_file in self.package_dir.glob("*.yaml"):
            with open(package_file) as f:
                package_name = package_file.stem
                self.packages[package_name] = yaml.safe_load(f)
                
    def get_package(self, name: str) -> Optional[Dict]:
        """Get package configuration.
        
        Args:
            name: Package name
            
        Returns:
            Package configuration if found, None otherwise
        """
        return self.packages.get(name)
        
    def create_package(self, name: str, config: Dict) -> None:
        """Create a new package.
        
        Args:
            name: Package name
            config: Package configuration
        """
        package_file = self.package_dir / f"{name}.yaml"
        with open(package_file, "w") as f:
            yaml.safe_dump(config, f)
        self.packages[name] = config
        
    def list_packages(self) -> List[str]:
        """List all packages.
        
        Returns:
            List of package names
        """
        return list(self.packages.keys()) 