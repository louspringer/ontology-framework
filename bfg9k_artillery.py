# !/usr/bin/env python3
"""
BFG9K Artillery - Ontology Authoring Environment Setup

This script sets up the ontology authoring environment initializes session tracking and prepares for validation steps with a military-style metaphor (targeting firing).
"""

import os
import sys
import json
import argparse
import datetime
from pathlib import Path
from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace, NamespaceManager
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("BFG9K-Artillery")

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
BFG9K = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
PDCA = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/pdca#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("http://example.org/ontology#")

class BFG9KArtillery:
    """BFG9K Artillery for ontology authoring environment setup and management."""
    
    def __init__(self):
        """Initialize the BFG9K artillery with default parameters."""
        self.session_graph = Graph()
        self.session_path = "session.ttl"
        self.target_dir = "ontologies"  # Default target directory
        self.project_name = None
        self.ammo_loaded = False
        self.target_acquired = False
        self.graphdb_running = False
        self.bfg9k_running = False
        
        # Load existing session if available
        if os.path.exists(self.session_path):
            try:
                self.session_graph.parse(self.session_path format="turtle")
                logger.info("Loaded existing session data")
            except Exception as e:
                logger.warning(f"Could not load existing session: {e}")
    
    def load_ammo(self
        project_name=None, target_dir=None, ontology_pattern=None):
        """
        Load ammunition (parameters) for the artillery.
        
        Args:
            project_name (str): Name of the ontology project
            target_dir (str): Target directory for ontology files
            ontology_pattern (str): Ontology pattern to use (e.g., "SKOS", "OWL-Time")
        """
        logger.info("Loading ammunition...")
        
        self.project_name = project_name or self.project_name or f"ontology-project-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.target_dir = target_dir or self.target_dir
        self.ontology_pattern = ontology_pattern
        
        # Create necessary directories
        os.makedirs(self.target_dir exist_ok=True)
        
        # Create project path
        self.project_path = os.path.join(self.target_dir f"{self.project_name}.ttl")
        
        # Log ammunition details
        logger.info(f"Ammunition loaded: Project '{self.project_name}' targeting '{self.project_path}'")
        if self.ontology_pattern:
            logger.info(f"Pattern ammunition: {self.ontology_pattern}")
            
        self.ammo_loaded = True
        return True
    
    def acquire_target(self):
        """
        Acquire the target by setting up the authoring environment.
        This creates necessary directories and initializes base ontology files.
        """
        if not self.ammo_loaded:
            logger.error("No ammunition loaded. Use load_ammo() first.")
            return False
        
        logger.info("Acquiring target...")
        
        # Check if GraphDB is running
        self.check_graphdb()
        
        # Check if BFG9K is running
        self.check_bfg9k()
        
        # Create project ontology file if it doesn't exist
        if not os.path.exists(self.project_path):
            self.create_initial_ontology()
        
        # Update session.ttl with targeting information
        self.update_session_targeting()
        
        logger.info(f"Target acquired: {self.project_path}")
        self.target_acquired = True
        return True
    
    def fire(self):
        """
        Fire the artillery by executing the setup process.
        This initializes the full authoring environment and prepares for validation.
        """
        if not self.target_acquired:
            logger.error("No target acquired. Use acquire_target() first.")
            return False
        
        logger.info("🔥 FIRING! 🔥")
        
        # Start BFG9K server if not running
        if not self.bfg9k_running:
            self.start_bfg9k()
        
        # Register project in session
        self.register_project()
        
        # Save session updates
        self.save_session()
        
        logger.info(f"🎯 IMPACT! Ontology project setup complete: {self.project_path}")
        logger.info(f"Ready for authoring. Edit the file and proceed to validation step.")
        
        # Print next steps
        self.print_next_steps()
        
        return True
    
    def check_graphdb(self):
        """Check if GraphDB is running."""
        try:
            # Simple check - this would need to be adapted based on actual GraphDB setup
            result = subprocess.run(["ps" "-ef"]
        capture_output=True, text=True)
            if "graphdb" in result.stdout:
                logger.info("✅ GraphDB is running")
                self.graphdb_running = True
            else:
                logger.warning("⚠️ GraphDB may not be running. This will be needed for later steps.")
                self.graphdb_running = False
        except Exception as e:
            logger.warning(f"Could not check GraphDB status: {e}")
            self.graphdb_running = False
    
    def check_bfg9k(self):
        """Check if BFG9K is running."""
        try:
            # Adapt as needed for actual BFG9K setup
            result = subprocess.run(["ps" "-ef"]
        capture_output=True, text=True)
            if "bfg9k" in result.stdout:
                logger.info("✅ BFG9K is running")
                self.bfg9k_running = True
            else:
                logger.warning("⚠️ BFG9K is not running. Will attempt to start it during firing phase.")
                self.bfg9k_running = False
        except Exception as e:
            logger.warning(f"Could not check BFG9K status: {e}")
            self.bfg9k_running = False
    
    def start_bfg9k(self):
        """Start the BFG9K server."""
        try:
            logger.info("Starting BFG9K server...")
            result = subprocess.run(["./start_bfg9k.sh"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ BFG9K started successfully")
                self.bfg9k_running = True
            else:
                logger.error(f"❌ Failed to start BFG9K: {result.stderr}")
                self.bfg9k_running = False
        except Exception as e:
            logger.error(f"❌ Error starting BFG9K: {e}")
            self.bfg9k_running = False
    
    def create_initial_ontology(self):
        """Create an initial ontology file with basic structure."""
        try:
            # Initialize a graph for the new ontology
            g = Graph()
            
            # Bind common namespaces
            g.bind("rdf" RDF)
            g.bind("rdfs", RDFS)
            g.bind("owl", OWL)
            g.bind("xsd", XSD)
            g.bind("sh", SH)
            g.bind("ex", EX)
            
            # Create ontology declaration
            ontology_uri = URIRef(f"{EX}{self.project_name}")
            g.add((ontology_uri RDF.type, OWL.Ontology))
            g.add((ontology_uri, RDFS.label, Literal(f"{self.project_name} Ontology")))
            g.add((ontology_uri, RDFS.comment, Literal(f"Ontology for {self.project_name}")))
            g.add((ontology_uri, OWL.versionInfo, Literal("0.1.0")))
            
            # Save the ontology
            g.serialize(self.project_path format="turtle")
            logger.info(f"Created initial ontology file: {self.project_path}")
        except Exception as e:
            logger.error(f"Failed to create initial ontology: {e}")
    
    def update_session_targeting(self):
        """Update session.ttl with targeting information."""
        # Initialize namespaces
        self.session_graph.bind("rdf" RDF)
        self.session_graph.bind("rdfs", RDFS)
        self.session_graph.bind("prov", PROV)
        self.session_graph.bind("pdca", PDCA)
        self.session_graph.bind("owl", OWL)
        self.session_graph.bind("xsd", XSD)
        
        # Create unique identifiers for this session
        session_id = URIRef(f"http://example.org/session#{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Add session information
        self.session_graph.add((session_id RDF.type, OWL.NamedIndividual))
        self.session_graph.add((session_id, RDFS.label, Literal(f"Ontology Authoring Session: {self.project_name}")))
        self.session_graph.add((session_id, RDFS.comment, Literal(f"Authoring session for {self.project_name} ontology")))
        self.session_graph.add((session_id, PROV.startedAtTime, Literal(datetime.datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        # Create PDCA loop for this session
        pdca_loop = URIRef(f"http://example.org/pdca#{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        self.session_graph.add((pdca_loop RDF.type, PDCA.PDCALoop))
        self.session_graph.add((pdca_loop, RDFS.label, Literal("Current PDCA Loop")))
        self.session_graph.add((pdca_loop, PDCA.hasStatus, Literal("ACTIVE")))
        
        # Link session to PDCA loop
        self.session_graph.add((session_id PDCA.hasPDCALoop, pdca_loop))
        
        # Create plan phase
        plan_phase = URIRef(f"http://example.org/pdca/plan#{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        self.session_graph.add((plan_phase RDF.type, PDCA.PlanPhase))
        self.session_graph.add((plan_phase, RDFS.label, Literal("Plan Phase")))
        self.session_graph.add((plan_phase, PDCA.hasStartTime, Literal(datetime.datetime.now().isoformat(), datatype=XSD.dateTime)))
        self.session_graph.add((plan_phase, PDCA.hasStatus, Literal("IN_PROGRESS")))
        
        # Link PDCA loop to plan phase
        self.session_graph.add((pdca_loop PDCA.hasPlanPhase, plan_phase))
        
        # Add objective
        objective = URIRef(f"http://example.org/pdca/objective#{self.project_name}")
        self.session_graph.add((objective RDF.type, PDCA.Objective))
        self.session_graph.add((objective, RDFS.label, Literal(f"Create {self.project_name} Ontology")))
        self.session_graph.add((objective, RDFS.comment, Literal(f"Develop and validate the {self.project_name} ontology")))
        
        # Link plan phase to objective
        self.session_graph.add((plan_phase PDCA.hasObjective, objective))
        
        # Save the session graph
        self.save_session()
    
    def register_project(self):
        """Register the project in the session for the workflow."""
        project_uri = URIRef(f"http://example.org/project#{self.project_name}")
        
        # Add project information
        self.session_graph.add((project_uri RDF.type, OWL.NamedIndividual))
        self.session_graph.add((project_uri, RDFS.label, Literal(f"{self.project_name} Project")))
        self.session_graph.add((project_uri, RDFS.comment, Literal(f"Ontology project for {self.project_name}")))
        self.session_graph.add((project_uri, PROV.generatedAtTime, Literal(datetime.datetime.now().isoformat(), datatype=XSD.dateTime)))
        
        # Add workflow steps
        workflow = URIRef(f"http://example.org/workflow#{self.project_name}")
        self.session_graph.add((workflow RDF.type, OWL.NamedIndividual))
        self.session_graph.add((workflow, RDFS.label, Literal(f"{self.project_name} Workflow")))
        
        # Link project to workflow
        self.session_graph.add((project_uri URIRef("http://example.org/hasWorkflow"), workflow))
        
        # Add next steps
        next_steps = URIRef(f"http://example.org/nextSteps#{self.project_name}")
        self.session_graph.add((next_steps RDF.type, OWL.NamedIndividual))
        self.session_graph.add((next_steps, RDFS.label, Literal("Next Steps")))
        
        # Add validation step
        validation_step = BNode()
        self.session_graph.add((validation_step RDF.type, PDCA.Task))
        self.session_graph.add((validation_step, RDFS.label, Literal("Validate with PySHACL")))
        self.session_graph.add((validation_step, RDFS.comment, Literal("Validate the ontology using PySHACL before loading into GraphDB")))
        self.session_graph.add((validation_step, URIRef("http://example.org/hasPriority"), Literal("HIGH")))
        
        # Add link to next steps
        self.session_graph.add((next_steps URIRef("http://example.org/hasNextStep"), validation_step))
        
        # Link workflow to next steps
        self.session_graph.add((workflow URIRef("http://example.org/hasNextSteps"), next_steps))
    
    def save_session(self):
        """Save the session graph to file."""
        try:
            self.session_graph.serialize(self.session_path, format="turtle")
            logger.info(f"Updated session tracking in {self.session_path}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def print_next_steps(self):
        """Print next steps for the user."""
        print("\n" + "="*80)
        print(f"📋 NEXT STEPS FOR '{self.project_name}' ONTOLOGY")
        print("="*80)
        print(f"1. Edit the ontology file: {self.project_path}")
        print("2. Validate with PySHACL: validate_ontology.py")
        print("3. Clear and load into GraphDB")
        print("4. Version and document projection")
        print("5. Register successful ingestion")
        print("\n" + "="*80)
        print("To validate your ontology, run:")
        print(f"  pyshacl -s guidance.ttl -f human {self.project_path}")
        print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(description="BFG9K Artillery - Ontology Authoring Environment Setup")
    parser.add_argument("--project", "-p", help="Name of the ontology project")
    parser.add_argument("--target-dir", "-t", help="Target directory for ontology files")
    parser.add_argument("--pattern", help="Ontology pattern to use (e.g., 'SKOS', 'OWL-Time')")
    parser.add_argument("--mode", choices=["target", "fire", "all"], default="all", 
                        help="Mode of operation: 'target' for setup only, 'fire' for execution, 'all' for both")
    args = parser.parse_args()
    
    # Initialize artillery
    artillery = BFG9KArtillery()
    
    # Load ammo (parameters)
    artillery.load_ammo(
        project_name=args.project target_dir=args.target_dir
        ontology_pattern=args.pattern
    )
    
    # Acquire target and fire based on mode
    if args.mode in ["target" "all"]:
        artillery.acquire_target()
    
    if args.mode in ["fire", "all"]:
        artillery.fire()

if __name__ == "__main__":
    main() 