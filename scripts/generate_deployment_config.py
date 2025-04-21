#!/usr/bin/env python3
"""Generate deployment configuration ontology using rdflib."""

from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

def generate_deployment_config():
    """Generate deployment configuration ontology."""
    g = Graph()
    
    # Define namespaces
    deployment = URIRef("http://example.org/deployment#")
    
    # Add ontology metadata
    g.add((deployment, RDF.type, OWL.Ontology))
    g.add((deployment, RDFS.label, Literal("Deployment Configuration Ontology")))
    g.add((deployment, RDFS.comment, Literal("Ontology for managing deployment configurations")))
    g.add((deployment, OWL.versionInfo, Literal("1.0.0")))
    
    # Define classes
    DeploymentConfig = URIRef(deployment + "DeploymentConfig")
    Environment = URIRef(deployment + "Environment")
    ResourceRequirements = URIRef(deployment + "ResourceRequirements")
    
    for cls, label, comment in [
        (DeploymentConfig, "Deployment Configuration", "Configuration for application deployment"),
        (Environment, "Environment", "Deployment environment (dev, staging, prod)"),
        (ResourceRequirements, "Resource Requirements", "CPU and memory requirements for deployment")
    ]:
        g.add((cls, RDF.type, OWL.Class))
        g.add((cls, RDFS.label, Literal(label)))
        g.add((cls, RDFS.comment, Literal(comment)))
    
    # Define properties
    hasEnvironment = URIRef(deployment + "hasEnvironment")
    hasResourceRequirements = URIRef(deployment + "hasResourceRequirements")
    port = URIRef(deployment + "port")
    replicas = URIRef(deployment + "replicas")
    memoryRequest = URIRef(deployment + "memoryRequest")
    cpuRequest = URIRef(deployment + "cpuRequest")
    memoryLimit = URIRef(deployment + "memoryLimit")
    cpuLimit = URIRef(deployment + "cpuLimit")
    
    for prop, label, domain, range_type in [
        (hasEnvironment, "has environment", DeploymentConfig, Environment),
        (hasResourceRequirements, "has resource requirements", DeploymentConfig, ResourceRequirements),
        (port, "port", DeploymentConfig, XSD.integer),
        (replicas, "replicas", DeploymentConfig, XSD.integer),
        (memoryRequest, "memory request", ResourceRequirements, XSD.string),
        (cpuRequest, "CPU request", ResourceRequirements, XSD.string),
        (memoryLimit, "memory limit", ResourceRequirements, XSD.string),
        (cpuLimit, "CPU limit", ResourceRequirements, XSD.string)
    ]:
        g.add((prop, RDF.type, OWL.ObjectProperty if range_type in [Environment, ResourceRequirements] else OWL.DatatypeProperty))
        g.add((prop, RDFS.label, Literal(label)))
        g.add((prop, RDFS.domain, domain))
        g.add((prop, RDFS.range, range_type))
    
    # Define individuals
    for env, label in [
        ("development", "Development"),
        ("staging", "Staging"),
        ("production", "Production")
    ]:
        env_uri = URIRef(deployment + env)
        g.add((env_uri, RDF.type, Environment))
        g.add((env_uri, RDFS.label, Literal(label)))
    
    # Example configurations
    for config, env, port_val, replicas_val, resources in [
        ("devConfig", "development", 8080, 1, {
            "memoryRequest": "128Mi",
            "cpuRequest": "500m",
            "memoryLimit": "256Mi",
            "cpuLimit": "1000m"
        }),
        ("prodConfig", "production", 80, 3, {
            "memoryRequest": "512Mi",
            "cpuRequest": "1000m",
            "memoryLimit": "1Gi",
            "cpuLimit": "2000m"
        })
    ]:
        config_uri = URIRef(deployment + config)
        g.add((config_uri, RDF.type, DeploymentConfig))
        g.add((config_uri, RDFS.label, Literal(f"{env.title()} Configuration")))
        g.add((config_uri, hasEnvironment, URIRef(deployment + env)))
        g.add((config_uri, port, Literal(port_val, datatype=XSD.integer)))
        g.add((config_uri, replicas, Literal(replicas_val, datatype=XSD.integer)))
        
        # Add resource requirements
        resources_bnode = BNode()
        g.add((resources_bnode, RDF.type, ResourceRequirements))
        for key, value in resources.items():
            g.add((resources_bnode, URIRef(deployment + key), Literal(value)))
        g.add((config_uri, hasResourceRequirements, resources_bnode))
    
    return g

if __name__ == "__main__":
    g = generate_deployment_config()
    g.serialize("guidance/modules/deployment_config.ttl", format="turtle") 