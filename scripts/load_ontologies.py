#!/usr/bin/env python3
"""Script to load ontologies and execute SPARQL updates."""

import logging
import os
from pathlib import Path
from ontology_framework.jena_client import JenaFusekiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_ontologies(client: JenaFusekiClient, ontology_dir: str) -> None:
    """Load all ontology files from a directory.

    Args:
        client: Jena Fuseki client
        ontology_dir: Directory containing ontology files
    """
    for file in Path(ontology_dir).glob("*.ttl"):
        logger.info(f"Loading ontology: {file}")
        client.load_ontology(str(file))

def add_test_error_handling(client: JenaFusekiClient) -> None:
    """Add test error handling components.

    Args:
        client: Jena Fuseki client
    """
    # Add test error handling steps
    query1 = """
    PREFIX ns1: <http://example.org/guidance#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {
        ns1:TestErrorIdentification a ns1:TestErrorHandlingStep ;
            ns1:hasStepOrder "1"^^xsd:integer ;
            ns1:hasStepAction "Identify failing tests and error patterns" ;
            rdfs:label "Test Error Identification" ;
            rdfs:comment "First step in test error handling process" .

        ns1:TestErrorAnalysis a ns1:TestErrorHandlingStep ;
            ns1:hasStepOrder "2"^^xsd:integer ;
            ns1:hasStepAction "Analyze root cause of test failures" ;
            rdfs:label "Test Error Analysis" ;
            rdfs:comment "Second step in test error handling process" .

        ns1:TestErrorRecovery a ns1:TestErrorHandlingStep ;
            ns1:hasStepOrder "3"^^xsd:integer ;
            ns1:hasStepAction "Implement fixes for failing tests" ;
            rdfs:label "Test Error Recovery" ;
            rdfs:comment "Third step in test error handling process" .

        ns1:TestErrorPrevention a ns1:TestErrorHandlingStep ;
            ns1:hasStepOrder "4"^^xsd:integer ;
            ns1:hasStepAction "Add validation to prevent similar failures" ;
            rdfs:label "Test Error Prevention" ;
            rdfs:comment "Fourth step in test error handling process" .
    }
    """
    client.update_sparql(query1)

    # Add SHACL validation for test error handling steps
    query2 = """
    PREFIX ns1: <http://example.org/guidance#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    INSERT DATA {
        ns1:TestErrorHandlingStepShape a sh:NodeShape ;
            sh:targetClass ns1:TestErrorHandlingStep ;
            sh:property [
                sh:path ns1:hasStepOrder ;
                sh:datatype xsd:integer ;
                sh:minCount 1 ;
                sh:maxCount 1 ;
            ] ;
            sh:property [
                sh:path ns1:hasStepAction ;
                sh:datatype xsd:string ;
                sh:minCount 1 ;
                sh:maxCount 1 ;
            ] .
    }
    """
    client.update_sparql(query2)

    # Add test error handling process
    query3 = """
    PREFIX ns1: <http://example.org/guidance#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    INSERT DATA {
        ns1:standardTestErrorHandling a ns1:TestErrorHandlingProcess ;
            rdfs:label "Standard Test Error Handling" ;
            rdfs:comment "Standard process for handling test errors" ;
            ns1:hasProcessStep ns1:TestErrorIdentification ;
            ns1:hasProcessStep ns1:TestErrorAnalysis ;
            ns1:hasProcessStep ns1:TestErrorRecovery ;
            ns1:hasProcessStep ns1:TestErrorPrevention ;
            ns1:hasProcessName "Standard Test Error Handling" ;
            ns1:hasProcessDescription "Standard process for identifying, analyzing, fixing and preventing test errors" .
    }
    """
    client.update_sparql(query3)

    # Add SHACL validation for test error handling process
    query4 = """
    PREFIX ns1: <http://example.org/guidance#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>

    INSERT DATA {
        ns1:TestErrorHandlingProcessShape a sh:NodeShape ;
            sh:targetClass ns1:TestErrorHandlingProcess ;
            sh:property [
                sh:path ns1:hasProcessStep ;
                sh:minCount 4 ;
                sh:maxCount 4
            ] .
    }
    """
    client.update_sparql(query4)

def main() -> None:
    """Main function."""
    client = JenaFusekiClient()
    
    # Load existing ontologies
    ontology_dir = os.path.join(os.path.dirname(__file__), "..", "guidance", "modules")
    load_ontologies(client, ontology_dir)
    
    # Add test error handling components
    add_test_error_handling(client)
    
    logger.info("Ontologies loaded and updated successfully")

if __name__ == "__main__":
    main() 