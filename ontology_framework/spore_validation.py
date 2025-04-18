import logging
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
META = Namespace("http://example.org/guidance#")

class SporeValidator:
    def __init__(self):
        self.graph = Graph()
        self.load_ontologies()
        
    def load_ontologies(self):
        """Load required ontologies for validation"""
        self.graph.parse("spore-xna-governance.ttl", format="turtle")
        self.graph.parse("guidance/modules/validation.ttl", format="turtle")
        
    def validate_spore(self, spore):
        """Validate a spore against governance rules"""
        if not spore:
            raise ValueError("Spore URI is required")
            
        # Check if spore exists
        if not self._spore_exists(spore):
            raise ValueError("Spore not found")
            
        # Validate structure
        if not self._validate_structure(spore):
            return False
            
        # Validate patterns
        if not self._validate_patterns(spore):
            return False
            
        # Validate patches
        if not self._validate_patches(spore):
            return False
            
        return True
        
    def _spore_exists(self, spore):
        """Check if spore exists in graph"""
        query = """
        ASK {
            ?spore a meta:TransformationPattern .
        }
        """
        
        return self.graph.query(query, initBindings={'spore': spore}).askAnswer
        
    def _validate_structure(self, spore):
        """Validate spore structure"""
        query = """
        ASK {
            ?spore a meta:TransformationPattern .
            ?spore rdfs:label ?label .
            ?spore rdfs:comment ?comment .
            ?spore owl:versionInfo ?version .
        }
        """
        
        return self.graph.query(query, initBindings={'spore': spore}).askAnswer
        
    def _validate_patterns(self, spore):
        """Validate transformation patterns"""
        query = """
        ASK {
            ?spore meta:hasPattern ?pattern .
            ?pattern a meta:TransformationPattern .
            ?pattern rdfs:label ?label .
            ?pattern rdfs:comment ?comment .
        }
        """
        
        return self.graph.query(query, initBindings={'spore': spore}).askAnswer
        
    def _validate_patches(self, spore):
        """Validate patches"""
        query = """
        ASK {
            ?spore meta:distributesPatch ?patch .
            ?patch a meta:ConceptPatch .
            ?patch rdfs:label ?label .
            ?patch rdfs:comment ?comment .
        }
        """
        
        return self.graph.query(query, initBindings={'spore': spore}).askAnswer
        
    def validate_shacl(self, spore):
        """Validate spore against SHACL rules"""
        if not spore:
            raise ValueError("Spore URI is required")
            
        # Get SHACL shapes
        shapes = self._get_shacl_shapes()
        
        # Validate against each shape
        for shape in shapes:
            if not self._validate_shape(spore, shape):
                return False
                
        return True
        
    def _get_shacl_shapes(self):
        """Get SHACL shapes for validation"""
        query = """
        SELECT ?shape
        WHERE {
            ?shape a sh:NodeShape .
            ?shape sh:targetClass meta:TransformationPattern .
        }
        """
        
        return [row.shape for row in self.graph.query(query)]
        
    def _validate_shape(self, spore, shape):
        """Validate spore against a SHACL shape"""
        query = """
        ASK {
            ?spore a meta:TransformationPattern .
            ?shape sh:targetClass meta:TransformationPattern .
            ?shape sh:property ?property .
            ?property sh:path ?path .
            ?spore ?path ?value .
        }
        """
        
        return self.graph.query(query, initBindings={
            'spore': spore,
            'shape': shape
        }).askAnswer

def main():
    validator = SporeValidator()
    
    # Example usage
    spore_uri = "http://example.org/spores/example-spore"
    results = validator.validate_spore(spore_uri)
    
    # Log results
    for check, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{check}: {status}")

if __name__ == "__main__":
    main() 