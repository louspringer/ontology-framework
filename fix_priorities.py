from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF

def fix_priorities():
    g = Graph()
    g.parse('guidance.ttl', format='turtle')
    GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ')
    # For each ValidationRule remove integer priorities, keep only string
    for rule in g.subjects(RDF.type, GUIDANCE.ValidationRule):
        priorities = list(g.objects(rule, GUIDANCE.hasPriority))
        for p in priorities:
            if not (isinstance(p, Literal) and isinstance(p.value, str) and p.value in ("HIGH", "MEDIUM", "LOW")):
                g.remove((rule, GUIDANCE.hasPriority, p))
        # If there are multiple string priorities keep only the first
        string_priorities = [p for p in g.objects(rule, GUIDANCE.hasPriority) if isinstance(p, Literal) and isinstance(p.value, str) and p.value in ("HIGH", "MEDIUM", "LOW")]
        if len(string_priorities) > 1:
            for p in string_priorities[1:]:
                g.remove((rule, GUIDANCE.hasPriority, p))
    g.serialize(destination='guidance.ttl', format='turtle')
    print("Fixed priorities for all validation rules.")

if __name__ == '__main__':
    fix_priorities() 