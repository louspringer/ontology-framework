#!/usr/bin/env python3
from pathlib import Path
from ontology_framework.guidance_loader import GuidanceLoader
import json

def main():
    # Initialize the guidance loader
    loader = GuidanceLoader(Path("guidance.ttl"))
    
    # Get all test requirements
    test_reqs = loader.get_test_requirements()
    
    # Print test protocols
    print("\nTest Protocols:")
    for protocol in test_reqs["protocols"]:
        print(f"- {protocol['label']}: {protocol['comment']}")
    
    # Print test phases
    print("\nTest Phases:")
    for phase in test_reqs["phases"]:
        print(f"- {phase['label']}: {phase['comment']}")
    
    # Print test coverage
    print("\nTest Coverage:")
    for coverage in test_reqs["coverage"]:
        print(f"- {coverage['label']}: {coverage['comment']}")
    
    # Print SHACL shapes
    print("\nSHACL Shapes:")
    for shape in test_reqs["shapes"]:
        print(f"- Shape: {shape['shape']}")
        print(f"  Target Class: {shape['targetClass']}")
        print(f"  Property: {shape['property']}")
        print(f"  Min Count: {shape['minCount']}")
        print(f"  Max Count: {shape['maxCount']}")
        print(f"  Datatype: {shape['datatype']}")
    
    # Get a specific section
    print("\nTest Protocol Section:")
    section = loader.get_section("TestProtocol")
    for triple in section:
        print(f"- {triple['subject']} {triple['predicate']} {triple['object']}")

if __name__ == "__main__":
    main() 