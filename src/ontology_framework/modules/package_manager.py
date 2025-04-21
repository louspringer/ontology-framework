"""
Module for managing package dependencies.
"""

from typing import Dict, List, Optional
from pathlib import Path
import yaml
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

class PackageManager:
    """Class for managing package dependencies."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "pyproject.toml"
        self.dependencies = self._load_dependencies()
        
    def _load_dependencies(self) -> Dict:
        """Load dependencies from configuration file."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            return {}
            
        if self.config_path.endswith('.toml'):
            import tomli
            with open(config_file, 'rb') as f:
                return tomli.load(f)
        elif self.config_path.endswith('.yaml'):
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
        
    def get_dependencies(self) -> Dict[str, str]:
        """Get all package dependencies."""
        if 'project' in self.dependencies:
            return self.dependencies['project'].get('dependencies', {})
        return {}
        
    def get_dev_dependencies(self) -> Dict[str, str]:
        """Get development dependencies."""
        if 'project' in self.dependencies:
            return self.dependencies['project'].get('optional-dependencies', {}).get('dev', {})
        return {}
        
    def create_dependency_graph(self) -> Graph:
        """Create an RDF graph representing package dependencies."""
        graph = Graph()
        
        # Bind namespaces
        graph.bind("rdf", RDF)
        graph.bind("rdfs", RDFS)
        graph.bind("owl", OWL)
        graph.bind("pkg", URIRef("http://example.org/package#"))
        
        # Create Package class
        package_class = URIRef("http://example.org/package#Package")
        graph.add((package_class, RDF.type, OWL.Class))
        graph.add((package_class, RDFS.label, Literal("Package")))
        
        # Add dependencies
        depends_on = URIRef("http://example.org/package#dependsOn")
        graph.add((depends_on, RDF.type, OWL.ObjectProperty))
        graph.add((depends_on, RDFS.domain, package_class))
        graph.add((depends_on, RDFS.range, package_class))
        
        # Add version property
        has_version = URIRef("http://example.org/package#hasVersion")
        graph.add((has_version, RDF.type, OWL.DatatypeProperty))
        graph.add((has_version, RDFS.domain, package_class))
        
        # Add dependencies to graph
        for name, version in self.get_dependencies().items():
            pkg = URIRef(f"http://example.org/package#{name}")
            graph.add((pkg, RDF.type, package_class))
            graph.add((pkg, RDFS.label, Literal(name)))
            graph.add((pkg, has_version, Literal(version)))
            
        return graph
        
    def validate_dependencies(self) -> List[str]:
        """Validate package dependencies."""
        issues = []
        
        # Check for required packages
        required = {'rdflib', 'pyshacl', 'pyyaml'}
        deps = set(self.get_dependencies().keys())
        missing = required - deps
        if missing:
            issues.append(f"Missing required packages: {missing}")
            
        # Check for version conflicts
        # This is a placeholder for more sophisticated version conflict detection
        
        return issues 