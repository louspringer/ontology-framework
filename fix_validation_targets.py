from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

def fix_validation_targets():
    # Load the ontology
    g = Graph()
    g.parse('guidance.ttl', format='turtle')
    
    # Define namespaces
    GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
    
    # Fix validation targets
    validation_targets = [
        ('SyntaxValidation', 'Syntax Validation', 'Validates syntax rules and patterns'),
        ('SemanticValidation', 'Semantic Validation', 'Validates semantic rules and relationships'),
        ('SPOREValidation', 'SPORE Validation', 'Validates SPORE-specific rules'),
        ('ConsistencyValidation', 'Consistency Validation', 'Validates consistency rules'),
        ('SecurityValidation', 'Security Validation', 'Validates security rules'),
        ('InstallationValidation', 'Installation Validation', 'Validates installation rules'),
        ('SensitiveDataValidation', 'Sensitive Data Validation', 'Validates sensitive data patterns')
    ]
    
    for id, label, comment in validation_targets:
        target = GUIDANCE[id]
        # Remove existing labels and comments
        g.remove((target, RDFS.label, None))
        g.remove((target, RDFS.comment, None))
        # Add English label and comment
        g.add((target, RDFS.label, Literal(label, lang='en')))
        g.add((target, RDFS.comment, Literal(comment, lang='en')))
        # Add type
        g.add((target, RDF.type, GUIDANCE.ValidationTarget))
    
    # Fix validation rules
    validation_rules = [
        ('SyntaxRule', 'Syntax', 'Validates syntax rules and patterns', 'validate_syntax', 'SyntaxValidation'),
        ('SemanticRule', 'Semantic', 'Validates semantic rules and relationships', 'validate_semantic', 'SemanticValidation'),
        ('SPORERule', 'SPORE', 'Validates SPORE-specific rules', 'validate_spore', 'SPOREValidation'),
        ('ConsistencyRule', 'Consistency', 'Validates consistency rules', 'validate_consistency', 'ConsistencyValidation'),
        ('SecurityRule', 'Security', 'Validates security rules', 'validate_security', 'SecurityValidation'),
        ('InstallationRule', 'Installation', 'Validates installation rules', 'validate_installation', 'InstallationValidation'),
        ('SensitiveDataRule', 'SensitiveData', 'Validates sensitive data patterns', 'validate_sensitive_data', 'SensitiveDataValidation')
    ]
    
    for rule_id, type_name, message, validator, target_id in validation_rules:
        rule_uri = GUIDANCE[rule_id]
        target_uri = GUIDANCE[target_id]
        
        # Remove existing properties
        g.remove((rule_uri, GUIDANCE.hasPriority, None))
        g.remove((rule_uri, GUIDANCE.hasType, None))
        g.remove((rule_uri, GUIDANCE.hasMessage, None))
        g.remove((rule_uri, GUIDANCE.hasValidator, None))
        g.remove((rule_uri, GUIDANCE.hasTarget, None))
        
        # Add rule properties
        g.add((rule_uri, RDF.type, GUIDANCE.ValidationRule))
        g.add((rule_uri, RDFS.label, Literal(rule_id)))
        g.add((rule_uri, GUIDANCE.hasType, Literal(type_name)))
        g.add((rule_uri, GUIDANCE.hasMessage, Literal(message)))
        g.add((rule_uri, GUIDANCE.hasValidator, Literal(validator)))
        g.add((rule_uri, GUIDANCE.hasTarget, target_uri))
        
        # Add priority as integer
        priority = Literal(2, datatype=XSD.integer)  # HIGH = 2
        g.add((rule_uri, GUIDANCE.hasPriority, priority))
    
    # Save the updated ontology
    g.serialize(destination='guidance.ttl', format='turtle')
    print("Patched all validation targets with English labels and comments.")

if __name__ == '__main__':
    fix_validation_targets() 