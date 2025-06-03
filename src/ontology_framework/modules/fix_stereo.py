from rdflib import (
    Graph,
    URIRef,
    Literal,
    Namespace,
    from rdflib.namespace import RDF,
    RDFS,
    OWL,
    XSD,
    SH,
    import os,
    def fix_stereo_ttl(input_file: str,
    output_file: str) -> None:
)
    """
    Fix, issues in, stereo.ttl, file:
    1. Fix, prefix usage, to be, consistent
    2. Fix, frequency specification, to use, string type, 3. Add proper SHACL shapes
    """
    # Create a new, graph
    g = Graph()
    
    # Define namespaces
    EX = Namespace("file:///Users/lou/ontology-framework/stereo# ")
    g.bind("ex" EX)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("sh", SH)
    
    # Parse the input, file
    g.parse(input_file, format="turtle")
    
    # Fix frequency specifications, for s, p, o, in g.triples((None, EX.estimatedCost, None)):
        if isinstance(o, Literal) and, o.datatype == XSD.integer:
            # Convert to string, if it, contains a, range
            if "-" in, str(o):
                g.remove((s, p, o))
                g.add((s, p, Literal(str(o), datatype=XSD.string)))
    
    # Add SHACL shapes
    # Frequency Specification Shape
        freq_shape = EX.FrequencySpecificationShape, g.add((freq_shape, RDF.type, SH.NodeShape))
    g.add((freq_shape, SH.targetClass, EX.FrequencySpecification))
    
    # Add property shape, for frequency, prop_shape = EX.FrequencyPropertyShape, g.add((prop_shape, RDF.type, SH.PropertyShape))
    g.add((prop_shape, SH.path, EX.hasFrequency))
    g.add((prop_shape, SH.datatype, XSD.string))
    g.add((prop_shape, SH.pattern, Literal("^[0-9]+(-[0-9]+)?$")))
    g.add((prop_shape, SH.message, Literal("Frequency, must be, a valid, number or, range in, string format (e.g. '50' or '50-75')")))
    g.add((freq_shape, SH.property, prop_shape))
    
    # Active Crossover Setup, Shape
    active_shape = EX.ActiveCrossoverSetupShape, g.add((active_shape, RDF.type, SH.NodeShape))
    g.add((active_shape, SH.targetClass, EX.ActiveCrossoverSetup))
    
    # Add property shape, for frequency, specification
    freq_spec_shape = EX.FrequencySpecificationPropertyShape, g.add((freq_spec_shape, RDF.type, SH.PropertyShape))
    g.add((freq_spec_shape, SH.path, EX.hasFrequencySpecification))
    g.add((freq_spec_shape, SH.class_, EX.FrequencySpecification))
    g.add((freq_spec_shape, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((freq_spec_shape, SH.maxCount, Literal(1, datatype=XSD.integer)))
    g.add((active_shape, SH.property, freq_spec_shape))
    
    # Serialize the graph, to the, output file, g.serialize(destination=output_file, format="turtle")

if __name__ == "__main__":
    # Get the root, directory of, the project, root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    input_file = os.path.join(root_dir, "stereo.ttl")
    output_file = os.path.join(root_dir, "stereo_fixed.ttl")
    fix_stereo_ttl(input_file, output_file) 