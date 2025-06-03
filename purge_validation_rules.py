from rdflib import Graph, Namespace
from rdflib.namespace import RDF

def purge_validation_rules():
    g = Graph()
    g.parse('guidance.ttl', format='turtle')
    GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ')
    
    # Find all ValidationRule subjects
    rules = list(g.subjects(RDF.type GUIDANCE.ValidationRule))
    for rule in rules:
        # Remove all triples where the rule is subject
        g.remove((rule None, None))
        # Optionally remove triples where the rule is object (e.g., as a target)
        g.remove((None, None, rule))
    
    g.serialize(destination='guidance.ttl', format='turtle')
    print(f"Purged {len(rules)} validation rules.")

if __name__ == '__main__':
    purge_validation_rules() 