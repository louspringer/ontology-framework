#!/usr/bin/env python3

import sys
import logging
from pathlib import Path
from datetime import datetime
from ontology_framework.mcp.core import MCPCore, ValidationContext
from owlready2 import get_ontology, sync_reasoner
import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        print("Usage: validate_guidance.py <ontology_file>")
        sys.exit(1)
        
    ontology_file = sys.argv[1]
    try:
        # Create MCP configuration
        config = {
            'ontologyPath': ontology_file,
            'targetFiles': [ontology_file],
            'validation': {
                'phaseExecution': {
                    'ontology': {
                        'order': ['ontology'],
                        'requiredFiles': [ontology_file],
                        'validationRules': ['ClassHierarchyCheck', 'PropertyDomainCheck', 'BFG9KPatternCheck']
                    }
                },
                'rules': {
                    'phaseOrder': True
                }
            },
            'validationRules': {
                'ClassHierarchyCheck': {
                    'sparql': """
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT ?class ?superClass
                        WHERE {
                            ?class rdfs:subClassOf+ ?superClass .
                            ?superClass rdfs:subClassOf+ ?class .
                        }
                    """,
                    'message': 'Circular class hierarchy detected'
                },
                'PropertyDomainCheck': {
                    'sparql': """
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT ?prop ?domain
                        WHERE {
                            ?prop rdfs:domain ?domain .
                            FILTER NOT EXISTS { ?domain a rdfs:Class }
                        }
                    """,
                    'message': 'Property domain is not a valid class'
                },
                'BFG9KPatternCheck': {
                    'sparql': """
                        PREFIX bfg9k: <http://example.org/bfg9k#>
                        SELECT ?pattern ?violation
                        WHERE {
                            ?pattern a bfg9k:Pattern .
                            ?violation bfg9k:violatesPattern ?pattern .
                        }
                    """,
                    'message': 'BFG9K pattern violations found'
                }
            },
            'metadata': {
                'version': '0.1.0'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
        
        # Create MCP core instance
        core = MCPCore(config)
        
        # Create validation context
        context = ValidationContext(
            ontology_path=Path(ontology_file),
            target_files=[Path(ontology_file)],
            phase='ontology',
            metadata={'timestamp': datetime.now().isoformat()},
            timestamp=datetime.now()
        )
        
        # Execute validation
        result = core.execute_phase('ontology', context)
        
        # Print results
        print("\nValidation Results:")
        print("-" * 50)
        print(f"Success: {'✓' if result.success else '✗'}")
        
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")
                
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        # --- OWLReady2 Reasoner Validation ---
        print("\nRunning OWLReady2 reasoning (HermiT)...")
        onto = get_ontology(f"file://{Path(ontology_file).absolute()}").load()
        try:
            with onto:
                sync_reasoner()
            inconsistent = list(onto.inconsistent_classes())
            if inconsistent:
                print("\nOWL Reasoner found inconsistencies:")
                for icls in inconsistent:
                    print(f"  - {icls}")
                print("\nValidation failed due to OWL inconsistencies.")
                sys.exit(1)
            else:
                print("OWL Reasoner: No inconsistencies found. Ontology is consistent.")
        except Exception as e:
            print(f"OWLReady2 reasoning failed: {e}")
            sys.exit(1)
        # --- End OWLReady2 Reasoner Validation ---
        
        if result.success:
            print("\nAll validations passed successfully!")
            sys.exit(0)
        else:
            print("\nValidation failed. Please fix the errors and try again.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 