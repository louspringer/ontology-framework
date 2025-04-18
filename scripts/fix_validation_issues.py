#!/usr/bin/env python3
"""
Script to fix validation issues in ontology modules by adding SHACL shapes and example instances.
"""

import logging
import os
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OntologyFixer:
    def __init__(self):
        self.base_uri = "http://ontologies.louspringer.com/guidance/modules/"

    def add_shacl_shapes(self, g: Graph, module_name: str) -> None:
        """Add comprehensive SHACL shapes to validate the ontology structure."""
        ns = Namespace(f"{self.base_uri}{module_name}#")
        
        # NodeShape for all classes
        class_shape = BNode()
        g.add((class_shape, RDF.type, SH.NodeShape))
        g.add((class_shape, SH.targetClass, OWL.Class))
        
        # Property shape for rdfs:label
        label_shape = BNode()
        g.add((class_shape, SH.property, label_shape))
        g.add((label_shape, SH.path, RDFS.label))
        g.add((label_shape, SH.minCount, Literal(1)))
        g.add((label_shape, SH.datatype, XSD.string))
        
        # Property shape for rdfs:comment
        comment_shape = BNode()
        g.add((class_shape, SH.property, comment_shape))
        g.add((comment_shape, SH.path, RDFS.comment))
        g.add((comment_shape, SH.minCount, Literal(1)))
        g.add((comment_shape, SH.datatype, XSD.string))
        
        # Property shape for owl:versionInfo
        version_shape = BNode()
        g.add((class_shape, SH.property, version_shape))
        g.add((version_shape, SH.path, OWL.versionInfo))
        g.add((version_shape, SH.minCount, Literal(1)))
        g.add((version_shape, SH.datatype, XSD.string))

        # NodeShape for all properties
        prop_shape = BNode()
        g.add((prop_shape, RDF.type, SH.NodeShape))
        g.add((prop_shape, SH.targetClass, RDF.Property))
        
        # Property shape for rdfs:domain
        domain_shape = BNode()
        g.add((prop_shape, SH.property, domain_shape))
        g.add((domain_shape, SH.path, RDFS.domain))
        g.add((domain_shape, SH.minCount, Literal(1)))
        
        # Property shape for rdfs:range
        range_shape = BNode()
        g.add((prop_shape, SH.property, range_shape))
        g.add((range_shape, SH.path, RDFS.range))
        g.add((range_shape, SH.minCount, Literal(1)))

    def add_example_instances(self, g: Graph, module_name: str) -> None:
        """Add example instances for each class in the ontology."""
        ns = Namespace(f"{self.base_uri}{module_name}#")
        
        # Find all classes
        for class_uri in g.subjects(RDF.type, OWL.Class):
            class_name = class_uri.split('#')[-1] if '#' in class_uri else class_uri.split('/')[-1]
            
            # Create two example instances for each class
            for i in range(1, 3):
                instance = URIRef(f"{ns}example{class_name}{i}")
                g.add((instance, RDF.type, class_uri))
                g.add((instance, RDFS.label, Literal(f"Example {class_name} {i}")))
                g.add((instance, RDFS.comment, Literal(f"This is example instance {i} of class {class_name}")))
                
                # Add example property values if the class has properties
                for prop in g.subjects(RDFS.domain, class_uri):
                    prop_range = g.value(prop, RDFS.range)
                    if prop_range:
                        if prop_range == XSD.string:
                            g.add((instance, prop, Literal(f"Example value {i}")))
                        elif prop_range == XSD.integer:
                            g.add((instance, prop, Literal(i)))
                        elif prop_range == XSD.dateTime:
                            g.add((instance, prop, Literal(f"2024-03-21T12:00:0{i}Z", datatype=XSD.dateTime)))
                        else:
                            # For object properties, create or reference another instance
                            range_instance = URIRef(f"{ns}example{prop_range.split('#')[-1]}{i}")
                            g.add((instance, prop, range_instance))

    def fix_date_formats(self, g: Graph) -> None:
        """Fix date format issues by ensuring proper ISO 8601 format."""
        for s, p, o in g.triples((None, None, None)):
            if isinstance(o, Literal) and o.datatype == XSD.dateTime:
                date_str = str(o)
                if 'T' not in date_str:
                    # Convert YYYY-MM-DD to YYYY-MM-DDT00:00:00Z
                    new_date = f"{date_str}T00:00:00Z"
                    g.remove((s, p, o))
                    g.add((s, p, Literal(new_date, datatype=XSD.dateTime)))

    def process_module(self, file_path: str) -> None:
        """Process a single module file."""
        try:
            g = Graph()
            g.parse(file_path, format="turtle")
            
            # Extract module name from file path
            module_name = Path(file_path).stem
            
            # Add SHACL shapes
            self.add_shacl_shapes(g, module_name)
            
            # Add example instances
            self.add_example_instances(g, module_name)
            
            # Fix date formats
            self.fix_date_formats(g)
            
            # Save the updated ontology
            g.serialize(file_path, format="turtle")
            logger.info(f"Updated {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")

    def process_all_modules(self, directory: str = "guidance/modules") -> None:
        """Process all .ttl files in the specified directory."""
        for file_name in os.listdir(directory):
            if file_name.endswith(".ttl"):
                file_path = os.path.join(directory, file_name)
                logger.info(f"Processing {file_path}")
                self.process_module(file_path)

def main():
    fixer = OntologyFixer()
    fixer.process_all_modules()
    logger.info("Completed processing all modules")

if __name__ == "__main__":
    main() 