#!/usr/bin/env python
"""
Creates a domain-specific ontology using GuidanceMCPService.
"""

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from ontology_framework.mcp.guidance_mcp_service import GuidanceMCPService
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_project_ontology():
    """Creates a new domain-specific project ontology."""
    logger.info("Creating new project ontology")
    
    # Create a new Graph for the project ontology
    g = Graph()
    PROJECT = Namespace("http://example.org/project#")
    g.bind("project", PROJECT)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    
    # Create the ontology
    g.add((URIRef(PROJECT), RDF.type, OWL.Ontology))
    g.add((URIRef(PROJECT), RDFS.label, Literal("Project Ontology", lang="en")))
    g.add((URIRef(PROJECT), RDFS.comment, Literal("Domain-specific project ontology", lang="en")))
    g.add((URIRef(PROJECT), OWL.versionInfo, Literal("0.1.0")))
    
    # Define core classes
    product_class = URIRef(PROJECT.Product)
    g.add((product_class, RDF.type, OWL.Class))
    g.add((product_class, RDFS.label, Literal("Product", lang="en")))
    g.add((product_class, RDFS.comment, Literal("A product in the domain", lang="en")))
    g.add((product_class, OWL.versionInfo, Literal("0.1.0")))
    
    component_class = URIRef(PROJECT.Component)
    g.add((component_class, RDF.type, OWL.Class))
    g.add((component_class, RDFS.label, Literal("Component", lang="en")))
    g.add((component_class, RDFS.comment, Literal("A component of a product", lang="en")))
    g.add((component_class, OWL.versionInfo, Literal("0.1.0")))
    
    feature_class = URIRef(PROJECT.Feature)
    g.add((feature_class, RDF.type, OWL.Class))
    g.add((feature_class, RDFS.label, Literal("Feature", lang="en")))
    g.add((feature_class, RDFS.comment, Literal("A feature of a product", lang="en")))
    g.add((feature_class, OWL.versionInfo, Literal("0.1.0")))
    
    # Define properties
    has_component = URIRef(PROJECT.hasComponent)
    g.add((has_component, RDF.type, OWL.ObjectProperty))
    g.add((has_component, RDFS.label, Literal("has component", lang="en")))
    g.add((has_component, RDFS.comment, Literal("Links a product to its components", lang="en")))
    g.add((has_component, RDFS.domain, product_class))
    g.add((has_component, RDFS.range, component_class))
    g.add((has_component, OWL.versionInfo, Literal("0.1.0")))
    
    has_feature = URIRef(PROJECT.hasFeature)
    g.add((has_feature, RDF.type, OWL.ObjectProperty))
    g.add((has_feature, RDFS.label, Literal("has feature", lang="en")))
    g.add((has_feature, RDFS.comment, Literal("Links a product to its features", lang="en")))
    g.add((has_feature, RDFS.domain, product_class))
    g.add((has_feature, RDFS.range, feature_class))
    g.add((has_feature, OWL.versionInfo, Literal("0.1.0")))
    
    has_name = URIRef(PROJECT.hasName)
    g.add((has_name, RDF.type, OWL.DatatypeProperty))
    g.add((has_name, RDFS.label, Literal("has name", lang="en")))
    g.add((has_name, RDFS.comment, Literal("The name of an entity", lang="en")))
    g.add((has_name, RDFS.domain, OWL.Thing))
    g.add((has_name, RDFS.range, XSD.string))
    g.add((has_name, OWL.versionInfo, Literal("0.1.0")))
    
    has_version = URIRef(PROJECT.hasVersion)
    g.add((has_version, RDF.type, OWL.DatatypeProperty))
    g.add((has_version, RDFS.label, Literal("has version", lang="en")))
    g.add((has_version, RDFS.comment, Literal("The version of an entity", lang="en")))
    g.add((has_version, RDFS.domain, OWL.Thing))
    g.add((has_version, RDFS.range, XSD.string))
    g.add((has_version, OWL.versionInfo, Literal("0.1.0")))
    
    has_description = URIRef(PROJECT.hasDescription)
    g.add((has_description, RDF.type, OWL.DatatypeProperty))
    g.add((has_description, RDFS.label, Literal("has description", lang="en")))
    g.add((has_description, RDFS.comment, Literal("The description of an entity", lang="en")))
    g.add((has_description, RDFS.domain, OWL.Thing))
    g.add((has_description, RDFS.range, XSD.string))
    g.add((has_description, OWL.versionInfo, Literal("0.1.0")))
    
    # Create instances
    product1 = URIRef(PROJECT.Product1)
    g.add((product1, RDF.type, product_class))
    g.add((product1, RDFS.label, Literal("Product 1", lang="en")))
    g.add((product1, has_name, Literal("Example Product")))
    g.add((product1, has_version, Literal("1.0.0")))
    g.add((product1, has_description, Literal("An example product")))
    
    product2 = URIRef(PROJECT.Product2)
    g.add((product2, RDF.type, product_class))
    g.add((product2, RDFS.label, Literal("Product 2", lang="en")))
    g.add((product2, has_name, Literal("Another Product")))
    g.add((product2, has_version, Literal("0.5.0")))
    g.add((product2, has_description, Literal("Another example product")))
    
    component1 = URIRef(PROJECT.Component1)
    g.add((component1, RDF.type, component_class))
    g.add((component1, RDFS.label, Literal("Component 1", lang="en")))
    g.add((component1, has_name, Literal("Core Component")))
    g.add((component1, has_description, Literal("The core component of the product")))
    
    component2 = URIRef(PROJECT.Component2)
    g.add((component2, RDF.type, component_class))
    g.add((component2, RDFS.label, Literal("Component 2", lang="en")))
    g.add((component2, has_name, Literal("UI Component")))
    g.add((component2, has_description, Literal("The UI component of the product")))
    
    feature1 = URIRef(PROJECT.Feature1)
    g.add((feature1, RDF.type, feature_class))
    g.add((feature1, RDFS.label, Literal("Feature 1", lang="en")))
    g.add((feature1, has_name, Literal("Authentication")))
    g.add((feature1, has_description, Literal("Authentication feature")))
    
    feature2 = URIRef(PROJECT.Feature2)
    g.add((feature2, RDF.type, feature_class))
    g.add((feature2, RDFS.label, Literal("Feature 2", lang="en")))
    g.add((feature2, has_name, Literal("Data Export")))
    g.add((feature2, has_description, Literal("Data export feature")))
    
    # Link instances
    g.add((product1, has_component, component1))
    g.add((product1, has_component, component2))
    g.add((product1, has_feature, feature1))
    g.add((product2, has_component, component2))
    g.add((product2, has_feature, feature2))
    
    # Save the ontology
    output_file = "project.ttl"
    g.serialize(destination=output_file, format="turtle")
    logger.info(f"Project ontology saved to {output_file}")
    
    # Now use GuidanceMCPService to validate and enhance the ontology
    try:
        mcp = GuidanceMCPService(output_file)
        
        # Add imports
        mcp.add_imports(["https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance"])
        
        # Validate the ontology
        result = mcp.validate()
        logger.info("Validation result:")
        logger.info(json.dumps(result, indent=2))
        
        # Save the updated ontology
        mcp.save()
        logger.info(f"Enhanced ontology saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error using GuidanceMCPService: {e}")

if __name__ == "__main__":
    create_project_ontology() 