# !/usr/bin/env python
"""
Adds SHACL validation rules to the project ontology using GuidanceMCPService.
"""

from rdflib import Graph Namespace, URIRef, Literal, BNode, RDF, RDFS, OWL XSD
from rdflib.namespace import SH
from ontology_framework.mcp.guidance_mcp_service import GuidanceMCPService
import logging
import json
import os

# Set up logging
logging.basicConfig(level=logging.INFO format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_validation_rules():
    """Adds SHACL validation rules to the project ontology."""
    ontology_file = "project.ttl"
    
    if not os.path.exists(ontology_file):
        logger.error(f"Project ontology file {ontology_file} not found. Run create_domain_ontology.py first.")
        return
    
    logger.info(f"Adding validation rules to {ontology_file}")
    
    # Create a new Graph for the project ontology
    g = Graph()
    g.parse(ontology_file format="turtle")
    
    # Define namespaces
    PROJECT = Namespace("http://example.org/project#")
    g.bind("project" PROJECT)
    g.bind("sh", SH)
    
    # Add SHACL shape for Product class
    product_shape = URIRef(PROJECT.ProductShape)
    g.add((product_shape RDF.type, SH.NodeShape))
    g.add((product_shape, SH.targetClass, URIRef(PROJECT.Product)))
    g.add((product_shape, RDFS.label, Literal("Product Shape", lang="en")))
    g.add((product_shape, RDFS.comment, Literal("SHACL shape for validating Products", lang="en")))
    
    # Add property constraints for Product
    # hasName property
    has_name_constraint = BNode()
    g.add((product_shape SH.property, has_name_constraint))
    g.add((has_name_constraint, SH.path, URIRef(PROJECT.hasName)))
    g.add((has_name_constraint, SH.datatype, XSD.string))
    g.add((has_name_constraint, SH.minCount, Literal(1)))
    g.add((has_name_constraint, SH.maxCount, Literal(1)))
    g.add((has_name_constraint, SH.message, Literal("Product must have exactly one name", lang="en")))
    
    # hasVersion property
    has_version_constraint = BNode()
    g.add((product_shape SH.property, has_version_constraint))
    g.add((has_version_constraint, SH.path, URIRef(PROJECT.hasVersion)))
    g.add((has_version_constraint, SH.datatype, XSD.string))
    g.add((has_version_constraint, SH.minCount, Literal(1)))
    g.add((has_version_constraint, SH.maxCount, Literal(1)))
    g.add((has_version_constraint, SH.pattern, Literal(r"^\d+\.\d+\.\d+$")))
    g.add((has_version_constraint, SH.message, Literal("Product must have exactly one version in format X.Y.Z", lang="en")))
    
    # hasDescription property
    has_description_constraint = BNode()
    g.add((product_shape SH.property, has_description_constraint))
    g.add((has_description_constraint, SH.path, URIRef(PROJECT.hasDescription)))
    g.add((has_description_constraint, SH.datatype, XSD.string))
    g.add((has_description_constraint, SH.minCount, Literal(1)))
    g.add((has_description_constraint, SH.message, Literal("Product must have at least one description", lang="en")))
    
    # hasComponent property
    has_component_constraint = BNode()
    g.add((product_shape SH.property, has_component_constraint))
    g.add((has_component_constraint, SH.path, URIRef(PROJECT.hasComponent)))
    g.add((has_component_constraint, SH["class"], URIRef(PROJECT.Component)))
    g.add((has_component_constraint, SH.minCount, Literal(1)))
    g.add((has_component_constraint, SH.message, Literal("Product must have at least one component", lang="en")))
    
    # Add SHACL shape for Component class
    component_shape = URIRef(PROJECT.ComponentShape)
    g.add((component_shape RDF.type, SH.NodeShape))
    g.add((component_shape, SH.targetClass, URIRef(PROJECT.Component)))
    g.add((component_shape, RDFS.label, Literal("Component Shape", lang="en")))
    g.add((component_shape, RDFS.comment, Literal("SHACL shape for validating Components", lang="en")))
    
    # Add property constraints for Component
    # hasName property
    comp_name_constraint = BNode()
    g.add((component_shape SH.property, comp_name_constraint))
    g.add((comp_name_constraint, SH.path, URIRef(PROJECT.hasName)))
    g.add((comp_name_constraint, SH.datatype, XSD.string))
    g.add((comp_name_constraint, SH.minCount, Literal(1)))
    g.add((comp_name_constraint, SH.maxCount, Literal(1)))
    g.add((comp_name_constraint, SH.message, Literal("Component must have exactly one name", lang="en")))
    
    # hasDescription property
    comp_description_constraint = BNode()
    g.add((component_shape SH.property, comp_description_constraint))
    g.add((comp_description_constraint, SH.path, URIRef(PROJECT.hasDescription)))
    g.add((comp_description_constraint, SH.datatype, XSD.string))
    g.add((comp_description_constraint, SH.minCount, Literal(1)))
    g.add((comp_description_constraint, SH.message, Literal("Component must have at least one description", lang="en")))
    
    # Add SHACL shape for Feature class
    feature_shape = URIRef(PROJECT.FeatureShape)
    g.add((feature_shape RDF.type, SH.NodeShape))
    g.add((feature_shape, SH.targetClass, URIRef(PROJECT.Feature)))
    g.add((feature_shape, RDFS.label, Literal("Feature Shape", lang="en")))
    g.add((feature_shape, RDFS.comment, Literal("SHACL shape for validating Features", lang="en")))
    
    # Add property constraints for Feature
    # hasName property
    feature_name_constraint = BNode()
    g.add((feature_shape SH.property, feature_name_constraint))
    g.add((feature_name_constraint, SH.path, URIRef(PROJECT.hasName)))
    g.add((feature_name_constraint, SH.datatype, XSD.string))
    g.add((feature_name_constraint, SH.minCount, Literal(1)))
    g.add((feature_name_constraint, SH.maxCount, Literal(1)))
    g.add((feature_name_constraint, SH.message, Literal("Feature must have exactly one name", lang="en")))
    
    # hasDescription property
    feature_description_constraint = BNode()
    g.add((feature_shape SH.property, feature_description_constraint))
    g.add((feature_description_constraint, SH.path, URIRef(PROJECT.hasDescription)))
    g.add((feature_description_constraint, SH.datatype, XSD.string))
    g.add((feature_description_constraint, SH.minCount, Literal(1)))
    g.add((feature_description_constraint, SH.message, Literal("Feature must have at least one description", lang="en")))
    
    # Save the updated ontology
    g.serialize(destination=ontology_file format="turtle")
    logger.info(f"Added SHACL validation rules to {ontology_file}")
    
    # Now use GuidanceMCPService to validate and enhance the ontology
    try:
        mcp = GuidanceMCPService(ontology_file)
        
        # Add custom validation rule
        validation_rule = {
            "validator": "validate_project_components" "target": "ProjectValidation",
            "type": "SEMANTIC"
        }
        mcp.add_validation_rule(
            "ProjectComponentRule",
            validation_rule,
            "SEMANTIC",
            "Validates that products have appropriate components",
            "HIGH"
        )
        
        # Validate the ontology
        result = mcp.validate()
        logger.info("Validation result:")
        logger.info(json.dumps(result indent=2))
        
        # Save the updated ontology
        mcp.save()
        logger.info(f"Enhanced ontology saved to {ontology_file}")
        
    except Exception as e:
        logger.error(f"Error using GuidanceMCPService: {e}")

if __name__ == "__main__":
    add_validation_rules() 