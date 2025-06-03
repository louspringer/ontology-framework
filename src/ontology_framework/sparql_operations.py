"""
Common SPARQL operations and patterns.
"""

from typing import Dict, List, Any, Optional, Union, cast
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
import requests
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
from rdflib.query import ResultRow
import warnings
from .graphdb_client import GraphDBClient

class QueryType(Enum):
    SELECT = "SELECT"
    ASK = "ASK"
    CONSTRUCT = "CONSTRUCT"
    DESCRIBE = "DESCRIBE"
    INSERT = "INSERT"
    DELETE = "DELETE"
    UPDATE = "UPDATE"

class QueryResult:
    def __init__(
        self,
        success: bool,
        data: Any,
        error: Optional[str],
        execution_time: float,
        query_type: QueryType,
        timestamp: datetime,
        query: str,
        empty: bool = False
    ):
        self.success = success
        self.data = data
        self.error = error
        self.execution_time = execution_time
        self.query_type = query_type
        self.timestamp = timestamp
        self.query = query
        self.empty = empty
    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILURE"
        if self.empty:
            status = "EMPTY"
        return f"{status} ({self.query_type.value}): {self.execution_time:.2f}s"

class QueryExecutor(ABC):
    @abstractmethod
    def execute_query(self, query: str, query_type: QueryType) -> QueryResult:
        pass

class GraphDBExecutor(QueryExecutor):
    def __init__(self, endpoint: str = "http://localhost:7200", repository: str = "guidance", base_url: Optional[str] = None):
        chosen_url = base_url if base_url is not None else endpoint
        self.client = GraphDBClient(chosen_url, repository)
    def execute_query(self, query: str, query_type: QueryType) -> QueryResult:
        start_time = datetime.now()
        try:
            if query_type in [QueryType.INSERT, QueryType.DELETE, QueryType.UPDATE]:
                success = self.client.update(query)
                data = success
            else:
                result = self.client.query(query)
                if query_type == QueryType.ASK:
                    data = result.get("boolean", False)
                else:
                    data = result.get("results", {}).get("bindings", [])
            execution_time = (datetime.now() - start_time).total_seconds()
            return QueryResult(
                success=True,
                data=data,
                error=None,
                execution_time=execution_time,
                query_type=query_type,
                timestamp=start_time,
                query=query,
                empty=(len(data) == 0 if isinstance(data, list) else False)
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return QueryResult(
                success=False,
                data=[],
                error=str(e),
                execution_time=execution_time,
                query_type=query_type,
                timestamp=start_time,
                query=query,
                empty=True
            )

class Neo4jExecutor(QueryExecutor):
    def execute_query(self, query: str, query_type: QueryType) -> QueryResult:
        raise NotImplementedError("Neo4j execution not implemented")

def execute_sparql(
    query: str,
    query_type: QueryType = QueryType.SELECT,
    executor: Optional[QueryExecutor] = None
) -> QueryResult:
    if executor is None:
        executor = GraphDBExecutor()
    return executor.execute_query(query, query_type)

class SparqlOperations:
    @staticmethod
    def get_classes(graph: Graph) -> List[Dict[str, Any]]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# >
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?class_uri ?label ?comment WHERE {
            ?class_uri a rdfs:Class .
            OPTIONAL { ?class_uri rdfs:label ?label }
            OPTIONAL { ?class_uri rdfs:comment ?comment }
        }
        """
        results = graph.query(query)
        return [
            {
                'uri': str(cast(ResultRow, row)[0]),
                'label': str(cast(ResultRow, row)[1]) if cast(ResultRow, row)[1] else None,
                'comment': str(cast(ResultRow, row)[2]) if cast(ResultRow, row)[2] else None
            }
            for row in results
        ]
    @staticmethod
    def get_properties(graph: Graph) -> List[Dict[str, Any]]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# >
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?property ?label ?comment ?domain ?range WHERE {
            ?property a rdf:Property .
            OPTIONAL { ?property rdfs:label ?label }
            OPTIONAL { ?property rdfs:comment ?comment }
            OPTIONAL { ?property rdfs:domain ?domain }
            OPTIONAL { ?property rdfs:range ?range }
        }
        """
        results = graph.query(query)
        return [
            {
                'uri': str(cast(ResultRow, row)[0]),
                'label': str(cast(ResultRow, row)[1]) if cast(ResultRow, row)[1] else None,
                'comment': str(cast(ResultRow, row)[2]) if cast(ResultRow, row)[2] else None,
                'domain': str(cast(ResultRow, row)[3]) if cast(ResultRow, row)[3] else None,
                'range': str(cast(ResultRow, row)[4]) if cast(ResultRow, row)[4] else None
            }
            for row in results
        ]
        
    @staticmethod
    def get_individuals(graph: Graph, class_uri: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# >
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?individual ?label ?comment WHERE {
            ?individual a ?class_uri .
            OPTIONAL { ?individual rdfs:label ?label }
            OPTIONAL { ?individual rdfs:comment ?comment }
        }
        """
        if class_uri:
            query = query.replace("?class_uri", f"<{class_uri}>")
        results = graph.query(query)
        return [
            {
                'uri': str(cast(ResultRow, row)[0]),
                'label': str(cast(ResultRow, row)[1]) if cast(ResultRow, row)[1] else None,
                'comment': str(cast(ResultRow, row)[2]) if cast(ResultRow, row)[2] else None
            }
            for row in results
        ]
        
    @staticmethod
    def get_shacl_shapes(graph: Graph) -> List[Dict[str, Any]]:
        query = """
        PREFIX sh: <http://www.w3.org/ns/shacl# >
        SELECT ?shape ?targetClass ?property ?minCount ?maxCount ?datatype WHERE {
            ?shape a sh:NodeShape .
            OPTIONAL { ?shape sh:targetClass ?targetClass }
            OPTIONAL {
                ?shape sh:property ?propertyNode .
                ?propertyNode sh:path ?property .
                OPTIONAL { ?propertyNode sh:minCount ?minCount }
                OPTIONAL { ?propertyNode sh:maxCount ?maxCount }
                OPTIONAL { ?propertyNode sh:datatype ?datatype }
            }
        }
        """
        results = graph.query(query)
        return [
            {
                'uri': str(cast(ResultRow, row)[0]),
                'targetClass': str(cast(ResultRow, row)[1]) if cast(ResultRow, row)[1] else None,
                'property': str(cast(ResultRow, row)[2]) if cast(ResultRow, row)[2] else None,
                'minCount': int(cast(ResultRow, row)[3]) if cast(ResultRow, row)[3] else None,
                'maxCount': int(cast(ResultRow, row)[4]) if cast(ResultRow, row)[4] else None,
                'datatype': str(cast(ResultRow, row)[5]) if cast(ResultRow, row)[5] else None
            }
            for row in results
        ]
        
    @staticmethod
    def get_ontology_metadata(graph: Graph) -> Dict[str, Any]:
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl# >
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        SELECT ?title ?description ?version ?creator ?created ?modified WHERE {
            ?ontology a owl:Ontology .
            OPTIONAL { ?ontology dc:title ?title }
            OPTIONAL { ?ontology dc:description ?description }
            OPTIONAL { ?ontology owl:versionInfo ?version }
            OPTIONAL { ?ontology dc:creator ?creator }
            OPTIONAL { ?ontology dcterms:created ?created }
            OPTIONAL { ?ontology dcterms:modified ?modified }
        }
        """
        results = graph.query(query)
        if results:
            row = next(results)
            return {
                'title': str(cast(ResultRow, row)[0]) if cast(ResultRow, row)[0] else None,
                'description': str(cast(ResultRow, row)[1]) if cast(ResultRow, row)[1] else None,
                'version': str(cast(ResultRow, row)[2]) if cast(ResultRow, row)[2] else None,
                'creator': str(cast(ResultRow, row)[3]) if cast(ResultRow, row)[3] else None,
                'created': str(cast(ResultRow, row)[4]) if cast(ResultRow, row)[4] else None,
                'modified': str(cast(ResultRow, row)[5]) if cast(ResultRow, row)[5] else None
            }
        return {}

# Add alias so tests can import SparqlExecutor
SparqlExecutor = GraphDBExecutor
