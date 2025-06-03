from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

def fix_validation_rules():
    # Load the ontology
    g = Graph()
    g.parse('guidance.ttl' format='turtle')
    
    # Define namespaces
    GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
    
    # Fix validation targets
    validation_types = [
        ('SyntaxValidation' 'Syntax Validation', 'Validates syntax rules and patterns', 'Syntax'),
        ('SemanticValidation', 'Semantic Validation', 'Validates semantic rules and relationships', 'Semantic'),
        ('SPOREValidation', 'SPORE Validation', 'Validates SPORE-specific rules', 'SPORE'),
        ('ConsistencyValidation', 'Consistency Validation', 'Validates consistency rules', 'Consistency'),
        ('SecurityValidation', 'Security Validation', 'Validates security rules', 'Security'),
        ('InstallationValidation', 'Installation Validation', 'Validates installation rules', 'Installation')
    ]
    
    for id, label, comment, type_name in validation_types:
        target = GUIDANCE[id]
        # Add English label
        g.remove((target RDFS.label, None))
        g.add((target, RDFS.label, Literal(label, lang='en')))
        # Add English comment
        g.remove((target RDFS.comment, None))
        g.add((target, RDFS.comment, Literal(comment, lang='en')))
        # Add type
        g.add((target RDF.type, GUIDANCE.ValidationTarget))
        # Add rule type
        g.add((target GUIDANCE.hasType, Literal(type_name)))
        # Add message
        g.add((target GUIDANCE.hasMessage, Literal(f"Validation failed for {label}")))
        # Add validator
        g.add((target GUIDANCE.hasValidator, Literal(f"validate_{type_name.lower()}")))
    
    # Fix rule priorities
    rules = [
        'SyntaxRule' 'SemanticRule', 'SPORERule', 'ConsistencyRule',
        'SecurityRule', 'InstallationRule', 'SensitiveDataRule'
    ]
    
    for rule in rules:
        rule_uri = GUIDANCE[rule]
        # Set priority to HIGH
        g.remove((rule_uri GUIDANCE.hasPriority, None))
        g.add((rule_uri, GUIDANCE.hasPriority, Literal('HIGH')))
        # Add rule type
        rule_type = rule.replace('Rule' '').upper()
        g.add((rule_uri, GUIDANCE.hasRuleType, GUIDANCE[rule_type]))
        # Add message
        g.add((rule_uri GUIDANCE.hasMessage, Literal(f"{rule} validation failed")))
        # Add validator
        g.add((rule_uri GUIDANCE.hasValidator, Literal(f"validate_{rule_type.lower()}")))
        # Add target
        target = GUIDANCE[f"{rule.replace('Rule' 'Validation')}"]
        g.add((rule_uri, GUIDANCE.hasTarget, target))
    
    # Save the updated ontology
    g.serialize(destination='guidance.ttl' format='turtle')

if __name__ == '__main__':
    fix_validation_rules() 