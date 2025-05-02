from rdflib import Graph, Namespace, URIRef, Literal, BNode, Node
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from rdflib.query import ResultRow
import pyshacl
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from pathlib import Path
from ontology_framework.validation.validation_rule_type import ValidationRuleType
from ontology_framework.validation.error_severity import ErrorSeverity
import uuid
import logging

class GuidanceManager:
    """Manages the guidance ontology using semantic web tools."""
    
    def __init__(self, guidance_path: str = 'guidance.ttl'):
        self.guidance_path = guidance_path
        self.graph = Graph()
        self.graph.parse(guidance_path, format='turtle')
        self.transaction_stack = []
        
        # Define namespaces
        self.GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
        self.META = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/meta#')
        self.PROBLEM = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/problem#')
        self.SOLUTION = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/solution#')
        
        # Bind namespaces
        self.graph.bind('guidance', self.GUIDANCE)
        self.graph.bind('meta', self.META)
        self.graph.bind('problem', self.PROBLEM)
        self.graph.bind('solution', self.SOLUTION)
        self.graph.bind('sh', SH)
        self.graph.bind('owl', OWL)
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('xsd', XSD)
        
        self.logger = logging.getLogger(__name__)
        
    def begin_transaction(self) -> str:
        """Start a new transaction.
        
        Returns:
            str: Transaction ID
        """
        transaction_id = str(uuid.uuid4())
        self.transaction_stack.append({
            'id': transaction_id,
            'graph': Graph(),
            'changes': []
        })
        return transaction_id

    def commit_transaction(self, transaction_id: str) -> bool:
        """Commit a transaction.
        
        Args:
            transaction_id: ID of the transaction to commit
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If transaction ID is invalid
        """
        for i, tx in enumerate(self.transaction_stack):
            if tx['id'] == transaction_id:
                # Apply changes to main graph
                self.graph += tx['graph']
                # Remove transaction from stack
                self.transaction_stack.pop(i)
                return True
        raise ValueError(f"Invalid transaction ID: {transaction_id}")

    def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback a transaction.
        
        Args:
            transaction_id: ID of the transaction to rollback
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If transaction ID is invalid
        """
        for i, tx in enumerate(self.transaction_stack):
            if tx['id'] == transaction_id:
                # Remove transaction from stack without applying changes
                self.transaction_stack.pop(i)
                return True
        raise ValueError(f"Invalid transaction ID: {transaction_id}")

    def _get_current_transaction(self) -> Optional[Dict]:
        """Get the current transaction if one exists.
        
        Returns:
            Optional[Dict]: Current transaction or None
        """
        return self.transaction_stack[-1] if self.transaction_stack else None

    def get_validation_patterns(self) -> List[Dict[str, str]]:
        """Get all validation patterns using SPARQL.
        
        Returns:
            List of dictionaries containing pattern information
        """
        query = """
        PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?pattern ?type ?label ?comment
        WHERE {
            {
                # Direct patterns
                ?pattern a guidance:ValidationPattern ;
                        guidance:hasType ?type .
                OPTIONAL { ?pattern rdfs:label ?label }
                OPTIONAL { ?pattern rdfs:comment ?comment }
            }
            UNION
            {
                # Patterns from rules
                ?rule a guidance:ValidationRule ;
                      guidance:hasPattern ?pattern ;
                      guidance:hasType ?type .
                OPTIONAL { ?pattern rdfs:label ?label }
                OPTIONAL { ?pattern rdfs:comment ?comment }
            }
        }
        """
        patterns = []
        results = self.graph.query(query)
        for row in results:
            pattern_dict = {
                'pattern': str(row.pattern),
                'type': str(row.type).split('#')[-1] if '#' in str(row.type) else str(row.type),
                'label': str(row.label) if row.label else None,
                'comment': str(row.comment) if row.comment else None
            }
            if pattern_dict not in patterns:  # Avoid duplicates
                patterns.append(pattern_dict)
        return patterns
        
    def get_validation_rules(self) -> List[Dict[str, Any]]:
        """Get all validation rules from the guidance ontology.
        
        Returns:
            List of dictionaries containing rule information
        """
        rules = []
        
        query = """
        PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?rule ?label ?type ?message ?priority ?pattern
        WHERE {
            ?rule a guidance:ValidationRule ;
                  rdfs:label ?label ;
                  guidance:hasType ?type .
            OPTIONAL { ?rule guidance:hasMessage ?message }
            OPTIONAL { ?rule guidance:hasPriority ?priority }
            OPTIONAL { ?rule guidance:hasPattern ?pattern }
        }
        """
        
        for row in self.graph.query(query):
            patterns = []
            # Get all patterns for this rule
            pattern_query = f"""
            PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
            SELECT ?pattern
            WHERE {{
                <{row.rule}> guidance:hasPattern ?pattern .
            }}
            """
            for pattern_row in self.graph.query(pattern_query):
                patterns.append(str(pattern_row[0]))
                
            rule_dict = {
                "id": str(row.label),
                "type": str(row.type).split('#')[-1],
                "message": str(row.message) if row.message else None,
                "priority": str(row.priority) if row.priority else "0",
                "patterns": patterns if patterns else None,
                "rule": self._get_rule_details(row.rule)
            }
            rules.append(rule_dict)
            
        return rules
        
    def validate_guidance(self) -> Dict[str, List[str]]:
        """Validate the guidance ontology using SHACL."""
        # Load SHACL shapes from the guidance ontology
        shapes_query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        CONSTRUCT {
            ?shape ?p ?o .
            ?o ?p2 ?o2 .
        }
        WHERE {
            ?shape a sh:NodeShape .
            ?shape ?p ?o .
            OPTIONAL { ?o ?p2 ?o2 }
        }
        """
        shapes_graph = Graph()
        query_result = self.graph.query(shapes_query)
        if hasattr(query_result, 'graph'):
            shapes_graph += query_result.graph
        
        # Validate using PyShacl
        conforms, results_graph, results_text = pyshacl.validate(
            self.graph,
            shacl_graph=shapes_graph,
            inference='rdfs',
            abort_on_first=False
        )
        
        # Process validation results using SPARQL
        results_query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        
        SELECT ?focusNode ?message ?severity
        WHERE {
            ?result a sh:ValidationResult ;
                    sh:focusNode ?focusNode ;
                    sh:resultMessage ?message ;
                    sh:resultSeverity ?severity .
        }
        """
        
        errors = []
        warnings = []
        
        if not conforms:
            for row in results_graph.query(results_query):
                if isinstance(row, ResultRow):
                    severity = str(row.severity)
                    message = f"{row.focusNode}: {row.message}"
                else:
                    severity = str(row[2])
                    message = f"{row[0]}: {row[1]}"
                
                if severity == str(SH.Violation):
                    errors.append(message)
                else:
                    warnings.append(message)
                    
        return {
            'errors': errors,
            'warnings': warnings
        }
        
    def add_validation_rule(
        self,
        rule_id: str,
        rule: Dict[str, Any],
        type: str,
        message: Optional[str] = None,
        priority: int = 0
    ) -> URIRef:
        """Add a validation rule to the guidance ontology.
        
        Args:
            rule_id: Unique identifier for the rule.
            rule: Rule configuration dictionary.
            type: Type of validation rule.
            message: Optional message to display for violations.
            priority: Rule execution priority.
            
        Returns:
            URIRef of the created rule.
            
        Raises:
            ValueError: If required parameters are missing.
        """
        rule_uri = URIRef(f"{self.GUIDANCE}{rule_id}")
        
        # Get the graph to modify (transaction or main)
        target_graph = self._get_current_transaction()['graph'] if self._get_current_transaction() else self.graph
        
        # Add basic rule properties
        target_graph.add((rule_uri, RDF.type, self.GUIDANCE.ValidationRule))
        target_graph.add((rule_uri, RDFS.label, Literal(rule_id)))
        target_graph.add((rule_uri, self.GUIDANCE.hasType, Literal(type)))
        
        if message:
            target_graph.add((rule_uri, self.GUIDANCE.hasMessage, Literal(message)))
            
        target_graph.add((rule_uri, self.GUIDANCE.hasPriority, Literal(priority, datatype=XSD.integer)))
        
        # Add rule-specific properties based on type
        if type == ValidationRuleType.SHACL.value:
            if "shapes_file" in rule:
                target_graph.add((rule_uri, self.GUIDANCE.hasShapesFile, Literal(rule["shapes_file"])))
        elif type == ValidationRuleType.SEMANTIC.value or type == "SPARQL":  # Added SPARQL type support
            if "query" in rule:
                target_graph.add((rule_uri, self.GUIDANCE.hasSPARQLQuery, Literal(rule["query"])))
        elif type == ValidationRuleType.SYNTAX.value:
            if "pattern" in rule:
                target_graph.add((rule_uri, self.GUIDANCE.hasPattern, Literal(rule["pattern"])))
        elif type == ValidationRuleType.SENSITIVE_DATA.value:
            if "patterns" in rule:
                for pattern in rule["patterns"]:
                    target_graph.add((rule_uri, self.GUIDANCE.hasPattern, Literal(pattern)))
        
        return rule_uri
        
    def save(self, path: Optional[str] = None) -> None:
        """Save changes back to the guidance ontology."""
        if self.transaction_stack:
            raise RuntimeError("Cannot save while transactions are active")
            
        target_path = path if path else self.guidance_path
        self.graph.serialize(destination=target_path, format='turtle')
        
    def load(self, path: str) -> None:
        """Load guidance ontology from a file."""
        self.guidance_path = path
        self.graph = Graph()
        self.graph.parse(path, format='turtle')
        
    def _get_rule_details(self, rule_uri: URIRef) -> Dict[str, Any]:
        """Get detailed configuration for a validation rule.
        
        Args:
            rule_uri: URI of the rule to get details for.
            
        Returns:
            Dictionary containing rule configuration.
        """
        details = {}
        
        # Get rule type
        type_query = f"""
        PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        
        SELECT ?type
        WHERE {{
            <{rule_uri}> guidance:hasType ?type .
        }}
        """
        
        for row in self.graph.query(type_query):
            rule_type = str(row.type)
            details["type"] = rule_type
            
            # Get type-specific properties
            if rule_type == ValidationRuleType.SHACL.value:
                shapes_query = f"""
                SELECT ?file
                WHERE {{
                    <{rule_uri}> guidance:hasShapesFile ?file .
                }}
                """
                for shape_row in self.graph.query(shapes_query):
                    details["shapes_file"] = str(shape_row.file)
                    
            elif rule_type == ValidationRuleType.SEMANTIC.value:
                query_query = f"""
                SELECT ?query
                WHERE {{
                    <{rule_uri}> guidance:hasSPARQLQuery ?query .
                }}
                """
                for query_row in self.graph.query(query_query):
                    details["query"] = str(query_row.query)
                    
            elif rule_type == ValidationRuleType.SYNTAX.value:
                pattern_query = f"""
                SELECT ?pattern
                WHERE {{
                    <{rule_uri}> guidance:hasPattern ?pattern .
                }}
                """
                for pattern_row in self.graph.query(pattern_query):
                    details["pattern"] = str(pattern_row.pattern)
                    
            elif rule_type == ValidationRuleType.SENSITIVE_DATA.value:
                patterns_query = f"""
                SELECT ?pattern
                WHERE {{
                    <{rule_uri}> guidance:hasPattern ?pattern .
                }}
                """
                patterns = []
                for pattern_row in self.graph.query(patterns_query):
                    patterns.append(str(pattern_row.pattern))
                if patterns:
                    details["patterns"] = patterns
                    
        return details 

    def add_imports(self, import_iris: list, base_iri: Optional[str] = None) -> None:
        """
        Add owl:imports triples to the ontology for the given IRIs.
        Args:
            import_iris: List of ontology IRIs to import.
            base_iri: The base ontology IRI to which imports are added. If None, uses the loaded ontology's base.
        """
        if base_iri is None:
            # Try to infer the base IRI from the ontology graph
            for s in self.graph.subjects(RDF.type, OWL.Ontology):
                base_iri = str(s)
                break
            if base_iri is None:
                raise ValueError("Base ontology IRI could not be determined. Please specify base_iri explicitly.")
        base_ref = URIRef(base_iri)
        for import_iri in import_iris:
            self.graph.add((base_ref, OWL.imports, URIRef(import_iri)))
        self.logger.info(f"Added owl:imports for: {import_iris} to {base_iri}") 