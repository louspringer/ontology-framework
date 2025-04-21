"""MCP configuration and validation module."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH

class MCPConfigError(Exception):
    """Base exception for MCP configuration errors."""
    pass

class MCPValidationError(Exception):
    """Exception for validation errors."""
    def __init__(self, message: str, validation_report: Optional[Graph] = None):
        super().__init__(message)
        self.validation_report = validation_report

class MCPConfig:
    """MCP configuration manager."""
    
    def __init__(self, config_path: Path) -> None:
        """Initialize the MCP configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger("mcp_config")
        
    def load(self) -> None:
        """Load the configuration from file."""
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
            self.logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            raise MCPConfigError(f"Failed to load configuration: {e}")
    
    def get_server_config(self, server_name: str = "datapilot") -> Dict[str, Any]:
        """Get the configuration for a specific server.
        
        Args:
            server_name: Name of the server to get configuration for
            
        Returns:
            Dictionary containing server configuration
        """
        try:
            return self.config["mcpServers"][server_name]
        except KeyError:
            raise MCPConfigError(f"Server configuration not found: {server_name}")
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get the validation rules configuration.
        
        Returns:
            Dictionary containing validation rules
        """
        try:
            return self.config["validation"]
        except KeyError:
            return {
                "enabled": True,
                "strict": False,
                "rules": {
                    "phaseOrder": True,
                    "contextRequired": True,
                    "serverConfigRequired": True
                }
            }
    
    def setup_logging(self) -> None:
        """Set up logging based on configuration."""
        try:
            log_config = self.config["logging"]
            level = getattr(logging, log_config["level"].upper())
            format_str = log_config["format"]
            file_path = log_config["file"]
            
            logging.basicConfig(
                level=level,
                format=format_str,
                filename=file_path
            )
            self.logger.info("Logging configured")
        except Exception as e:
            self.logger.warning(f"Failed to configure logging: {e}")
            # Fall back to basic logging
            logging.basicConfig(level=logging.INFO)

class MCPValidator:
    """MCP validation manager."""
    
    def __init__(self, config: MCPConfig) -> None:
        """Initialize the MCP validator.
        
        Args:
            config: MCP configuration instance
        """
        self.config = config
        self.logger = logging.getLogger("mcp_validator")
        self.validation_rules = config.get_validation_rules()
    
    def validate_ontology(self, data_graph: Graph, shapes_graph: Optional[Graph] = None) -> bool:
        """Validate an ontology using SHACL shapes.
        
        Args:
            data_graph: The RDF graph to validate
            shapes_graph: Optional SHACL shapes graph. If not provided, will look for shapes in data_graph
            
        Returns:
            True if validation passes, False otherwise
            
        Raises:
            MCPValidationError: If validation fails with details in the validation report
        """
        try:
            # If no shapes graph provided, use shapes from data graph
            if shapes_graph is None:
                shapes_graph = Graph()
                for shape in data_graph.subjects(RDF.type, SH.NodeShape):
                    for p, o in data_graph.predicate_objects(shape):
                        shapes_graph.add((shape, p, o))
            
            # Import pyshacl dynamically to avoid hard dependency
            from pyshacl import validate
            
            conforms, results_graph, results_text = validate(
                data_graph,
                shacl_graph=shapes_graph,
                inference='rdfs',
                abort_on_first=not self.validation_rules["strict"],
                meta_shacl=True
            )
            
            if not conforms:
                self.logger.warning(f"SHACL validation failed:\n{results_text}")
                raise MCPValidationError(
                    "Ontology validation failed",
                    validation_report=results_graph
                )
            
            return True
            
        except ImportError:
            self.logger.warning("pyshacl not installed - skipping SHACL validation")
            return True
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
    
    def validate_phase_order(self, phases: List[str]) -> bool:
        """Validate that phases follow the correct order.
        
        Args:
            phases: List of phase names
            
        Returns:
            True if phase order is valid, False otherwise
        """
        if not self.validation_rules["rules"]["phaseOrder"]:
            return True
            
        required_order = ["discovery", "plan", "do", "check", "act"]
        try:
            for i, phase in enumerate(phases):
                if phase.lower() != required_order[i]:
                    self.logger.warning(f"Invalid phase order: {phase} should be {required_order[i]}")
                    return False
            return True
        except IndexError:
            self.logger.warning("Invalid phase order: too many phases")
            return False
    
    def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate the prompt context.
        
        Args:
            context: Dictionary containing prompt context
            
        Returns:
            True if context is valid, False otherwise
        """
        if not self.validation_rules["rules"]["contextRequired"]:
            return True
            
        required_fields = ["ontology_path", "target_files", "server_config"]
        for field in required_fields:
            if field not in context:
                self.logger.warning(f"Missing required context field: {field}")
                return False
                
        # Validate paths exist
        if not Path(context["ontology_path"]).exists():
            self.logger.warning(f"Ontology path does not exist: {context['ontology_path']}")
            return False
            
        for target_file in context["target_files"]:
            if not Path(target_file).exists():
                self.logger.warning(f"Target file does not exist: {target_file}")
                return False
                
        return True
    
    def validate_server_config(self, server_config: Dict[str, Any]) -> bool:
        """Validate the server configuration.
        
        Args:
            server_config: Dictionary containing server configuration
            
        Returns:
            True if server config is valid, False otherwise
        """
        if not self.validation_rules["rules"]["serverConfigRequired"]:
            return True
            
        required_fields = ["url", "type", "timeout"]
        for field in required_fields:
            if field not in server_config:
                self.logger.warning(f"Missing required server config field: {field}")
                return False
                
        # Validate URL format
        from urllib.parse import urlparse
        try:
            result = urlparse(server_config["url"])
            if not all([result.scheme, result.netloc]):
                self.logger.warning(f"Invalid server URL: {server_config['url']}")
                return False
        except Exception:
            self.logger.warning(f"Invalid server URL: {server_config['url']}")
            return False
            
        # Validate timeout is positive
        if not isinstance(server_config["timeout"], (int, float)) or server_config["timeout"] <= 0:
            self.logger.warning(f"Invalid timeout value: {server_config['timeout']}")
            return False
            
        return True 