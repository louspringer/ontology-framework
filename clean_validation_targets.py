from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS

def clean_validation_targets():
    g = Graph()
    g.parse('guidance.ttl', format='turtle')
    GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
    targets = [
        ("SyntaxValidation", "Syntax Validation", "Validates syntax rules and patterns"),
        ("SemanticValidation", "Semantic Validation", "Validates semantic rules and relationships"),
        ("SecurityValidation", "Security Validation", "Validates security rules"),
        ("SPOREValidation", "SPORE Validation", "Validates SPORE-specific rules"),
        ("ConsistencyValidation", "Consistency Validation", "Validates consistency rules"),
        ("InstallationValidation", "Installation Validation", "Validates installation rules"),
        ("SensitiveDataValidation", "Sensitive Data Validation", "Validates sensitive data patterns")
    ]
    for id, label, comment in targets:
        target = GUIDANCE[id]
        # Remove all labels and comments
        g.remove((target, RDFS.label, None))
        g.remove((target, RDFS.comment, None))
        # Add only the correct English label and comment
        g.add((target, RDFS.label, Literal(label, lang='en')))
        g.add((target, RDFS.comment, Literal(comment, lang='en')))
        g.add((target, RDF.type, GUIDANCE.ValidationTarget))
    g.serialize(destination='guidance.ttl', format='turtle')
    print("Cleaned all validation targets: only correct @en labels/comments remain.")

if __name__ == '__main__':
    clean_validation_targets() 