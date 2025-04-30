"""BFG9K pattern for ontology validation."""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from rdflib import Graph, URIRef, Namespace, RDF, BNode, Literal
import pyshacl

@dataclass
class BFG9KValidationResult:
    """Result of a BFG9K pattern validation."""
    
    conforms: bool
    """Whether the validation passed."""
    
    violations: List[Dict[str, str]]
    """List of violations found during validation."""
    
    focus_nodes: List[URIRef]
    """List of nodes that were the focus of violations."""
    
    severity: str
    """Severity level of the violations."""
    
    message: str
    """Human-readable message describing the validation result."""

class BFG9KPhase(Enum):
    """Phases of BFG9K validation pattern."""
    INITIALIZATION = "initialization"
    EXACT_MATCH = "exact_match"
    SIMILARITY_MATCH = "similarity_match"
    LLM_SELECTION = "llm_selection"
    FINAL_VALIDATION = "final_validation"

class BFG9KPattern:
    """Implementation of the BFG9K validation pattern.
    
    The BFG9K pattern is a semantic validation approach that combines
    SHACL validation with custom semantic rules and graph patterns.
    """
    
    def __init__(self, graph: Optional[Graph] = None):
        """Initialize the BFG9K pattern.
        
        Args:
            graph: Optional graph to validate.
        """
        self.graph = graph
        self.current_phase = BFG9KPhase.INITIALIZATION
        self.validation_history: List[Dict[str, Any]] = []
        self.shacl_shapes = self._load_shacl_shapes()
        self._similarity_cache: Dict[str, float] = {}
        
    def _load_shacl_shapes(self) -> Graph:
        """Load SHACL shapes for validation."""
        shapes_graph = Graph()
        try:
            # Load core SHACL shapes from guidance.ttl
            shapes_graph.parse("guidance.ttl", format="turtle")
            
            # Add validation shapes using proper RDFLib terms
            SHACL = Namespace("http://www.w3.org/ns/shacl#")
            GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
            
            shapes_graph.bind("sh", SHACL)
            shapes_graph.bind("guidance", GUIDANCE)
            
            validation_shape = URIRef(GUIDANCE + "ValidationRuleShape")
            validation_class = URIRef(GUIDANCE + "ValidationRule")
            temporal_prop = URIRef(GUIDANCE + "hasTemporalCharacteristic")
            dependency_prop = URIRef(GUIDANCE + "hasDependency")
            
            # Add shape triples using proper RDFLib terms
            shapes_graph.add((validation_shape, RDF.type, SHACL.NodeShape))
            shapes_graph.add((validation_shape, SHACL.targetClass, validation_class))
            
            # Add property shapes
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
            
        # Phase 1: SHACL Validation
        conforms, results_graph, results_text = pyshacl.validate(
            graph,
            shacl_graph=self.shacl_shapes,
            inference='rdfs',
            abort_on_error=False
        )
        
        # Extract violations using SPARQL
        violations_query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        SELECT ?focusNode ?message ?severity
        WHERE {
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
                
                # Track highest severity
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
        """Set the graph to validate.
        
        Args:
            graph: The graph to validate.
        """
        self.graph = graph
    
    def _validate_initialization(self, data: Dict[str, Any]) -> bool:
        """Validate initialization phase."""
        required_fields = {"ontology_id", "validation_type", "security_level"}
        return all(field in data for field in required_fields)
    
    def _validate_exact_match(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate exact pattern matching."""
        # Validate against SHACL shapes
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
        # Calculate similarity score with caching
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
        
        # Pre-compute required fields for faster lookups
        required_fields = {
            "ontology_id", "validation_type", "security_level",
            "pattern_type", "pattern_elements", "constraints", "relationships"
        }
        
        # Early return if missing required fields
        if not all(field in data for field in required_fields):
            return 0.0
        
        # Use set operations for faster field presence checks
        present_fields = set(data.keys())
        matching_fields = required_fields.intersection(present_fields)
        
        # Calculate base score from field presence
        base_score = len(matching_fields) / len(required_fields)
        
        # Add type matching bonus
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
            
        # Normalize and return final score
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
        # Check SHACL validation
        conforms, _, results_graph = pyshacl.validate(
            self.graph,
            shacl_graph=self.shacl_shapes,
            inference='rdfs',
            abort_on_error=True
        )
        
        # Check required metadata
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
        return datetime.utcnow().isoformat() 