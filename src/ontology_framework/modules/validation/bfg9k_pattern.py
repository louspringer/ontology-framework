# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

"""BFG9K pattern for ontology validation."""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from rdflib import Graph, URIRef, Namespace, RDF, BNode, Literal
from rdflib.term import Node
import pyshacl  # type: ignore

@dataclass
class BFG9KValidationResult:
    """Result of a BFG9K pattern validation."""
    conforms: bool
    violations: List[Dict[str, str]]
    focus_nodes: List[URIRef]
    severity: str
    message: str

class BFG9KPhase(Enum):
    INITIALIZATION = "initialization"
    EXACT_MATCH = "exact_match"
    SIMILARITY_MATCH = "similarity_match"
    LLM_SELECTION = "llm_selection"
    FINAL_VALIDATION = "final_validation"

class BFG9KPattern:
    """Implementation of the BFG9K validation pattern."""
    def __init__(self, graph: Optional[Graph] = None):
        """Initialize the BFG9K pattern."""
        self.graph = graph
        self.current_phase = BFG9KPhase.INITIALIZATION
        self.validation_history: List[Dict[str, Any]] = []
        self.shacl_shapes = self._load_shacl_shapes()
        self._similarity_cache: Dict[str, float] = {}

    def _load_shacl_shapes(self) -> Graph:
        """Load SHACL shapes for validation."""
        shapes_graph = Graph()
        try:
            SHACL = Namespace("http://www.w3.org/ns/shacl# ")
            GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
            shapes_graph.bind("sh", SHACL)
            shapes_graph.bind("guidance", GUIDANCE)
            validation_shape = URIRef(GUIDANCE + "ValidationRuleShape")
            validation_class = URIRef(GUIDANCE + "ValidationRule")
            temporal_prop = URIRef(GUIDANCE + "hasTemporalCharacteristic")
            dependency_prop = URIRef(GUIDANCE + "hasDependency")
            shapes_graph.add((validation_shape, SHACL.targetClass, validation_class))
            temporal_shape = BNode()
            shapes_graph.add((validation_shape, SHACL.property, temporal_shape))
            shapes_graph.add((temporal_shape, SHACL.path, temporal_prop))
            shapes_graph.add((temporal_shape, SHACL.minCount, Literal(1)))
            dependency_shape = BNode()
            shapes_graph.add((validation_shape, SHACL.property, dependency_shape))
            shapes_graph.add((dependency_shape, SHACL.path, dependency_prop))
            return shapes_graph
        except Exception as e:
            raise RuntimeError(f"Failed to load SHACL shapes: {str(e)}")

    def validate(self, graph: Optional[Graph] = None) -> BFG9KValidationResult:
        """Validate a graph using the BFG9K pattern."""
        if graph is None:
            graph = self.graph
        if graph is None:
            raise ValueError("No graph provided for validation")
        conforms, results_graph, results_text = pyshacl.validate(
            graph,
            shacl_graph=self.shacl_shapes,
            inference='rdfs',
            abort_on_error=False
        )
        violations_query = """
        PREFIX sh: <http://www.w3.org/ns/shacl# >
        SELECT ?focusNode ?message ?severity WHERE {
            ?result a sh:ValidationResult ;
                    sh:focusNode ?focusNode ;
                    sh:resultMessage ?message ;
                    sh:resultSeverity ?severity .
        }
        """
        violations = []
        focus_nodes = []
        max_severity = "sh:Info"
        if not conforms:
            for row in results_graph.query(violations_query):
                violation = {
                    "focusNode": str(row.focusNode),
                    "message": str(row.message),
                    "severity": str(row.severity)
                }
                violations.append(violation)
                focus_nodes.append(row.focusNode)
                if str(row.severity) == "sh:Violation":
                    max_severity = "sh:Violation"
                elif str(row.severity) == "sh:Warning" and max_severity != "sh:Violation":
                    max_severity = "sh:Warning"
        return BFG9KValidationResult(
            conforms=conforms,
            violations=violations,
            focus_nodes=focus_nodes,
            severity=max_severity,
            message=results_text
        )

    def set_graph(self, graph: Graph) -> None:
        """Set the graph to validate."""
        self.graph = graph

    def _validate_initialization(self, data: Dict[str, Any]) -> bool:
        """Validate initialization phase."""
        required_fields = {"ontology_id", "validation_type", "security_level"}
        return all(field in data for field in required_fields)

    def _validate_exact_match(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate exact pattern matching."""
        conforms, _, results_graph = pyshacl.validate(
            self.graph,
            shacl_graph=self.shacl_shapes,
            inference='rdfs',
            abort_on_error=True
        )
        return {
            "valid": conforms,
            "results": str(results_graph),
            "timestamp": self._get_timestamp()
        }

    def _validate_similarity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pattern similarity matching with performance optimizations."""
        cache_key = str(sorted(data.items()))
        if cache_key in self._similarity_cache:
            similarity_score = self._similarity_cache[cache_key]
        else:
            similarity_score = self._calculate_similarity(data)
            self._similarity_cache[cache_key] = similarity_score
        return {
            "valid": similarity_score >= 0.85,
            "similarity_score": similarity_score,
            "timestamp": self._get_timestamp(),
            "cache_hit": cache_key in self._similarity_cache
        }

    def _calculate_similarity(self, data: Dict[str, Any]) -> float:
        """Calculate similarity score for pattern matching with optimized performance."""
        if not isinstance(data, dict):
            return 0.0
        required_fields = {
            "ontology_id", "validation_type", "security_level",
            "pattern_type", "pattern_elements", "constraints", "relationships"
        }
        if not all(field in data for field in required_fields):
            return 0.0
        present_fields = set(data.keys())
        matching_fields = required_fields.intersection(present_fields)
        base_score = len(matching_fields) / len(required_fields)
        type_bonus = 0.0
        for field in matching_fields:
            value = data[field]
            if field in ["pattern_elements", "relationships"]:
                if isinstance(value, list):
                    type_bonus += 0.1
            elif field == "constraints":
                if isinstance(value, dict):
                    type_bonus += 0.1
            elif isinstance(value, str):
                type_bonus += 0.1
        return min(1.0, base_score + (type_bonus / len(required_fields)))

    def _validate_llm_selection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LLM selection criteria."""
        required_llm_fields = {"model_type", "temperature", "max_tokens"}
        is_valid = all(field in data.get("llm_config", {}) for field in required_llm_fields)
        return {
            "valid": is_valid,
            "timestamp": self._get_timestamp()
        }

    def _validate_final(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform final validation checks."""
        conforms, _, results_graph = pyshacl.validate(
            self.graph,
            shacl_graph=self.shacl_shapes,
            inference='rdfs',
            abort_on_error=True
        )
        required_metadata = {
            "ontology_id": str,
            "validation_type": str,
            "security_level": str,
            "pattern_type": str,
            "pattern_elements": list,
            "constraints": dict,
            "relationships": list
        }
        metadata_valid = all(
            isinstance(data.get(key), expected_type)
            for key, expected_type in required_metadata.items()
        )
        return {
            "valid": conforms and metadata_valid,
            "shacl_conforms": conforms,
            "metadata_valid": metadata_valid,
            "timestamp": self._get_timestamp()
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat() 