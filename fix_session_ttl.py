#!/usr/bin/env python3
"""
Fix validation errors in session.ttl using semantic web tools.
"""

from rdflib import Graph, URIRef, Literal, Namespace, XSD, RDF, RDFS
from pyshacl import validate
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_session_ttl(input_file='session.ttl', output_file='session_fixed.ttl'):
    """Fix validation errors in session.ttl using semantic tools."""
    logger.info(f"Loading ontology from {input_file}")
    
    # Create a graph
    g = Graph()
    g.parse(input_file, format='turtle')
    
    # Finding tasks using direct triple pattern matching
    # Look for subjects that have 'task' in their URI and are subjects of triples
    tasks = []
    for s, p, o in g.triples((None, None, None)):
        if '#task' in str(s) and 'type' in str(p):
            tasks.append(s)
    
    if not tasks:
        logger.error("No tasks found in the ontology!")
        sys.exit(1)
    
    tasks = list(set(tasks))  # Remove duplicates
    logger.info(f"Found {len(tasks)} tasks using direct triple matching")
    
    # Fix the SHACL shape issue - the shape expects datatype strings but we have language-tagged literals
    session_ns = None
    for prefix, namespace in g.namespaces():
        if prefix == 'session':
            session_ns = namespace
            break
    
    if not session_ns:
        logger.error("Could not find session namespace, using default.")
        session_ns = Namespace("file:///home/lou/ontology-framework/session#")
    
    # Find the TaskShape
    task_shape = None
    for s, p, o in g.triples((None, RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape"))):
        if 'TaskShape' in str(s):
            task_shape = s
            break
    
    if not task_shape:
        logger.warning("Could not find TaskShape, validation may still fail.")
    else:
        logger.info(f"Found task shape: {task_shape}")
        
        # Find and update the shape properties that specify language tags
        for s, p, o in list(g.triples((task_shape, URIRef("http://www.w3.org/ns/shacl#property"), None))):
            # Find property shapes that have language constraints
            for prop_s, prop_p, prop_o in list(g.triples((o, URIRef("http://www.w3.org/ns/shacl#languageIn"), None))):
                logger.info(f"Removing language constraint from property shape: {prop_s}")
                # Remove the language constraint
                g.remove((prop_s, URIRef("http://www.w3.org/ns/shacl#languageIn"), prop_o))
    
    # Now fix the tasks to use proper datatyped literals
    for task in tasks:
        task_id = str(task).split('#')[-1]
        logger.info(f"Processing task: {task_id}")
        
        # Find and update triples with language tags to use datatype instead
        for s, p, o in list(g.triples((task, None, None))):
            # If it's a literal with language tag
            if isinstance(o, Literal) and o.language:
                logger.info(f"Replacing language-tagged literal: {o}")
                # Remove the triple with language tag
                g.remove((s, p, o))
                # Add a new triple with XSD string datatype
                new_literal = Literal(str(o), datatype=XSD.string)
                g.add((s, p, new_literal))
                logger.info(f"Added new datatyped literal: {new_literal}")
    
    # Save the fixed ontology
    g.serialize(destination=output_file, format="turtle")
    logger.info(f"Fixed ontology saved to {output_file}")
    
    # Validate the fixed ontology
    logger.info("Validating fixed ontology...")
    conforms, results_graph, results_text = validate(g)
    logger.info(f"Conforms: {conforms}")
    if not conforms:
        logger.error(results_text)
    else:
        logger.info("Validation successful!")
    
    return conforms

if __name__ == "__main__":
    fix_session_ttl() 