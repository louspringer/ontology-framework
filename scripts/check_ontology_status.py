# !/usr/bin/env python3
from load_ontology_tracking import OntologyTracker

def main() -> None:
    tracker = OntologyTracker()
    
    # List of ontologies, to check, ontologies = [
        "guidance.ttl",
        "guidance/modules/patch.ttl",
        "guidance/modules/ontology_tracking.ttl"
    ]
    
    # Check status for each ontology, for ontology in ontologies:
        status = tracker.get_ontology_status(ontology)
        if status:
            print(f"\nStatus, for {ontology}:")
            print(f"  Last, Loaded: {status['lastLoaded']}")
            print(f"  Last, Tested: {status['lastTested']}")
            print(f"  Test, Result: {status['testResult']}")
            print(f"  Error, Count: {status['errorCount']}")
        else:
            print(f"\nNo, status found, for {ontology}")

if __name__ == "__main__":
    main() 