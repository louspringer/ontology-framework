"""Model manager for GraphDB client using semantic web tools."""

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
import pyshacl
from typing import Dict, Any, Optional
import logging

# Define namespaces
GDB = Namespace("http://example.org/graphdb#")
CODE = Namespace("http://example.org/code#")
TEST = Namespace("http://example.org/test#")
REQ = Namespace("http://example.org/requirement#")
RISK = Namespace("http://example.org/risk#")
CONST = Namespace("http://example.org/constraint#")

class GraphDBModelManager:
    """Manages the GraphDB client model using semantic web tools."""
    
    def __init__(self):
        """Initialize the model manager."""
        self.graph = Graph()
        self._bind_namespaces()
        self.logger = logging.getLogger(__name__)
        
    def _bind_namespaces(self):
        """Bind namespaces to the graph."""
        self.graph.bind("gdb", GDB)
        self.graph.bind("code", CODE)
        self.graph.bind("test", TEST)
        self.graph.bind("req", REQ)
        self.graph.bind("risk", RISK)
        self.graph.bind("const", CONST)
        self.graph.bind("sh", SH)
        
    def create_model(self):
        """Create the GraphDB client model."""
        # Add GraphDBClient class
        self.graph.add((GDB.GraphDBClient, RDF.type, OWL.Class))
        self.graph.add((GDB.GraphDBClient, RDFS.label, Literal("GraphDB Client")))
        self.graph.add((GDB.GraphDBClient, RDFS.comment, Literal("Client for interacting with GraphDB server")))
        
        # Add properties
        self._add_property(GDB.base_url, "Base URL", "Base URL of the GraphDB server", XSD.string)
        self._add_property(GDB.repository, "Repository", "Repository name", XSD.string)
        self._add_property(GDB.query, "Query", "SPARQL query", XSD.string)
        self._add_property(GDB.update, "Update", "SPARQL update", XSD.string)
        self._add_property(GDB.graph_uri, "Graph URI", "URI of the graph", XSD.string)
        self._add_property(GDB.backup_path, "Backup Path", "Path to backup file", XSD.string)
        
        # Add SHACL shapes
        self._add_shacl_shapes()
        
        # Add requirements
        self._add_requirements()
        
        # Add risks
        self._add_risks()
        
        # Add constraints
        self._add_constraints()
        
    def _add_property(self, prop: URIRef, label: str, comment: str, datatype: URIRef):
        """Add a property to the model."""
        self.graph.add((prop, RDF.type, OWL.DatatypeProperty))
        self.graph.add((prop, RDFS.label, Literal(label)))
        self.graph.add((prop, RDFS.comment, Literal(comment)))
        self.graph.add((prop, RDFS.range, datatype))
        
    def _add_shacl_shapes(self):
        """Add SHACL shapes for validation."""
        # GraphDBClient shape
        client_shape = BNode()
        self.graph.add((client_shape, RDF.type, SH.NodeShape))
        self.graph.add((client_shape, SH.targetClass, GDB.GraphDBClient))
        
        # Add property constraints
        self._add_property_constraint(client_shape, GDB.base_url, min_count=1)
        self._add_property_constraint(client_shape, GDB.repository, min_count=1)
        
    def _add_property_constraint(self, shape: BNode, prop: URIRef, min_count: int = 0, max_count: Optional[int] = None):
        """Add a property constraint to a SHACL shape."""
        constraint = BNode()
        self.graph.add((shape, SH.property, constraint))
        self.graph.add((constraint, SH.path, prop))
        if min_count > 0:
            self.graph.add((constraint, SH.minCount, Literal(min_count)))
        if max_count is not None:
            self.graph.add((constraint, SH.maxCount, Literal(max_count)))
            
    def _add_requirements(self):
        """Add system requirements."""
        requirements = [
            (REQ.SPARQLSupport, "SPARQL Query Support", "Must support SPARQL query execution"),
            (REQ.GraphManagement, "Graph Management", "Must support graph upload/download/clear operations"),
            (REQ.ErrorHandling, "Error Handling", "Must implement proper error handling"),
            (REQ.Authentication, "Authentication", "Must support authentication mechanisms"),
            (REQ.Validation, "Validation", "Must support data validation")
        ]
        
        for uri, label, comment in requirements:
            self.graph.add((uri, RDF.type, REQ.Requirement))
            self.graph.add((uri, RDFS.label, Literal(label)))
            self.graph.add((uri, RDFS.comment, Literal(comment)))
            
    def _add_risks(self):
        """Add system risks."""
        risks = [
            (RISK.ConnectionFailure, "Connection Failure", "Risk of connection to GraphDB server failing"),
            (RISK.DataLoss, "Data Loss", "Risk of data loss during operations"),
            (RISK.Security, "Security Risk", "Risk of unauthorized access"),
            (RISK.Performance, "Performance Risk", "Risk of performance degradation")
        ]
        
        for uri, label, comment in risks:
            self.graph.add((uri, RDF.type, RISK.Risk))
            self.graph.add((uri, RDFS.label, Literal(label)))
            self.graph.add((uri, RDFS.comment, Literal(comment)))
            
    def _add_constraints(self):
        """Add system constraints."""
        constraints = [
            (CONST.GraphDBServer, "GraphDB Server", "Must have access to GraphDB server"),
            (CONST.Authentication, "Authentication", "Must have valid credentials"),
            (CONST.Network, "Network", "Must have network connectivity"),
            (CONST.Storage, "Storage", "Must have sufficient storage for graphs")
        ]
        
        for uri, label, comment in constraints:
            self.graph.add((uri, RDF.type, CONST.Constraint))
            self.graph.add((uri, RDFS.label, Literal(label)))
            self.graph.add((uri, RDFS.comment, Literal(comment)))
            
    def validate_model(self) -> Dict[str, Any]:
        """Validate the model using SHACL."""
        try:
            conforms, results_graph, results_text = pyshacl.validate(
                self.graph,
                shacl_graph=self.graph,
                inference='rdfs',
                abort_on_first=False
            )
            
            return {
                "conforms": conforms,
                "results_graph": results_graph,
                "results_text": results_text
            }
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return {
                "conforms": False,
                "error": str(e)
            }
            
    def save_model(self, format: str = "xml") -> None:
        """Save the model to a file."""
        try:
            if format == "xml":
                self.graph.serialize("graphdb_client_model.rdf", format="xml")
            else:
                self.graph.serialize("graphdb_client_model.ttl", format="turtle")
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            
    def load_model(self, format: str = "xml") -> None:
        """Load the model from a file."""
        try:
            if format == "xml":
                self.graph.parse("graphdb_client_model.rdf", format="xml")
            else:
                self.graph.parse("graphdb_client_model.ttl", format="turtle")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            
    def query_model(self, query: str) -> Any:
        """Query the model using SPARQL."""
        try:
            return self.graph.query(query)
        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            return None 