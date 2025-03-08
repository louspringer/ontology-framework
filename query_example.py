import requests
import json

def run_sparql_query(query):
    """Send a SPARQL query to the endpoint and print the results."""
    response = requests.post('http://localhost:5001/sparql',
                           json={'query': query},
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        results = response.json()
        print(json.dumps(results, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Example queries for namespace exploration
namespace_queries = [
    """
    # List all available namespaces
    SELECT DISTINCT ?prefix ?uri
    WHERE {
        ?s ?p ?o .
        BIND(REPLACE(STR(?s), "^([^#]*#).*$", "$1") AS ?uri)
        BIND(REPLACE(?uri, "^.*/([^/]*)$", "$1") AS ?prefix)
    }
    ORDER BY ?prefix
    """,
    
    """
    # Get all classes in a specific namespace (replace 'meta' with your namespace)
    PREFIX meta: <./meta#>
    SELECT DISTINCT ?class ?label ?comment
    WHERE {
        ?class a rdfs:Class .
        FILTER(STRSTARTS(STR(?class), STR(meta:)))
        OPTIONAL { ?class rdfs:label ?label }
        OPTIONAL { ?class rdfs:comment ?comment }
    }
    ORDER BY ?class
    """,
    
    """
    # Get all instances of classes in a namespace (replace 'meta' with your namespace)
    PREFIX meta: <./meta#>
    SELECT DISTINCT ?instance ?class ?label
    WHERE {
        ?instance a ?class .
        FILTER(STRSTARTS(STR(?class), STR(meta:)))
        OPTIONAL { ?instance rdfs:label ?label }
    }
    ORDER BY ?class ?instance
    """,
    
    """
    # Get all properties in a namespace with their domains and ranges (replace 'meta' with your namespace)
    PREFIX meta: <./meta#>
    SELECT DISTINCT ?property ?domain ?range ?label ?comment
    WHERE {
        ?property a rdf:Property .
        FILTER(STRSTARTS(STR(?property), STR(meta:)))
        OPTIONAL { ?property rdfs:domain ?domain }
        OPTIONAL { ?property rdfs:range ?range }
        OPTIONAL { ?property rdfs:label ?label }
        OPTIONAL { ?property rdfs:comment ?comment }
    }
    ORDER BY ?property
    """,
    
    """
    # Get all relationships between instances in a namespace (replace 'meta' with your namespace)
    PREFIX meta: <./meta#>
    SELECT DISTINCT ?subject ?predicate ?object
    WHERE {
        ?subject ?predicate ?object .
        FILTER(STRSTARTS(STR(?subject), STR(meta:)) && 
               STRSTARTS(STR(?predicate), STR(meta:)) && 
               STRSTARTS(STR(?object), STR(meta:)))
    }
    ORDER BY ?subject ?predicate ?object
    """
]

if __name__ == '__main__':
    print("Getting graph information...")
    response = requests.get('http://localhost:5001/info')
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    
    print("\nRunning namespace exploration queries...")
    for i, query in enumerate(namespace_queries, 1):
        print(f"\nQuery {i}:")
        print(query.strip())
        print("\nResults:")
        run_sparql_query(query) 