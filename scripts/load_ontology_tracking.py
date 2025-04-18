#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from rdflib import Graph, URIRef, Literal, XSD, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
import requests
from typing import List, Dict, Optional, Any, TypedDict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ontology_tracking.log'),
        logging.StreamHandler()
    ]
)

# Namespace definitions
TRACKING = Namespace("http://example.org/ontology_tracking#")

# Define tracking terms
ONTOLOGY_STATUS = TRACKING["OntologyStatus"]
CONSUMPTION_STATUS = TRACKING["ConsumptionStatus"]
TESTING_STATUS = TRACKING["TestingStatus"]
HAS_CONSUMPTION_STATUS = TRACKING["hasConsumptionStatus"]
HAS_TESTING_STATUS = TRACKING["hasTestingStatus"]
LAST_LOADED = TRACKING["lastLoaded"]
LAST_TESTED = TRACKING["lastTested"]
TEST_RESULT = TRACKING["testResult"]
ERROR_COUNT = TRACKING["errorCount"]

class OntologyStatus(TypedDict):
    lastLoaded: str
    lastTested: str
    testResult: str
    errorCount: int

class OntologyTracker:
    def __init__(self, graphdb_url: str = "http://localhost:7200") -> None:
        self.graphdb_url = graphdb_url
        self.repo_name = "test-ontology-framework"
        self.sparql_endpoint = f"{graphdb_url}/repositories/{self.repo_name}"
        self.g = Graph()

    def load_tracking_ontology(self) -> bool:
        """Load the ontology tracking module into GraphDB."""
        try:
            # Load the tracking ontology
            tracking_path = "guidance/modules/ontology_tracking.ttl"
            self.g.parse(tracking_path, format="turtle")
            
            # Upload to GraphDB
            headers = {"Content-Type": "application/x-turtle"}
            data = self.g.serialize(format="turtle")
            
            response = requests.post(
                f"{self.graphdb_url}/repositories/{self.repo_name}/statements",
                headers=headers,
                data=data
            )
            
            if response.status_code == 204:
                logging.info("Successfully loaded ontology tracking module into GraphDB")
                return True
            else:
                logging.error(f"Failed to load tracking ontology: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error loading tracking ontology: {str(e)}")
            return False

    def scan_ontologies(self) -> List[str]:
        """Scan the repository for ontology files."""
        ontologies = []
        
        # Scan root directory
        for file in os.listdir("."):
            if file.endswith(".ttl"):
                ontologies.append(file)
        
        # Scan guidance/modules directory
        modules_dir = "guidance/modules"
        if os.path.exists(modules_dir):
            for file in os.listdir(modules_dir):
                if file.endswith(".ttl"):
                    ontologies.append(f"{modules_dir}/{file}")
        
        return ontologies

    def update_ontology_status(self, ontology_path: str, loaded: bool = False, tested: bool = False) -> bool:
        """Update the status of an ontology in GraphDB."""
        try:
            # Create URIs for the ontology and its status
            ontology_uri = URIRef(f"file://{os.path.abspath(ontology_path)}")
            status_uri = URIRef(f"{ontology_uri}_status")
            consumption_uri = URIRef(f"{ontology_uri}_consumption")
            testing_uri = URIRef(f"{ontology_uri}_testing")
            
            # Create the status graph
            status_g = Graph()
            
            # Add ontology status
            status_g.add((status_uri, RDF.type, ONTOLOGY_STATUS))
            status_g.add((status_uri, HAS_CONSUMPTION_STATUS, consumption_uri))
            status_g.add((status_uri, HAS_TESTING_STATUS, testing_uri))
            
            # Add consumption status
            status_g.add((consumption_uri, RDF.type, CONSUMPTION_STATUS))
            status_g.add((consumption_uri, LAST_LOADED, 
                         Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
            
            # Add testing status
            status_g.add((testing_uri, RDF.type, TESTING_STATUS))
            status_g.add((testing_uri, LAST_TESTED, 
                         Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
            status_g.add((testing_uri, TEST_RESULT, 
                         Literal("PASS" if tested else "UNKNOWN")))
            status_g.add((testing_uri, ERROR_COUNT, 
                         Literal(0, datatype=XSD.integer)))
            
            # Upload to GraphDB
            headers = {"Content-Type": "application/x-turtle"}
            data = status_g.serialize(format="turtle")
            
            response = requests.post(
                f"{self.graphdb_url}/repositories/{self.repo_name}/statements",
                headers=headers,
                data=data
            )
            
            if response.status_code == 204:
                logging.info(f"Successfully updated status for {ontology_path}")
                return True
            else:
                logging.error(f"Failed to update status for {ontology_path}: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error updating status for {ontology_path}: {str(e)}")
            return False

    def get_ontology_status(self, ontology_path: str) -> Optional[OntologyStatus]:
        """Get the current status of an ontology from GraphDB."""
        try:
            ontology_uri = URIRef(f"file://{os.path.abspath(ontology_path)}")
            status_uri = URIRef(f"{ontology_uri}_status")
            
            query = f"""
            PREFIX tracking: <{TRACKING}>
            SELECT ?lastLoaded ?lastTested ?testResult ?errorCount
            WHERE {{
                <{status_uri}> tracking:hasConsumptionStatus ?consumption .
                <{status_uri}> tracking:hasTestingStatus ?testing .
                ?consumption tracking:lastLoaded ?lastLoaded .
                ?testing tracking:lastTested ?lastTested .
                ?testing tracking:testResult ?testResult .
                ?testing tracking:errorCount ?errorCount .
            }}
            """
            
            response = requests.post(
                self.sparql_endpoint,
                headers={"Accept": "application/sparql-results+json"},
                data={"query": query}
            )
            
            if response.status_code == 200:
                results = response.json()
                if results["results"]["bindings"]:
                    binding = results["results"]["bindings"][0]
                    return {
                        "lastLoaded": binding["lastLoaded"]["value"],
                        "lastTested": binding["lastTested"]["value"],
                        "testResult": binding["testResult"]["value"],
                        "errorCount": int(binding["errorCount"]["value"])
                    }
                return None
            else:
                logging.error(f"Failed to query status for {ontology_path}: {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error querying status for {ontology_path}: {str(e)}")
            return None

def main() -> None:
    tracker = OntologyTracker()
    
    # Load the tracking ontology
    if not tracker.load_tracking_ontology():
        sys.exit(1)
    
    # Scan for ontologies
    ontologies = tracker.scan_ontologies()
    logging.info(f"Found {len(ontologies)} ontology files")
    
    # Update status for each ontology
    for ontology in ontologies:
        # Check if the ontology is already in GraphDB
        status = tracker.get_ontology_status(ontology)
        if status:
            logging.info(f"Status for {ontology}: {status}")
        else:
            # Update status for new ontology
            tracker.update_ontology_status(ontology)

if __name__ == "__main__":
    main() 