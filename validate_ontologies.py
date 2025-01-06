import rdflib
import os

# List of ontology files to validate
ontology_files = [
    "solution_space.ttl",
    "problem_space.ttl",
    "project_risks.ttl",
    "ai_tools.ttl",
    "meta-guidance.ttl",
    "metameta-core.ttl",
    "creative_analogies.ttl",
    "ssh-debug-ontology.ttl",
    "solution_space_fixed.ttl",
    "meta-core.ttl"
]

def validate_ontology(file_path):
    try:
        g = rdflib.Graph()
        g.parse(file_path, format='turtle')
        print(f"{file_path}: Valid RDF")
    except Exception as e:
        print(f"{file_path}: Error - {e}")

def main():
    for ontology_file in ontology_files:
        if os.path.exists(ontology_file):
            validate_ontology(ontology_file)
        else:
            print(f"{ontology_file}: File not found.")

if __name__ == "__main__":
    main()
