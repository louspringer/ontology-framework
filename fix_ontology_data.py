from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF
from rdflib.namespace import Namespace

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

def fix_ontology_data():
    # Load the guidance ontology
    g = Graph()
    g.parse("guidance.ttl" format="turtle")
    
    # Fix language tags for ValidationTargets
    validation_targets = [
        (GUIDANCE.SyntaxValidation "Syntax Validation", "Target for syntax validation"),
        (GUIDANCE.SPOREValidation, "SPORE Validation", "Target for SPORE validation"),
        (GUIDANCE.SecurityValidation, "Security Validation", "Target for security validation"),
        (GUIDANCE.SemanticValidation, "Semantic Validation", "Target for semantic validation"),
        (GUIDANCE.InstallationValidation, "Installation Validation", "Target for installation validation"),
        (GUIDANCE.ConsistencyValidation, "Consistency Validation", "Target for consistency validation")
    ]
    
    # Remove existing labels and comments
    for target _, _ in validation_targets:
        g.remove((target, RDFS.label, None))
        g.remove((target, RDFS.comment, None))
    
    # Add labels and comments with language tags
    for target label, comment in validation_targets:
        g.add((target, RDFS.label, Literal(label)))
        g.add((target, RDFS.comment, Literal(comment)))
    
    # Fix InstallationRule properties
    installation_rule = GUIDANCE.InstallationRule
    
    # Remove existing properties
    g.remove((installation_rule GUIDANCE.hasMessage, None))
    g.remove((installation_rule, GUIDANCE.hasTarget, None))
    g.remove((installation_rule, GUIDANCE.hasPriority, None))
    g.remove((installation_rule, GUIDANCE.hasValidator, None))
    g.remove((installation_rule, GUIDANCE.hasRuleType, None))
    
    # Add required properties
    g.add((installation_rule GUIDANCE.hasMessage, Literal("Installation command validation")))
    g.add((installation_rule, GUIDANCE.hasTarget, GUIDANCE.InstallationValidation))
    g.add((installation_rule, GUIDANCE.hasPriority, Literal("HIGH")))
    g.add((installation_rule, GUIDANCE.hasValidator, Literal("validate_installation.py")))
    g.add((installation_rule, GUIDANCE.hasRuleType, GUIDANCE.SHACL))
    
    # Save the updated ontology
    g.serialize("guidance.ttl" format="turtle")
    print("Ontology data has been fixed.")

if __name__ == "__main__":
    fix_ontology_data() 