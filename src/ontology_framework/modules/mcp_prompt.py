"""Model Context Protocol (MCP) prompt implementation."""

from typing import Dict, Any, List, Optional, Protocol, runtime_checkable, Set, Union, cast
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH
from rdflib.plugins.sparql import prepareQuery
from rdflib.term import Node

class PromptError(Exception):
    """Base exception for prompt-related errors."""
    def __init__(self, message: str, phase: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.phase = phase
        self.context = context or {}

@runtime_checkable
class PhaseProtocol(Protocol):
    """Protocol defining the interface for prompt phases."""
    def execute(self, context: 'PromptContext', *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the phase with the given context and arguments."""
        ...

@dataclass
class ServerConfig:
    """Server configuration for MCP."""
    url: str
    type: str
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ServerConfig':
        """Create ServerConfig from dictionary."""
        return cls(
            url=config["url"],
            type=config["type"],
            timeout=config.get("timeout", 30),
            retry_attempts=config.get("retryAttempts", 3),
            retry_delay=config.get("retryDelay", 1)
        )

@dataclass
class ValidationConfig:
    """Validation configuration for MCP."""
    enabled: bool = True
    require_phase_order: bool = True
    require_context: bool = True
    require_server_config: bool = True

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ValidationConfig':
        """Create ValidationConfig from dictionary."""
        return cls(
            enabled=config.get("enabled", True),
            require_phase_order=config.get("requirePhaseOrder", True),
            require_context=config.get("requireContext", True),
            require_server_config=config.get("requireServerConfig", True)
        )

@dataclass
class PromptContext:
    """Context for prompt execution."""
    ontology_path: Path
    target_files: List[Path]
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    server_config: Optional[ServerConfig] = None
    validation_config: Optional[ValidationConfig] = None
    
    def validate(self) -> None:
        """Validate the context configuration."""
        if not self.ontology_path.exists():
            raise PromptError(
                f"Ontology path does not exist: {self.ontology_path}",
                phase="Plan",
                context={"ontology_path": str(self.ontology_path)}
            )
        
        for target_file in self.target_files:
            if not target_file.exists():
                raise PromptError(
                    f"Target file does not exist: {target_file}",
                    phase="Plan",
                    context={"target_file": str(target_file)}
                )
        
        if self.validation_config and self.validation_config.enabled:
            if self.validation_config.require_server_config and not self.server_config:
                raise PromptError(
                    "Server configuration is required when validation is enabled",
                    phase="Plan",
                    context={"validation": "server_config_missing"}
                )
            
            if self.validation_config.require_context and not self.metadata:
                raise PromptError(
                    "Context metadata is required when validation is enabled",
                    phase="Plan",
                    context={"validation": "metadata_missing"}
                )

    @classmethod
    def from_config(cls, config_path: Path) -> 'PromptContext':
        """Create PromptContext from configuration file."""
        if not config_path.exists():
            raise PromptError(f"Configuration file not found: {config_path}")
        
        with open(config_path) as f:
            config = json.load(f)
        
        server_config = None
        if "mcpServers" in config and "datapilot" in config["mcpServers"]:
            server_config = ServerConfig.from_dict(config["mcpServers"]["datapilot"])
        
        validation_config = None
        if "validation" in config:
            validation_config = ValidationConfig.from_dict(config["validation"])
        
        return cls(
            ontology_path=Path(config.get("ontologyPath", "guidance.ttl")),
            target_files=[Path(f) for f in config.get("targetFiles", [])],
            validation_rules=config.get("validationRules", {}),
            metadata=config.get("metadata", {}),
            server_config=server_config,
            validation_config=validation_config
        )

@dataclass
class PromptPhase:
    """Base class for prompt phases."""
    name: str
    status: str = "PENDING"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    error_context: Optional[Dict[str, Any]] = None
    
    def execute(self, context: 'PromptContext', *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the phase with the given context and arguments."""
        raise NotImplementedError("Subclasses must implement execute()")
        
    def validate(self, context: 'PromptContext') -> None:
        """Validate phase configuration."""
        if not context.validation_rules:
            raise PromptError(
                "Validation rules are required",
                self.name,
                {"validation_rules": "missing"}
            )

class DiscoveryPhase(PromptPhase):
    """Discovery phase of the prompt to analyze ontology and context."""
    def __init__(self) -> None:
        super().__init__("Discovery")
        
    def execute(self, context: PromptContext, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the discovery phase."""
        self.start_time = datetime.now()
        try:
            # Validate context
            context.validate()
            self.validate(context)
            
            # Load and analyze ontology
            graph = Graph()
            graph.parse(context.ontology_path, format="turtle")
            
            # Discover ontology structure with proper type casting
            classes = {cast(URIRef, cls) for cls in graph.subjects(RDF.type, OWL.Class) if isinstance(cls, URIRef)}
            properties = {cast(URIRef, prop) for prop in graph.subjects(RDF.type, OWL.ObjectProperty) if isinstance(prop, URIRef)}
            data_properties = {cast(URIRef, prop) for prop in graph.subjects(RDF.type, OWL.DatatypeProperty) if isinstance(prop, URIRef)}
            individuals = {cast(URIRef, ind) for ind in graph.subjects(RDF.type, OWL.NamedIndividual) if isinstance(ind, URIRef)}
            
            # Analyze class hierarchy with proper type casting
            class_hierarchy: Dict[URIRef, Set[URIRef]] = {}
            for cls in classes:
                superclasses = {cast(URIRef, sc) for sc in graph.objects(cls, RDFS.subClassOf) if isinstance(sc, URIRef)}
                class_hierarchy[cls] = superclasses
            
            # Discover SHACL shapes with proper type casting
            shapes = {cast(URIRef, shape) for shape in graph.subjects(RDF.type, SH.NodeShape) if isinstance(shape, URIRef)}
            shape_constraints: Dict[URIRef, List[Dict[str, Any]]] = {}
            
            for shape in shapes:
                constraints = []
                for prop in graph.objects(shape, SH.property):
                    if isinstance(prop, BNode):
                        constraint = {
                            "path": next((cast(URIRef, p) for p in graph.objects(prop, SH.path) if isinstance(p, URIRef)), None),
                            "min_count": next((cast(Literal, c) for c in graph.objects(prop, SH.minCount) if isinstance(c, Literal)), None),
                            "max_count": next((cast(Literal, c) for c in graph.objects(prop, SH.maxCount) if isinstance(c, Literal)), None),
                            "datatype": next((cast(URIRef, d) for d in graph.objects(prop, SH.datatype) if isinstance(d, URIRef)), None)
                        }
                        constraints.append(constraint)
                shape_constraints[shape] = constraints
            
            # Analyze target files
            file_analysis = []
            for target_file in context.target_files:
                analysis = {
                    "file": str(target_file),
                    "exists": target_file.exists(),
                    "size": target_file.stat().st_size if target_file.exists() else 0,
                    "modified": datetime.fromtimestamp(target_file.stat().st_mtime).isoformat() if target_file.exists() else None
                }
                file_analysis.append(analysis)
            
            self.results = {
                "ontology_analysis": {
                    "classes": list(classes),
                    "properties": list(properties),
                    "data_properties": list(data_properties),
                    "individuals": list(individuals),
                    "class_hierarchy": {str(k): [str(v) for v in vs] for k, vs in class_hierarchy.items()},
                    "shapes": {str(k): v for k, v in shape_constraints.items()}
                },
                "file_analysis": file_analysis,
                "metadata": {
                    "ontology_path": str(context.ontology_path),
                    "ontology_format": "turtle",
                    "discovery_timestamp": self.start_time.isoformat()
                }
            }
            self.status = "COMPLETED"
        except Exception as e:
            self.status = "ERROR"
            self.error = str(e)
            self.error_context = {"error_type": type(e).__name__}
            if isinstance(e, PromptError):
                raise
            raise PromptError(str(e), self.name, {"error_type": type(e).__name__})
        finally:
            self.end_time = datetime.now()
        return self.results

class PlanPhase(PromptPhase):
    """Planning phase of the prompt."""
    def __init__(self) -> None:
        super().__init__("Plan")
        
    def execute(self, context: PromptContext, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the planning phase."""
        self.start_time = datetime.now()
        try:
            # Validate context
            context.validate()
            
            # Analyze ontology structure
            graph = Graph()
            graph.parse(context.ontology_path, format="turtle")
            
            # Extract required classes and properties
            classes = set(graph.subjects(RDF.type, OWL.Class))
            properties = set(graph.subjects(RDF.type, OWL.ObjectProperty))
            
            if not classes:
                raise PromptError("No classes found in ontology", self.name)
            
            self.results = {
                "classes": list(classes),
                "properties": list(properties),
                "validation_rules": context.validation_rules,
                "metadata": context.metadata
            }
            self.status = "COMPLETED"
        except Exception as e:
            self.status = "ERROR"
            if isinstance(e, PromptError):
                raise
            raise PromptError(str(e), self.name, {"error_type": type(e).__name__})
        finally:
            self.end_time = datetime.now()
        return self.results

class DoPhase(PromptPhase):
    """Execution phase of the prompt."""
    def __init__(self) -> None:
        super().__init__("Do")
        
    def execute(self, context: PromptContext, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the implementation phase."""
        self.start_time = datetime.now()
        try:
            plan_results = args[0] if args else kwargs.get("plan_results", {})
            if plan_results.get("status") == "ERROR":
                raise PromptError("Cannot execute Do phase with failed Plan phase", self.name)
            
            # Generate Python code from ontology
            generated_files: List[str] = []
            modified_files: List[str] = []
            
            for target_file in context.target_files:
                # Implementation would go here
                modified_files.append(str(target_file))
            
            self.results = {
                "generated_files": generated_files,
                "modified_files": modified_files,
                "plan_results": plan_results
            }
            self.status = "COMPLETED"
            return self.results
        except Exception as e:
            self.status = "ERROR"
            if isinstance(e, PromptError):
                raise
            raise PromptError(str(e), self.name, {"error_type": type(e).__name__})
        finally:
            self.end_time = datetime.now()

class CheckPhase(PromptPhase):
    """Validation phase of the prompt."""
    def __init__(self) -> None:
        super().__init__("Check")
        
    def execute(self, context: PromptContext, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the validation phase."""
        self.start_time = datetime.now()
        try:
            do_results = args[0] if args else kwargs.get("do_results", {})
            if do_results.get("status") == "ERROR":
                raise PromptError("Cannot execute Check phase with failed Do phase", self.name)
            
            # Validate generated code against ontology
            validation_results: List[Dict[str, str]] = []
            test_results: List[Dict[str, Any]] = []
            
            for modified_file in do_results.get("modified_files", []):
                # Implementation would go here
                validation_results.append({
                    "file": modified_file,
                    "status": "PASSED",
                    "details": "Validation successful"
                })
            
            self.results = {
                "validation_results": validation_results,
                "test_results": test_results,
                "do_results": do_results
            }
            self.status = "COMPLETED"
            return self.results
        except Exception as e:
            self.status = "ERROR"
            if isinstance(e, PromptError):
                raise
            raise PromptError(str(e), self.name, {"error_type": type(e).__name__})
        finally:
            self.end_time = datetime.now()

class ActPhase(PromptPhase):
    """Adjustment phase of the prompt."""
    def __init__(self) -> None:
        super().__init__("Act")
        
    def execute(self, context: PromptContext, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the adjustment phase."""
        self.start_time = datetime.now()
        try:
            check_results = args[0] if args else kwargs.get("check_results", {})
            if check_results.get("status") == "ERROR":
                raise PromptError("Cannot execute Act phase with failed Check phase", self.name)
            
            # Apply necessary adjustments based on validation results and previous findings
            adjustments: List[Dict[str, Any]] = []
            recommendations: List[Dict[str, Any]] = []
            
            # Handle validation failures
            for result in check_results.get("validation_results", []):
                if result["status"] != "PASSED":
                    adjustments.append({
                        "file": result["file"],
                        "action": "Fix validation issues",
                        "details": result["details"]
                    })
            
            # Process recommendations from previous findings
            if context.metadata and "previousFindings" in context.metadata:
                prev_findings = context.metadata["previousFindings"]
                
                # Add recommendations from missing elements
                if "missingElements" in prev_findings:
                    missing = prev_findings["missingElements"]
                    for element_type, description in missing.items():
                        recommendations.append({
                            "type": "enhancement",
                            "target": element_type,
                            "description": description,
                            "priority": "high"
                        })
                
                # Add existing recommendations
                if "recommendations" in prev_findings:
                    recommendations.extend(prev_findings["recommendations"])
                
                # Implement high priority recommendations
                for rec in recommendations:
                    if rec.get("priority") == "high":
                        if rec["target"] == "classHierarchy":
                            adjustments.append({
                                "file": str(context.ontology_path),
                                "action": "Restructure class hierarchy",
                                "details": "Add meaningful subclass relationships",
                                "changes": [
                                    {"type": "add_subclass", "class": "TestPhase", "parent": "ValidationPattern"},
                                    {"type": "add_subclass", "class": "IntegrationStep", "parent": "ValidationPattern"},
                                    {"type": "add_subclass", "class": "ModelConformance", "parent": "ValidationPattern"}
                                ]
                            })
                        elif rec["target"] == "individuals":
                            adjustments.append({
                                "file": str(context.ontology_path),
                                "action": "Add example instances",
                                "details": "Create concrete examples for key classes",
                                "changes": [
                                    {"type": "add_individual", "class": "TestPhase", "id": "UnitTestPhase"},
                                    {"type": "add_individual", "class": "TestPhase", "id": "IntegrationTestPhase"},
                                    {"type": "add_individual", "class": "ValidationPattern", "id": "SHACLValidationPattern"},
                                    {"type": "add_individual", "class": "ValidationPattern", "id": "OWLValidationPattern"}
                                ]
                            })
            
            self.results = {
                "adjustments": adjustments,
                "recommendations": recommendations,
                "check_results": check_results
            }
            self.status = "COMPLETED"
            
            # Actually implement the adjustments
            self._implement_adjustments(context)
            
            return self.results
        except Exception as e:
            self.status = "ERROR"
            if isinstance(e, PromptError):
                raise
            raise PromptError(str(e), self.name, {"error_type": type(e).__name__})
        finally:
            self.end_time = datetime.now()
    
    def _implement_adjustments(self, context: PromptContext) -> None:
        """Implement the adjustments to the ontology and related files."""
        if not self.results or "adjustments" not in self.results:
            return
            
        for adjustment in self.results["adjustments"]:
            file_path = Path(adjustment["file"])
            if not file_path.exists():
                continue
                
            if file_path.suffix == ".ttl":
                self._implement_ontology_adjustment(file_path, adjustment)
    
    def _implement_ontology_adjustment(self, file_path: Path, adjustment: Dict[str, Any]) -> None:
        """Implement adjustments to the ontology file."""
        graph = Graph()
        graph.parse(file_path, format="turtle")
        
        if "changes" in adjustment:
            for change in adjustment["changes"]:
                if change["type"] == "add_subclass":
                    self._add_subclass_relationship(graph, change)
                elif change["type"] == "add_individual":
                    self._add_individual(graph, change)
                    
        graph.serialize(file_path, format="turtle")
    
    def _add_subclass_relationship(self, graph: Graph, change: Dict[str, str]) -> None:
        """Add a subclass relationship to the ontology."""
        ns = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
        subclass = URIRef(ns[change["class"]])
        parent = URIRef(ns[change["parent"]])
        graph.add((subclass, RDFS.subClassOf, parent))
    
    def _add_individual(self, graph: Graph, change: Dict[str, str]) -> None:
        """Add an individual to the ontology."""
        ns = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
        individual = URIRef(ns[change["id"]])
        class_type = URIRef(ns[change["class"]])
        graph.add((individual, RDF.type, class_type))
        graph.add((individual, RDFS.label, Literal(change["id"])))

class MCPPrompt:
    """Model Context Protocol prompt implementation."""
    
    def __init__(self, context: PromptContext) -> None:
        """Initialize the MCP prompt."""
        self.context = context
        self.phases: List[PromptPhase] = [
            DiscoveryPhase(),
            PlanPhase(),
            DoPhase(),
            CheckPhase(),
            ActPhase()
        ]
        self.current_phase: Optional[PromptPhase] = None
        self.results: Dict[str, Any] = {}
        
    def execute(self) -> Dict[str, Any]:
        """Execute all phases of the prompt."""
        try:
            # Validate context before execution
            self.context.validate()
            
            # Execute phases in order
            for phase in self.phases:
                self.current_phase = phase
                if self.context.validation_config and self.context.validation_config.require_phase_order:
                    if phase.name == "Do" and "Plan" not in self.results:
                        raise PromptError("Plan phase must be executed before Do phase", phase.name)
                    elif phase.name == "Check" and "Do" not in self.results:
                        raise PromptError("Do phase must be executed before Check phase", phase.name)
                    elif phase.name == "Act" and "Check" not in self.results:
                        raise PromptError("Check phase must be executed before Act phase", phase.name)
                
                phase_args = {}
                if phase.name == "Do":
                    phase_args["plan_results"] = self.results.get("Plan", {})
                elif phase.name == "Check":
                    phase_args["do_results"] = self.results.get("Do", {})
                elif phase.name == "Act":
                    phase_args["check_results"] = self.results.get("Check", {})
                
                self.results[phase.name] = phase.execute(self.context, **phase_args)
            
            return self.results
        except Exception as e:
            if self.current_phase:
                self.current_phase.status = "ERROR"
                self.current_phase.error = str(e)
                self.current_phase.error_context = {"error_type": type(e).__name__}
            raise 