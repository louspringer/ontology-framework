"""
Ontology registration functionality for the ontology framework.

This module provides functionality for registering and loading ontologies,
including version tracking and dependency management.
"""

# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

from typing import Dict, List, Optional, Set, Union
import logging
from pathlib import Path
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from .exceptions import RegistrationError

logger = logging.getLogger(__name__)


def onto_register_ontology(ontology_file: Union[str, Path], 
                          version: str,
                          dependencies: Optional[List[str]] = None) -> None:
    """Register an ontology with version and dependency information.
    
    Args:
        ontology_file: Path to ontology TTL file
        version: Version string (MAJOR.MINOR.PATCH)
        dependencies: Optional list of dependency URIs
        
    Raises:
        RegistrationError: If registration fails
    """
    try:
        ontology_path = Path(ontology_file)
        graph = Graph()
        graph.parse(str(ontology_path), format="turtle")
        
        # Add version info
        ontology_uri = graph.value(None, RDF.type, OWL.Ontology)
        if not ontology_uri:
            raise RegistrationError("No ontology declaration found")
            
        graph.remove((ontology_uri, OWL.versionInfo, None))
        graph.add((ontology_uri, OWL.versionInfo, Literal(version)))
        
        # Add dependencies
        if dependencies:
            for dep in dependencies:
                graph.add((ontology_uri, OWL.imports, URIRef(dep)))
                
        # Write updated ontology
        graph.serialize(ontology_path, format="turtle")
        logger.info(f"Registered ontology {ontology_file} with version {version}")
        
        # Update session.ttl
        onto_update_session_ttl(ontology_file, version)
        
    except Exception as e:
        raise RegistrationError(f"Failed to register ontology: {str(e)}")


def onto_load_ontology(ontology_file: Union[str, Path], 
                      load_imports: bool = True) -> Graph:
    """Load an ontology and optionally its imports.
    
    Args:
        ontology_file: Path to ontology TTL file
        load_imports: Whether to load imported ontologies
        
    Returns:
        Loaded RDFlib Graph
        
    Raises:
        RegistrationError: If loading fails
    """
    try:
        graph = Graph()
        graph.parse(str(ontology_file), format="turtle")
        
        if load_imports:
            # Load imported ontologies
            for import_uri in graph.objects(None, OWL.imports):
                try:
                    import_graph = Graph()
                    import_graph.parse(str(import_uri))
                    graph += import_graph
                    logger.info(f"Loaded imported ontology {import_uri}")
                except Exception as e:
                    logger.warning(f"Failed to load import {import_uri}: {str(e)}")
                    
        return graph
        
    except Exception as e:
        raise RegistrationError(f"Failed to load ontology: {str(e)}")


def onto_update_session_ttl(ontology_file: Union[str, Path], 
                           version: str) -> None:
    """Update session.ttl with ontology registration info.
    
    Args:
        ontology_file: Path to registered ontology
        version: Version string
        
    Raises:
        RegistrationError: If update fails
    """
    try:
        session_file = Path("session.ttl")
        if not session_file.exists():
            # Create new session.ttl
            graph = Graph()
            graph.bind("owl", OWL)
            graph.bind("rdf", RDF)
            graph.bind("rdfs", RDFS)
        else:
            graph = Graph()
            graph.parse(str(session_file), format="turtle")
            
        # Add registration info
        session_ns = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/session#")
        graph.bind("session", session_ns)
        
        reg = URIRef(f"{session_ns}registration_{datetime.now().isoformat()}")
        graph.add((reg, RDF.type, session_ns.Registration))
        graph.add((reg, session_ns.ontologyFile, Literal(str(ontology_file))))
        graph.add((reg, session_ns.version, Literal(version)))
        graph.add((reg, session_ns.timestamp, Literal(datetime.now().isoformat())))
        
        graph.serialize(session_file, format="turtle")
        logger.info(f"Updated session.ttl with registration of {ontology_file}")
        
    except Exception as e:
        raise RegistrationError(f"Failed to update session.ttl: {str(e)}")


def onto_get_registered_ontologies() -> List[Dict[str, str]]:
    """Get list of registered ontologies from session.ttl.
    
    Returns:
        List of dictionaries with ontology info
        
    Raises:
        RegistrationError: If reading fails
    """
    try:
        session_file = Path("session.ttl")
        if not session_file.exists():
            return []
            
        graph = Graph()
        graph.parse(str(session_file), format="turtle")
        
        session_ns = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/session#")
        registrations = []
        
        for reg in graph.subjects(RDF.type, session_ns.Registration):
            info = {
                "file": str(graph.value(reg, session_ns.ontologyFile)),
                "version": str(graph.value(reg, session_ns.version)),
                "timestamp": str(graph.value(reg, session_ns.timestamp))
            }
            registrations.append(info)
            
        return registrations
        
    except Exception as e:
        raise RegistrationError(f"Failed to get registered ontologies: {str(e)}")


# Backward compatibility aliases
register_ontology = onto_register_ontology
load_ontology = onto_load_ontology
update_session_ttl = onto_update_session_ttl
get_registered_ontologies = onto_get_registered_ontologies
