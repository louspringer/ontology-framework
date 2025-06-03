"""MCP Configuration and Validation Module."""

import json
import logging
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
)

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
    
    def validate_bfg9k(self, context: Dict[str, Any]) -> bool:
        """Validate using BFG9K pattern.
        
        Args:
            context: Dictionary containing prompt context
            
        Returns:
            True if validation passes, False otherwise
        """
        if "BFG9K" not in self.validation_rules.get("guidance", {}):
            return True
            
        bfg9k_rules = self.validation_rules["guidance"]["BFG9K"]["rules"]
        validation_results = []
        
        # Check semantic first approach
        if bfg9k_rules["semanticFirst"]["enabled"]:
            if not self._validate_semantic_first(context):
                validation_results.append((
                    "semanticFirst",
                    bfg9k_rules["semanticFirst"]["message"]
                ))
        
        # Check validation approach
        if bfg9k_rules["validationApproach"]["enabled"]:
            if not self._validate_shacl_approach(context):
                validation_results.append((
                    "validationApproach",
                    bfg9k_rules["validationApproach"]["message"]
                ))
        
        # Check ontology context
        if bfg9k_rules["ontologyContext"]["enabled"]:
            if not self._validate_ontology_context(context):
                validation_results.append((
                    "ontologyContext",
                    bfg9k_rules["ontologyContext"]["message"]
                ))
        
        if validation_results:
            for rule, message in validation_results:
                self.logger.warning(f"BFG9K validation failed for {rule}: {message}")
            return False
            
        return True
        
    def _validate_semantic_first(self, context: Dict[str, Any]) -> bool:
        """Validate semantic first approach."""
        if "ontology_path" not in context:
            return False
            
        ontology_path = Path(context["ontology_path"])
        if not ontology_path.exists():
            return False
            
        # Load ontology into graph
        try:
            graph = Graph()
            graph.parse(str(ontology_path), format="turtle")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load ontology: {str(e)}")
            return False
            
    def _validate_shacl_approach(self, context: Dict[str, Any]) -> bool:
        """Validate SHACL validation approach."""
        if "target_files" not in context:
            return False
            
        for target_file in context["target_files"]:
            if not Path(target_file).exists():
                return False
                
            # Check for SHACL shapes
            try:
                graph = Graph()
                graph.parse(str(target_file), format="turtle")
                shapes = list(graph.triples((None, RDF.type, SH.NodeShape)))
                if not shapes:
                    return False
            except Exception as e:
                self.logger.error(f"Failed to validate SHACL: {str(e)}")
                return False
                
        return True
        
    def _validate_ontology_context(self, context: Dict[str, Any]) -> bool:
        """Validate ontology context coherence."""
        if "ontology_path" not in context or "target_files" not in context:
            return False
            
        try:
            # Load main ontology
            main_graph = Graph()
            main_graph.parse(str(context["ontology_path"]), format="turtle")
            
            # Check imports and references
            for target_file in context["target_files"]:
                target_graph = Graph()
                target_graph.parse(str(target_file), format="turtle")
                
                # Check for common namespaces and references
                main_namespaces = set(main_graph.namespaces())
                target_namespaces = set(target_graph.namespaces())
                
                if not main_namespaces.intersection(target_namespaces):
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to validate ontology context: {str(e)}")
            return False
            
        return True 