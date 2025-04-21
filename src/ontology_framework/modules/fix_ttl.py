from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SHACL
import os

def fix_ttl_file(input_file: str, output_file: str = None) -> None:
    """Fix TTL file issues using RDFLib.
    
    Args:
        input_file: Path to input TTL file
        output_file: Optional path to output file. If None, overwrites input file.
    """
    # Create a new graph
    g = Graph()
    
    # Bind the correct prefixes
    g.bind('rdf', URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
    g.bind('rdfs', URIRef('http://www.w3.org/2000/01/rdf-schema#'))
    g.bind('owl', URIRef('http://www.w3.org/2002/07/owl#'))
    g.bind('xsd', URIRef('http://www.w3.org/2001/XMLSchema#'))
    g.bind('sh', URIRef('http://www.w3.org/ns/shacl#'))
    
    # Parse the input file
    g.parse(input_file, format='turtle')
    
    # Create namespace for the ontology
    ex = Namespace('./stereo#')
    g.bind('ex', ex)
    
    # Add SHACL shapes if they don't exist
    shapes_graph = Graph()
    
    # Problem Space Shape
    problem_shape = BNode()
    shapes_graph.add((problem_shape, RDF.type, SHACL.NodeShape))
    shapes_graph.add((problem_shape, SHACL.targetClass, ex.ProblemSpace))
    
    # Add label property constraint
    label_constraint = BNode()
    shapes_graph.add((problem_shape, SHACL.property, label_constraint))
    shapes_graph.add((label_constraint, SHACL.path, RDFS.label))
    shapes_graph.add((label_constraint, SHACL.minCount, Literal(1)))
    shapes_graph.add((label_constraint, SHACL.maxCount, Literal(1)))
    shapes_graph.add((label_constraint, SHACL.datatype, XSD.string))
    
    # Add comment property constraint
    comment_constraint = BNode()
    shapes_graph.add((problem_shape, SHACL.property, comment_constraint))
    shapes_graph.add((comment_constraint, SHACL.path, RDFS.comment))
    shapes_graph.add((comment_constraint, SHACL.minCount, Literal(1)))
    shapes_graph.add((comment_constraint, SHACL.datatype, XSD.string))
    
    # Merge shapes into main graph
    g += shapes_graph
    
    # Write the output
    if output_file is None:
        output_file = input_file
    
    g.serialize(destination=output_file, format='turtle')

if __name__ == '__main__':
    # Get the absolute path to stereo.ttl
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    stereo_ttl = os.path.join(base_dir, 'stereo.ttl')
    
    # Fix the file
    fix_ttl_file(stereo_ttl)
    print(f"Fixed TTL file: {stereo_ttl}") 