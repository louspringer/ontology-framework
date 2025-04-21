from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from typing import List, Dict, Any, Tuple
import datetime

def add_validation_rules(g: Graph) -> None:
    """Add detailed validation rules to the guidance graph."""
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    
    # Prefix Validation Rules
    prefix_shape = GUIDANCE.PrefixValidationShape
    g.add((prefix_shape, RDF.type, SH.NodeShape))
    g.add((prefix_shape, SH.targetClass, GUIDANCE.IntegrationStep))
    g.add((prefix_shape, RDFS.label, Literal("Prefix Validation Rules")))
    g.add((prefix_shape, RDFS.comment, Literal("Rules for validating prefix usage")))
    
    # Add property shapes for prefix validation
    prefix_property = BNode()
    g.add((prefix_shape, SH.property, prefix_property))
    g.add((prefix_property, SH.path, GUIDANCE.stepOrder))
    g.add((prefix_property, SH.datatype, XSD.string))
    g.add((prefix_property, SH.minCount, Literal(1)))
    g.add((prefix_property, SH.maxCount, Literal(1)))
    g.add((prefix_property, SH.pattern, Literal("^[0-9]+$")))
    g.add((prefix_property, SH.message, Literal("Step order must be a positive integer")))
    
    # Namespace Validation Rules
    namespace_shape = GUIDANCE.NamespaceValidationShape
    g.add((namespace_shape, RDF.type, SH.NodeShape))
    g.add((namespace_shape, SH.targetClass, GUIDANCE.IntegrationStep))
    g.add((namespace_shape, RDFS.label, Literal("Namespace Validation Rules")))
    g.add((namespace_shape, RDFS.comment, Literal("Rules for validating namespace usage")))
    
    # Add property shapes for namespace validation
    namespace_property = BNode()
    g.add((namespace_shape, SH.property, namespace_property))
    g.add((namespace_property, SH.path, GUIDANCE.stepDescription))
    g.add((namespace_property, SH.datatype, XSD.string))
    g.add((namespace_property, SH.minCount, Literal(1)))
    g.add((namespace_property, SH.maxCount, Literal(1)))
    g.add((namespace_property, SH.message, Literal("Step must have a description")))
    
    # Model Conformance Rules
    conformance_shape = GUIDANCE.ModelConformanceShape
    g.add((conformance_shape, RDF.type, SH.NodeShape))
    g.add((conformance_shape, SH.targetClass, GUIDANCE.TestProtocol))
    g.add((conformance_shape, RDFS.label, Literal("Model Conformance Rules")))
    g.add((conformance_shape, RDFS.comment, Literal("Rules for model conformance validation")))
    
    # Add property shapes for conformance validation
    conformance_property = BNode()
    g.add((conformance_shape, SH.property, conformance_property))
    g.add((conformance_property, SH.path, GUIDANCE.conformanceLevel))
    g.add((conformance_property, SH.datatype, XSD.string))
    g.add((conformance_property, SH.message, Literal("Conformance level must be STRICT, MODERATE, or RELAXED")))
    
    # Add allowed values using SH.hasValue
    for value in ["STRICT", "MODERATE", "RELAXED"]:
        g.add((conformance_property, SH.hasValue, Literal(value)))

def check_consistency(g: Graph) -> List[str]:
    """Perform SPARQL consistency checks on the guidance graph."""
    checks = []
    
    # Check 1: Verify all integration steps have required properties
    query1 = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?step ?missing
    WHERE {
        ?step rdf:type guidance:IntegrationStep .
        OPTIONAL { ?step guidance:stepOrder ?order }
        OPTIONAL { ?step guidance:stepDescription ?desc }
        BIND(IF(!BOUND(?order) || !BOUND(?desc), "Missing required properties", "") AS ?missing)
        FILTER(?missing != "")
    }
    """
    results1 = g.query(query1)
    for row in results1:
        checks.append(f"Consistency Error: {row.step} is missing required properties")
    
    # Check 2: Verify step order sequence
    query2 = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?step ?order
    WHERE {
        ?step rdf:type guidance:IntegrationStep .
        ?step guidance:stepOrder ?order .
    }
    ORDER BY ?order
    """
    results2 = g.query(query2)
    orders = [int(row.order) for row in results2]
    if orders != sorted(orders):
        checks.append("Consistency Error: Step orders are not sequential")
    if orders != list(range(1, len(orders) + 1)):
        checks.append("Consistency Error: Step orders are not continuous")
    
    # Check 3: Verify test protocol requirements
    query3 = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?protocol ?level ?prefix ?namespace
    WHERE {
        ?protocol rdf:type guidance:TestProtocol .
        OPTIONAL { ?protocol guidance:conformanceLevel ?level }
        OPTIONAL { ?protocol guidance:requiresPrefixValidation ?prefix }
        OPTIONAL { ?protocol guidance:requiresNamespaceValidation ?namespace }
        FILTER(!BOUND(?level) || !BOUND(?prefix) || !BOUND(?namespace))
    }
    """
    results3 = g.query(query3)
    for row in results3:
        checks.append(f"Consistency Error: Test protocol {row.protocol} is missing required properties")
    
    return checks

def main() -> None:
    # Load the updated guidance
    g = Graph()
    g.parse("guidance_updated.ttl", format="turtle")
    
    # Add validation rules
    print("Adding validation rules...")
    add_validation_rules(g)
    
    # Perform consistency checks
    print("\nPerforming consistency checks...")
    issues = check_consistency(g)
    
    if issues:
        print("\nConsistency Issues Found:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("\nNo consistency issues found!")
    
    # Save the updated guidance with validation rules
    g.serialize("guidance_validated.ttl", format="turtle")
    print("\nUpdated guidance saved as 'guidance_validated.ttl'")

if __name__ == "__main__":
    main() 