from typing import Dict, Any, List, Set, Optional, Union, Sequence, Tuple, cast
from rdflib import Graph, URIRef, Literal, RDF, Namespace, Node, Variable
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.query import ResultRow, Result
import pyshacl
from ontology_framework.validation.validation_rule_type import ValidationRuleType
from ontology_framework.validation.error_severity import ErrorSeverity
from ontology_framework.tools.validation_ontology_manager import ValidationOntologyManager
from ontology_framework.tools.guidance_manager import GuidanceManager
from ontology_framework.validation.pattern_manager import PatternManager
import uuid
from datetime import datetime
import re
import os
import logging
from enum import Enum
from pyshacl import validate

# Define namespaces
SH = Namespace('http://www.w3.org/ns/shacl#')
EX = Namespace('http://example.org/')
GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')

class ConformanceLevel(Enum):
    """Validation conformance levels."""
    STRICT = "strict"
    MODERATE = "moderate"
    BASIC = "basic"

class ValidationTarget(Enum):
    """Validation targets."""
    CLASS_HIERARCHY = "class_hierarchy"
    PROPERTY_CONSTRAINTS = "property_constraints"
    DATA_INTEGRITY = "data_integrity"

class ValidationHandler:
    # SHACL shape templates for common validations
    SHACL_TEMPLATES = {
        "identifier": """
            sh:property [
                sh:path {path} ;
                sh:pattern "^[A-Za-z0-9_-]+$" ;
                sh:minCount 1 ;
                sh:maxCount 1 ;
                sh:message "Invalid identifier format - must contain only letters, numbers, underscores, and hyphens" ;
            ]
        """,
        "enum": """
            sh:property [
                sh:path {path} ;
                sh:in ({values}) ;
                sh:minCount 1 ;
                sh:maxCount 1 ;
                sh:message "Value must be one of: {values}" ;
            ]
        """,
        "required_string": """
            sh:property [
                sh:path {path} ;
                sh:datatype xsd:string ;
                sh:minCount 1 ;
                sh:maxCount 1 ;
                sh:message "Required string field is missing or invalid" ;
            ]
        """,
        "sensitive_data": """
            sh:property [
                sh:path {path} ;
                sh:pattern {pattern} ;
                sh:message "Sensitive data pattern detected: {message}" ;
            ]
        """,
        "syntax": """
            sh:property [
                sh:path {path} ;
                sh:nodeKind sh:Literal ;
                sh:pattern {pattern} ;
                sh:message "Syntax validation failed: {message}" ;
            ]
        """
    }

    def __init__(self, graphdb_connection=None):
        self.rules: Dict[str, Dict[str, Any]] = {}
        self.validation_manager = ValidationOntologyManager()
        self.pattern_manager = PatternManager()
        self.guidance_manager = GuidanceManager()
        self.graphdb_connection = graphdb_connection
        self.shacl_shapes = Graph()
        
        # Load validation rules from guidance ontology
        self._load_validation_rules()
        self._load_shacl_templates()
        
    def _load_validation_rules(self):
        """Load validation rules from the guidance ontology using GuidanceManager."""
        rules = self.guidance_manager.get_validation_rules()
        for rule in rules:
            rule_id = rule['rule'].split('#')[-1]
            self.rules[rule_id] = {
                'type': ValidationRuleType[rule['type']],
                'message': rule['message'],
                'priority': int(rule['priority'])
            }
            
    def register_rule(
        self,
        rule_id: str,
        rule: Dict[str, Any],
        rule_type: Optional[ValidationRuleType] = None,
        message: Optional[str] = None,
        priority: int = 0,
        dependencies: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """Register a validation rule.
        
        Args:
            rule_id: Unique identifier for the rule.
            rule: Rule configuration dictionary.
            rule_type: Optional type of validation rule. If not provided, will be extracted from rule dict.
            message: Optional message to display for violations.
            priority: Rule execution priority (lower executes first).
            dependencies: List of rule IDs this rule depends on.
            **kwargs: Additional keyword arguments for backward compatibility.
            
        Returns:
            The registered rule ID.
            
        Raises:
            ValueError: If rule type is invalid or required parameters missing.
        """
        # Handle rule type from different sources
        if rule_type is None:
            # Try to get from rule dict first
            if "type" in rule:
                rule_type = rule["type"]
            # Then try kwargs for backward compatibility
            elif "type" in kwargs:
                rule_type = kwargs["type"]
            else:
                raise ValueError("Rule type must be provided either as argument or in rule dictionary")

        # Ensure rule_type is ValidationRuleType
        if not isinstance(rule_type, ValidationRuleType):
            try:
                rule_type = ValidationRuleType(rule_type)
            except (ValueError, TypeError):
                try:
                    rule_type = ValidationRuleType.from_string(str(rule_type))
                except ValueError:
                    raise ValueError(f"Invalid rule type: {rule_type}")

        # Get message from rule if not provided
        if not message and "message" in rule:
            message = rule["message"]

        # Get priority from rule if not provided
        if not priority and "priority" in rule:
            priority = rule["priority"]

        # Get dependencies from rule if not provided
        if not dependencies and "dependencies" in rule:
            dependencies = rule["dependencies"]

        # For non-SHACL rules that require a message, generate a default if none provided
        if not message and rule_type != ValidationRuleType.SHACL:
            message = f"Validation failed for rule {rule_id}"

        rule_uri = self.guidance_manager.add_validation_rule(
            rule_id=rule_id,
            rule=rule,
            type=rule_type.value,
            message=message,
            priority=priority
        )
        
        # Flatten the rule dict into self.rules[rule_id]
        flat_rule = dict(rule)  # copy
        flat_rule.update({
            "type": rule_type,
            "message": message,
            "priority": priority,
            "dependencies": dependencies or []
        })
        self.rules[rule_id] = flat_rule
        
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
            
            for dep in self.rules[rid].get("dependencies", []):
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
        patterns = rule.get("patterns", [])
        if isinstance(patterns, str):
            patterns = [patterns]
        elif not patterns:
            raise ValueError("Sensitive data rule must specify pattern(s)")
        for pattern in patterns:
            for s, p, o in graph:
                if isinstance(o, Literal) and re.search(pattern, str(o)):
                    results.append({
                        "rule_id": rule_id,
                        "message": rule.get("message", "Sensitive data found"),
                        "subject": str(s),
                        "predicate": str(p),
                        "object": str(o),
                        "severity": ErrorSeverity.ERROR.value
                    })
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
            key=lambda x: x[1].get("priority", 0)
        )
        
        # Execute rules in priority order
        for rule_id, _ in sorted_rules:
            try:
                self._validate_dependencies(rule_id)
                rule = self.rules[rule_id]
                if conformance_level and ConformanceLevel(rule["conformance_level"]).value > conformance_level.value:
                    continue
                result = self.execute_rule(rule_id, graph)
                if not result["is_valid"]:
                    results.extend(result["results"])
            except ValueError as e:
                logging.error(f"Error executing rule {rule_id}: {str(e)}")
                raise  # Re-raise so tests can catch
            except Exception as e:
                logging.error(f"Error executing rule {rule_id}: {str(e)}")
                results.append({
                    "rule_id": rule_id,
                    "message": f"Rule execution failed: {str(e)}",
                    "error": str(e)
                })
                
        return {
            "is_valid": len(results) == 0,
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
                        SELECT ?s ?p ?o
                        WHERE {{
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
                
                ex:SyntaxShape
                    a sh:NodeShape ;
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

    def validate(self, rule_type: ValidationRuleType, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against a rule type using SHACL."""
        if rule_type not in self.rules:
            raise ValueError(f"Unsupported rule type: {rule_type}")

        # Convert data to RDF graph
        data_graph = self._data_to_graph(data)
        
        # Get shapes graph for rule type
        shapes_graph = self.rules[rule_type]["shapes_graph"]
        
        # Validate using SHACL
        conforms, results_graph, results_text = pyshacl.validate(
            data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs',
            abort_on_first=False
        )
        
        return {
            "is_valid": conforms,
            "results": self._process_shacl_results(results_graph) if not conforms else []
        }

    def validate_shacl(self, data_graph: Graph, shapes_graph: Graph) -> Dict[str, Any]:
        """Validate data against SHACL shapes.
        
        Args:
            data_graph: RDF graph containing data to validate
            shapes_graph: RDF graph containing SHACL shapes
            
        Returns:
            Dictionary containing validation results:
                - conforms: bool indicating if validation passed
                - results: list of validation messages
        """
        try:
            conforms, results_graph, results_text = pyshacl.validate(
                data_graph,
                shacl_graph=shapes_graph,
                inference='rdfs',
                abort_on_first=False,
                allow_infos=True,
                allow_warnings=True
            )
            
            return {
                'conforms': conforms,
                'results': self._process_shacl_results(results_graph) if not conforms else []
            }
            
        except Exception as e:
            return {
                'conforms': False,
                'results': [{
                    'severity': ErrorSeverity.ERROR,
                    'message': f'SHACL validation failed: {str(e)}'
                }]
            }

    def add_rule(
        self,
        rule_type: ValidationRuleType,
        priority: int = 999,
        depends_on: Optional[List[ValidationRuleType]] = None
    ) -> None:
        """Add a validation rule.
        
        Args:
            rule_type: Type of validation rule
            priority: Rule priority (lower is higher priority)
            depends_on: Optional list of rule types this rule depends on. Defaults to None.
        """
        rule_id = f"{str(rule_type).lower()}_{str(uuid.uuid4())}"
        rule = {
            "type": rule_type,
            "priority": priority
        }
        
        if depends_on is not None:
            rule["dependencies"] = [f"{str(dep).lower()}" for dep in depends_on]
            
        self.register_rule(rule_id, rule)

    def validate_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against all registered rules.
        
        Args:
            data: Data to validate
            
        Returns:
            Dictionary containing validation results with keys:
                - is_valid: bool indicating if validation passed
                - results: list of validation results per rule
                - metadata: additional validation metadata
        """
        results = []
        is_valid = True
        
        # Sort rules by priority
        sorted_rules = sorted(self.rules.items(), key=lambda x: x[1].get("priority", 999))
        
        for rule_id, rule in sorted_rules:
            try:
                result = self.execute_rule(rule_id, self._data_to_graph(data))
                results.append({
                    "rule_id": rule_id,
                    **result
                })
                if not result["is_valid"]:
                    is_valid = False
            except Exception as e:
                results.append({
                    "rule_id": rule_id,
                    "is_valid": False,
                    "results": [{
                        "severity": ErrorSeverity.CRITICAL,
                        "message": f"Error executing rule {rule_id}: {str(e)}"
                    }]
                })
                is_valid = False
                
        return {
            "is_valid": is_valid,
            "results": results,
            "metadata": {
                "timestamp": str(datetime.now()),
                "rule": "ALL",
                "total_rules": len(sorted_rules)
            }
        }

    def _data_to_graph(self, data: Dict[str, Any]) -> Graph:
        """Convert dictionary data to RDF graph with proper typing.
        
        Args:
            data: Dictionary data to convert
            
        Returns:
            RDF graph containing the data
        """
        graph = Graph()
        graph.bind('ex', EX)
        graph.bind('xsd', XSD)
        
        # Create a blank node for the root object
        root = URIRef(EX['data'])
        graph.add((root, RDF.type, EX.ValidationTarget))
        
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    self._add_typed_literal(graph, root, key, item)
            else:
                self._add_typed_literal(graph, root, key, value)
        
        return graph

    def _add_typed_literal(self, graph: Graph, subject: Node, predicate: str, value: Any) -> None:
        """Add a typed literal to the graph based on Python type.
        
        Args:
            graph: Target RDF graph
            subject: Subject node
            predicate: Predicate string
            value: Value to add
        """
        pred = URIRef(EX[predicate])
        
        if isinstance(value, bool):
            graph.add((subject, pred, Literal(value, datatype=XSD.boolean)))
        elif isinstance(value, int):
            graph.add((subject, pred, Literal(value, datatype=XSD.integer)))
        elif isinstance(value, float):
            graph.add((subject, pred, Literal(value, datatype=XSD.decimal)))
        elif isinstance(value, datetime):
            graph.add((subject, pred, Literal(value, datatype=XSD.dateTime)))
        else:
            graph.add((subject, pred, Literal(str(value), datatype=XSD.string)))

    def _load_shacl_templates(self):
        """Load SHACL shape templates into the shacl_shapes graph."""
        self.shacl_shapes.bind('sh', SH)
        self.shacl_shapes.bind('ex', EX)
        
        for template_name, template_text in self.SHACL_TEMPLATES.items():
            shape_text = template_text.format(path="?p", values="", pattern="", message="")
            shape = Graph()
            shape.parse(data=shape_text, format='turtle')
            self.shacl_shapes.add(shape) 