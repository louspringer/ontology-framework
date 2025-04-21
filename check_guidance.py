from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib.query import Result
import rdflib
from typing import List, Dict, Any, Tuple

# Load the guidance ontology
g = Graph()
g.parse("guidance.ttl", format="turtle")

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

def get_next_steps() -> Result:
    """Query the guidance ontology for next steps in the integration process."""
    query = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?step ?order ?description
    WHERE {
        ?step rdf:type guidance:IntegrationStep .
        ?step guidance:stepOrder ?order .
        ?step guidance:stepDescription ?description .
    }
    ORDER BY ?order
    """
    
    results = g.query(query)
    return results

def get_test_protocol() -> Result:
    """Query the guidance ontology for test protocol requirements."""
    query = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?protocol ?conformance ?prefixValidation ?namespaceValidation
    WHERE {
        ?protocol rdf:type guidance:TestProtocol .
        ?protocol guidance:conformanceLevel ?conformance .
        ?protocol guidance:requiresPrefixValidation ?prefixValidation .
        ?protocol guidance:requiresNamespaceValidation ?namespaceValidation .
    }
    """
    
    results = g.query(query)
    return results

def get_conformance_requirements() -> Result:
    """Query the guidance ontology for model conformance requirements."""
    query = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?conformance ?level
    WHERE {
        ?conformance rdf:type guidance:ModelConformance .
        ?conformance guidance:conformanceLevel ?level .
    }
    """
    
    results = g.query(query)
    return results

def main() -> None:
    print("Next Steps in Integration Process:")
    print("---------------------------------")
    for row in get_next_steps():
        print(f"Step {row.order}: {row.description}")
    
    print("\nTest Protocol Requirements:")
    print("--------------------------")
    for row in get_test_protocol():
        print(f"Protocol: {row.protocol}")
        print(f"Conformance Level: {row.conformance}")
        print(f"Requires Prefix Validation: {row.prefixValidation}")
        print(f"Requires Namespace Validation: {row.namespaceValidation}")
    
    print("\nConformance Requirements:")
    print("------------------------")
    for row in get_conformance_requirements():
        print(f"Conformance: {row.conformance}")
        print(f"Level: {row.level}")

if __name__ == "__main__":
    main() 