"""MCP prompt implementation."""

import logging
from typing import Dict, Any, Optional, Protocol, runtime_checkable, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH
from rdflib.plugins.sparql import prepareQuery
from rdflib.term import Node
from ..mcp.bfg9k_targeting import BFG9KTargeter
from ..mcp.hypercube_analysis import HypercubeAnalyzer
from .prompt_base import PromptPhase as BasePromptPhase
from .prompt_base import PromptContext as BasePromptContext
from .prompt_base import PromptError
from .validator import MCPValidator

logger = logging.getLogger(__name__)

# Define namespaces
PDCA = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/pdca#")
MCP = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/mcp#")

@runtime_checkable
class ServerProtocol(Protocol):
    """Protocol for server configuration."""
    def validate(self) -> bool:
        """Validate server configuration."""
        raise NotImplementedError

@dataclass
class ServerConfig:
    """Server configuration."""
    host: str
    port: int
    url: Optional[str] = None
    server_type: str = "default"  # Changed from 'type' to avoid keyword conflict
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ServerConfig':
        """Create ServerConfig from dictionary."""
        return cls(
            host=config["host"],
            port=config["port"],
            url=config.get("url"),
            server_type=config.get("type", "default"),
            timeout=config.get("timeout", 30),
            retry_attempts=config.get("retryAttempts", 3),
            retry_delay=config.get("retryDelay", 5)
        )

@runtime_checkable
class PhaseProtocol(Protocol):
    """Protocol defining the interface for prompt phases."""
    def execute(self, context: 'PromptContext', *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the phase with the given context and arguments."""
        ...

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
    improvements: Dict[str, Any] = field(default_factory=dict)
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
        if "mcpServers" in config and "bfg9k" in config["mcpServers"]:
            server_config = ServerConfig.from_dict(config["mcpServers"]["bfg9k"])
        
        validation_config = None
        if "validation" in config:
            validation_config = ValidationConfig.from_dict(config["validation"])
        
        validation_rules = {}
        if "validationRules" in config:
            validation_rules = config["validationRules"]
        
        return cls(
            ontology_path=Path(config.get("ontologyPath", "guidance.ttl")),
            target_files=[Path(f) for f in config.get("targetFiles", [])],
            validation_rules=validation_rules,
            metadata=config.get("metadata", {}),
            improvements=config.get("improvements", {}),
            server_config=server_config,
            validation_config=validation_config
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            'ontologyPath': str(self.ontology_path),
            'targetFiles': [str(f) for f in self.target_files],
            'validationRules': self.validation_rules,
            'mcpServers': self.server_config,
            'validation': self.validation_config,
            'metadata': self.metadata,
            'improvements': self.improvements
        }

class PromptPhase:
    """Base class for prompt phases."""
    
    def __init__(self, name: str):
        """Initialize phase."""
        self.name = name
        self.status = "PENDING"
    
    def validate(self, context: PromptContext) -> None:
        """Validate phase context."""
        if not isinstance(context, PromptContext):
            raise PromptError(
                f"Invalid context type: {type(context)}",
                phase=self.name,
                context={"expected": "PromptContext", "got": str(type(context))}
            )

class DiscoveryPhase(BasePromptPhase):
    """Phase for analyzing ontologies and files to discover targets for optimization."""

    def __init__(self) -> None:
        """Initialize the Discovery phase with BFG9K targeting and hypercube analysis."""
        super().__init__(name="Discovery")
        self.targeter = BFG9KTargeter()
        self.analyzer = HypercubeAnalyzer()

    def execute(self, context: BasePromptContext) -> Dict[str, Any]:
        """Execute the Discovery phase to analyze ontologies and files.
        
        Args:
            context: The prompt context containing paths to ontologies and target files.
            
        Returns:
            Dict containing analysis results including:
                - ontology_analysis: Classes, properties, individuals, and shapes
                - file_analysis: File metrics and content analysis
                - metrics: Calculated metrics for BFG9K targeting
                - targets: Detected optimization targets
                
        Raises:
            PromptError: If context configuration is invalid or execution fails.
        """
        try:
            self.start_time = datetime.now()
            self.status = "RUNNING"
            
            # Validate context
            if not context.ontology_paths or not context.target_files:
                self.status = "ERROR"
                self.error = "Invalid context configuration"
                self.error_context = "Missing ontology paths or target files"
                raise PromptError("Invalid context configuration")

            # Initialize results
            results = {
                "ontology_analysis": {},
                "file_analysis": {},
                "metrics": {},
                "targets": []
            }

            # Analyze ontologies
            for onto_path in context.ontology_paths:
                g = Graph()
                g.parse(onto_path, format="turtle")
                
                # Collect classes, properties, individuals
                classes = [str(s) for s in g.subjects(RDF.type, OWL.Class)]
                properties = [str(s) for s in g.subjects(RDF.type, OWL.ObjectProperty)]
                individuals = [str(s) for s in g.subjects(RDF.type, OWL.NamedIndividual)]
                
                # Analyze SHACL shapes
                shapes = [str(s) for s in g.subjects(RDF.type, SH.NodeShape)]
                
                results["ontology_analysis"][onto_path] = {
                    "classes": classes,
                    "properties": properties,
                    "individuals": individuals,
                    "shapes": shapes
                }

            # Analyze files
            for file_path in context.target_files:
                path = Path(file_path)
                if path.exists():
                    stats = path.stat()
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    results["file_analysis"][file_path] = {
                        "size": stats.st_size,
                        "lines": len(content.splitlines()),
                        "modified": datetime.fromtimestamp(stats.st_mtime).isoformat()
                    }

            # Calculate metrics for BFG9K targeting
            metrics = {
                "total_classes": sum(len(a["classes"]) for a in results["ontology_analysis"].values()),
                "total_properties": sum(len(a["properties"]) for a in results["ontology_analysis"].values()),
                "total_individuals": sum(len(a["individuals"]) for a in results["ontology_analysis"].values()),
                "total_shapes": sum(len(a["shapes"]) for a in results["ontology_analysis"].values()),
                "total_files": len(results["file_analysis"]),
                "total_lines": sum(f["lines"] for f in results["file_analysis"].values())
            }
            results["metrics"] = metrics

            # Detect targets using BFG9K
            results["targets"] = self.targeter.detect_targets(metrics)

            self.status = "COMPLETED"
            self.end_time = datetime.now()
            return results

        except Exception as e:
            self.status = "FAILED"
            self.error = str(e)
            self.error_context = "Error during Discovery phase execution"
            self.end_time = datetime.now()
            raise PromptError(f"Discovery phase failed: {str(e)}")

class PlanPhase(PromptPhase):
    """Plan phase of the MCP prompt."""
    def __init__(self):
        super().__init__(name="Plan")
    
    def execute(self, context: PromptContext, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the plan phase."""
        self.start_time = datetime.now()
        try:
            self.validate(context)
            
            # Create RDF graph for plan
            g = Graph()
            g.bind("pdca", PDCA)
            g.bind("mcp", MCP)
            
            # Add plan phase instance
            plan_phase = URIRef(f"{PDCA}PlanPhase_{self.start_time.isoformat()}")
            g.add((plan_phase, RDF.type, PDCA.PlanPhase))
            g.add((plan_phase, PDCA.hasStartTime, self.start_time.isoformat()))
            
            # Analyze ontology
            ontology_path = context.ontology_path
            g.parse(ontology_path, format="turtle")
            
            # Get classes and properties
            classes = []
            properties = []
            for s, p, o in g.triples((None, RDF.type, OWL.Class)):
                classes.append(str(s))
            for s, p, o in g.triples((None, RDF.type, OWL.ObjectProperty)):
                properties.append(str(s))
            
            # Create plan
            plan = {
                'classes': classes,
                'properties': properties,
                'metadata': context.metadata,
                'validation_rules': context.validation_rules,
                'target_files': [str(f) for f in context.target_files],
                'rdf_graph': g.serialize(format='turtle')
            }
            
            g.add((plan_phase, PDCA.hasEndTime, datetime.now().isoformat()))
            g.add((plan_phase, PDCA.hasStatus, "COMPLETED"))
            
            self.status = "SUCCESS"
            self.results = plan
            return self.results
            
        except Exception as e:
            self.status = "ERROR"
            self.error = str(e)
            self.error_context = {"phase": "Plan"}
            raise
        finally:
            self.end_time = datetime.now()

class DoPhase(PromptPhase):
    """Do phase of the MCP prompt."""
    def __init__(self):
        super().__init__(name="Do")
    
    def execute(self, context: PromptContext, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the do phase."""
        self.start_time = datetime.now()
        try:
            self.validate(context)
            
            # Create RDF graph for do phase
            g = Graph()
            g.bind("pdca", PDCA)
            g.bind("mcp", MCP)
            
            # Add do phase instance
            do_phase = URIRef(f"{PDCA}DoPhase_{self.start_time.isoformat()}")
            g.add((do_phase, RDF.type, PDCA.DoPhase))
            g.add((do_phase, PDCA.hasStartTime, self.start_time.isoformat()))
            
            # Get plan results
            plan = context.metadata.get('plan', {})
            improvements = plan.get('improvements', {})
            
            # Track modified files
            modified_files = []
            generated_files = []
            
            # Apply improvements if specified
            if improvements:
                ontology_path = context.ontology_path
                g.parse(ontology_path, format="turtle")
                
                # Apply object properties
                for prop_id, prop_info in improvements.get('objectProperties', {}).items():
                    prop_uri = URIRef(f"http://example.org/guidance#{prop_id}")
                    g.add((prop_uri, RDF.type, OWL.ObjectProperty))
                    if 'domain' in prop_info:
                        domain = URIRef(f"http://example.org/guidance#{prop_info['domain']}")
                        g.add((prop_uri, RDFS.domain, domain))
                    if 'range' in prop_info:
                        range_ = URIRef(f"http://example.org/guidance#{prop_info['range']}")
                        g.add((prop_uri, RDFS.range, range_))
                    if 'description' in prop_info:
                        g.add((prop_uri, RDFS.comment, prop_info['description']))
                
                # Save changes
                g.serialize(ontology_path, format='turtle')
                modified_files.append(ontology_path)
            
            results = {
                'generated_files': generated_files,
                'modified_files': modified_files,
                'rdf_graph': g.serialize(format='turtle')
            }
            
            g.add((do_phase, PDCA.hasEndTime, datetime.now().isoformat()))
            g.add((do_phase, PDCA.hasStatus, "COMPLETED"))
            
            self.status = "SUCCESS"
            self.results = results
            return self.results
            
        except Exception as e:
            self.status = "ERROR"
            self.error = str(e)
            self.error_context = {"phase": "Do"}
            raise
        finally:
            self.end_time = datetime.now()

class CheckPhase(PromptPhase):
    """Check phase of the MCP prompt."""
    def __init__(self):
        super().__init__(name="Check")
    
    def execute(self, context: PromptContext, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the check phase."""
        self.start_time = datetime.now()
        try:
            self.validate(context)
            
            # Create RDF graph for check phase
            g = Graph()
            g.bind("pdca", PDCA)
            g.bind("mcp", MCP)
            
            # Add check phase instance
            check_phase = URIRef(f"{PDCA}CheckPhase_{self.start_time.isoformat()}")
            g.add((check_phase, RDF.type, PDCA.CheckPhase))
            g.add((check_phase, PDCA.hasStartTime, self.start_time.isoformat()))
            
            # Get do results
            do_results = context.metadata.get('do', {})
            validation_rules = context.validation_rules
            
            validation_results = []
            test_results = []
            
            # Perform validation
            ontology_path = context.ontology_path
            g.parse(ontology_path, format="turtle")
            
            for rule_id, rule in validation_rules.items():
                try:
                    query = rule.get('sparql')
                    if not query:
                        continue
                        
                    results = g.query(query)
                    if not results:
                        validation_results.append({
                            'file': ontology_path,
                            'rule': rule_id,
                            'status': 'PASSED',
                            'details': 'Validation successful'
                        })
                    else:
                        violations = [str(row) for row in results]
                        validation_results.append({
                            'file': ontology_path,
                            'rule': rule_id,
                            'status': 'FAILED',
                            'details': f'Validation failed: {violations}'
                        })
                except Exception as e:
                    validation_results.append({
                        'file': ontology_path,
                        'rule': rule_id,
                        'status': 'ERROR',
                        'details': f'Validation error: {str(e)}'
                    })
            
            results = {
                'do_results': do_results,
                'validation_results': validation_results,
                'test_results': test_results,
                'rdf_graph': g.serialize(format='turtle')
            }
            
            g.add((check_phase, PDCA.hasEndTime, datetime.now().isoformat()))
            g.add((check_phase, PDCA.hasStatus, "COMPLETED"))
            
            self.status = "SUCCESS"
            self.results = results
            return self.results
            
        except Exception as e:
            self.status = "ERROR"
            self.error = str(e)
            self.error_context = {"phase": "Check"}
            raise
        finally:
            self.end_time = datetime.now()

class ActPhase(PromptPhase):
    """Act phase of the PDCA cycle - analyze check results and determine adjustments."""
    
    def __init__(self):
        """Initialize the Act phase."""
        super().__init__()
        self.analyzer = HypercubeAnalyzer()
        self.targeter = BFG9KTargeter()
    
    async def execute(self, context: PromptContext, check_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Act phase.
        
        Args:
            context: The prompt context
            check_results: Results from the Check phase
            
        Returns:
            Dict containing adjustments and recommendations
        """
        try:
            if check_results.get("status") != "COMPLETED":
                raise PromptError("Cannot execute Act phase with failed Check phase")
            
            # Initialize results structure
            results = {
                "adjustments": [],
                "recommendations": [],
                "check_results": check_results,
                "status": "COMPLETED"
            }
            
            # Analyze validation results
            validation_results = check_results.get("validation_results", [])
            for result in validation_results:
                if result.get("status") != "PASSED":
                    # Calculate trajectory for failed validation
                    trajectory = self.analyzer.calculate_trajectory(
                        result.get("current_position", {}),
                        result.get("target_position", {})
                    )
                    
                    # Generate adjustment based on trajectory
                    adjustment = {
                        "file": result.get("file"),
                        "issue": result.get("details"),
                        "trajectory": trajectory,
                        "recommended_changes": self._generate_recommendations(trajectory)
                    }
                    results["adjustments"].append(adjustment)
            
            # Update status
            self.status = "COMPLETED"
            return results
            
        except Exception as e:
            self.status = "ERROR"
            raise PromptError(f"Act phase failed: {str(e)}")
    
    def _generate_recommendations(self, trajectory: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on trajectory analysis.
        
        Args:
            trajectory: The calculated trajectory
            
        Returns:
            List of recommended changes
        """
        recommendations = []
        
        # Analyze trajectory components
        for component, value in trajectory.items():
            if value > 0:
                recommendations.append(f"Increase {component} by {value}")
            elif value < 0:
                recommendations.append(f"Decrease {component} by {abs(value)}")
        
        return recommendations

class AdjustPhase(PromptPhase):
    """Adjust phase of the MCP prompt."""
    
    def __init__(self):
        super().__init__(name="Adjust")
    
    def execute(self, context: PromptContext, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the adjust phase."""
        self.start_time = datetime.now()
        try:
            self.validate(context)
            
            # Create RDF graph for adjust phase
            g = Graph()
            g.bind("pdca", PDCA)
            g.bind("mcp", MCP)
            
            # Add adjust phase instance
            adjust_phase = URIRef(f"{PDCA}AdjustPhase_{self.start_time.isoformat()}")
            g.add((adjust_phase, RDF.type, PDCA.AdjustPhase))
            g.add((adjust_phase, PDCA.hasStartTime, self.start_time.isoformat()))
            
            # Get check results
            check_results = context.metadata.get('check', {})
            validation_results = check_results.get('validation_results', [])
            
            # Determine if any adjustments needed
            adjustments = []
            recommendations = []
            
            # Check validation results
            for result in validation_results:
                if result['status'] == 'FAILED':
                    adjustments.append({
                        'file': result['file'],
                        'rule': result['rule'],
                        'action': f"Fix validation error: {result['details']}"
                    })
                    recommendations.append(f"Fix {result['rule']} in {result['file']}: {result['details']}")
            
            results = {
                'check_results': check_results,
                'adjustments': adjustments,
                'recommendations': recommendations,
                'rdf_graph': g.serialize(format='turtle')
            }
            
            g.add((adjust_phase, PDCA.hasEndTime, datetime.now().isoformat()))
            g.add((adjust_phase, PDCA.hasStatus, "COMPLETED"))
            
            self.status = "SUCCESS"
            self.results = results
            return self.results
            
        except Exception as e:
            self.status = "ERROR"
            self.error = str(e)
            self.error_context = {"phase": "Adjust"}
            raise
        finally:
            self.end_time = datetime.now()

class MCPPrompt:
    """MCP prompt implementation."""
    def __init__(self, context: PromptContext):
        self.context = context
        self.phases = [
            PlanPhase(),
            DoPhase(),
            CheckPhase(),
            ActPhase(),
            AdjustPhase()
        ]
    
    def execute(self) -> Dict[str, Dict[str, Any]]:
        """Execute the MCP prompt."""
        results = {}
        for phase in self.phases:
            try:
                phase_results = phase.execute(self.context)
                results[phase.name.lower()] = phase_results
                self.context.metadata[phase.name.lower()] = phase_results
            except Exception as e:
                logger.error(f"Error in {phase.name} phase: {str(e)}")
                raise
        return results

    def _format_results(self, results: Dict[str, Dict[str, Any]]) -> str:
        """Format validation results for display."""
        output = []
        output.append("\n=== MCP Prompt Results ===\n")

        # Discovery Phase
        output.append("Discovery Phase:")
        discovery = results.get("discovery", {})
        if "graph" in discovery:
            graph = discovery["graph"]
            if graph:
                # Count classes
                query = """
                SELECT (COUNT(DISTINCT ?class) as ?count)
                WHERE { ?class a owl:Class }
                """
                count = graph.query(query).bindings[0]["count"]
                output.append(f"Classes found: {count}")

                # Count properties
                query = """
                SELECT (COUNT(DISTINCT ?prop) as ?count)
                WHERE { ?prop a owl:ObjectProperty }
                """
                count = graph.query(query).bindings[0]["count"]
                output.append(f"Properties found: {count}")

                # Count data properties
                query = """
                SELECT (COUNT(DISTINCT ?prop) as ?count)
                WHERE { ?prop a owl:DatatypeProperty }
                """
                count = graph.query(query).bindings[0]["count"]
                output.append(f"Data properties found: {count}")

                # Count individuals
                query = """
                SELECT (COUNT(DISTINCT ?individual) as ?count)
                WHERE {
                    ?individual a ?type .
                    FILTER(?type != owl:Class && ?type != owl:Property)
                }
                """
                count = graph.query(query).bindings[0]["count"]
                output.append(f"Individuals found: {count}")

                # Count SHACL shapes
                query = """
                SELECT (COUNT(DISTINCT ?shape) as ?count)
                WHERE { ?shape a sh:NodeShape }
                """
                count = graph.query(query).bindings[0]["count"]
                output.append(f"SHACL shapes found: {count}")

                # List classes
                output.append("\nDetailed Class Information:")
                query = """
                SELECT DISTINCT ?class
                WHERE { ?class a owl:Class }
                """
                for row in graph.query(query):
                    output.append(f"  - {row[0]}")

                # List properties
                output.append("\nDetailed Property Information:")
                query = """
                SELECT DISTINCT ?prop
                WHERE { ?prop a owl:DatatypeProperty }
                """
                for row in graph.query(query):
                    output.append(f"  - {row[0]}")

                # Show validation targets
                if "validation_targets" in discovery:
                    output.append("\nValidation Targets:")
                    targets = discovery["validation_targets"]
                    for target_type, target_list in targets.items():
                        if target_list:
                            output.append(f"\n{target_type.capitalize()} Targets:")
                            for target in target_list:
                                output.append(f"  - {target['uri']}")
                                output.append(f"    Priority: {target['priority']}")
                                if target.get('errors'):
                                    output.append(f"    Issues: {', '.join(target['errors'])}")

        # File Analysis
        output.append("\nFile Analysis:\n")
        file_path = discovery.get("file_path")
        if file_path:
            output.append(f"File: {Path(file_path).name}")
            output.append(f"Exists: {Path(file_path).exists()}")
            if Path(file_path).exists():
                output.append(f"Size: {Path(file_path).stat().st_size} bytes")
                output.append(f"Last Modified: {discovery.get('last_modified', 'Unknown')}")

        # Plan Phase
        output.append("\nPlan Phase:")
        plan = results.get("plan", {})
        output.append(f"Classes to process: {plan.get('classes_to_process', 0)}")
        output.append(f"Properties to process: {plan.get('properties_to_process', 0)}")

        if "classes_to_process" in plan and plan["classes_to_process"] > 0:
            output.append("\nClasses to Process:")
            for class_uri in discovery.get("classes", []):
                output.append(f"  - {class_uri}")

        if "properties_to_process" in plan and plan["properties_to_process"] > 0:
            output.append("\nProperties to Process:")
            for prop_uri in discovery.get("properties", []):
                output.append(f"  - {prop_uri}")

        # Do Phase
        output.append("\nDo Phase:")
        do_phase = results.get("do", {})
        output.append(f"Generated files: {len(do_phase.get('files_generated', []))}")
        output.append(f"Modified files: {len(do_phase.get('files_modified', []))}")

        # Check Phase
        output.append("\nCheck Phase:")
        check = results.get("check", {})
        validation_results = check.get("validation_results", {})
        output.append(f"Validation results: {len(validation_results)}")
        if validation_results:
            output.append("\nValidation Details:")
            for rule, result in validation_results.items():
                output.append(f"  {rule}:")
                output.append(f"    Success: {result.get('success', False)}")
                if not result.get('success', False):
                    for error in result.get('errors', []):
                        output.append(f"    Error: {error}")

        output.append(f"Test results: {len(check.get('test_results', []))}")

        # Act Phase
        output.append("\nAct Phase:")
        act = results.get("act", {})
        output.append(f"Adjustments needed: {len(act.get('adjustments', []))}")
        output.append(f"Recommendations: {len(act.get('recommendations', []))}")

        # Adjust Phase
        output.append("\nAdjust Phase:")
        adjust = results.get("adjust", {})
        output.append(f"Adjustments needed: {len(adjust.get('adjustments', []))}")
        output.append(f"Recommendations: {len(adjust.get('recommendations', []))}")

        return "\n".join(output) 