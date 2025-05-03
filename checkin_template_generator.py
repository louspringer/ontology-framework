#!/usr/bin/env python3
"""
CheckIn Template Generator - PCA Implementation

This script generates properly structured check-in plan TTL files that
will pass validation in the CheckinManager. It ensures all required
prefixes, properties, and relationships are included.
"""

import os
import sys
import argparse
import datetime
from uuid import uuid4
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Define namespaces
CHECKIN = Namespace("http://example.org/checkin#")
TIME = Namespace("http://www.w3.org/2006/time#")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

class CheckinTemplateGenerator:
    """Generates valid check-in plan TTL files."""
    
    def __init__(self):
        """Initialize the template generator."""
        self.graph = Graph()
        
        # Bind required namespaces - these are mandatory
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.graph.bind("checkin", CHECKIN)
        self.graph.bind("time", TIME)
    
    def create_plan(self, plan_id, name, description, version="0.1.0", steps=None):
        """
        Create a check-in plan with the given ID.
        
        Args:
            plan_id: Unique identifier for the plan
            name: Display name for the plan
            description: Description of the plan
            version: Version information
            steps: Optional list of step dictionaries, each with name, description, and order
            
        Returns:
            URI of the created plan
        """
        # Create plan URI and add required properties
        plan_uri = CHECKIN[plan_id]
        
        # Add required type assertions - both types are needed
        self.graph.add((plan_uri, RDF.type, GUIDANCE.IntegrationProcess))
        self.graph.add((plan_uri, RDF.type, CHECKIN.CheckinPlan))
        
        # Add mandatory properties
        self.graph.add((plan_uri, RDFS.label, Literal(name)))
        self.graph.add((plan_uri, RDFS.comment, Literal(description)))
        self.graph.add((plan_uri, OWL.versionInfo, Literal(version)))
        self.graph.add((plan_uri, TIME.created, Literal(datetime.datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        # Add default steps if none provided
        if not steps:
            steps = [
                {"name": "Validate", "description": "Validate content", "order": 1},
                {"name": "Check", "description": "Check for issues", "order": 2},
                {"name": "Store", "description": "Store in repository", "order": 3}
            ]
            
        # Create steps
        step_uris = []
        for step in steps:
            step_uri = self._create_step(
                step.get("id", f"step-{uuid4().hex[:8]}"),
                step["name"],
                step["description"],
                step["order"]
            )
            step_uris.append(step_uri)
            
        # Link steps to plan
        for step_uri in step_uris:
            self.graph.add((plan_uri, CHECKIN.hasStep, step_uri))
            
        return plan_uri
        
    def _create_step(self, step_id, name, description, order):
        """
        Create a check-in step.
        
        Args:
            step_id: Unique identifier for the step
            name: Display name for the step
            description: Description of the step
            order: Order of execution (integer)
            
        Returns:
            URI of the created step
        """
        step_uri = CHECKIN[step_id]
        
        # Add required type assertion
        self.graph.add((step_uri, RDF.type, CHECKIN.IntegrationStep))
        
        # Add mandatory properties
        self.graph.add((step_uri, RDFS.label, Literal(name)))
        self.graph.add((step_uri, CHECKIN.stepDescription, Literal(description)))
        self.graph.add((step_uri, CHECKIN.stepOrder, Literal(order, datatype=XSD.integer)))
        
        return step_uri
    
    def save_plan(self, file_path):
        """
        Save the generated plan to a TTL file.
        
        Args:
            file_path: Path to save the plan file
        """
        self.graph.serialize(destination=file_path, format="turtle")
        print(f"✅ Generated check-in plan saved to: {file_path}")
        print(f"Found {len(self.graph)} triples in the plan")

def main():
    parser = argparse.ArgumentParser(description="Generate valid check-in plan TTL files")
    parser.add_argument("--id", required=True, help="Unique identifier for the plan")
    parser.add_argument("--name", help="Display name for the plan")
    parser.add_argument("--description", help="Description of the plan")
    parser.add_argument("--version", default="0.1.0", help="Version information")
    parser.add_argument("--output", help="Output file path (defaults to <id>.ttl)")
    args = parser.parse_args()
    
    # Set defaults
    name = args.name or f"Check-in Plan: {args.id}"
    description = args.description or f"Generated check-in plan for {args.id}"
    output = args.output or f"{args.id}.ttl"
    
    # Generate the plan
    generator = CheckinTemplateGenerator()
    generator.create_plan(args.id, name, description, args.version)
    generator.save_plan(output)
    
    # Validate using the CheckinManager if available
    try:
        from ontology_framework.modules.checkin_manager import CheckinManager
        print("\nValidating with CheckinManager...")
        manager = CheckinManager()
        try:
            manager.load_plan(output)
            print("✅ Plan validated successfully with CheckinManager")
        except Exception as e:
            print(f"❌ CheckinManager validation failed: {str(e)}")
    except ImportError:
        print("\nNote: ontology_framework module not available for validation")

if __name__ == "__main__":
    main() 