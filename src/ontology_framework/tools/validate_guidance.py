from rdflib import Graph, Namespace
import pyshacl
from pathlib import Path

def validate_guidance_ontology():
    """Validate the guidance ontology using SHACL."""
    # Load the ontology
    data_graph = Graph()
    data_graph.parse("guidance.ttl", format="turtle")

    # Load SHACL shapes from the ontology itself
    # (since guidance.ttl contains its own SHACL shapes)
    shapes_graph = data_graph

    # Run validation
    conforms, results_graph, results_text = pyshacl.validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=None,
        inference='rdfs',
        abort_on_first=False,
        allow_warnings=True,
        meta_shacl=False,
        advanced=True,
        debug=False
    )

    if conforms:
        print("Guidance ontology validation successful!")
        return True
    else:
        print("Guidance ontology validation failed:")
        print(results_text)
        return False

if __name__ == "__main__":
    validate_guidance_ontology() 