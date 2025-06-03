from typing import Dict, Any, List, Set, Optional, Union, Sequence, Tuple, cast
from rdflib import Graph, URIRef, Literal, RDF, Namespace, Variable, BNode
from rdflib.namespace import RDF, RDFS, XSD, SH, OWL
from rdflib.query import ResultRow, Result
import pyshacl
from enum import Enum
import uuid
from datetime import datetime
import re
import os
import logging
from ontology_framework.validation.validation_rule_type import ValidationRuleType
from ontology_framework.validation.error_severity import ErrorSeverity
from ontology_framework.tools.validation_ontology_manager import ValidationOntologyManager
from ontology_framework.tools.guidance_manager import GuidanceManager
from ontology_framework.validation.pattern_manager import PatternManager
from pyshacl import validate
from .validation_rule import ValidationRule
from .conformance_level import ConformanceLevel
from ..ontology_types import (
    ValidationRule as OntologyValidationRule,
    ErrorSeverity as OntologyErrorSeverity
)
from rdflib.term import Node

# Define namespaces
GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
EX = Namespace('http://example.org/')

class ValidationRuleType(Enum):
    """Validation rule types from the guidance ontology."""
    SHACL = GUIDANCE.SHACL
    SEMANTIC = GUIDANCE.SEMANTIC
    SYNTAX = GUIDANCE.SYNTAX
    STRUCTURAL = GUIDANCE.STRUCTURAL

class ValidationHandler:
    """Handles validation operations using the validation ontology."""
    
    def __init__(self, base_url: str = "http://localhost:7200", repository: str = "validation"):
        self.manager = ValidationOntologyManager(base_url, repository)
        self.logger = logging.getLogger(__name__)
        
    def add_validation_rule(self, rule: ValidationRule, description: str, severity: ErrorSeverity) -> URIRef:
        """Add a validation rule to the ontology."""
        try:
            return self.manager.add_validation_rule(
                rule.name,
                description,
                severity.name
            )
        except Exception as e:
            self.logger.error(f"Failed to add validation rule: {e}")
            raise
            
    def get_validation_rules(self) -> List[Dict[str, Union[str, Optional[str]]]]:
        """Get all validation rules from the ontology."""
        try:
            return self.manager.get_validation_rules()
        except Exception as e:
            self.logger.error(f"Failed to get validation rules: {e}")
            return []
            
    def validate_rule_exists(self, rule: ValidationRule) -> bool:
        """Check if a validation rule exists in the ontology."""
        try:
            return self.manager.validate_rule_exists(rule.name)
        except Exception as e:
            self.logger.error(f"Failed to validate rule existence: {e}")
            return False

    def __init__(self, rules: Optional[List[ValidationRule]] = None):
        """Initialize the validation handler with optional rules.
        
        Args:
            rules: Optional list of validation rules to use
        """
        self.logger = logging.getLogger(__name__)
        self.rules: Dict[ValidationRuleType, List[ValidationRule]] = {}
        self.validation_manager = ValidationOntologyManager()
        self.pattern_manager = PatternManager()
        self.guidance_manager = GuidanceManager()
        self.shacl_shapes = Graph()
        
        # Bind namespaces
        self.shacl_shapes.bind('sh', SH)
        self.shacl_shapes.bind('xsd', XSD)
        self.shacl_shapes.bind('guidance', GUIDANCE)
        
        # Load validation rules from guidance ontology
        self._load_validation_rules()
        self._load_shacl_templates()
        
        self._initialize_rules(rules or [])
        
    def _initialize_rules(self, rules: List[ValidationRule]) -> None:
        """Initialize the rules dictionary with the provided rules.
        
        Args:
            rules: List of validation rules to initialize
        """
        for rule in rules:
            if rule.rule_type not in self.rules:
                self.rules[rule.rule_type] = []
            self.rules[rule.rule_type].append(rule)
        
    def _load_validation_rules(self):
        """Load validation rules from the guidance ontology using GuidanceManager."""
        try:
            rules = self.guidance_manager.get_validation_rules()
            for rule in rules:
                rule_id = str(rule['rule']).split('#')[-1]
                try:
                    rule_type = ValidationRuleType[rule.get('type', 'SEMANTIC')]
                    if rule_type not in self.rules:
                        self.rules[rule_type] = []
                    self.rules[rule_type].append(ValidationRule(rule_id, rule))
                except (KeyError, ValueError) as e:
                    logging.warning(f"Failed to load rule {rule_id}: {str(e)}")
        except Exception as e:
            logging.error(f"Failed to load validation rules: {str(e)}")

    def _create_shacl_shape(self, shape_id: str, target_class: URIRef) -> BNode:
        """Create a new SHACL shape with basic structure."""
        shape = BNode()
        self.shacl_shapes.add((shape, RDF.type, SH.NodeShape))
        self.shacl_shapes.add((shape, SH.targetClass, target_class))
        return shape

    def _add_property_constraint(self, shape: Node, path: URIRef, constraint_type: URIRef, value: Any):
        """Add a property constraint to a SHACL shape."""
        prop = BNode()
        self.shacl_shapes.add((shape, SH.property, prop))
        self.shacl_shapes.add((prop, SH.path, path))
        self.shacl_shapes.add((prop, constraint_type, value))

    def _load_shacl_templates(self):
        """Load SHACL templates into the shapes graph."""
        # Clear existing templates
        self.shacl_shapes = Graph()
        self.shacl_shapes.bind('sh', SH)
        self.shacl_shapes.bind('xsd', XSD)
        
        # Create base validation shapes
        class_shape = self._create_shacl_shape('ClassShape', RDFS.Class)
        self._add_property_constraint(class_shape, RDFS.label, SH.minCount, Literal(1))
        self._add_property_constraint(class_shape, RDFS.comment, SH.minCount, Literal(1))
        
        property_shape = self._create_shacl_shape('PropertyShape', RDF.Property)
        self._add_property_constraint(property_shape, RDFS.domain, SH.minCount, Literal(1))
        self._add_property_constraint(property_shape, RDFS.range, SH.minCount, Literal(1))

    def register_rule(
        self,
        rule_id: str,
        rule: Dict[str, Any],
        rule_type: Optional[ValidationRuleType] = None,
        message: Optional[str] = None,
        priority: int = 0,
        dependencies: Optional[List[str]] = None,
        conformance_level: Optional[ConformanceLevel] = None,
        **kwargs
    ) -> str:
        """Register a validation rule.
        
        Args:
            rule_id: Unique identifier for the rule
            rule: Rule definition dictionary
            rule_type: Type of validation rule
            message: Optional error message
            priority: Priority of the rule (higher numbers = higher priority)
            dependencies: Optional list of rule IDs this rule depends on
            conformance_level: Optional conformance level for the rule
            **kwargs: Additional rule parameters
            
        Returns:
            str: The rule ID
        """
        if conformance_level is not None:
            rule["conformance_level"] = conformance_level.value
        if rule_type is not None:
            rule["type"] = rule_type.value
        if message is not None:
            rule["message"] = message
        rule["priority"] = priority
        if dependencies is not None:
            rule["dependencies"] = dependencies
        self.rules[rule_id] = rule
        return rule_id
        
    def _validate_dependencies(self, rule_id: str) -> None:
        """Validate rule dependencies to detect cycles.
        
        Args:
            rule_id: ID of the rule to validate
            
        Raises:
            ValueError: If circular dependency detected or missing dependency
        """
        visited: set = set()
        path: list = []
        
        def visit(rid: str) -> None:
            if rid in path:
                cycle = path[path.index(rid):] + [rid]
                raise ValueError(f"Circular dependency detected: {' -> '.join(cycle)}")
                
            if rid in visited:
                return
            if rid not in self.rules:
                raise ValueError(f"Missing dependency: {rid}")
                
            visited.add(rid)
            path.append(rid)
            
            for dep in self.rules[rid]["dependencies"]:
                if dep not in self.rules:
                    raise ValueError(f"Missing dependency: {dep}")
                visit(dep)
                
            path.pop()
            
        visit(rule_id)

    def execute_rule(self, rule_id: str, graph: Graph) -> Dict[str, Any]:
        """Execute a single validation rule.
        
        Args:
            rule_id: ID of the rule to execute
            graph: RDF graph to validate
            
        Returns:
            Dictionary containing validation results
            
        Raises:
            ValueError: If rule_id is not found
        """
        if rule_id not in self.rules:
            raise ValueError(f"Rule {rule_id} not found")
            
        rule = self.rules[rule_id]
        rule_type = rule["type"]
        
        results = []
        
        if rule_type == ValidationRuleType.SHACL:
            results = self._execute_shacl_rule(rule_id, rule, graph)
        elif rule_type == ValidationRuleType.SEMANTIC:
            results = self._execute_semantic_rule(rule_id, rule, graph)
        elif rule_type == ValidationRuleType.SYNTAX:
            results = self._execute_syntax_rule(rule_id, rule, graph)
        elif rule_type == ValidationRuleType.PATTERN:
            results = self._execute_pattern_rule(rule_id, rule, graph)
        elif rule_type == ValidationRuleType.SENSITIVE_DATA:
            results = self._execute_sensitive_data_rule(rule_id, rule, graph)
        elif rule_type == ValidationRuleType.INDIVIDUAL_TYPE:
            results = self._execute_individual_type_rule(rule_id, rule, graph)
        else:
            raise ValueError(f"Unsupported rule type: {rule_type}")
            
        return {
            "rule_id": rule_id,
            "type": rule_type.value,
            "results": results,
            "message": rule.get("message", "Validation failed"),
            "is_valid": len(results) == 0
        }

    def _execute_pattern_rule(self, rule_id: str, rule: Dict[str, Any], graph: Graph) -> List[Dict[str, Any]]:
        """Execute a pattern validation rule.
        
        Args:
            rule_id: ID of the rule
            rule: Rule configuration
            graph: Graph to validate
            
        Returns:
            List of validation results
        """
        results = []
        pattern = rule.get("pattern")
        if not pattern:
            raise ValueError("Pattern rule must specify a pattern")
        for s, p, o in graph:
            if isinstance(o, Literal):
                logging.debug(f"Pattern check: {s} {p} {o}")
                if re.search(pattern, str(o)):
                    results.append({
                        "rule_id": rule_id,
                        "message": rule.get("message", "Pattern validation failed"),
                        "subject": str(s),
                        "predicate": str(p),
                        "object": str(o),
                        "severity": ErrorSeverity.ERROR.value
                    })
        return results

    def _execute_sensitive_data_rule(self, rule_id: str, rule: Dict[str, Any], graph: Graph) -> List[Dict[str, Any]]:
        """Execute a sensitive data validation rule.
        
        Args:
            rule_id: ID of the rule
            rule: Rule configuration
            graph: RDF graph to validate
            
        Returns:
            List of validation results
        """
        results = []
        patterns = []
        
        # Get patterns from rule configuration
        if "patterns" in rule:
            patterns.extend(rule["patterns"])
        elif "pattern" in rule:
            patterns.append(rule["pattern"])
            
        # Get patterns from guidance ontology if none specified
        if not patterns:
            guidance_patterns = self.guidance_manager.get_validation_patterns()
            for pattern_info in guidance_patterns:
                if pattern_info.get("type") == "SENSITIVE_DATA":
                    patterns.append(pattern_info["pattern"])
                    
        if not patterns:
            self.logger.warning(f"No patterns found for sensitive data rule {rule_id}")
            return results
            
        for pattern in patterns:
            try:
                for s, p, o in graph:
                    if isinstance(o, Literal) and re.search(pattern, str(o)):
                        results.append({
                            "rule_id": rule_id,
                            "message": rule.get("message", "Sensitive data found"),
                            "subject": str(s),
                            "predicate": str(p),
                            "object": str(o),
                            "pattern": pattern,
                            "severity": ErrorSeverity.ERROR.value
                        })
            except re.error as e:
                self.logger.error(f"Invalid regex pattern in rule {rule_id}: {e}")
                
        return results

    def _execute_individual_type_rule(self, rule_id: str, rule: Dict[str, Any], graph: Graph) -> List[Dict[str, Any]]:
        """Execute an individual type validation rule.
        
        Args:
            rule_id: ID of the rule
            rule: Rule configuration
            graph: Graph to validate
            
        Returns:
            List of validation results
        """
        results = []
        class_uri = rule.get("class_uri")
        property_types = rule.get("property_types", {})
        
        if not class_uri:
            raise ValueError("Individual type rule must specify class_uri")
            
        for s in graph.subjects(RDF.type, URIRef(class_uri)):
            for p, expected_type in property_types.items():
                for o in graph.objects(s, URIRef(p)):
                    if isinstance(o, Literal) and o.datatype != URIRef(expected_type):
                        results.append({
                            "rule_id": rule_id,
                            "message": rule.get("message", f"Invalid datatype for property {p}"),
                            "subject": str(s),
                            "predicate": str(p),
                            "object": str(o),
                            "expected_type": expected_type,
                            "actual_type": str(o.datatype)
                        })
                        
        return results

    def validate_graph(self, graph: Graph, conformance_level: Optional[ConformanceLevel] = None) -> Dict[str, Any]:
        """Validate a graph against all registered rules.
        
        Args:
            graph: RDF graph to validate
            conformance_level: Optional conformance level for filtering rules
            
        Returns:
            Dictionary containing validation results
        """
        results = []
        
        # Sort rules by priority
        sorted_rules = sorted(
            self.rules.items(),
            key=lambda x: x[1][0].priority
        )
        
        # Execute rules in priority order
        for rule_type, rules in sorted_rules:
            try:
                self._validate_dependencies(rules[0].rule_id)
                for rule in rules:
                    if conformance_level and ConformanceLevel(rule.conformance_level).value > conformance_level.value:
                        continue
                    result = self.execute_rule(rule.rule_id, graph)
                    if not result["is_valid"]:
                        results.extend(result["results"])
            except ValueError as e:
                logging.error(f"Error executing rule {rule.rule_id}: {str(e)}")
                raise  # Re-raise so tests can catch
            except Exception as e:
                logging.error(f"Error executing rule {rule.rule_id}: {str(e)}")
                results.append({
                    "rule_id": rule.rule_id,
                    "message": f"Rule execution failed: {str(e)}",
                    "error": str(e)
                })
                
        return {
            "valid": len(results) == 0,
            "results": results
        }

    def _execute_shacl_rule(self, rule_id: str, rule: Dict[str, Any], graph: Graph) -> List[Dict[str, Any]]:
        """Execute a SHACL validation rule.
        
        Args:
            rule_id: ID of the rule
            rule: Rule configuration
            graph: RDF graph to validate
            
        Returns:
            List of validation results
        """
        try:
            conforms, results_graph, results_text = validate(
                graph,
                shacl_graph=self.shacl_shapes,
                ont_graph=None,
                inference='rdfs',
                abort_on_first=False,
                allow_infos=False,
                allow_warnings=False,
                meta_shacl=False,
                debug=False
            )
            
            if not conforms:
                return [{
                    "rule_id": rule_id,
                    "message": rule.get("message", "SHACL validation failed"),
                    "details": str(results_text)
                }]
            return []
        except Exception as e:
            logging.error(f"SHACL validation error: {str(e)}")
            return [{
                "rule_id": rule_id,
                "message": f"SHACL validation error: {str(e)}"
            }]

    def _execute_semantic_rule(self, rule_id: str, rule: Dict[str, Any], graph: Graph) -> List[Dict[str, Any]]:
        """Execute a semantic validation rule using SPARQL queries.
        
        Args:
            rule_id: ID of the rule
            rule: Rule configuration
            graph: RDF graph to validate
            
        Returns:
            List of validation results
        """
        try:
            query = rule.get("query")
            if not query:
                if rule.get("class_uri"):
                    class_uri = rule["class_uri"]
                    property_types = rule.get("property_types", {})
                    property_clauses: list = []
                    filter_clauses: list = []
                    for prop, expected_type in property_types.items():
                        var_name = f"o{len(property_clauses)}"
                        property_clauses.append(f"OPTIONAL {{ ?s <{prop}> ?{var_name} }}")
                        filter_clauses.append(
                            f"(bound(?{var_name}) && datatype(?{var_name}) != <{expected_type}>)"
                        )
                    query = f"""
                        SELECT ?s ?p ?o WHERE {{
                            ?s a <{class_uri}> .
                            ?s ?p ?o .
                            {' '.join(property_clauses)}
                            FILTER({' || '.join(filter_clauses)})
                        }}
                    """
                else:
                    raise ValueError("No query defined for rule")
            
            results = []
            query_results = cast(Result, graph.query(query))
            
            for row in query_results:
                if isinstance(row, ResultRow):
                    # Handle named results
                    subject = str(row['s']) if 's' in row.labels else ''
                    predicate = str(row['p']) if 'p' in row.labels else ''
                    obj = str(row['o']) if 'o' in row.labels else ''
                else:
                    # Handle tuple results safely
                    row_tuple = cast(Tuple[Node, ...], row)
                    subject = str(row_tuple[0]) if len(row_tuple) > 0 else ''
                    predicate = str(row_tuple[1]) if len(row_tuple) > 1 else ''
                    obj = str(row_tuple[2]) if len(row_tuple) > 2 else ''
                
                results.append({
                    "rule_id": rule_id,
                    "message": rule.get("message", f"Invalid property type for {predicate}"),
                    "subject": subject,
                    "predicate": predicate,
                    "object": obj
                })
            
            return results
            
        except Exception as e:
            return [{
                "rule_id": rule_id,
                "severity": ErrorSeverity.ERROR,
                "message": f"Error executing semantic rule: {str(e)}"
            }]

    def _execute_syntax_rule(self, rule_id: str, rule: Dict[str, Any], graph: Graph) -> List[Dict[str, Any]]:
        """Execute a syntax validation rule using SHACL.
        
        Args:
            rule_id: ID of the rule
            rule: Rule configuration
            graph: RDF graph to validate
            
        Returns:
            List of validation results
        """
        try:
            pattern = rule.get("pattern")
            if not pattern:
                raise ValueError("Syntax rule must contain a pattern")

            # Create SHACL shapes graph for syntax validation
            shapes = Graph()
            shapes.bind('sh', SH)
            shapes.bind('ex', EX)
            
            # Create shape using template
            shape_text = f"""
                @prefix sh: <http://www.w3.org/ns/shacl#> .
                @prefix ex: <http://example.org/> .
                
                ex:SyntaxShape a sh:NodeShape ;
                    {self.SHACL_TEMPLATES["syntax"].format(
                        path="?p",
                        pattern=f'"{pattern}"',
                        message="Value does not match required syntax"
                    )} .
            """
            shapes.parse(data=shape_text, format='turtle')

            # Validate using pyshacl
            conforms, results_graph, results_text = pyshacl.validate(
                graph,
                shacl_graph=shapes,
                inference='rdfs',
                abort_on_first=False
            )

            return self._process_shacl_results(results_graph)

        except Exception as e:
            return [{
                "severity": ErrorSeverity.CRITICAL,
                "message": f"Syntax validation error: {str(e)}"
            }]

    def _process_shacl_results(self, results_graph: Graph) -> List[Dict[str, Any]]:
        """Process SHACL validation results into a standardized format.
        
        Args:
            results_graph: Graph containing SHACL validation results
            
        Returns:
            List of processed validation results
        """
        results = []
        for result in results_graph.subjects(RDF.type, SH.ValidationResult):
            severity = results_graph.value(result, SH.resultSeverity)
            message = results_graph.value(result, SH.resultMessage)
            
            results.append({
                "severity": self._map_shacl_severity(severity),
                "message": str(message)
            })
            
        return results

    def _map_shacl_severity(self, severity: Any) -> ErrorSeverity:
        """Map SHACL severity to framework ErrorSeverity.
        
        Args:
            severity: SHACL severity value
            
        Returns:
            Mapped ErrorSeverity value
        """
        severity_map = {
            str(SH.Violation): ErrorSeverity.CRITICAL,
            str(SH.Warning): ErrorSeverity.MEDIUM,
            str(SH.Info): ErrorSeverity.LOW
        }
        return severity_map.get(str(severity), ErrorSeverity.HIGH)

    def validate(self, graph: Graph, rule_types: Optional[Set[ValidationRuleType]] = None) -> Dict[str, Union[bool, List[str]]]:
        """Validate a graph using the specified rule types.
        
        Args:
            graph: The RDF graph to validate
            rule_types: Optional set of rule types to use for validation
            
        Returns:
            Dictionary containing validation results and messages
        """
        results = {
            "valid": True,
            "messages": []
        }
        
        # If no rule types specified, use all available
        if not rule_types:
            rule_types = set(self.rules.keys())
            
        for rule_type in rule_types:
            if rule_type not in self.rules:
                self.logger.warning(f"No rules found for type {rule_type}")
                continue
            for rule in self.rules[rule_type]:
                try:
                    rule_result = rule.validate(graph)
                    if not rule_result["valid"]:
                        results["valid"] = False
                        results["messages"].extend(rule_result["messages"])
                except Exception as e:
                    self.logger.error(f"Error validating with rule {rule}: {str(e)}")
                    results["valid"] = False
                    results["messages"].append(f"Error validating with rule {rule}: {str(e)}")
                    
        return results

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a new validation rule.
        
        Args:
            rule: The validation rule to add
        """
        if rule.rule_type not in self.rules:
            self.rules[rule.rule_type] = []
        self.rules[rule.rule_type].append(rule)
        
    def remove_rule(self, rule: ValidationRule) -> None:
        """Remove a validation rule.
        
        Args:
            rule: The validation rule to remove
        """
        if rule.rule_type in self.rules:
            self.rules[rule.rule_type] = [r for r in self.rules[rule.rule_type] if r != rule]
            
    def get_rules(self, rule_type: Optional[ValidationRuleType] = None) -> List[ValidationRule]:
        """Get all rules or rules of a specific type.
        
        Args:
            rule_type: Optional rule type to filter by
            
        Returns:
            List of validation rules
        """
        if rule_type:
            return self.rules.get(rule_type, [])
        return [rule for rules in self.rules.values() for rule in rules]

    def validate_ontology(self, ontology_graph: Graph, conformance_level: ConformanceLevel = ConformanceLevel.STRICT) -> Tuple[bool, str, Graph]:
        """
        Validate an ontology graph using SHACL shapes and custom rules.
        
        Args:
            ontology_graph: The RDF graph to validate
            conformance_level: The validation conformance level
            
        Returns:
            Tuple of (is_valid, validation_report_text, validation_report_graph)
        """
        try:
            # Combine ontology with shapes graph
            validation_graph = Graph()
            validation_graph += ontology_graph
            validation_graph += self.shacl_shapes
            
            # Run SHACL validation
            is_valid, validation_graph, validation_text = pyshacl.validate(
                validation_graph,
                shacl_graph=self.shacl_shapes,
                ont_graph=None,
                inference='rdfs',
                abort_on_first=False,
                meta_shacl=True,
                debug=False
            )
            
            # Apply custom validation rules based on conformance level
            if conformance_level == ConformanceLevel.STRICT:
                custom_results = self._apply_custom_rules(ontology_graph)
                if custom_results:
                    is_valid = False
                    validation_text += "\n\nCustom Validation Results:\n" + "\n".join(custom_results)
            
            return is_valid, validation_text, validation_graph
        except Exception as e:
            error_msg = f"Validation failed with error: {str(e)}"
            logging.error(error_msg)
            return False, error_msg, Graph()
    
    def _apply_custom_rules(self, graph: Graph) -> List[str]:
        """Apply custom validation rules to the graph."""
        validation_results = []
        
        try:
            for rule_id, rules in self.rules.items():
                if rule_id == ValidationRuleType.SEMANTIC:
                    # Apply semantic validation rules
                    for rule in rules:
                        query = self.pattern_manager.get_validation_pattern(rule.rule_id)
                        if query:
                            results = graph.query(query)
                            if results and len(results) > 0:
                                validation_results.append(f"Rule {rule.rule_id}: {rule.message}")
                            
                elif rule_id == ValidationRuleType.STRUCTURAL:
                    # Apply structural validation rules
                    for rule in rules:
                        shape = self._create_rule_shape(rule.rule_id, rule)
                        if shape:
                            temp_graph = Graph()
                            temp_graph += graph
                            temp_graph += shape
                            is_valid, _, report = pyshacl.validate(
                                temp_graph,
                                shacl_graph=shape,
                                inference='rdfs'
                            )
                            
                            if not is_valid:
                                validation_results.append(f"Rule {rule.rule_id}: {rule.message}")
                            
        except Exception as e:
            logging.error(f"Error applying custom rules: {str(e)}")
            validation_results.append(f"Custom validation error: {str(e)}")
            
        return validation_results
    
    def _create_rule_shape(self, rule_id: str, rule: ValidationRule) -> Optional[Graph]:
        """Create a SHACL shape graph for a validation rule.
        
        Args:
            rule_id: ID of the rule
            rule: The validation rule
            
        Returns:
            Optional Graph containing SHACL shapes
        """
        try:
            shape_graph = Graph()
            shape_graph.bind('sh', SH)
            shape_graph.bind('ex', EX)
            
            # Create basic shape
            shape = BNode()
            shape_graph.add((shape, RDF.type, SH.NodeShape))
            
            # Add rule-specific constraints
            if hasattr(rule, 'pattern') and rule.pattern:
                # Add pattern constraint
                prop = BNode()
                shape_graph.add((shape, SH.property, prop))
                shape_graph.add((prop, SH.path, RDFS.label))  # Default to rdfs:label
                shape_graph.add((prop, SH.pattern, Literal(rule.pattern)))
                shape_graph.add((prop, SH.message, Literal(rule.message or f"Pattern validation failed: {rule.pattern}")))
            
            return shape_graph
        except Exception as e:
            logging.error(f"Error creating rule shape for {rule_id}: {str(e)}")
            return None
            
    def get_shacl_rules(self) -> Graph:
        """Get all SHACL rules as a combined graph.
        
        Returns:
            Graph containing all SHACL shapes
        """
        return self.shacl_shapes
