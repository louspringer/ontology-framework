"""Jena Fuseki client for SPARQL operations."""

import logging
from typing import Any, Dict, List, Optional
import requests
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLStore

logger = logging.getLogger(__name__)

class JenaFusekiClient:
    """Client for interacting with Jena Fuseki SPARQL server."""

    def __init__(self, endpoint: str = "http://localhost:3030/guidance"):
        """Initialize Jena Fuseki client.

        Args:
            endpoint: SPARQL endpoint URL
        """
        self.endpoint = endpoint
        self.store = SPARQLStore(endpoint)
        self.graph = Graph(store=self.store)
        self._setup_namespaces()

    def _setup_namespaces(self) -> None:
        """Set up common namespaces."""
        self.ns1 = Namespace("http://example.org/guidance#")
        self.rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        self.owl = Namespace("http://www.w3.org/2002/07/owl#")
        self.xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
        self.sh = Namespace("http://www.w3.org/ns/shacl#")

    def execute_sparql(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SPARQL query.

        Args:
            query: SPARQL query string

        Returns:
            List of query results
        """
        try:
            response = requests.post(
                f"{self.endpoint}/sparql",
                data={"query": query},
                headers={"Content-Type": "application/sparql-query"}
            )
            response.raise_for_status()
            return response.json()["results"]["bindings"]
        except Exception as e:
            logger.error(f"Failed to execute SPARQL query: {e}")
            raise

    def update_sparql(self, query: str) -> None:
        """Execute a SPARQL UPDATE query.

        Args:
            query: SPARQL UPDATE query string
        """
        try:
            response = requests.post(
                f"{self.endpoint}/update",
                data={"update": query},
                headers={"Content-Type": "application/sparql-update"}
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to execute SPARQL UPDATE: {e}")
            raise

    def load_ontology(self, file_path: str) -> None:
        """Load an ontology file into the store.

        Args:
            file_path: Path to the ontology file
        """
        try:
            with open(file_path, 'r') as f:
                data = f.read()
            response = requests.post(
                f"{self.endpoint}/data",
                data=data,
                headers={"Content-Type": "text/turtle"}
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to load ontology: {e}")
            raise

    def add_triple(self, subject: URIRef, predicate: URIRef, object: Any) -> None:
        """Add a triple to the store.

        Args:
            subject: Subject URI
            predicate: Predicate URI
            object: Object (URI or literal)
        """
        query = f"""
        INSERT DATA {{
            <{subject}> <{predicate}> {object} .
        }}
        """
        self.update_sparql(query)

    def remove_triple(self, subject: URIRef, predicate: URIRef, object: Any) -> None:
        """Remove a triple from the store.

        Args:
            subject: Subject URI
            predicate: Predicate URI
            object: Object (URI or literal)
        """
        query = f"""
        DELETE DATA {{
            <{subject}> <{predicate}> {object} .
        }}
        """
        self.update_sparql(query) 