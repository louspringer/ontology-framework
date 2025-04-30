"""
MCP Validator implementation for ontology validation.
"""
from typing import Dict, List, Optional, Any, Tuple, Union, Set, Mapping, cast, Type
import logging
from pathlib import Path
from datetime import datetime
from rdflib import Graph, URIRef, Namespace, BNode, Literal, Variable
from rdflib.query import Result as ResultRow
from rdflib.term import Node, Identifier
from rdflib.namespace import RDFS, OWL, SH, RDF, XSD
import pyshacl
import sys
import json

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Define our namespaces
BFG = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

class ValidationTarget:
    """Represents a validation target with priority and metadata."""
    def __init__(self, uri: URIRef, target_type: str, priority: str = "LOW"):
        self.uri = uri
        self.target_type = target_type  # 'class', 'property', 'individual', 'shape'
        self.priority = priority
        self.metadata: Dict[str, Any] = {}
        self.validation_errors: List[str] = []

    def __str__(self) -> str:
        return f"{self.target_type}({self.uri}) - Priority: {self.priority}"

    def add_error(self, error: str):
        self.validation_errors.append(error)

class MCPValidator:
    """Model Context Protocol Validator implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the validator with optional configuration."""
        self.config = config if config is not None else {}
        self.validation_rules = {
            "validate_bfg9k": self.validate_bfg9k,
            "validateHierarchy": self.validate_hierarchy,
            "validateSemantics": self.validate_semantics,
            "validateSHACL": self.validate_shacl,
            "validateProperties": self.validate_properties,
            "validateIndividuals": self.validate_individuals
        }
        logger.debug("Initialized MCPValidator")
    
    def _to_uriref(self, identifier: Any) -> URIRef:
        """Convert a SPARQL result identifier to URIRef."""
        if isinstance(identifier, URIRef):
            return identifier
        elif isinstance(identifier, (str, Literal)):
            return URIRef(str(identifier))
        else:
            raise ValueError(f"Cannot convert {type(identifier)} to URIRef")
    
    def _create_validation_target(self, identifier: Any, target_type: str, priority: str = "LOW") -> ValidationTarget:
        """Create a ValidationTarget from a SPARQL result identifier."""
        return ValidationTarget(self._to_uriref(identifier), target_type, priority)
    
    def _log_query_results(self, query: str, results: Any) -> None:
        """Log SPARQL query results for debugging."""
        logger.debug("=== SPARQL Query ===")
        logger.debug(query)
        logger.debug("=== Query Results ===")
        if hasattr(results, "__len__"):
            result_count = len(results)
            logger.debug(f"Found {result_count} results")
            if result_count > 0:
                for row in results:
                    if isinstance(row, ResultRow):
                        logger.debug(f"  - Row: {row}")
                        logger.debug(f"  - Bindings: {row.bindings}")
                        logger.debug(f"  - Variables: {row.vars}")
                    else:
                        logger.debug(f"  - {row}")
        else:
            logger.debug("Results object has no length")
            for row in results:
                if isinstance(row, ResultRow):
                    logger.debug(f"  - Row: {row}")
                    logger.debug(f"  - Bindings: {row.bindings}")
                    logger.debug(f"  - Variables: {row.vars}")
                else:
                    logger.debug(f"  - {row}")
        logger.debug("===================")
    
    def _examine_sparql_result(self, row: ResultRow) -> None:
        """Examine and log the structure of a SPARQL result row."""
        logger.debug("=== SPARQL Result Structure ===")
        logger.debug(f"Row type: {type(row)}")
        logger.debug(f"Row vars: {row.vars}")
        logger.debug(f"Row bindings: {row.bindings}")
        logger.debug(f"Row asdict: {row.asdict()}")
        logger.debug("=== End Result Structure ===")

    def _get_sparql_value(self, row: Union[ResultRow, Dict[str, Any], Tuple[Any, ...]], var_name: str) -> Optional[Any]:
        """Get a value from a SPARQL query result row."""
        try:
            if isinstance(row, ResultRow):
                return row[var_name]
            elif isinstance(row, dict):
                return row.get(var_name)
            elif isinstance(row, tuple):
                # Handle tuple results by position
                if var_name in row:
                    return row[row.index(var_name)]
            return None
        except Exception as e:
            logger.error(f"Error getting SPARQL value: {str(e)}")
            return None

    def _log_graph_stats(self, graph: Graph) -> None:
        """Log statistics about the graph."""
        logger.debug("=== Graph Statistics ===")
        logger.debug(f"Total triples: {len(graph)}")
        
        # Count classes
        query = """
        SELECT (COUNT(DISTINCT ?class) as ?count)
        WHERE { ?class a owl:Class }
        """
        results = graph.query(query)
        self._log_query_results(query, results)
        if results.bindings:
            count = self._get_sparql_value(results.bindings[0], 'count')
            logger.debug(f"Classes: {count}")
        
        # Count properties
        query = """
        SELECT (COUNT(DISTINCT ?prop) as ?count)
        WHERE { ?prop a owl:DatatypeProperty }
        """
        results = graph.query(query)
        self._log_query_results(query, results)
        if results.bindings:
            count = self._get_sparql_value(results.bindings[0], 'count')
            logger.debug(f"DatatypeProperties: {count}")
        
        # Count SHACL shapes
        query = """
        SELECT (COUNT(DISTINCT ?shape) as ?count)
        WHERE { ?shape a sh:NodeShape }
        """
        results = graph.query(query)
        self._log_query_results(query, results)
        if results.bindings:
            count = self._get_sparql_value(results.bindings[0], 'count')
            logger.debug(f"SHACL shapes: {count}")
        
        # Count ValidationRule subclasses
        query = """
        SELECT (COUNT(DISTINCT ?class) as ?count)
        WHERE { ?class rdfs:subClassOf :ValidationRule }
        """
        results = graph.query(query)
        self._log_query_results(query, results)
        if results.bindings:
            count = self._get_sparql_value(results.bindings[0], 'count')
            logger.debug(f"ValidationRule subclasses: {count}")
        
        logger.debug("===================")
    
    def acquire_targets(self, graph: Graph) -> Dict[str, List[ValidationTarget]]:
        """Acquire validation targets using BFG9K pattern."""
        targets: Dict[str, List[ValidationTarget]] = {
            'classes': [],
            'properties': [],
            'shapes': [],
            'individuals': []
        }
        
        # Check ValidationRule hierarchy
        rule_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        
        SELECT ?rule ?issue WHERE {
            {
                # Check ValidationRule class
                :ValidationRule ?p ?o .
                BIND("ValidationRule" AS ?rule)
                BIND(
                    IF(?p = rdfs:label && !BOUND(?o), "missing_label",
                    IF(?p = rdfs:comment && !BOUND(?o), "missing_comment",
                    IF(?p = :message && !BOUND(?o), "missing_message",
                    IF(?p = :priority && !BOUND(?o), "missing_priority",
                    IF(?p = :target && !BOUND(?o), "missing_target",
                    IF(?p = :validator && !BOUND(?o), "missing_validator", ""))))))
                    AS ?issue
                )
                FILTER(?issue != "")
            }
            UNION
            {
                # Check subclasses
                ?subclass rdfs:subClassOf :ValidationRule .
                BIND(STR(?subclass) AS ?rule)
                BIND(
                    IF(NOT EXISTS { ?subclass owl:versionInfo ?v }, "missing_version_info",
                    IF(NOT EXISTS { ?subclass rdfs:label ?l }, "missing_label",
                    IF(NOT EXISTS { ?subclass rdfs:comment ?c }, "missing_comment", "")))
                    AS ?issue
                )
                FILTER(?issue != "")
            }
            UNION
            {
                # Check properties
                ?property rdfs:domain :ValidationRule .
                BIND(STR(?property) AS ?rule)
                BIND(
                    IF(NOT EXISTS { ?property rdfs:range ?r }, "missing_range",
                    IF(NOT EXISTS { ?property rdfs:label ?l }, "missing_label",
                    IF(NOT EXISTS { ?property rdfs:comment ?c }, "missing_comment", "")))
                    AS ?issue
                )
                FILTER(?issue != "")
            }
            UNION
            {
                # Check SHACL shapes
                ?shape sh:targetClass :ValidationRule .
                BIND(STR(?shape) AS ?rule)
                BIND(
                    IF(NOT EXISTS { ?shape sh:property ?p }, "missing_property_constraints",
                    IF(NOT EXISTS { ?shape rdfs:label ?l }, "missing_label",
                    IF(NOT EXISTS { ?shape rdfs:comment ?c }, "missing_comment", "")))
                    AS ?issue
                )
                FILTER(?issue != "")
            }
            UNION
            {
                # Check validation targets
                ?target rdf:type :ValidationTarget .
                BIND(STR(?target) AS ?rule)
                BIND(
                    IF(NOT EXISTS { ?target rdfs:label ?l }, "missing_label",
                    IF(NOT EXISTS { ?target rdfs:comment ?c }, "missing_comment",
                    IF(NOT EXISTS { ?target owl:versionInfo ?v }, "missing_version_info", "")))
                    AS ?issue
                )
                FILTER(?issue != "")
            }
        }
        """
        
        try:
            results = graph.query(rule_query)
            self._log_query_results(rule_query, results)
            
            for row in results:
                if isinstance(row, (ResultRow, Tuple)):
                    self._examine_sparql_result(row)
                    rule_value = self._get_sparql_value(row, 'rule')
                    issue_value = self._get_sparql_value(row, 'issue')
                    
                    if rule_value and issue_value:
                        if isinstance(rule_value, Literal):
                            rule_uri = URIRef(str(rule_value))
                        elif isinstance(rule_value, URIRef):
                            rule_uri = rule_value
                        else:
                            rule_uri = URIRef(str(rule_value))
                            
                        target = ValidationTarget(
                            uri=rule_uri,
                            target_type='class' if 'ValidationRule' in str(rule_value) else 'property'
                        )
                        target.priority = 'HIGH'
                        target.add_error(f"[HIGH] {str(issue_value)}")
                        
                        if 'ValidationRule' in str(rule_value):
                            targets['classes'].append(target)
                        elif 'ValidationTarget' in str(rule_value):
                            targets['classes'].append(target)
                        else:
                            targets['properties'].append(target)
                        logger.info(f"Found target: {rule_uri} with issue: {issue_value}")
        except Exception as e:
            logger.error(f"Error acquiring targets: {str(e)}")
        
        return targets
    
    def validate_target(self, target: ValidationTarget, graph: Graph) -> List[str]:
        """Validate a specific target using appropriate validation rules."""
        errors: List[str] = []
        
        if target.target_type == "class":
            # Validate class metadata
            query = f"""
            ASK {{
                <{target.uri}> rdfs:label ?label ;
                    rdfs:comment ?comment ;
                    owl:versionInfo ?version .
            }}
            """
            if not graph.query(query).askAnswer:
                errors.append(f"[HIGH] Class {target.uri} missing required metadata")
            
            # Validate class hierarchy
            query = f"""
            ASK {{
                <{target.uri}> rdfs:subClassOf+ <{target.uri}> .
            }}
            """
            if graph.query(query).askAnswer:
                errors.append(f"[HIGH] Class {target.uri} has circular hierarchy")
        
        elif target.target_type == "property":
            # Validate property constraints
            query = f"""
            ASK {{
                <{target.uri}> rdfs:domain ?domain ;
                    rdfs:range ?range ;
                    rdfs:label ?label ;
                    rdfs:comment ?comment .
            }}
            """
            if not graph.query(query).askAnswer:
                errors.append(f"[HIGH] Property {target.uri} missing constraints or metadata")
        
        elif target.target_type == "shape":
            # Validate SHACL shape completeness
            query = f"""
            ASK {{
                <{target.uri}> a sh:NodeShape ;
                    sh:property ?prop .
                ?prop sh:path ?path ;
                    sh:minCount ?min .
            }}
            """
            if not graph.query(query).askAnswer:
                errors.append(f"[HIGH] Shape {target.uri} incomplete or missing constraints")
        
        elif target.target_type == "individual":
            # Validate individual metadata
            query = f"""
            ASK {{
                <{target.uri}> rdfs:label ?label ;
                    rdfs:comment ?comment .
            }}
            """
            if not graph.query(query).askAnswer:
                errors.append(f"[HIGH] Individual {target.uri} missing metadata")
        
        return errors
    
    def validate_hierarchy(self, graph: Graph) -> List[str]:
        """Validate class hierarchy consistency using SPARQL."""
        errors: List[str] = []
        
        # High-priority BFG9K check: Class hierarchy must use semantic web tools
        query = """
        ASK {
            ?class rdfs:subClassOf ?superclass .
            ?class a owl:Class .
            ?superclass a owl:Class .
        }
        """
        if not graph.query(query).askAnswer:
            errors.append("[HIGH] Class hierarchy must be defined using semantic web tools")
        
        # Check for circular hierarchies
        query = """
        SELECT ?class ?superclass
        WHERE {
            ?class rdfs:subClassOf+ ?superclass .
            ?superclass rdfs:subClassOf+ ?class .
        }
        """
        results = graph.query(query)
        for row in results:
            if isinstance(row, ResultRow):
                errors.append(f"[HIGH] Circular class hierarchy detected: {str(row[0])} -> {str(row[1])}")
        
        # Check for missing labels in hierarchy
        query = """
        SELECT ?class
        WHERE {
            ?class rdfs:subClassOf ?superclass .
            FILTER NOT EXISTS { ?class rdfs:label ?label }
        }
        """
        results = graph.query(query)
        for row in results:
            if isinstance(row, ResultRow):
                errors.append(f"[HIGH] Class in hierarchy missing label: {str(row[0])}")
        
        return errors
    
    def validate_semantics(self, graph: Graph) -> List[str]:
        """Validate semantic relationships using SPARQL."""
        errors: List[str] = []
        
        # High-priority BFG9K check: Properties must use semantic web tools
        query = """
        ASK {
            ?prop a ?type .
            FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
            ?prop rdfs:domain ?domain .
            ?prop rdfs:range ?range .
        }
        """
        if not graph.query(query).askAnswer:
            errors.append("[HIGH] Properties must be defined using semantic web tools with domain and range")
        
        # Check property domains and ranges
        query = """
        SELECT ?prop ?type
        WHERE {
            ?prop a ?type .
            FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
            FILTER NOT EXISTS { ?prop rdfs:domain ?domain }
            FILTER NOT EXISTS { ?prop rdfs:range ?range }
        }
        """
        results = graph.query(query)
        for row in results:
            if isinstance(row, ResultRow):
                errors.append(f"[HIGH] Property {str(row[0])} missing domain or range")
        
        # Check for missing property characteristics
        query = """
        SELECT ?prop
        WHERE {
            ?prop a owl:ObjectProperty .
            FILTER NOT EXISTS { ?prop owl:inverseOf ?inverse }
            FILTER NOT EXISTS { ?prop owl:SymmetricProperty ?symmetric }
            FILTER NOT EXISTS { ?prop owl:TransitiveProperty ?transitive }
        }
        """
        results = graph.query(query)
        for row in results:
            if isinstance(row, ResultRow):
                errors.append(f"[HIGH] Property {str(row[0])} missing characteristics")
        
        return errors
    
    def validate_shacl(self, graph: Graph) -> List[str]:
        """Validate SHACL constraints."""
        errors: List[str] = []
        try:
            # High-priority BFG9K check: Must use SHACL validation
            query = """
            ASK {
                ?shape a sh:NodeShape .
                ?shape sh:property ?prop .
                ?prop sh:path ?path .
            }
            """
            if not graph.query(query).askAnswer:
                errors.append("[HIGH] Must use SHACL validation for constraints")
            
            # Create SHACL shapes graph
            shapes_graph = Graph()
            shapes_graph.parse(data="""
                @prefix sh: <http://www.w3.org/ns/shacl#> .
                @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
                @prefix owl: <http://www.w3.org/2002/07/owl#> .
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
                @prefix bfg: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .
                
                # ValidationRuleShape
                bfg:ValidationRuleShape a sh:NodeShape ;
                    sh:targetClass bfg:ValidationRule ;
                    sh:property [
                        sh:path bfg:hasMessage ;
                        sh:minCount 1 ;
                        sh:maxCount 1 ;
                        sh:datatype xsd:string ;
                    ] ;
                    sh:property [
                        sh:path bfg:hasPriority ;
                        sh:minCount 1 ;
                        sh:maxCount 1 ;
                        sh:datatype xsd:string ;
                    ] ;
                    sh:property [
                        sh:path bfg:hasValidator ;
                        sh:minCount 1 ;
                        sh:maxCount 1 ;
                        sh:datatype xsd:string ;
                    ] .
                
                # ValidationPatternShape
                bfg:ValidationPatternShape a sh:NodeShape ;
                    sh:targetClass bfg:ValidationPattern ;
                    sh:property [
                        sh:path bfg:hasMessage ;
                        sh:minCount 1 ;
                        sh:maxCount 1 ;
                        sh:datatype xsd:string ;
                    ] ;
                    sh:property [
                        sh:path bfg:hasPriority ;
                        sh:minCount 1 ;
                        sh:maxCount 1 ;
                        sh:datatype xsd:string ;
                    ] .
                
                # Class shape with high-priority constraints
                [] a sh:NodeShape ;
                    sh:targetClass owl:Class ;
                    sh:property [
                        sh:path rdfs:label ;
                        sh:minCount 1 ;
                        sh:datatype xsd:string ;
                        sh:message "[HIGH] Class must have a label" ;
                    ] ;
                    sh:property [
                        sh:path rdfs:comment ;
                        sh:minCount 1 ;
                        sh:datatype xsd:string ;
                        sh:message "[HIGH] Class must have a comment" ;
                    ] ;
                    sh:property [
                        sh:path owl:versionInfo ;
                        sh:minCount 1 ;
                        sh:datatype xsd:string ;
                        sh:message "[HIGH] Class must have version info" ;
                    ] .
            """, format="turtle")
            
            conforms, results_graph, results_text = pyshacl.validate(
                graph,
                shacl_graph=shapes_graph,
                inference='rdfs',
                abort_on_first=False
            )
            
            if not conforms:
                errors.append(f"[HIGH] SHACL validation failed: {results_text}")
                
        except Exception as e:
            errors.append(f"[HIGH] SHACL validation error: {str(e)}")
        return errors

    def validate_bfg9k(self, graph: Graph) -> List[str]:
        """Validate using BFG9K pattern with three-step validation process."""
        errors: List[str] = []
        
        # Step 1: ExactMatch (Generation Step)
        # Check for required metadata on validation rules
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        
        SELECT ?rule ?missing
        WHERE {
            ?rule a :ValidationRule .
            BIND(
                IF(NOT EXISTS { ?rule rdfs:label ?label }, "missing_label",
                IF(NOT EXISTS { ?rule rdfs:comment ?comment }, "missing_comment",
                IF(NOT EXISTS { ?rule :hasMessage ?message }, "missing_message",
                IF(NOT EXISTS { ?rule :hasPriority ?priority }, "missing_priority",
                IF(NOT EXISTS { ?rule :hasTarget ?target }, "missing_target",
                IF(NOT EXISTS { ?rule :hasValidator ?validator }, "missing_validator", ""))))))
                AS ?missing
            )
            FILTER(?missing != "")
        }
        """
        results = list(graph.query(query))
        for row in results:
            rule = self._get_sparql_value(row, 'rule')
            missing = self._get_sparql_value(row, 'missing')
            if rule and missing:
                errors.append(f"[HIGH] Rule {rule} has {missing}")
        
        # Step 2: SimilarityMatch (Answering Step)
        # Check for validation paths between components
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        
        SELECT ?component ?path
        WHERE {
            ?component a :ValidationRule .
            FILTER NOT EXISTS {
                ?path a :ValidationPath ;
                    :hasStartNode ?component ;
                    :hasEndNode ?target .
            }
        }
        """
        results = list(graph.query(query))
        for row in results:
            component = self._get_sparql_value(row, 'component')
            if component:
                errors.append(f"[HIGH] Component {component} missing validation path")
        
        # Step 3: LLMSelect (Checking Step)
        # Check quality thresholds and confidence levels
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        
        SELECT ?component ?quality
        WHERE {
            ?component a :ValidationRule ;
                :hasQuality ?quality .
            FILTER(?quality < 0.85)
        }
        """
        results = list(graph.query(query))
        for row in results:
            component = self._get_sparql_value(row, 'component')
            quality = self._get_sparql_value(row, 'quality')
            if component and quality:
                errors.append(f"[HIGH] Component {component} below quality threshold: {quality}")
        
        return errors
    
    def validate_properties(self, graph: Graph) -> List[str]:
        """Validate property definitions."""
        errors: List[str] = []
        
        # High-priority BFG9K check: Properties must have metadata
        query = """
        ASK {
            ?prop a ?type .
            FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
            ?prop rdfs:label ?label .
            ?prop rdfs:comment ?comment .
        }
        """
        if not graph.query(query).askAnswer:
            errors.append("[HIGH] Properties must have complete metadata (label and comment)")
        
        # Check for missing property characteristics
        query = """
        SELECT ?prop ?type
        WHERE {
            ?prop a ?type .
            FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
            FILTER NOT EXISTS { ?prop rdfs:label ?label }
            FILTER NOT EXISTS { ?prop rdfs:comment ?comment }
        }
        """
        results = graph.query(query)
        for row in results:
            if isinstance(row, ResultRow):
                errors.append(f"[HIGH] Property {str(row[0])} missing metadata")
        
        return errors
    
    def validate_individuals(self, graph: Graph) -> List[str]:
        """Validate individual instances."""
        errors: List[str] = []
        
        # High-priority BFG9K check: Individuals must have metadata
        query = """
        ASK {
            ?individual a ?class .
            ?individual rdfs:label ?label .
            ?individual rdfs:comment ?comment .
        }
        """
        if not graph.query(query).askAnswer:
            errors.append("[HIGH] Individuals must have complete metadata (label and comment)")
        
        # Check for missing instance metadata
        query = """
        SELECT ?individual ?class
        WHERE {
            ?individual a ?class .
            FILTER NOT EXISTS { ?individual rdfs:label ?label }
            FILTER NOT EXISTS { ?individual rdfs:comment ?comment }
        }
        """
        results = graph.query(query)
        for row in results:
            if isinstance(row, ResultRow):
                errors.append(f"[HIGH] Individual {str(row[0])} of class {str(row[1])} missing metadata")
        
        return errors
    
    def validate(self, graph: Graph, target: ValidationTarget, ordinance: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ontology against rules"""
        try:
            # Load validation rules
            rules = ordinance.get("rules", [])
            config = ordinance.get("config", {})
            
            # Execute validation
            results = []
            for rule in rules:
                if rule == "shacl":
                    shacl_result = self.validate_shacl(graph)
                    results.append({
                        "rule": rule,
                        "conforms": len(shacl_result) == 0,
                        "results_text": "\n".join(shacl_result)
                    })
                elif rule == "semantics":
                    semantic_errors = self.validate_semantics(graph)
                    results.append({
                        "rule": rule,
                        "errors": semantic_errors
                    })
                elif rule == "hierarchy":
                    hierarchy_errors = self.validate_hierarchy(graph)
                    results.append({
                        "rule": rule,
                        "errors": hierarchy_errors
                    })
                elif rule == "bfg9k":
                    bfg9k_errors = self.validate_bfg9k(graph)
                    results.append({
                        "rule": rule,
                        "errors": bfg9k_errors
                    })
            
            return {
                "target": str(target.uri),
                "rules": rules,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                "target": str(target.uri),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 