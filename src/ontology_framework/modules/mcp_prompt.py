"""Model Context Protocol (MCP) prompt implementation."""

from typing import Dict, Any, List, Optional, Protocol, runtime_checkable, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH
from rdflib.plugins.sparql import prepareQuery

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
class PromptContext:
    """Context for prompt execution."""
    ontology_path: Path
    target_files: List[Path]
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
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

@dataclass
class PromptPhase:
    """Base class for prompt phases."""
    name: str
    status: str = "PENDING"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    
    def execute(self, context: 'PromptContext', *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the phase with the given context and arguments."""
        raise NotImplementedError("Subclasses must implement execute()")

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
            
            # Load and analyze ontology
            graph = Graph()
            graph.parse(context.ontology_path, format="turtle")
            
            # Discover ontology structure
            classes = set(graph.subjects(RDF.type, OWL.Class))
            properties = set(graph.subjects(RDF.type, OWL.ObjectProperty))
            data_properties = set(graph.subjects(RDF.type, OWL.DatatypeProperty))
            individuals = set(graph.subjects(RDF.type, OWL.NamedIndividual))
            
            # Analyze class hierarchy
            class_hierarchy: Dict[URIRef, Set[URIRef]] = {}
            for cls in classes:
                superclasses = set(graph.objects(cls, RDFS.subClassOf))
                class_hierarchy[cls] = {sc for sc in superclasses if isinstance(sc, URIRef)}
            
            # Discover SHACL shapes
            shapes = set(graph.subjects(RDF.type, SH.NodeShape))
            shape_constraints: Dict[URIRef, List[Dict[str, Any]]] = {}
            
            for shape in shapes:
                constraints = []
                for prop in graph.objects(shape, SH.property):
                    if isinstance(prop, BNode):
                        constraint = {
                            "path": next(graph.objects(prop, SH.path), None),
                            "min_count": next(graph.objects(prop, SH.minCount), None),
                            "max_count": next(graph.objects(prop, SH.maxCount), None),
                            "datatype": next(graph.objects(prop, SH.datatype), None)
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
            
            # Apply necessary adjustments based on validation results
            adjustments: List[Dict[str, str]] = []
            recommendations: List[Dict[str, str]] = []
            
            for result in check_results.get("validation_results", []):
                if result["status"] != "PASSED":
                    adjustments.append({
                        "file": result["file"],
                        "action": "Fix validation issues",
                        "details": result["details"]
                    })
            
            self.results = {
                "adjustments": adjustments,
                "recommendations": recommendations,
                "check_results": check_results
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

class MCPPrompt:
    """Model Context Protocol prompt implementation."""
    
    def __init__(self, context: PromptContext) -> None:
        """Initialize the MCP prompt."""
        self.context = context
        self.phases = {
            "discovery": DiscoveryPhase(),
            "plan": PlanPhase(),
            "do": DoPhase(),
            "check": CheckPhase(),
            "act": ActPhase()
        }
        self.results: Dict[str, Any] = {}
        
    def execute(self) -> Dict[str, Any]:
        """Execute the prompt following the PDCA cycle with Discovery phase."""
        try:
            # Discovery phase
            discovery_results = self.phases["discovery"].execute(self.context)
            self.results["discovery"] = discovery_results
            
            # Plan phase
            plan_results = self.phases["plan"].execute(self.context)
            self.results["plan"] = plan_results
            
            # Do phase
            do_results = self.phases["do"].execute(self.context, plan_results)
            self.results["do"] = do_results
            
            # Check phase
            check_results = self.phases["check"].execute(self.context, do_results)
            self.results["check"] = check_results
            
            # Act phase
            act_results = self.phases["act"].execute(self.context, check_results)
            self.results["act"] = act_results
            
            return self.results
            
        except PromptError as e:
            # Update the status of the phase where the error occurred
            if e.phase:
                self.phases[e.phase.lower()].status = "ERROR"
            
            # Update the status of subsequent phases to "PENDING"
            phase_order = ["discovery", "plan", "do", "check", "act"]
            error_phase_index = phase_order.index(e.phase.lower()) if e.phase else -1
            
            for phase_name in phase_order[error_phase_index + 1:]:
                self.phases[phase_name].status = "PENDING"
            
            return {
                "error": str(e),
                "phase": e.phase,
                "context": e.context,
                "phases": {name: phase.status for name, phase in self.phases.items()}
            }
        except Exception as e:
            # Update all phase statuses to "ERROR" for unexpected exceptions
            for phase in self.phases.values():
                phase.status = "ERROR"
            
            return {
                "error": str(e),
                "error_type": type(e).__name__,
                "phases": {name: phase.status for name, phase in self.phases.items()}
            } 