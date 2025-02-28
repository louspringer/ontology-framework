import rdflib


def main():
    # Check rdflib version
    print("rdflib version:", rdflib.__version__)

    # Create a new RDF graph
    g = rdflib.Graph()

    # Add a triple to the graph
    g.add(
        (
            rdflib.URIRef("http://example.org/subject"),
            rdflib.URIRef("http://example.org/predicate"),
            rdflib.Literal("Object"),
        ),
    )

    # Print out the graph in Turtle format
    print("Serialized RDF Graph in Turtle format:")
    print(g.serialize(format="turtle"))


if __name__ == "__main__":
    main()
