import os
import json
from pathlib import Path
from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace

# Define namespaces
SPORE = Namespace("https://example.org/spore#")
EX = Namespace("https://example.org/bfg9k#")

class SporeInjector:
    def __init__(self, spore_path="bfg9k-containment.ttl"):
        self.spore = Graph()
        self.spore.parse(spore_path, format="turtle")
        self.base_dir = Path(os.path.dirname(os.path.abspath(spore_path)))
        
    def inject_paths(self):
        """Inject file paths into the spore package."""
        # Get the spore package
        spore_package = self.spore.value(predicate=RDF.type, object=SPORE.SporePackage)
        if not spore_package:
            raise ValueError("No spore:SporePackage found in the ontology")
            
        # Get included files
        included_files = list(self.spore.objects(spore_package, SPORE.includesFile))
        
        # Update paths
        for file_path in included_files:
            abs_path = self.base_dir / str(file_path)
            if abs_path.exists():
                # Update the path in the spore
                self.spore.remove((spore_package, SPORE.includesFile, file_path))
                self.spore.add((spore_package, SPORE.includesFile, Literal(str(abs_path))))
                
        # Handle WASM paths
        wasm_tool = self.spore.value(predicate=RDF.type, object=EX.BFG9KTool)
        if wasm_tool:
            wasm_path = self.spore.value(wasm_tool, EX.hasPath)
            if wasm_path:
                abs_wasm_path = self.base_dir / "static" / "wasm" / "bfg9k_rdf_engine.wasm"
                if abs_wasm_path.exists():
                    self.spore.remove((wasm_tool, EX.hasPath, wasm_path))
                    self.spore.add((wasm_tool, EX.hasPath, Literal(str(abs_wasm_path))))
                    
    def save(self, output_path=None):
        """Save the updated spore package."""
        if output_path is None:
            output_path = self.base_dir / "bfg9k-containment.ttl"
        self.spore.serialize(destination=str(output_path), format="turtle")
        
def main():
    injector = SporeInjector()
    injector.inject_paths()
    injector.save()
    
if __name__ == "__main__":
    main() 