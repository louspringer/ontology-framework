#!/usr/bin/env python3
"""Model generator for GraphDB client system."""

from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, PROV, SH
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import ast
import importlib.util
import sys

# Define namespaces
GDB = Namespace("http://example.org/graphdb#")
CODE = Namespace("http://example.org/code#")
TEST = Namespace("http://example.org/test#")
REQ = Namespace("http://example.org/requirement#")
RISK = Namespace("http://example.org/risk#")
CONST = Namespace("http://example.org/constraint#")
SHACL = Namespace("http://www.w3.org/ns/shacl#")

def load_module(file_path: str) -> Any:
    """Load a Python module from file."""
    spec = importlib.util.spec_from_file_location("module", file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def add_shacl_validation(graph: Graph, method_uri: URIRef, method: Any) -> None:
    """Add SHACL validation rules for a method."""
    # Create shape for method
    shape_uri = URIRef(f"{method_uri}_shape")
    graph.add((shape_uri, RDF.type, SH.NodeShape))
    graph.add((shape_uri, SH.targetClass, method_uri))
    
    # Add parameter validation
    sig = inspect.signature(method)
    for param_name, param in sig.parameters.items():
        if param_name != 'self':
            property_shape = BNode()
            graph.add((shape_uri, SH.property, property_shape))
            graph.add((property_shape, SH.path, URIRef(f"{method_uri}/{param_name}")))
            
            # Add type validation
            if param.annotation != inspect.Parameter.empty:
                graph.add((property_shape, SH.datatype, Literal(str(param.annotation))))
            
            # Add required validation
            if param.default == inspect.Parameter.empty:
                graph.add((property_shape, SH.minCount, Literal(1)))
                graph.add((property_shape, SH.message, Literal(f"Parameter {param_name} is required")))

def analyze_class(cls: type, graph: Graph, base_uri: str) -> None:
    """Analyze a Python class and add its structure to the RDF graph."""
    class_uri = URIRef(f"{base_uri}{cls.__name__}")
    
    # Add class definition
    graph.add((class_uri, RDF.type, OWL.Class))
    graph.add((class_uri, RDFS.label, Literal(cls.__name__)))
    if cls.__doc__:
        graph.add((class_uri, RDFS.comment, Literal(cls.__doc__)))
    
    # Add class shape
    class_shape = URIRef(f"{class_uri}_shape")
    graph.add((class_shape, RDF.type, SH.NodeShape))
    graph.add((class_shape, SH.targetClass, class_uri))
    
    # Analyze methods
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        if not name.startswith('_'):  # Skip private methods
            method_uri = URIRef(f"{base_uri}{cls.__name__}/{name}")
            
            # Add method definition
            graph.add((method_uri, RDF.type, OWL.ObjectProperty))
            graph.add((method_uri, RDFS.label, Literal(name)))
            if method.__doc__:
                graph.add((method_uri, RDFS.comment, Literal(method.__doc__)))
            
            # Add method to class shape
            property_shape = BNode()
            graph.add((class_shape, SH.property, property_shape))
            graph.add((property_shape, SH.path, method_uri))
            
            # Add method parameters
            sig = inspect.signature(method)
            for param_name, param in sig.parameters.items():
                param_uri = URIRef(f"{base_uri}{cls.__name__}/{name}/{param_name}")
                graph.add((param_uri, RDF.type, OWL.DatatypeProperty))
                graph.add((param_uri, RDFS.label, Literal(param_name)))
                if param.annotation != inspect.Parameter.empty:
                    graph.add((param_uri, RDFS.range, Literal(str(param.annotation))))
                if param.default != inspect.Parameter.empty:
                    graph.add((param_uri, OWL.hasValue, Literal(str(param.default))))
            
            # Add SHACL validation
            add_shacl_validation(graph, method_uri, method)

def analyze_tests(test_file: str, graph: Graph, base_uri: str) -> None:
    """Analyze test file and add test structure to the RDF graph."""
    with open(test_file, 'r') as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            test_uri = URIRef(f"{base_uri}test/{node.name}")
            
            # Add test definition
            graph.add((test_uri, RDF.type, TEST.TestCase))
            graph.add((test_uri, RDFS.label, Literal(node.name)))
            if ast.get_docstring(node):
                graph.add((test_uri, RDFS.comment, Literal(ast.get_docstring(node))))
            
            # Add test assertions
            for stmt in node.body:
                if isinstance(stmt, ast.Assert):
                    assertion_uri = URIRef(f"{base_uri}test/{node.name}/assertion")
                    graph.add((assertion_uri, RDF.type, TEST.Assertion))
                    graph.add((assertion_uri, TEST.asserts, Literal(ast.unparse(stmt))))

def add_requirements(graph: Graph) -> None:
    """Add system requirements to the RDF graph."""
    requirements = [
        (REQ.SPARQLSupport, "SPARQL Query Support", "Must support SPARQL query execution"),
        (REQ.GraphManagement, "Graph Management", "Must support graph upload/download/clear operations"),
        (REQ.ErrorHandling, "Error Handling", "Must implement proper error handling"),
        (REQ.Authentication, "Authentication", "Must support authentication mechanisms"),
        (REQ.Validation, "Validation", "Must support data validation")
    ]
    
    for uri, label, comment in requirements:
        graph.add((uri, RDF.type, REQ.Requirement))
        graph.add((uri, RDFS.label, Literal(label)))
        graph.add((uri, RDFS.comment, Literal(comment)))

def add_risks(graph: Graph) -> None:
    """Add system risks to the RDF graph."""
    risks = [
        (RISK.ConnectionFailure, "Connection Failure", "Risk of connection to GraphDB server failing"),
        (RISK.DataLoss, "Data Loss", "Risk of data loss during operations"),
        (RISK.Security, "Security Risk", "Risk of unauthorized access"),
        (RISK.Performance, "Performance Risk", "Risk of performance degradation")
    ]
    
    for uri, label, comment in risks:
        graph.add((uri, RDF.type, RISK.Risk))
        graph.add((uri, RDFS.label, Literal(label)))
        graph.add((uri, RDFS.comment, Literal(comment)))

def add_constraints(graph: Graph) -> None:
    """Add system constraints to the RDF graph."""
    constraints = [
        (CONST.GraphDBServer, "GraphDB Server", "Must have access to GraphDB server"),
        (CONST.Authentication, "Authentication", "Must have valid credentials"),
        (CONST.Network, "Network", "Must have network connectivity"),
        (CONST.Storage, "Storage", "Must have sufficient storage for graphs")
    ]
    
    for uri, label, comment in constraints:
        graph.add((uri, RDF.type, CONST.Constraint))
        graph.add((uri, RDFS.label, Literal(label)))
        graph.add((uri, RDFS.comment, Literal(comment)))

def main():
    """Generate the RDF model of the GraphDB client system."""
    # Create RDF graph
    graph = Graph()
    
    # Bind namespaces
    graph.bind("gdb", GDB)
    graph.bind("code", CODE)
    graph.bind("test", TEST)
    graph.bind("req", REQ)
    graph.bind("risk", RISK)
    graph.bind("const", CONST)
    
    # Load and analyze the GraphDB client module
    module = load_module("src/ontology_framework/graphdb_client.py")
    analyze_class(module.GraphDBClient, graph, "http://example.org/graphdb#")
    
    # Analyze test file
    analyze_tests("tests/test_graphdb_client.py", graph, "http://example.org/graphdb#")
    
    # Add requirements, risks, and constraints
    add_requirements(graph)
    add_risks(graph)
    add_constraints(graph)
    
    # Serialize the graph
    graph.serialize("graphdb_client_model.ttl", format="turtle")
    graph.serialize("graphdb_client_model.rdf", format="xml")

if __name__ == "__main__":
    main() 