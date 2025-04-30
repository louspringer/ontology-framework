from rdflib import Graph
from rdflib.namespace import SH, RDF, RDFS

def analyze_shapes():
    g = Graph()
    g.parse('src/ontology_framework/validation/validation_shapes.ttl', format='turtle')
    print('Loaded validation shapes successfully\n')
    
    # Query to get all shapes and their target classes
    shapes_query = """
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX val: <http://example.org/validation#>
    PREFIX code: <http://example.org/code#>
    
    SELECT DISTINCT ?shape ?targetClass ?propertyPath ?pattern ?message
    WHERE {
        ?shape a sh:NodeShape ;
               sh:targetClass ?targetClass .
        OPTIONAL {
            ?shape sh:property ?prop .
            ?prop sh:path ?propertyPath .
            OPTIONAL { ?prop sh:pattern ?pattern }
            OPTIONAL { ?prop sh:message ?message }
        }
    }
    ORDER BY ?shape
    """
    
    print('Validation Shapes Analysis:')
    print('==========================\n')
    
    for row in g.query(shapes_query):
        print(f'Shape: {row.shape}')
        print(f'Target Class: {row.targetClass}')
        if row.propertyPath:
            print(f'Property Path: {row.propertyPath}')
        if row.pattern:
            print(f'Pattern: {row.pattern}')
        if row.message:
            print(f'Message: {row.message}')
        print('-' * 50)

if __name__ == '__main__':
    analyze_shapes() 