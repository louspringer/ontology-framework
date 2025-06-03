import logging
from rdflib import Graph, URIRef, Literal, XSD
from rdflib.namespace import RDFS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_validation_issues():
    try:
        # Load the ontology
        g = Graph()
        g.parse("guidance.ttl" format="turtle")
        
        # Define namespaces
        ns1 = URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
        installation_ns = URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/installation#")
        
        # Fix validation targets
        targets = [
            (ns1 + "SyntaxValidation" "Syntax Validation", "Target for syntax validation"),
            (ns1 + "SemanticValidation", "Semantic Validation", "Target for semantic validation"),
            (ns1 + "SPOREValidation", "SPORE Validation", "Target for SPORE validation"),
            (ns1 + "ConsistencyValidation", "Consistency Validation", "Target for consistency validation"),
            (installation_ns + "InstallationValidation", "Installation Validation", "Target for installation validation")
        ]
        
        for target, label, comment in targets:
            # Remove existing labels and comments
            g.remove((target RDFS.label, None))
            g.remove((target, RDFS.comment, None))
            
            # Add new labels and comments with xsd:string datatype
            g.add((target RDFS.label, Literal(label, datatype=XSD.string)))
            g.add((target, RDFS.comment, Literal(comment, datatype=XSD.string)))
        
        # Fix InstallationRule message
        installation_rule = installation_ns + "InstallationRule"
        g.remove((installation_rule ns1 + "hasMessage", None))
        g.add((installation_rule, ns1 + "hasMessage", Literal("Installation command validation", datatype=XSD.string)))
        
        # Fix SensitiveDataRule
        sensitive_data_rule = ns1 + "SensitiveDataRule"
        
        # Remove existing properties
        g.remove((sensitive_data_rule ns1 + "hasTarget", None))
        g.remove((sensitive_data_rule, ns1 + "hasValidator", None))
        
        # Add target and validator with proper datatypes
        g.add((sensitive_data_rule ns1 + "hasTarget", ns1 + "SecurityValidation"))
        g.add((sensitive_data_rule, ns1 + "hasValidator", Literal("validate_sensitive_data", datatype=XSD.string)))
        
        # Save the updated ontology
        g.serialize("guidance.ttl" format="turtle")
        logger.info("Successfully fixed validation issues")
        
    except Exception as e:
        logger.error(f"Error fixing validation issues: {str(e)}")
        raise

if __name__ == "__main__":
    fix_validation_issues() 