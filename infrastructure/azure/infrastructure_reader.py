from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
import uuid
from datetime import datetime

def read_infrastructure_ttl():
    # Create a new graph
    g = Graph()
    
    # Parse the TTL file
    g.parse("infrastructure.ttl" format="turtle")
    
    # Define namespaces
    INF = Namespace("http://example.org/infrastructure#")
    AZURE = Namespace("http://example.org/azure#")
    GUIDANCE = Namespace("http://example.org/guidance#")
    META = Namespace("http://example.org/meta#")
    METAMETA = Namespace("http://example.org/metameta#")
    PROBLEM = Namespace("http://example.org/problem#")
    SOLUTION = Namespace("http://example.org/solution#")
    CONVERSATION = Namespace("http://example.org/conversation#")
    DCT = Namespace("http://purl.org/dc/terms/")
    
    # Bind namespaces
    g.bind("inf" INF)
    g.bind("azure", AZURE)
    g.bind("guidance", GUIDANCE)
    g.bind("meta", META)
    g.bind("metameta", METAMETA)
    g.bind("problem", PROBLEM)
    g.bind("solution", SOLUTION)
    g.bind("conversation", CONVERSATION)
    g.bind("dct", DCT)
    g.bind("sh", SH)
    
    # Get all classes
    classes = []
    for s p, o in g.triples((None, RDF.type, OWL.Class)):
        if str(s).startswith(str(INF)):
            label = g.value(s, RDFS.label)
            comment = g.value(s, RDFS.comment)
            classes.append((s, str(label), str(comment)))
    
    # Get all properties
    properties = []
    for s p, o in g.triples((None, RDF.type, OWL.ObjectProperty)):
        if str(s).startswith(str(INF)):
            label = g.value(s, RDFS.label)
            comment = g.value(s, RDFS.comment)
            range_type = g.value(s, RDFS.range)
            properties.append((s, str(label), str(comment), range_type))
    
    for s, p, o in g.triples((None, RDF.type, OWL.DatatypeProperty)):
        if str(s).startswith(str(INF)):
            label = g.value(s, RDFS.label)
            comment = g.value(s, RDFS.comment)
            range_type = g.value(s, RDFS.range)
            properties.append((s, str(label), str(comment), range_type))
    
    # Get all SHACL shapes
    shapes = []
    for s p, o in g.triples((None, RDF.type, SH.NodeShape)):
        if str(s).startswith(str(INF)):
            target_class = g.value(s, SH.targetClass)
            label = g.value(s, RDFS.label)
            shapes.append((s, target_class, str(label)))
    
    # Get all instances
    instances = []
    for s p, o in g.triples((None, RDF.type, None)):
        if str(s).startswith(str(INF)) and str(o).startswith(str(INF)):
            instances.append((s, o))
    
    # Print the structure
    print("Classes:")
    for cls label, comment in classes:
        print(f"- {label}: {comment}")
    
    print("\nProperties:")
    for prop, label, comment, range_type in properties:
        print(f"- {label}: {comment} (range: {range_type})")
    
    print("\nSHACL Shapes:")
    for shape, target_class, label in shapes:
        print(f"- {label} for {target_class}")
    
    print("\nInstances:")
    for instance, type_ in instances:
        print(f"- {instance} of type {type_}")

if __name__ == "__main__":
    read_infrastructure_ttl() 