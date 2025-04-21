from rdflib import Graph, RDF, OWL, RDFS, Namespace, SH
from rdflib.namespace import XSD
import pprint

def analyze_guidance():
    # Initialize graph
    g = Graph()
    
    # Load the guidance ontology
    g.parse('guidance.ttl', format='turtle')
    
    # Define namespaces
    GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
    
    # Initialize pretty printer
    pp = pprint.PrettyPrinter(indent=2)
    
    print("\n=== Classes ===")
    for s, p, o in g.triples((None, RDF.type, OWL.Class)):
        print(f"\nClass: {s}")
        for _, label, value in g.triples((s, RDFS.label, None)):
            print(f"  Label: {value}")
        for _, comment, value in g.triples((s, RDFS.comment, None)):
            print(f"  Comment: {value}")
    
    print("\n=== Properties ===")
    for s, p, o in g.triples((None, RDF.type, OWL.ObjectProperty)):
        print(f"\nObject Property: {s}")
        for _, label, value in g.triples((s, RDFS.label, None)):
            print(f"  Label: {value}")
        for _, comment, value in g.triples((s, RDFS.comment, None)):
            print(f"  Comment: {value}")
        for _, domain, value in g.triples((s, RDFS.domain, None)):
            print(f"  Domain: {value}")
        for _, range, value in g.triples((s, RDFS.range, None)):
            print(f"  Range: {value}")
    
    print("\n=== SHACL Shapes ===")
    for s, p, o in g.triples((None, RDF.type, SH.NodeShape)):
        print(f"\nShape: {s}")
        for _, label, value in g.triples((s, RDFS.label, None)):
            print(f"  Label: {value}")
        for _, comment, value in g.triples((s, RDFS.comment, None)):
            print(f"  Comment: {value}")
        for _, target, value in g.triples((s, SH.targetClass, None)):
            print(f"  Target Class: {value}")
    
    print("\n=== Individuals ===")
    for s, p, o in g.triples((None, RDF.type, None)):
        if o != OWL.Class and o != OWL.ObjectProperty and o != SH.NodeShape:
            print(f"\nIndividual: {s}")
            print(f"  Type: {o}")
            for _, label, value in g.triples((s, RDFS.label, None)):
                print(f"  Label: {value}")
            for _, comment, value in g.triples((s, RDFS.comment, None)):
                print(f"  Comment: {value}")

if __name__ == "__main__":
    analyze_guidance() 