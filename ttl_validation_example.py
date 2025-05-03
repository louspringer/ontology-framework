#!/usr/bin/env python3
"""
Simple TTL file validation example
"""
from rdflib import Graph
import sys

def validate_ttl(file_path):
    """Validate a TTL file"""
    print(f"Validating {file_path}...")
    g = Graph()
    try:
        g.parse(file_path, format="turtle")
        print(f"✅ Valid TTL file: {file_path}")
        print(f"Found {len(g)} triples")
        return True
    except Exception as e:
        print(f"❌ Invalid TTL file: {file_path}")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ttl_validation_example.py <ttl_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = validate_ttl(file_path)
    sys.exit(0 if success else 1) 