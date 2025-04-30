#!/usr/bin/env python3
"""Generate PlantUML diagram from RDF model."""

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
import re

def generate_plantuml(graph: Graph, output_file: str) -> None:
    """Generate PlantUML diagram from RDF graph."""
    plantuml = ["@startuml GraphDB Client Model"]
    
    # Add skinparam settings
    plantuml.extend([
        "skinparam classAttributeIconSize 0",
        "skinparam classFontSize 10",
        "skinparam classFontStyle bold",
        "skinparam classBackgroundColor white",
        "skinparam classBorderColor black",
        "skinparam classArrowColor black",
        "skinparam packageBackgroundColor white",
        "skinparam packageBorderColor black",
        "skinparam noteBackgroundColor white",
        "skinparam noteBorderColor black",
    ])
    
    # Add classes
    for s, p, o in graph.triples((None, RDF.type, OWL.Class)):
        class_name = re.sub(r'.*#', '', str(s))
        plantuml.append(f"class {class_name} {{")
        for _, _, comment in graph.triples((s, RDFS.comment, None)):
            plantuml.append(f"  {comment}")
        plantuml.append("}")
    
    # Add properties
    for s, p, o in graph.triples((None, RDF.type, OWL.ObjectProperty)):
        prop_name = re.sub(r'.*#', '', str(s))
        domain = None
        range_ = None
        for _, _, d in graph.triples((s, RDFS.domain, None)):
            domain = re.sub(r'.*#', '', str(d))
        for _, _, r in graph.triples((s, RDFS.range, None)):
            range_ = re.sub(r'.*#', '', str(r))
        if domain and range_:
            plantuml.append(f"{domain} --> {range_} : {prop_name}")
    
    # Add datatype properties
    for s, p, o in graph.triples((None, RDF.type, OWL.DatatypeProperty)):
        prop_name = re.sub(r'.*#', '', str(s))
        domain = None
        range_ = None
        for _, _, d in graph.triples((s, RDFS.domain, None)):
            domain = re.sub(r'.*#', '', str(d))
        for _, _, r in graph.triples((s, RDFS.range, None)):
            range_ = re.sub(r'.*#', '', str(r))
        if domain and range_:
            plantuml.append(f"{domain} : {prop_name}: {range_}")
    
    # Add requirements, risks, and constraints
    plantuml.append("package Requirements {")
    for s, p, o in graph.triples((None, RDF.type, URIRef("http://example.org/requirement#Requirement"))):
        req_name = re.sub(r'.*#', '', str(s))
        plantuml.append(f"class {req_name} <<Requirement>> {{")
        for _, _, comment in graph.triples((s, RDFS.comment, None)):
            plantuml.append(f"  {comment}")
        plantuml.append("}")
    plantuml.append("}")
    
    plantuml.append("package Risks {")
    for s, p, o in graph.triples((None, RDF.type, URIRef("http://example.org/risk#Risk"))):
        risk_name = re.sub(r'.*#', '', str(s))
        plantuml.append(f"class {risk_name} <<Risk>> {{")
        for _, _, comment in graph.triples((s, RDFS.comment, None)):
            plantuml.append(f"  {comment}")
        plantuml.append("}")
    plantuml.append("}")
    
    plantuml.append("package Constraints {")
    for s, p, o in graph.triples((None, RDF.type, URIRef("http://example.org/constraint#Constraint"))):
        const_name = re.sub(r'.*#', '', str(s))
        plantuml.append(f"class {const_name} <<Constraint>> {{")
        for _, _, comment in graph.triples((s, RDFS.comment, None)):
            plantuml.append(f"  {comment}")
        plantuml.append("}")
    plantuml.append("}")
    
    plantuml.append("@enduml")
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write('\n'.join(plantuml))

def main():
    """Generate PlantUML diagram from RDF model."""
    # Load RDF model
    graph = Graph()
    graph.parse("graphdb_client_model.ttl", format="turtle")
    
    # Generate PlantUML
    generate_plantuml(graph, "graphdb_client_model.puml")

if __name__ == "__main__":
    main() 