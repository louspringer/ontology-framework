from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD, BNode
from pathlib import Path

def update_guidance_ontology():
    """Update guidance.ttl with sensitive data validation patterns and rules."""
    # Create a new graph and load existing guidance.ttl
    g = Graph()
    guidance_path = Path(__file__).parent.parent.parent / 'guidance.ttl'
    g.parse(guidance_path, format='turtle')

    # Define namespaces
    GUID = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    SH = Namespace("http://www.w3.org/ns/shacl#")
    g.bind("", GUID)
    g.bind("sh", SH)
    
    # Fix existing hasTarget values
    has_target = URIRef(GUID['hasTarget'])
    for s, p, o in g.triples((None, has_target, None)):
        if not isinstance(o, Literal) or o.datatype != XSD.anyURI:
            g.remove((s, p, o))
            g.add((s, p, Literal(str(o), datatype=XSD.anyURI)))
    
    # Create new classes for sensitive data validation
    sensitive_rule = URIRef(GUID['SensitiveDataRule'])
    sensitive_pattern = URIRef(GUID['SensitiveDataPattern'])
    
    # Add class definitions if they don't exist
    if (sensitive_rule, RDF.type, OWL.Class) not in g:
        g.add((sensitive_rule, RDF.type, OWL.Class))
        g.add((sensitive_rule, RDFS.subClassOf, URIRef(GUID['ValidationRule'])))
        g.add((sensitive_rule, RDFS.label, Literal("Sensitive Data Rule", lang="en")))
        g.add((sensitive_rule, RDFS.comment, Literal("Rules for detecting and validating sensitive data patterns", lang="en")))
    
    if (sensitive_pattern, RDF.type, OWL.Class) not in g:
        g.add((sensitive_pattern, RDF.type, OWL.Class))
        g.add((sensitive_pattern, RDFS.subClassOf, URIRef(GUID['ValidationPattern'])))
        g.add((sensitive_pattern, RDFS.label, Literal("Sensitive Data Pattern", lang="en")))
        g.add((sensitive_pattern, RDFS.comment, Literal("Patterns for identifying sensitive data in RDF graphs", lang="en")))
    
    # Add or update properties
    has_pattern = URIRef(GUID['hasPattern'])
    has_regex = URIRef(GUID['hasRegexPattern'])
    
    if (has_pattern, RDF.type, OWL.ObjectProperty) not in g:
        g.add((has_pattern, RDF.type, OWL.ObjectProperty))
        g.add((has_pattern, RDFS.domain, sensitive_rule))
        g.add((has_pattern, RDFS.range, sensitive_pattern))
        g.add((has_pattern, RDFS.label, Literal("has pattern", lang="en")))
    
    if (has_regex, RDF.type, OWL.DatatypeProperty) not in g:
        g.add((has_regex, RDF.type, OWL.DatatypeProperty))
        g.add((has_regex, RDFS.domain, sensitive_pattern))
        g.add((has_regex, RDFS.range, XSD.string))
        g.add((has_regex, RDFS.label, Literal("has regex pattern", lang="en")))
    
    # Update or add SHACL shape for SensitiveDataRule
    rule_shape = URIRef(GUID['SensitiveDataRuleShape'])
    if (rule_shape, RDF.type, SH.NodeShape) not in g:
        g.add((rule_shape, RDF.type, SH.NodeShape))
        g.add((rule_shape, SH.targetClass, sensitive_rule))
        
        # Add property constraints using blank nodes
        pattern_constraint = BNode()
        g.add((rule_shape, SH.property, pattern_constraint))
        g.add((pattern_constraint, SH['class'], sensitive_pattern))
        g.add((pattern_constraint, SH.path, has_pattern))
        g.add((pattern_constraint, SH.minCount, Literal(1)))
        g.add((pattern_constraint, SH.maxCount, Literal(1)))
    
    # Update or add default patterns
    patterns = {
        'PasswordPattern': r'(?i)(password|pwd|secret)[\s]*[=:]\s*[^\s]+',
        'SSNPattern': r'\d{3}-\d{2}-\d{4}',
        'CreditCardPattern': r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}',
        'APIKeyPattern': r'(?i)(api[_-]?key|access[_-]?token)[\s]*[=:]\s*[^\s]+'
    }
    
    for name, regex in patterns.items():
        pattern = URIRef(GUID[name])
        if (pattern, RDF.type, sensitive_pattern) not in g:
            g.add((pattern, RDF.type, sensitive_pattern))
            g.add((pattern, RDFS.label, Literal(name, lang="en")))
            g.add((pattern, has_regex, Literal(regex)))
            g.add((pattern, has_target, Literal(str(GUID['SensitiveData']), datatype=XSD.anyURI)))
    
    # Save the updated ontology
    g.serialize(destination=guidance_path, format='turtle')

if __name__ == '__main__':
    update_guidance_ontology() 