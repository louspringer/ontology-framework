#!/usr/bin/env python3
"""Fix guidance ontology imports and registry using semantic web tools."""

import logging
from pathlib import Path
import rdflib
from rdflib import Graph, Namespace, RDF, URIRef, Literal
from pyshacl import validate
from rdflib.namespace import RDFS, OWL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_ontology(file_path):
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

def save_ontology(graph, file_path):
    graph.serialize(destination=file_path, format="turtle")
    logger.info(f"Saved ontology to {file_path}")
    # Also save as RDF/XML for diagnostic purposes
    rdfxml_path = file_path.with_suffix('.rdf')
    graph.serialize(destination=rdfxml_path, format="xml")
    logger.info(f"Saved ontology to {rdfxml_path}")

def validate_ontology(graph):
    conforms, _, results_text = validate(graph)
    if not conforms:
        logger.error(f"SHACL validation failed:\n{results_text}")
    else:
        logger.info("SHACL validation passed.")
    return conforms

def ensure_imports(graph, root_uri, module_uris):
    for module_uri in module_uris:
        triple = (root_uri, OWL.imports, URIRef(module_uri))
        if triple not in graph:
            graph.add(triple)
            logger.info(f"Added owl:imports: {root_uri} -> {module_uri}")

def remove_instance(graph, instance_uri):
    to_remove = list(graph.triples((instance_uri, None, None)))
    for triple in to_remove:
        graph.remove(triple)
        logger.info(f"Removed triple: {triple}")

def ensure_registry_and_legacy(graph, guidance_ns, module_uris):
    # Use fully expanded URIs
    registry = URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#ModuleRegistryInstance")
    registry_type = guidance_ns.ModuleRegistry
    registeredModule = guidance_ns.registeredModule
    legacy = URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#LegacySupportInstance")
    legacy_type = guidance_ns.LegacySupport
    hasLegacyMapping = guidance_ns.hasLegacyMapping

    # Remove any existing triples for these instances
    remove_instance(graph, registry)
    remove_instance(graph, legacy)

    # Add ModuleRegistryInstance
    graph.add((registry, RDF.type, registry_type))
    for module_uri in module_uris:
        graph.add((registry, registeredModule, URIRef(module_uri)))
        logger.info(f"Registered module: {module_uri}")
    # Add LegacySupportInstance
    graph.add((legacy, RDF.type, legacy_type))
    for module_uri in module_uris:
        graph.add((legacy, hasLegacyMapping, URIRef(module_uri)))
        logger.info(f"Added legacy mapping: {module_uri}")

def main():
    ontology_path = Path("guidance.ttl")
    graph = load_ontology(ontology_path)
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    graph.bind("guidance", GUIDANCE)
    root_uri = URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    module_uris = [
        "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/core#",
        "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/model#",
        "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/security#",
        "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation#",
        "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/collaboration#",
    ]
    ensure_imports(graph, root_uri, module_uris)
    # Use guidance: prefix for instances
    ensure_registry_and_legacy(graph, GUIDANCE, module_uris)
    if validate_ontology(graph):
        save_ontology(graph, ontology_path)
        logger.info("Guidance ontology imports and registry fixed.")
    else:
        logger.error("Validation failed. Ontology not saved.")

if __name__ == "__main__":
    main() 