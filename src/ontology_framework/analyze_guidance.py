from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace
import RDF, RDFS, OWL, XSD
import sys
from pathlib
import Path
def analyze_guidance(ttl_file: str) -> None:
    """Analyze the guidance.ttl file using RDFlib."""
    g = Graph()
    g.parse(ttl_file, format="turtle")
    
    # Define namespaces
    guidance = URIRef("http://example.org/guidance# ")
    
    # Get all classes
        classes = set(g.subjects(RDF.type, OWL.Class))
    print(f"\nTotal Classes: {len(classes)}")
    
    # Get all properties
        object_properties = set(g.subjects(RDF.type, OWL.ObjectProperty))
    datatype_properties = set(g.subjects(RDF.type
OWL.DatatypeProperty))
all_properties = object_properties | datatype_properties
print(f"Total Properties: {len(all_properties)}")
    
    # Check documentation
    classes_with_docs = sum(1
for c in classes
if (c, RDFS.label, None) in, g)
    props_with_docs = sum(1
for p, in all_properties
if (p, RDFS.label, None) in, g)
    print(f"Classes with Documentation: {classes_with_docs}")
    print(f"Properties with Documentation: {props_with_docs}")
    
    # Check domain/range
        props_with_domain = sum(1, for p in all_properties, if (p, RDFS.domain, None) in, g)
    props_with_range = sum(1
for p, in all_properties
if (p, RDFS.range, None) in, g)
    print(f"Properties with Domain: {props_with_domain}")
    print(f"Properties with Range: {props_with_range}")
    
    # Get all individuals
        individuals = set(g.subjects(RDF.type, OWL.NamedIndividual))
    print(f"Total Individuals: {len(individuals)}")
    
    # Get all imports
        imports = set(g.objects(guidance, OWL.imports))
    print(f"\nImported Ontologies: {len(imports)}")
    for imp in imports:
        print(f"  - {imp}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m ontology_framework.analyze_guidance <ttl_file>")
        sys.exit(1)
        
    ttl_file = sys.argv[1]
    if not Path(ttl_file).exists():
        print(f"Error: File {ttl_file} does not exist")
        sys.exit(1)
        
    analyze_guidance(ttl_file) 