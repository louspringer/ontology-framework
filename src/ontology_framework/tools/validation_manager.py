from pathlib import Path
from typing import Optional, List, Dict
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib.query import ResultRow

# Define namespaces
ONT = Namespace("http://example.org/ontology#")

class ValidationManager:
    def __init__(self, ontology_path: Optional[str] = None):
        """Initialize the ValidationManager with an optional ontology path."""
        self.graph = Graph()
        self.default_path = Path(__file__).parent.parent / "ontologies" / "validation_rules.ttl"
        if ontology_path:
            self.load_ontology(ontology_path)
        else:
            # Default to validation_rules.ttl in the ontologies directory
            self.load_ontology(str(self.default_path))

    def load_ontology(self, path: str) -> None:
        """Load the validation rules ontology from a file."""
        self.graph.parse(path, format="turtle")
        self.graph.bind("ont", ONT)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)

    def add_validation_rule(self, rule_name: str, rule_value: str) -> None:
        """Add a new validation rule to the ontology."""
        rule_uri = ONT[rule_name]
        self.graph.add((rule_uri, RDF.type, ONT.ValidationRule))
        self.graph.add((rule_uri, ONT.hasValue, Literal(rule_value)))
        self.graph.add((rule_uri, RDFS.label, Literal(rule_name, lang="en")))

    def get_validation_rules(self) -> List[Dict[str, str]]:
        """Query all validation rules using SPARQL."""
        query = """
        SELECT ?rule ?value WHERE {
            ?rule a ont:ValidationRule ;
                  ont:hasValue ?value .
        }
        """
        results = []
        for row in self.graph.query(query):
            if isinstance(row, ResultRow):
                results.append({
                    "rule": str(row[0]),  # Access by index instead of attribute
                    "value": str(row[1])
                })
        return results

    def save_ontology(self, path: Optional[str] = None) -> None:
        """Save the ontology back to a file."""
        save_path = path if path else str(self.default_path)
        # Ensure the directory exists
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        self.graph.serialize(destination=save_path, format="turtle")
