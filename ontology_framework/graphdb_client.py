#!/usr/bin/env python3
"""GraphDB client for ontology framework."""

import requests
import uuid
import logging
import json
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

class GraphDBError(Exception):
    """Base exception for GraphDB errors."""
    def __init__(self, message: str, correlation_id: str, status_code: Optional[int] = None, 
                 error_details: Optional[Dict] = None):
        self.message = message
        self.correlation_id = correlation_id
        self.status_code = status_code
        self.error_details = error_details or {}
        self.timestamp = datetime.now().isoformat()
        super().__init__(f"[{correlation_id}] {message}")

class GraphDBClient:
    """Client for interacting with GraphDB."""
    
    def __init__(self, 
                 base_url: str = "http://localhost:7200",
                 repository: str = "ontology-framework"):
        """Initialize GraphDB client.
        
        Args:
            base_url: GraphDB server URL
            repository: Repository name
        """
        self.base_url = base_url.rstrip('/')
        self.repository = repository
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def _generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for tracking requests."""
        return str(uuid.uuid4())
        
    def _log_error(self, correlation_id: str, error: Exception, context: Dict[str, Any]) -> None:
        """Log error with correlation ID and context."""
        error_context = {
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        self.logger.error(json.dumps(error_context, indent=2))
        
    def _handle_error(self, error: Exception, correlation_id: str, context: Dict[str, Any]) -> None:
        """Handle and transform error into GraphDBError."""
        if isinstance(error, requests.exceptions.RequestException):
            status_code = getattr(error.response, 'status_code', None)
            error_details = {}
            if error.response is not None:
                try:
                    error_details = error.response.json()
                except:
                    error_details = {"raw_response": error.response.text}
            raise GraphDBError(
                message=str(error),
                correlation_id=correlation_id,
                status_code=status_code,
                error_details=error_details
            )
        else:
            self._log_error(correlation_id, error, context)
            raise GraphDBError(
                message=str(error),
                correlation_id=correlation_id,
                error_details={"context": context}
            )
            
    def create_repository(self, 
                         config: Optional[Dict] = None) -> bool:
        """Create a new repository.
        
        Args:
            config: Repository configuration
            
        Returns:
            bool: True if successful
            
        Raises:
            GraphDBError: If repository creation fails
        """
        correlation_id = self._generate_correlation_id()
        context = {"operation": "create_repository", "config": config}
        
        if config is None:
            config = {
                "id": self.repository,
                "title": "Ontology Framework Repository",
                "type": "graphdb:FreeSailRepository",
                "params": {
                    "ruleset": "owl-horst-optimized",
                    "queryTimeout": 0,
                    "queryLimitResults": 0,
                    "checkForInconsistencies": False,
                    "disableSameAs": True,
                    "enablePredicateList": True,
                    "enableContextIndex": True,
                    "enablePredicateList": True,
                    "enableSesameLiteralIndex": True,
                    "enableSesameDirectType": True
                }
            }
            
        try:
            response = self.session.post(
                f"{self.base_url}/rest/repositories",
                json=config,
                headers={"X-Correlation-ID": correlation_id}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self._handle_error(e, correlation_id, context)
            
    def import_data(self, 
                   file_path: Union[str, Path],
                   format: str = "turtle",
                   context: Optional[str] = None) -> bool:
        """Import RDF data from a file.
        
        Args:
            file_path: Path to RDF file
            format: RDF format (turtle, n3, rdfxml, etc.)
            context: Optional context URI
            
        Returns:
            bool: True if successful
            
        Raises:
            GraphDBError: If data import fails
            ValidationError: If validation fails
        """
        correlation_id = self._generate_correlation_id()
        context = context or "<http://example.org/default>"
        
        # Validate before import
        validator = OntologyValidator()
        errors = validator.validate_before_import(file_path, context)
        if errors:
            error_details = {
                "validation_errors": errors,
                "file_path": str(file_path),
                "context": context
            }
            raise ValidationError("Validation failed", error_details)
            
        try:
            with open(file_path, 'rb') as f:
                response = self.session.post(
                    f"{self.base_url}/rest/repositories/{self.repository}/statements",
                    params={"context": context},
                    headers={
                        "Content-Type": f"application/x-{format}",
                        "X-Correlation-ID": correlation_id
                    },
                    data=f.read()
                )
                response.raise_for_status()
                return True
        except Exception as e:
            self._handle_error(e, correlation_id, {
                "operation": "import_data",
                "file_path": str(file_path),
                "format": format,
                "context": context
            })
            
    def query(self, 
              query: str,
              format: str = "json") -> Optional[Dict]:
        """Execute a SPARQL query.
        
        Args:
            query: SPARQL query string
            format: Response format (json, xml, csv, etc.)
            
        Returns:
            Optional[Dict]: Query results
            
        Raises:
            GraphDBError: If query execution fails
        """
        correlation_id = self._generate_correlation_id()
        context = {
            "operation": "query",
            "query": query,
            "format": format
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/rest/repositories/{self.repository}",
                params={"query": query},
                headers={
                    "Accept": f"application/sparql-results+{format}",
                    "X-Correlation-ID": correlation_id
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._handle_error(e, correlation_id, context)
            
    def update(self, 
               update: str) -> bool:
        """Execute a SPARQL update.
        
        Args:
            update: SPARQL update string
            
        Returns:
            bool: True if successful
            
        Raises:
            GraphDBError: If update execution fails
        """
        correlation_id = self._generate_correlation_id()
        context = {
            "operation": "update",
            "update": update
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/rest/repositories/{self.repository}/statements",
                params={"update": update},
                headers={
                    "Content-Type": "application/sparql-update",
                    "X-Correlation-ID": correlation_id
                }
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self._handle_error(e, correlation_id, context)
            
    def get_namespaces(self) -> Dict[str, str]:
        """Get repository namespaces.
        
        Returns:
            Dict[str, str]: Prefix to namespace mapping
            
        Raises:
            GraphDBError: If namespace retrieval fails
        """
        correlation_id = self._generate_correlation_id()
        context = {"operation": "get_namespaces"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/rest/repositories/{self.repository}/namespaces",
                headers={"X-Correlation-ID": correlation_id}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._handle_error(e, correlation_id, context)
            
    def add_namespace(self, 
                     prefix: str,
                     namespace: str) -> bool:
        """Add a namespace.
        
        Args:
            prefix: Namespace prefix
            namespace: Namespace URI
            
        Returns:
            bool: True if successful
            
        Raises:
            GraphDBError: If namespace addition fails
        """
        correlation_id = self._generate_correlation_id()
        context = {
            "operation": "add_namespace",
            "prefix": prefix,
            "namespace": namespace
        }
        
        try:
            response = self.session.put(
                f"{self.base_url}/rest/repositories/{self.repository}/namespaces/{prefix}",
                data=namespace,
                headers={"X-Correlation-ID": correlation_id}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self._handle_error(e, correlation_id, context) 