from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL

def analyze_guidance():
    g = Graph()
    g.parse("guidance.ttl", format="turtle")
    
    # Define and bind namespaces
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    META = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/meta#")
    g.bind("guidance", GUIDANCE)
    g.bind("meta", META)
    
    # Query 1: Check Module Registry
    print("\nChecking Module Registry:")
    q1 = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?registry ?module
    WHERE {
        ?registry a ?registryClass .
        ?registryClass rdfs:subClassOf* guidance:ModuleRegistry .
        OPTIONAL { ?registry guidance:registeredModule ?module }
    }
    """
    for row in g.query(q1):
        print(f"Registry: {row.registry}, Module: {row.module}")
    
    # Query 2: Check Legacy Support
    print("\nChecking Legacy Support:")
    q2 = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    
    SELECT ?support ?mapping ?source ?target
    WHERE {
        ?support a guidance:LegacySupport .
        OPTIONAL {
            ?support guidance:hasLegacyMapping ?mapping .
            ?mapping guidance:sourceModule ?source ;
                     guidance:targetModule ?target .
        }
    }
    """
    for row in g.query(q2):
        print(f"Support: {row.support}, Mapping: {row.mapping}")
        if row.mapping:
            print(f"  Source: {row.source}")
            print(f"  Target: {row.target}")
    
    # Query 3: Check Meta Integration
    print("\nChecking Meta Integration:")
    q3 = """
    PREFIX meta: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/meta#>
    
    SELECT ?subject ?metaProp ?object
    WHERE {
        ?subject ?metaProp ?object .
        FILTER(STRSTARTS(STR(?metaProp), STR(meta:)))
    }
    """
    for row in g.query(q3):
        print(f"{row.subject} {row.metaProp} {row.object}")

if __name__ == "__main__":
    analyze_guidance() 