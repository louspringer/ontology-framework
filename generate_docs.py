from rdflib import Graph, Namespace, RDF, URIRef, OWL, RDFS
from pathlib import Path
import mdformat

def generate_markdown():
    print("Starting markdown generation...")
    
    # Load the ontology
    g = Graph()
    g.parse("secure-ontologist-prompt.ttl", format="turtle")
    print(f"Loaded {len(g)} triples")
    
    # Debug: print all triples
    print("\nDEBUG: All triples in graph:")
    for s, p, o in g:
        print(f"{s} {p} {o}")
    
    # Load SPARQL query from file
    with open("generate_docs.sparql", "r") as f:
        query = f.read().strip()
    print("Loaded SPARQL query")
    
    # Execute query and collect results
    print("Executing SPARQL query...")
    results = g.query(query)
    print(f"Got {len(results)} results")
    
    # Collect all markdown content first
    markdown_content = []
    for row in results:
        print(f"Processing: {row.markdown[:50]}...")
        markdown_content.append(row.markdown)
    
    # Join and format markdown
    full_markdown = "\n".join(markdown_content)
    formatted_markdown = mdformat.text(full_markdown)
    
    # Write formatted markdown to file
    with open("secure-ontologist-prompt.md", "w") as f:
        f.write(formatted_markdown)
    
    print("Done!")

if __name__ == "__main__":
    generate_markdown() 