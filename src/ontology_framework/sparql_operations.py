#!/usr/bin/env python3
"""Consolidated SPARQL operations for ontology framework."""

import logging
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of SPARQL queries."""
    SELECT = "SELECT"
    ASK = "ASK"
    CONSTRUCT = "CONSTRUCT"
    DESCRIBE = "DESCRIBE"
    INSERT = "INSERT"
    DELETE = "DELETE"
    LOAD = "LOAD"
    CLEAR = "CLEAR"

@dataclass
class QueryResult:
    """Container for SPARQL query results."""
    success: bool
    data: Optional[Union[List[Dict[str, Any]], bool, str]]
    error: Optional[str]
    execution_time: float
    query_type: QueryType
    timestamp: datetime
    query: str  # Store the actual query for debugging
    empty: bool = False  # Flag to indicate if results are empty

    def __str__(self) -> str:
        """String representation of query result."""
        status = "SUCCESS" if self.success else "FAILURE"
        empty = " (EMPTY)" if self.empty else ""
        return f"Query {status}{empty} - Type: {self.query_type.value} - Time: {self.execution_time:.2f}s"

class SparqlExecutor(ABC):
    """Abstract base class for SPARQL executors."""
    
    @abstractmethod
    def execute_query(self, query: str, query_type: QueryType) -> QueryResult:
        """Execute a SPARQL query.
        
        Args:
            query: The SPARQL query string
            query_type: Type of query being executed
            
        Returns:
            QueryResult containing the results
        """
        pass

class JenaFusekiExecutor(SparqlExecutor):
    """Executor for Jena Fuseki SPARQL server."""
    
    def __init__(self, endpoint: str = "http://localhost:3030/guidance"):
        """Initialize Jena Fuseki executor.
        
        Args:
            endpoint: SPARQL endpoint URL
        """
        self.endpoint = endpoint
        self._setup_namespaces()
        
    def _setup_namespaces(self) -> None:
        """Set up common namespaces."""
        self.namespaces = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "sh": "http://www.w3.org/ns/shacl#",
            "meta": "http://example.org/guidance/meta#"
        }
        
    def _add_prefixes(self, query: str) -> str:
        """Add namespace prefixes to query.
        
        Args:
            query: Original query string
            
        Returns:
            Query with prefixes added
        """
        prefixes = "\n".join([f"PREFIX {prefix}: <{uri}>" 
                            for prefix, uri in self.namespaces.items()])
        return f"{prefixes}\n{query}"
        
    def _check_endpoint_availability(self) -> None:
        """Check if the SPARQL endpoint is available."""
        try:
            response = requests.get(self.endpoint)
            response.raise_for_status()
        except RequestException as e:
            raise ConnectionError(f"SPARQL endpoint {self.endpoint} is not available: {str(e)}")
        
    def execute_query(self, query: str, query_type: QueryType) -> QueryResult:
        """Execute a SPARQL query against Jena Fuseki.
        
        Args:
            query: The SPARQL query string
            query_type: Type of query being executed
            
        Returns:
            QueryResult containing the results
        """
        start_time = datetime.now()
        
        try:
            # Check endpoint availability
            self._check_endpoint_availability()
            
            # Add prefixes
            query = self._add_prefixes(query)
            
            # Log query execution
            logger.info(f"Executing {query_type.value} query")
            logger.debug(f"Query:\n{query}")
            
            # Execute based on query type
            if query_type in [QueryType.SELECT, QueryType.ASK]:
                response = self._execute_select_or_ask(query, query_type)
            elif query_type in [QueryType.INSERT, QueryType.DELETE]:
                self._execute_update(query)
                response = True  # Indicate successful update
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
                
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Check for empty results
            empty = False
            if query_type == QueryType.SELECT and isinstance(response, list) and not response:
                empty = True
                logger.warning("Query returned empty results")
            elif query_type == QueryType.ASK and response is False:
                empty = True
                logger.warning("ASK query returned false")
            
            return QueryResult(
                success=True,
                data=response,
                error=None,
                execution_time=execution_time,
                query_type=query_type,
                timestamp=start_time,
                query=query,
                empty=empty
            )
            
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(error_msg)
            return QueryResult(
                success=False,
                data=None,
                error=error_msg,
                execution_time=(datetime.now() - start_time).total_seconds(),
                query_type=query_type,
                timestamp=start_time,
                query=query,
                empty=True
            )
            
    def _execute_select_or_ask(self, query: str, query_type: QueryType) -> Union[List[Dict[str, Any]], bool]:
        """Execute SELECT or ASK query.
        
        Args:
            query: The SPARQL query string
            query_type: Type of query (SELECT or ASK)
            
        Returns:
            Query results
            
        Raises:
            ValueError: If response format is invalid
            RequestException: If HTTP request fails
        """
        try:
            response = requests.post(
                f"{self.endpoint}/sparql",
                data={"query": query},
                headers={"Content-Type": "application/sparql-query"}
            )
            response.raise_for_status()
            
            json_response = response.json()
            
            if query_type == QueryType.ASK:
                if "boolean" not in json_response:
                    raise ValueError("Invalid ASK response format: missing 'boolean' field")
                return json_response["boolean"]
            else:
                if "results" not in json_response or "bindings" not in json_response["results"]:
                    raise ValueError("Invalid SELECT response format: missing 'results.bindings' field")
                return json_response["results"]["bindings"]
                
        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")
            
    def _execute_update(self, query: str) -> None:
        """Execute UPDATE query.
        
        Args:
            query: The SPARQL UPDATE query string
            
        Raises:
            RequestException: If HTTP request fails
        """
        response = requests.post(
            f"{self.endpoint}/update",
            data={"update": query},
            headers={"Content-Type": "application/sparql-update"}
        )
        response.raise_for_status()

class Neo4jExecutor(SparqlExecutor):
    """Executor for Neo4j graph database (placeholder for future implementation)."""
    
    def execute_query(self, query: str, query_type: QueryType) -> QueryResult:
        """Execute a SPARQL query against Neo4j.
        
        Args:
            query: The SPARQL query string
            query_type: Type of query being executed
            
        Returns:
            QueryResult containing the results
        """
        # TODO: Implement Neo4j SPARQL execution
        raise NotImplementedError("Neo4j executor not yet implemented")

def execute_sparql(
    query: str,
    query_type: QueryType = QueryType.SELECT,
    executor: Optional[SparqlExecutor] = None
) -> QueryResult:
    """Execute a SPARQL query using the specified executor.
    
    Args:
        query: The SPARQL query string
        query_type: Type of query being executed
        executor: Optional executor to use. If None, uses default JenaFusekiExecutor.
        
    Returns:
        QueryResult containing the results
    """
    if executor is None:
        executor = JenaFusekiExecutor()
        
    result = executor.execute_query(query, query_type)
    
    # Log result status
    if result.success:
        if result.empty:
            logger.warning(f"Query executed successfully but returned no results: {result}")
        else:
            logger.info(f"Query executed successfully: {result}")
    else:
        logger.error(f"Query execution failed: {result}")
        
    return result 