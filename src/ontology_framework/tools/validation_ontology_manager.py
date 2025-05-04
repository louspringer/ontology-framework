from pathlib import Path
from typing import List, Dict, Optional, Union
from rdflib import Literal, URIRef, Graph, Namespace
from rdflib.namespace import RDF, RDFS
import logging

from ..graphdb_client import GraphDBClient

class ValidationOntologyManager:
    """Manages validation rules using GraphDB for safe ontology operations."""
    
    def __init__(self, base_url: str = "http://localhost:7200", repository: str = "validation"):
        self.client = GraphDBClient(base_url, repository)
        self.ns = Namespace("http://example.org/validation#")
        self._setup_validation_structure()
        
    def _setup_validation_structure(self):
        """Initialize the core validation ontology structure."""
        # Create core validation classes
        self.validation_rule_class = URIRef(self.ns["ValidationRule"])
        self.validation_level_class = URIRef(self.ns["ValidationLevel"])
        
        # Add validation properties
        self.has_level = URIRef(self.ns["hasLevel"])
        self.has_description = URIRef(self.ns["hasDescription"])
        
        # Create the initial graph with validation structure
        graph = Graph()
        graph.bind("val", self.ns)
        
        # Add core classes
        graph.add((self.validation_rule_class, RDF.type, RDFS.Class))
        graph.add((self.validation_rule_class, RDFS.label, Literal("Validation Rule")))
        graph.add((self.validation_rule_class, RDFS.comment, Literal("Base class for all validation rules")))
        
        graph.add((self.validation_level_class, RDF.type, RDFS.Class))
        graph.add((self.validation_level_class, RDFS.label, Literal("Validation Level")))
        graph.add((self.validation_level_class, RDFS.comment, Literal("Defines the severity level of validation rules")))
        
        # Add properties
        graph.add((self.has_level, RDF.type, RDF.Property))
        graph.add((self.has_level, RDFS.domain, self.validation_rule_class))
        graph.add((self.has_level, RDFS.range, self.validation_level_class))
        graph.add((self.has_level, RDFS.label, Literal("has validation level")))
        
        graph.add((self.has_description, RDF.type, RDF.Property))
        graph.add((self.has_description, RDFS.domain, self.validation_rule_class))
        graph.add((self.has_description, RDFS.range, RDFS.Literal))
        graph.add((self.has_description, RDFS.label, Literal("has description")))
        
        # Upload the initial structure
        self.client.upload_graph(graph)
        
    def add_validation_rule(self, rule_id: str, description: str, level: str) -> URIRef:
        """Add a new validation rule to the ontology or update if exists."""
        rule_uri = URIRef(self.ns[f"Rule_{rule_id}"])
        level_uri = URIRef(self.ns[f"Level_{level}"])
        
        # Create the update query
        update = f"""
        PREFIX val: <{str(self.ns)}>
        PREFIX rdf: <{str(RDF)}>
        PREFIX rdfs: <{str(RDFS)}>
        
        DELETE {{
            <{str(rule_uri)}> ?p ?o .
            <{str(level_uri)}> ?p2 ?o2 .
        }}
        INSERT {{
            <{str(rule_uri)}> rdf:type val:ValidationRule ;
                             val:hasDescription "{description}" ;
                             val:hasLevel <{str(level_uri)}> .
            <{str(level_uri)}> rdf:type val:ValidationLevel .
        }}
        WHERE {{
            OPTIONAL {{ <{str(rule_uri)}> ?p ?o . }}
            OPTIONAL {{ <{str(level_uri)}> ?p2 ?o2 . }}
        }}
        """
        
        try:
            self.client.update(update)
            return rule_uri
        except Exception as e:
            logging.error(f"Failed to add validation rule: {e}")
            raise
        
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
            results = self.client.query(query)
            if not isinstance(results, dict) or "results" not in results:
                logging.error("Unexpected query result format")
                return []
                
            bindings = results["results"]["bindings"]
            return [
                {
                    "rule": binding["rule"]["value"],
                    "description": binding["description"]["value"],
                    "level": binding.get("level", {}).get("value")
                }
                for binding in bindings
            ]
        except Exception as e:
            logging.error(f"Failed to get validation rules: {e}")
            return []
        
    def validate_rule_exists(self, rule_id: str) -> bool:
        """Check if a validation rule with the given ID exists in the ontology."""
        query = f"""
        PREFIX rdf: <{str(RDF)}>
        PREFIX val: <{str(self.ns)}>
        
        ASK {{
            ?rule rdf:type val:ValidationRule .
            FILTER(?rule = val:Rule_{rule_id})
        }}
        """
        try:
            result = self.client.query(query)
            return result.get("boolean", False)
        except Exception as e:
            logging.error(f"Failed to validate rule existence: {e}")
            return False 