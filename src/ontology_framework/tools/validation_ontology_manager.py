from pathlib import Path
from typing import List, Dict, Optional, Union
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS
import logging

from .ontology_manager import OntologyManager

class ValidationOntologyManager(OntologyManager):
    """Manages validation rules using RDFlib for safe ontology operations."""
    
    def __init__(self):
        super().__init__(base_uri="http://example.org/validation#")
        self._setup_validation_structure()
        
    def _setup_validation_structure(self):
        """Initialize the core validation ontology structure."""
        # Create core validation classes
        self.validation_rule_class = self.add_class(
            "ValidationRule",
            "Validation Rule",
            "Base class for all validation rules"
        )
        
        self.validation_level_class = self.add_class(
            "ValidationLevel",
            "Validation Level",
            "Defines the severity level of validation rules"
        )
        
        # Add validation properties
        self.has_level = self.add_property(
            "hasLevel",
            self.validation_rule_class,
            self.validation_level_class,
            "has validation level"
        )
        
        self.has_description = self.add_property(
            "hasDescription",
            self.validation_rule_class,
            RDFS.Literal,
            "has description"
        )
        
    def add_validation_rule(self, rule_id: str, description: str, 
                          level: str) -> URIRef:
        """Add a new validation rule to the ontology or update if exists."""
        rule_uri = self.ns[f"Rule_{rule_id}"]
        
        # Remove any existing triples for this rule
        self.graph.remove((rule_uri, None, None))
        
        # Add the rule as an instance of ValidationRule
        self.graph.add((rule_uri, RDF.type, self.validation_rule_class))
        self.graph.add((rule_uri, self.has_description, Literal(description)))
        
        # Create and link the validation level
        level_uri = self.ns[f"Level_{level}"]
        self.graph.add((level_uri, RDF.type, self.validation_level_class))
        self.graph.add((rule_uri, self.has_level, level_uri))
        
        return rule_uri
        
    def get_validation_rules(self) -> List[Dict[str, Union[str, Optional[str]]]]:
        """Retrieve all validation rules using SPARQL."""
        query = f"""
        PREFIX val: <{str(self.ns)}>
        
        SELECT DISTINCT ?rule ?description ?level
        WHERE {{
            ?rule a val:ValidationRule ;
                  val:hasDescription ?description .
            OPTIONAL {{
                ?rule val:hasLevel ?levelUri .
                ?levelUri a val:ValidationLevel .
                BIND(STRAFTER(STR(?levelUri), "#") AS ?level)
            }}
            FILTER(STRSTARTS(STR(?rule), STR(val:Rule_)))
        }}
        """
        
        try:
            results = self.execute_sparql_query(query)
            if isinstance(results, bool):
                logging.error("Unexpected boolean result from SELECT query")
                return []
                
            return [
                {
                    "rule": str(rule),
                    "description": str(desc),
                    "level": str(level) if level else None
                }
                for rule, desc, level in results
            ]
        except Exception as e:
            logging.error(f"Failed to get validation rules: {e}")
            return []
        
    def validate_rule_exists(self, rule_id: str) -> bool:
        """Check if a validation rule with the given ID exists in the ontology.
        
        Args:
            rule_id (str): The unique identifier of the validation rule to check.
            
        Returns:
            bool: True if the rule exists, False otherwise.
            
        Example:
            >>> manager = ValidationOntologyManager()
            >>> manager.validate_rule_exists("RULE_001")
            True
        """
        # Debug: Print all validation rules in the graph
        for s, p, o in self.graph.triples((None, RDF.type, self.validation_rule_class)):
            logging.debug(f"Found validation rule: {s}")
            
        query = f"""
        PREFIX rdf: <{str(RDF)}>
        PREFIX val: <{str(self.ns)}>
        
        ASK {{
            ?rule rdf:type ?validationRule .
            FILTER(?rule = val:Rule_{rule_id} && ?validationRule = ?validationRuleClass)
            VALUES (?validationRuleClass) {{ (<{str(self.validation_rule_class)}>) }}
        }}
        """
        try:
            return bool(self.execute_sparql_query(query))
        except Exception as e:
            logging.error(f"Failed to validate rule existence: {e}")
            return False 