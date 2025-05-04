from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import pyshacl
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_module_organization():
    g = Graph()
    g.parse("guidance_updated.ttl", format="turtle")
    
    # Define validation rules in SHACL
    shapes_graph = Graph()
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    
    # Core module shape
    shapes_graph.add((GUIDANCE.CoreModuleShape, RDF.type, SH.NodeShape))
    shapes_graph.add((GUIDANCE.CoreModuleShape, SH.targetClass, GUIDANCE.CoreModule))
    shapes_graph.add((GUIDANCE.CoreModuleShape, SH.property, GUIDANCE.labelProperty))
    shapes_graph.add((GUIDANCE.CoreModuleShape, SH.property, GUIDANCE.commentProperty))
    
    # Label property shape
    shapes_graph.add((GUIDANCE.labelProperty, SH.path, RDFS.label))
    shapes_graph.add((GUIDANCE.labelProperty, SH.minCount, Literal(1)))
    shapes_graph.add((GUIDANCE.labelProperty, SH.maxCount, Literal(1)))
    
    # Comment property shape
    shapes_graph.add((GUIDANCE.commentProperty, SH.path, RDFS.comment))
    shapes_graph.add((GUIDANCE.commentProperty, SH.minCount, Literal(1)))
    shapes_graph.add((GUIDANCE.commentProperty, SH.maxCount, Literal(1)))
    
    # Validate the graph
    conforms, results_graph, results_text = pyshacl.validate(
        g,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_error=False
    )
    
    if conforms:
        logger.info("Module organization validation passed")
        return True
    else:
        logger.error(f"Validation failed:\n{results_text}")
        return False

def check_orphaned_modules():
    g = Graph()
    g.parse("guidance_updated.ttl", format="turtle")
    
    # Query for any remaining orphaned modules
    q = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?module ?type
    WHERE {
        ?module a ?type .
        FILTER NOT EXISTS { ?other guidance:hasModule ?module }
        FILTER(?type != owl:Ontology)
        FILTER(?type != guidance:CoreModule)
    }
    """
    
    orphaned = list(g.query(q))
    if orphaned:
        logger.warning(f"Found {len(orphaned)} remaining orphaned modules:")
        for module, type in orphaned:
            logger.warning(f"Module: {module} (Type: {type})")
        return False
    else:
        logger.info("No orphaned modules found")
        return True

if __name__ == "__main__":
    if validate_module_organization() and check_orphaned_modules():
        print("All validation checks passed")
    else:
        print("Some validation checks failed - see log for details") 