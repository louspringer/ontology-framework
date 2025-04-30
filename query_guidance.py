from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import rdflib

# Create a graph and parse the guidance ontology
g = Graph()
g.parse("guidance.ttl", format="turtle")

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

# SPARQL query to get validation rules and setup instructions
query = """
PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?subject ?label ?comment ?prop ?propValue
WHERE {
    {
        ?subject a owl:Class .
        ?subject rdfs:label ?label .
        ?subject rdfs:comment ?comment .
        OPTIONAL {
            ?subject ?prop ?propValue .
            FILTER (?prop != rdf:type && ?prop != rdfs:label && ?prop != rdfs:comment)
        }
    }
    UNION
    {
        ?subject a :ValidationRule .
        ?subject rdfs:label ?label .
        ?subject rdfs:comment ?comment .
        OPTIONAL {
            ?subject ?prop ?propValue .
            FILTER (?prop != rdf:type && ?prop != rdfs:label && ?prop != rdfs:comment)
        }
    }
    FILTER (lang(?label) = "en" && lang(?comment) = "en")
}
ORDER BY ?subject ?prop
"""

# Execute the query
results = g.query(query)

# Print the results
print("Project Setup and Validation Rules from Guidance Ontology:")
print("-" * 60)

current_subject = None
for row in results:
    subject_uri = str(row[0])
    if current_subject != subject_uri:
        if current_subject is not None:
            print()
        print(f"\n{row[1]}:")  # Label
        print(f"  Description: {row[2]}")  # Comment
        current_subject = subject_uri
    
    if row[3] and row[4]:  # Property and value
        prop_name = str(row[3]).split('#')[-1]
        prop_value = str(row[4])
        if '#' in prop_value:
            prop_value = prop_value.split('#')[-1]
        print(f"  - {prop_name}: {prop_value}") 