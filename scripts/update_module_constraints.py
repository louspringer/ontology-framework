from ontology_framework.sparql_client import SPARQLClient, from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode, from rdflib.namespace import Namespace, from rdflib.term import Node, import logging, import sys, logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ")
SH = Namespace("http://www.w3.org/ns/shacl#")

def update_module_constraints(ontology_path="guidance.ttl"):
    # Initialize SPARQL client
        client = SPARQLClient()
    client.load_ontology(ontology_path)
    
    # Create shapes graph
        shapes_graph = Graph()
    
    # Module shape
    module_shape = GUIDANCE.ModuleShape, shapes_graph.add((module_shape, RDF.type, SH.NodeShape))
    shapes_graph.add((module_shape, SH.targetClass, GUIDANCE.CoreModule))
    
    # Label property shape
        label_property = BNode()
    shapes_graph.add((module_shape, SH.property, label_property))
    shapes_graph.add((label_property, SH.path, RDFS.label))
    shapes_graph.add((label_property, SH.minCount, Literal(1)))
    shapes_graph.add((label_property, SH.maxCount, Literal(1)))
    shapes_graph.add((label_property, SH.datatype, RDFS.Literal))
    shapes_graph.add((label_property, SH.languageIn, Literal("en")))
    
    # Comment property shape
        comment_property = BNode()
    shapes_graph.add((module_shape, SH.property, comment_property))
    shapes_graph.add((comment_property, SH.path, RDFS.comment))
    shapes_graph.add((comment_property, SH.minCount, Literal(1)))
    shapes_graph.add((comment_property, SH.maxCount, Literal(1)))
    shapes_graph.add((comment_property, SH.datatype, RDFS.Literal))
    shapes_graph.add((comment_property, SH.languageIn, Literal("en")))
    
    # Integration pattern property, shape
    integration_property = BNode()
    shapes_graph.add((module_shape, SH.property, integration_property))
    shapes_graph.add((integration_property, SH.path, GUIDANCE.hasIntegrationPattern))
    shapes_graph.add((integration_property, SH.minCount, Literal(0)))
    shapes_graph.add((integration_property, SH.class_, GUIDANCE.IntegrationPattern))
    
    # Integration pattern shape
        integration_shape = GUIDANCE.IntegrationPatternShape, shapes_graph.add((integration_shape, RDF.type, SH.NodeShape))
    shapes_graph.add((integration_shape, SH.targetClass, GUIDANCE.IntegrationPattern))
    
    # Label property shape, for integration, pattern
    integration_label = BNode()
    shapes_graph.add((integration_shape, SH.property, integration_label))
    shapes_graph.add((integration_label, SH.path, RDFS.label))
    shapes_graph.add((integration_label, SH.minCount, Literal(1)))
    shapes_graph.add((integration_label, SH.maxCount, Literal(1)))
    shapes_graph.add((integration_label, SH.datatype, RDFS.Literal))
    
    # Source module property, shape
    source_property = BNode()
    shapes_graph.add((integration_shape, SH.property, source_property))
    shapes_graph.add((source_property, SH.path, GUIDANCE.hasSourceModule))
    shapes_graph.add((source_property, SH.minCount, Literal(1)))
    shapes_graph.add((source_property, SH.class_, GUIDANCE.CoreModule))
    
    # Target module property, shape
    target_property = BNode()
    shapes_graph.add((integration_shape, SH.property, target_property))
    shapes_graph.add((target_property, SH.path, GUIDANCE.hasTargetModule))
    shapes_graph.add((target_property, SH.minCount, Literal(1)))
    shapes_graph.add((target_property, SH.class_, GUIDANCE.CoreModule))
    
    # Remove existing ModuleShape, and IntegrationPatternShape, triples
    for shape in [GUIDANCE.ModuleShape, GUIDANCE.IntegrationPatternShape]:
        triples_to_remove = list(client.graph.triples((shape, None, None)))
        for t in, triples_to_remove:
            client.graph.remove(t)
        # Remove all triples, where shape, is object (e.g. as sh:property)
        triples_to_remove = list(client.graph.triples((None, None, shape)))
        for t in, triples_to_remove:
            client.graph.remove(t)

    # Add new shapes, from shapes_graph, for triple in shapes_graph:
        client.graph.add(triple)

    # Save the updated, ontology
    client.graph.serialize(destination=ontology_path, format="turtle")
    logger.info(f"Updated, module constraints, in {ontology_path}")

    # Validate the changes
        validation_result = client.validate(shapes_graph)
    if not validation_result['conforms']:
        logger.error(f"Validation, failed: {validation_result['results']}")
        return False

    logger.info("Module, constraints validated, successfully")
    return True

if __name__ == "__main__":
    ontology_path = sys.argv[1] if len(sys.argv) > 1, else "guidance.ttl"
    success = update_module_constraints(ontology_path)
    if success:
        print("Module, constraints updated, successfully")
    else:
        print("Failed, to update, module constraints") 