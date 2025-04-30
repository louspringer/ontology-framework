"""Validation handler for ontology framework.

This module implements a comprehensive validation system based on the guidance ontology,
including SPORE, Semantic, Syntax, and Consistency rules, along with SHACL validation patterns.

Example usage:
    ```python
    from rdflib import Graph
    from ontology_framework.validation_handler import ValidationHandler
    
    # Create a validation handler
    handler = ValidationHandler()
    
    # Load your ontology
    ontology = Graph()
    ontology.parse("your_ontology.ttl", format="turtle")
    
    # Basic validation
    result = handler.validate(ontology)
    if not result.is_valid:
        print("Validation issues found:")
        for issue in result.issues:
            print(f"- {issue['severity']}: {issue['message']}")
            print(f"  Context: {issue['context']}")
    
    # SHACL validation with pyshacl
    shacl_result = handler.validate_shacl(ontology)
    if not shacl_result.is_valid:
        print("SHACL validation issues:")
        for issue in shacl_result.get_issues_by_severity("ERROR"):
            print(f"- {issue['message']}")
    
    # Validate specific targets
    result = handler.validate(ontology, targets=["classes", "properties"])
    
    # Add custom validation rule
    def custom_validator(data: Graph) -> ValidationResult:
        issues = []
        # Custom validation logic
        return ValidationResult(is_valid=True, issues=issues)
    
    handler.add_rule(SemanticRule(
        priority="HIGH",
        message="Custom validation rule",
        validator=custom_validator,
        target="custom"
    ))
    
    # Export validation results
    result.export_report("validation_report.json")
    ```

Advanced usage:
    ```python
    # Create validation handler with GraphDB connection
    from ontology_framework.graphdb import GraphDBConnection
    db_connection = GraphDBConnection("http://localhost:7200", "repository")
    handler = ValidationHandler(graphdb_connection=db_connection)
    
    # Validate with custom SHACL shapes
    shapes = Graph()
    shapes.parse("custom_shapes.ttl", format="turtle")
    result = handler.validate_shacl(ontology, shapes)
    
    # Get validation statistics
    stats = result.get_statistics()
    print(f"Total issues: {stats['total']}")
    print(f"Errors: {stats['errors']}")
    print(f"Warnings: {stats['warnings']}")
    
    # Filter issues by context
    class_issues = result.get_issues_by_context("class")
    property_issues = result.get_issues_by_context("property")
    ```

Use Cases:
    1. Ontology Development
        ```python
        # During ontology development
        handler = ValidationHandler()
        ontology = Graph()
        
        # Validate after each change
        result = handler.validate(ontology)
        if not result.is_valid:
            result.export_report("development_report.html")
        
        # Check specific aspects
        class_result = handler.validate(ontology, targets=["classes"])
        property_result = handler.validate(ontology, targets=["properties"])
        ```
        
    2. CI/CD Pipeline
        ```python
        # In CI/CD pipeline
        handler = ValidationHandler()
        ontology = Graph()
        ontology.parse("ontology.ttl", format="turtle")
        
        # Run all validations
        result = handler.validate(ontology)
        shacl_result = handler.validate_shacl(ontology)
        
        # Fail pipeline if critical issues found
        if not result.is_valid or not shacl_result.is_valid:
            result.export_report("validation_report.json")
            raise ValidationError("Critical validation issues found")
        ```
        
    3. Documentation Generation
        ```python
        # Generate documentation with validation
        handler = ValidationHandler()
        ontology = Graph()
        ontology.parse("ontology.ttl", format="turtle")
        
        # Validate and generate report
        result = handler.validate(ontology)
        result.export_report("documentation/validation.html")
        
        # Use validation results in documentation
        stats = result.get_statistics()
        print(f"Documentation coverage: {stats['info'] / stats['total'] * 100}%")
        ```
        
    4. Quality Assurance
        ```python
        # Quality assurance process
        handler = ValidationHandler()
        ontology = Graph()
        ontology.parse("ontology.ttl", format="turtle")
        
        # Run comprehensive validation
        result = handler.validate(ontology)
        shacl_result = handler.validate_shacl(ontology)
        
        # Generate quality report
        quality_report = {
            "validation": result.to_dict(),
            "shacl": shacl_result.to_dict(),
            "statistics": result.get_statistics()
        }
        ```
        
    5. Integration Testing
        ```python
        # Integration testing
        handler = ValidationHandler()
        test_ontology = Graph()
        
        # Test specific features
        def test_class_validation():
            test_ontology.add((URIRef("http://example.org/TestClass"), RDF.type, OWL.Class))
            result = handler.validate(test_ontology, targets=["classes"])
            assert result.is_valid
            
        def test_property_validation():
            test_ontology.add((URIRef("http://example.org/testProperty"), RDF.type, OWL.ObjectProperty))
            result = handler.validate(test_ontology, targets=["properties"])
            assert result.is_valid
        ```
"""

from typing import Dict, List, Optional, Set, Union, Any, Callable, Iterable, Tuple
import logging
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD
from pyshacl import validate as pyshacl_validate
from pyshacl.rdfutil import load_from_source
from .exceptions import ValidationError
from .graphdb import GraphDBConnection
from .validation.conformance_level import ConformanceLevel
import json

logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("http://example.org/guidance#")
SHACL = Namespace("http://www.w3.org/ns/shacl#")

class ValidationResult:
    """Detailed validation result with severity levels and context."""
    
    def __init__(self, is_valid: bool, issues: List[Dict[str, Any]]):
        self.is_valid = is_valid
        self.issues = issues
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "is_valid": self.is_valid,
            "issues": self.issues
        }
        
    def get_issues_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get issues filtered by severity."""
        return [issue for issue in self.issues if issue["severity"] == severity]
        
    def get_issues_by_context(self, context_key: str) -> List[Dict[str, Any]]:
        """Get issues filtered by context key."""
        return [issue for issue in self.issues if context_key in issue["context"]]
        
    def get_statistics(self) -> Dict[str, int]:
        """Get validation statistics."""
        return {
            "total": len(self.issues),
            "errors": len(self.get_issues_by_severity("ERROR")),
            "warnings": len(self.get_issues_by_severity("WARNING")),
            "info": len(self.get_issues_by_severity("INFO"))
        }
        
    def export_report(self, filename: str, format: str = "json") -> None:
        """Export validation report to file.
        
        Args:
            filename: Output file path
            format: Export format ("json" or "html")
        """
        if format == "json":
            import json
            with open(filename, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
        elif format == "html":
            self._export_html_report(filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _export_html_report(self, filename: str) -> None:
        """Export validation report as HTML."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Validation Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .issue { margin: 10px 0; padding: 10px; border-radius: 5px; }
                .error { background-color: #ffebee; border-left: 4px solid #f44336; }
                .warning { background-color: #fff3e0; border-left: 4px solid #ff9800; }
                .info { background-color: #e3f2fd; border-left: 4px solid #2196f3; }
                .context { margin-left: 20px; color: #666; }
            </style>
        </head>
        <body>
            <h1>Validation Report</h1>
            <p>Overall status: <strong>{status}</strong></p>
            <h2>Issues</h2>
            {issues}
        </body>
        </html>
        """
        
        issues_html = ""
        for issue in self.issues:
            issues_html += f"""
            <div class="issue {issue['severity'].lower()}">
                <p><strong>{issue['severity']}</strong>: {issue['message']}</p>
                <div class="context">
                    <pre>{json.dumps(issue['context'], indent=2)}</pre>
                </div>
            </div>
            """
            
        with open(filename, "w") as f:
            f.write(html.format(
                status="Valid" if self.is_valid else "Invalid",
                issues=issues_html
            ))

class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, priority: str, message: str, validator: Callable[[Any], ValidationResult], target: str):
        self.priority = priority
        self.message = message
        self.validator = validator
        self.target = target
        
    def validate(self, data: Any) -> ValidationResult:
        """Validate data against this rule."""
        try:
            return self.validator(data)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": f"Validation error in {self.target}: {str(e)}",
                    "severity": "ERROR",
                    "context": {"target": self.target}
                }]
            )

class SPORERule(ValidationRule):
    """SPORE (Semantic, Pragmatic, Ontological, and Representational) validation rule."""
    pass

class SemanticRule(ValidationRule):
    """Semantic validation rule."""
    pass

class SyntaxRule(ValidationRule):
    """Syntax validation rule."""
    pass

class ConsistencyRule(ValidationRule):
    """Consistency validation rule."""
    pass

class ValidationHandler:
    """Handles validation operations for the ontology framework."""
    
    def __init__(self, graphdb_connection: Optional[GraphDBConnection] = None):
        """Initialize the validation handler.
        
        Args:
            graphdb_connection: Optional GraphDB connection for validation
        """
        self.graphdb = graphdb_connection
        self.rules: Dict[str, ValidationRule] = {}
        self._setup_default_rules()
        self._setup_shacl_patterns()
        
    def _setup_default_rules(self) -> None:
        """Set up default validation rules based on guidance ontology."""
        # SPORE Rules
        self.add_rule(SPORERule(
            priority="HIGH",
            message="Ontology must have proper semantic structure",
            validator=self._validate_semantic_structure,
            target="ontology"
        ))
        
        # Semantic Rules
        self.add_rule(SemanticRule(
            priority="HIGH",
            message="Classes must have proper semantic relationships",
            validator=self._validate_semantic_relationships,
            target="classes"
        ))
        
        # Syntax Rules
        self.add_rule(SyntaxRule(
            priority="MEDIUM",
            message="URIs must follow proper syntax",
            validator=self._validate_uri_syntax,
            target="uris"
        ))
        
        # Consistency Rules
        self.add_rule(ConsistencyRule(
            priority="HIGH",
            message="Ontology must be consistent",
            validator=self._validate_consistency,
            target="ontology"
        ))
        
        # Additional Rules
        self.add_rule(SemanticRule(
            priority="HIGH",
            message="Properties must have proper cardinality",
            validator=self._validate_property_cardinality,
            target="properties"
        ))
        
        self.add_rule(SPORERule(
            priority="MEDIUM",
            message="Ontology must have proper documentation",
            validator=self._validate_documentation,
            target="documentation"
        ))
        
        self.add_rule(SyntaxRule(
            priority="MEDIUM",
            message="Namespaces must be properly defined",
            validator=self._validate_namespaces,
            target="namespaces"
        ))
        
        self.add_rule(ConsistencyRule(
            priority="HIGH",
            message="Ontology must have consistent imports",
            validator=self._validate_imports,
            target="imports"
        ))
        
    def _setup_shacl_patterns(self) -> None:
        """Set up default SHACL validation patterns."""
        self.shacl_patterns = {
            "class_shape": """
                @prefix sh: <http://www.w3.org/ns/shacl#> .
                @prefix owl: <http://www.w3.org/2002/07/owl#> .
                
                [] a sh:NodeShape ;
                   sh:targetClass owl:Class ;
                   sh:property [
                       sh:path rdfs:label ;
                       sh:minCount 1 ;
                       sh:maxCount 1 ;
                   ] ;
                   sh:property [
                       sh:path rdfs:comment ;
                       sh:minCount 1 ;
                   ] .
            """,
            "property_shape": """
                @prefix sh: <http://www.w3.org/ns/shacl#> .
                @prefix owl: <http://www.w3.org/2002/07/owl#> .
                
                [] a sh:NodeShape ;
                   sh:targetClass owl:ObjectProperty ;
                   sh:property [
                       sh:path rdfs:domain ;
                       sh:minCount 1 ;
                   ] ;
                   sh:property [
                       sh:path rdfs:range ;
                       sh:minCount 1 ;
                   ] .
            """,
            "datatype_shape": """
                @prefix sh: <http://www.w3.org/ns/shacl#> .
                @prefix owl: <http://www.w3.org/2002/07/owl#> .
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
                
                [] a sh:NodeShape ;
                   sh:targetClass owl:DatatypeProperty ;
                   sh:property [
                       sh:path rdfs:range ;
                       sh:in (xsd:string xsd:integer xsd:boolean xsd:dateTime) ;
                   ] .
            """,
            "individual_shape": """
                @prefix sh: <http://www.w3.org/ns/shacl#> .
                @prefix owl: <http://www.w3.org/2002/07/owl#> .
                
                [] a sh:NodeShape ;
                   sh:targetClass owl:NamedIndividual ;
                   sh:property [
                       sh:path rdf:type ;
                       sh:minCount 1 ;
                   ] .
            """,
            "ontology_shape": """
                @prefix sh: <http://www.w3.org/ns/shacl#> .
                @prefix owl: <http://www.w3.org/2002/07/owl#> .
                
                [] a sh:NodeShape ;
                   sh:targetClass owl:Ontology ;
                   sh:property [
                       sh:path owl:versionInfo ;
                       sh:minCount 1 ;
                   ] ;
                   sh:property [
                       sh:path owl:imports ;
                       sh:minCount 0 ;
                   ] .
            """
        }
        
    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule.
        
        Args:
            rule: The validation rule to add
        """
        self.rules[rule.target] = rule
        
    def remove_rule(self, target: str) -> None:
        """Remove a validation rule.
        
        Args:
            target: The target of the rule to remove
        """
        if target in self.rules:
            del self.rules[target]
            
    def validate(self, data: Any, targets: Optional[List[str]] = None) -> ValidationResult:
        """Validate data against specified rules.
        
        Args:
            data: The data to validate
            targets: Optional list of specific validation targets
            
        Returns:
            ValidationResult containing detailed validation results
        """
        all_issues: List[Dict[str, Any]] = []
        is_valid = True
        
        try:
            targets_to_validate = targets if targets else self.rules.keys()
            
            for target in targets_to_validate:
                if target in self.rules:
                    result = self.rules[target].validate(data)
                    if not result.is_valid:
                        is_valid = False
                        all_issues.extend(result.issues)
                        
            return ValidationResult(is_valid=is_valid, issues=all_issues)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": f"Validation error: {str(e)}",
                    "severity": "ERROR",
                    "context": {"error": str(e)}
                }]
            )
            
    def validate_shacl(self, data_graph: Graph, shapes_graph: Optional[Graph] = None) -> ValidationResult:
        """Validate data against SHACL shapes using pyshacl.
        
        Args:
            data_graph: RDFlib Graph containing the data to validate
            shapes_graph: Optional RDFlib Graph containing SHACL shapes
            
        Returns:
            ValidationResult containing detailed validation results
        """
        try:
            if shapes_graph is None:
                shapes_graph = Graph()
                for pattern in self.shacl_patterns.values():
                    shapes_graph.parse(data=pattern, format="turtle")
                    
            conforms, results_graph, results_text = pyshacl_validate(
                data_graph,
                shacl_graph=shapes_graph,
                inference="rdfs",
                abort_on_first=False,
                meta_shacl=False,
                debug=False
            )
            
            issues = []
            if not conforms:
                for result in results_graph.subjects(RDF.type, SH.ValidationResult):
                    severity = str(results_graph.value(result, SH.severity))
                    message = str(results_graph.value(result, SH.resultMessage))
                    focus_node = str(results_graph.value(result, SH.focusNode))
                    result_path = str(results_graph.value(result, SH.resultPath))
                    
                    issues.append({
                        "message": message,
                        "severity": severity,
                        "context": {
                            "focus_node": focus_node,
                            "result_path": result_path,
                            "validation_result": str(result)
                        }
                    })
                    
            return ValidationResult(is_valid=conforms, issues=issues)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": f"SHACL validation failed: {str(e)}",
                    "severity": "ERROR",
                    "context": {"error": str(e)}
                }]
            )
            
    def _validate_semantic_structure(self, data: Any) -> ValidationResult:
        """Validate semantic structure of ontology."""
        issues: List[Dict[str, Any]] = []
        is_valid = True
        
        if not isinstance(data, Graph):
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": "Data must be an RDFlib Graph",
                    "severity": "ERROR",
                    "context": {"data_type": type(data).__name__}
                }]
            )
            
        # Check for ontology declaration
        ontology_uri = data.value(None, RDF.type, OWL.Ontology)
        if not ontology_uri:
            is_valid = False
            issues.append({
                "message": "Missing ontology declaration",
                "severity": "ERROR",
                "context": {"check": "ontology_declaration"}
            })
            
        # Check for class definitions
        classes = list(data.subjects(RDF.type, OWL.Class))
        if not classes:
            is_valid = False
            issues.append({
                "message": "No classes defined in ontology",
                "severity": "ERROR",
                "context": {"check": "class_definitions"}
            })
            
        # Check for property definitions
        properties = list(data.subjects(RDF.type, OWL.ObjectProperty)) + \
                    list(data.subjects(RDF.type, OWL.DatatypeProperty))
        if not properties:
            is_valid = False
            issues.append({
                "message": "No properties defined in ontology",
                "severity": "ERROR",
                "context": {"check": "property_definitions"}
            })
            
        return ValidationResult(is_valid=is_valid, issues=issues)
        
    def _validate_semantic_relationships(self, data: Any) -> ValidationResult:
        """Validate semantic relationships in ontology."""
        issues: List[Dict[str, Any]] = []
        is_valid = True
        
        if not isinstance(data, Graph):
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": "Data must be an RDFlib Graph",
                    "severity": "ERROR",
                    "context": {"data_type": type(data).__name__}
                }]
            )
            
        # Check domain and range for properties
        for prop in data.subjects(RDF.type, OWL.ObjectProperty):
            if not any(data.triples((prop, RDFS.domain, None))):
                is_valid = False
                issues.append({
                    "message": f"Property {prop} has no domain",
                    "severity": "ERROR",
                    "context": {"property": str(prop), "check": "domain"}
                })
            if not any(data.triples((prop, RDFS.range, None))):
                is_valid = False
                issues.append({
                    "message": f"Property {prop} has no range",
                    "severity": "ERROR",
                    "context": {"property": str(prop), "check": "range"}
                })
                
        # Check class hierarchy
        for class_uri in data.subjects(RDF.type, OWL.Class):
            if not any(data.triples((class_uri, RDFS.subClassOf, None))):
                is_valid = False
                issues.append({
                    "message": f"Class {class_uri} has no superclass",
                    "severity": "WARNING",
                    "context": {"class": str(class_uri), "check": "superclass"}
                })
                
        return ValidationResult(is_valid=is_valid, issues=issues)
        
    def _validate_uri_syntax(self, data: Any) -> ValidationResult:
        """Validate URI syntax."""
        issues: List[Dict[str, Any]] = []
        is_valid = True
        
        if not isinstance(data, Graph):
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": "Data must be an RDFlib Graph",
                    "severity": "ERROR",
                    "context": {"data_type": type(data).__name__}
                }]
            )
            
        # Check URI syntax for all resources
        for subject in data.subjects():
            if isinstance(subject, URIRef):
                uri = str(subject)
                if not uri.startswith(("http://", "https://")):
                    is_valid = False
                    issues.append({
                        "message": f"Invalid URI scheme: {uri}",
                        "severity": "ERROR",
                        "context": {"uri": uri, "check": "scheme"}
                    })
                if "#" in uri and not uri.endswith("#"):
                    is_valid = False
                    issues.append({
                        "message": f"Invalid fragment in URI: {uri}",
                        "severity": "ERROR",
                        "context": {"uri": uri, "check": "fragment"}
                    })
                    
        return ValidationResult(is_valid=is_valid, issues=issues)
        
    def _validate_consistency(self, data: Any) -> ValidationResult:
        """Validate ontology consistency."""
        issues: List[Dict[str, Any]] = []
        is_valid = True
        
        if not isinstance(data, Graph):
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": "Data must be an RDFlib Graph",
                    "severity": "ERROR",
                    "context": {"data_type": type(data).__name__}
                }]
            )
            
        # Check for cycles in class hierarchy
        def has_cycle(class_uri: URIRef, visited: Set[URIRef]) -> bool:
            if class_uri in visited:
                return True
            visited.add(class_uri)
            for superclass in data.objects(class_uri, RDFS.subClassOf):
                if isinstance(superclass, URIRef):
                    if has_cycle(superclass, visited):
                        return True
            visited.remove(class_uri)
            return False
            
        for class_uri in data.subjects(RDF.type, OWL.Class):
            if isinstance(class_uri, URIRef) and has_cycle(class_uri, set()):
                is_valid = False
                issues.append({
                    "message": f"Cycle detected in class hierarchy: {class_uri}",
                    "severity": "ERROR",
                    "context": {"class": str(class_uri), "check": "cycle"}
                })
                
        # Check for inconsistent property definitions
        for prop in data.subjects(RDF.type, OWL.ObjectProperty):
            domain = data.value(prop, RDFS.domain)
            range_ = data.value(prop, RDFS.range)
            if domain and range_:
                # Check if domain and range are compatible
                if isinstance(domain, URIRef) and isinstance(range_, URIRef):
                    if not any(data.triples((range_, RDFS.subClassOf, domain))):
                        is_valid = False
                        issues.append({
                            "message": f"Incompatible domain and range for property {prop}",
                            "severity": "ERROR",
                            "context": {
                                "property": str(prop),
                                "domain": str(domain),
                                "range": str(range_),
                                "check": "domain_range"
                            }
                        })
                        
        return ValidationResult(is_valid=is_valid, issues=issues)
        
    def _validate_property_cardinality(self, data: Any) -> ValidationResult:
        """Validate property cardinality constraints."""
        issues: List[Dict[str, Any]] = []
        is_valid = True
        
        if not isinstance(data, Graph):
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": "Data must be an RDFlib Graph",
                    "severity": "ERROR",
                    "context": {"data_type": type(data).__name__}
                }]
            )
            
        # Check for functional properties
        for prop in data.subjects(RDF.type, OWL.FunctionalProperty):
            if not any(data.triples((prop, OWL.cardinality, Literal(1)))):
                is_valid = False
                issues.append({
                    "message": f"Functional property {prop} should have cardinality 1",
                    "severity": "WARNING",
                    "context": {"property": str(prop), "check": "cardinality"}
                })
                
        return ValidationResult(is_valid=is_valid, issues=issues)
        
    def _validate_documentation(self, data: Any) -> ValidationResult:
        """Validate ontology documentation."""
        issues: List[Dict[str, Any]] = []
        is_valid = True
        
        if not isinstance(data, Graph):
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": "Data must be an RDFlib Graph",
                    "severity": "ERROR",
                    "context": {"data_type": type(data).__name__}
                }]
            )
            
        # Check for class documentation
        for class_uri in data.subjects(RDF.type, OWL.Class):
            if not any(data.triples((class_uri, RDFS.comment, None))):
                is_valid = False
                issues.append({
                    "message": f"Class {class_uri} has no documentation",
                    "severity": "WARNING",
                    "context": {"class": str(class_uri), "check": "documentation"}
                })
                
        # Check for property documentation
        for prop in data.subjects(RDF.type, OWL.ObjectProperty):
            if not any(data.triples((prop, RDFS.comment, None))):
                is_valid = False
                issues.append({
                    "message": f"Property {prop} has no documentation",
                    "severity": "WARNING",
                    "context": {"property": str(prop), "check": "documentation"}
                })
                
        return ValidationResult(is_valid=is_valid, issues=issues)
        
    def _validate_namespaces(self, data: Any) -> ValidationResult:
        """Validate namespace definitions."""
        issues: List[Dict[str, Any]] = []
        is_valid = True
        
        if not isinstance(data, Graph):
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": "Data must be an RDFlib Graph",
                    "severity": "ERROR",
                    "context": {"data_type": type(data).__name__}
                }]
            )
            
        # Check for required namespaces
        required_namespaces = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        }
        
        for prefix, uri in required_namespaces.items():
            ns = Namespace(uri)
            if not any(data.triples((None, None, None))):
                is_valid = False
                issues.append({
                    "message": f"Required namespace not used: {prefix}",
                    "severity": "WARNING",
                    "context": {"namespace": prefix, "uri": uri}
                })
                
        return ValidationResult(is_valid=is_valid, issues=issues)
        
    def _validate_imports(self, data: Any) -> ValidationResult:
        """Validate ontology imports."""
        issues: List[Dict[str, Any]] = []
        is_valid = True
        
        if not isinstance(data, Graph):
            return ValidationResult(
                is_valid=False,
                issues=[{
                    "message": "Data must be an RDFlib Graph",
                    "severity": "ERROR",
                    "context": {"data_type": type(data).__name__}
                }]
            )
            
        # Check for circular imports
        imports = list(data.objects(None, OWL.imports))
        if len(imports) != len(set(imports)):
            is_valid = False
            issues.append({
                "message": "Circular imports detected",
                "severity": "ERROR",
                "context": {"imports": [str(i) for i in imports]}
            })
            
        return ValidationResult(is_valid=is_valid, issues=issues) 