import logging
from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from ontology_framework.sparql_client import SPARQLClient
import pyshacl
import os

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
SH = Namespace("http://www.w3.org/ns/shacl#")

def validate_module_constraints():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize SPARQL client
        client = SPARQLClient()
        
        # Load guidance ontology
        guidance_path = os.getenv('GUIDANCE_ONTOLOGY_PATH', 'guidance.ttl')
        logger.info(f"Loading guidance ontology from {guidance_path}")
        client.load_ontology(guidance_path)
        
        # Create shapes graph
        shapes_graph = Graph()
        
        # Add ModuleShape
        module_shape = URIRef(f"{GUIDANCE}ModuleShape")
        shapes_graph.add((module_shape, RDF.type, SH.NodeShape))
        shapes_graph.add((module_shape, SH.targetClass, GUIDANCE.CoreModule))
        
        # Add label property
        label_property = BNode()
        shapes_graph.add((module_shape, SH.property, label_property))
        shapes_graph.add((label_property, SH.path, RDFS.label))
        shapes_graph.add((label_property, SH.minCount, Literal(1, datatype=XSD.integer)))
        shapes_graph.add((label_property, SH.maxCount, Literal(1, datatype=XSD.integer)))
        shapes_graph.add((label_property, SH.datatype, RDFS.Literal))
        shapes_graph.add((label_property, SH.languageIn, Literal("en")))
        
        # Add comment property
        comment_property = BNode()
        shapes_graph.add((module_shape, SH.property, comment_property))
        shapes_graph.add((comment_property, SH.path, RDFS.comment))
        shapes_graph.add((comment_property, SH.minCount, Literal(1, datatype=XSD.integer)))
        shapes_graph.add((comment_property, SH.maxCount, Literal(1, datatype=XSD.integer)))
        shapes_graph.add((comment_property, SH.datatype, RDFS.Literal))
        
        # Add integration pattern property
        integration_property = BNode()
        shapes_graph.add((module_shape, SH.property, integration_property))
        shapes_graph.add((integration_property, SH.path, GUIDANCE.hasIntegrationPattern))
        shapes_graph.add((integration_property, SH.minCount, Literal(0, datatype=XSD.integer)))
        shapes_graph.add((integration_property, SH.class_, GUIDANCE.IntegrationPattern))
        
        # Add IntegrationPatternShape
        pattern_shape = URIRef(f"{GUIDANCE}IntegrationPatternShape")
        shapes_graph.add((pattern_shape, RDF.type, SH.NodeShape))
        shapes_graph.add((pattern_shape, SH.targetClass, GUIDANCE.IntegrationPattern))
        
        # Add label property
        pattern_label_property = BNode()
        shapes_graph.add((pattern_shape, SH.property, pattern_label_property))
        shapes_graph.add((pattern_label_property, SH.path, RDFS.label))
        shapes_graph.add((pattern_label_property, SH.minCount, Literal(1, datatype=XSD.integer)))
        shapes_graph.add((pattern_label_property, SH.maxCount, Literal(1, datatype=XSD.integer)))
        shapes_graph.add((pattern_label_property, SH.datatype, RDFS.Literal))
        
        # Add source module property
        source_property = BNode()
        shapes_graph.add((pattern_shape, SH.property, source_property))
        shapes_graph.add((source_property, SH.path, GUIDANCE.hasSourceModule))
        shapes_graph.add((source_property, SH.minCount, Literal(1, datatype=XSD.integer)))
        shapes_graph.add((source_property, SH.class_, GUIDANCE.CoreModule))
        
        # Add target module property
        target_property = BNode()
        shapes_graph.add((pattern_shape, SH.property, target_property))
        shapes_graph.add((target_property, SH.path, GUIDANCE.hasTargetModule))
        shapes_graph.add((target_property, SH.minCount, Literal(1, datatype=XSD.integer)))
        shapes_graph.add((target_property, SH.class_, GUIDANCE.CoreModule))
        
        # Validate against shapes
        logger.info("Validating module constraints...")
        conforms, results_graph, results_text = pyshacl.validate(
            client.graph,
            shacl_graph=shapes_graph,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=False,
            allow_warnings=False,
            meta_shacl=False,
            debug=False
        )
        
        if conforms:
            logger.info("Module constraints validation successful!")
            return True
        else:
            logger.error("Module constraints validation failed:")
            logger.error(results_text)
            return False
            
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        return False

if __name__ == '__main__':
    validate_module_constraints() 