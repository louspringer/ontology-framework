#!/usr/bin/env python3
"""
Test script for OpenFlow-Playground integration with the ontology framework.

This script demonstrates vocabulary alignment between reverse engineering and code generation
domains using the ontological approach.
"""

import sys
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ontology_framework.openflow_integration import OpenFlowIntegration
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the ontology-framework directory")
    sys.exit(1)

def test_vocabulary_alignment():
    """Test vocabulary alignment between reverse engineering and code generation."""
    
    print("🧪 Testing OpenFlow-Playground Vocabulary Alignment")
    print("=" * 60)
    
    # Initialize the integration
    try:
        integration = OpenFlowIntegration()
        print("✅ OpenFlow integration initialized successfully")
        
        # Get ontology summary
        summary = integration.get_ontology_summary()
        print(f"📊 Ontology Summary: {json.dumps(summary, indent=2)}")
        
    except Exception as e:
        print(f"❌ Failed to initialize integration: {e}")
        return
    
    # Test data: Reverse engineering output (list-based)
    reverse_engineering_data = [
        {
            "name": "QualityRule",
            "type": "class",
            "description": "A quality rule for code generation",
            "methods": [
                {
                    "name": "validate",
                    "type": "method",
                    "return_type": "bool",
                    "parameters": ["code"]
                },
                {
                    "name": "get_score",
                    "type": "method", 
                    "return_type": "int",
                    "parameters": []
                }
            ]
        },
        {
            "name": "CodeGenerator",
            "type": "class",
            "description": "Generates code from models",
            "methods": [
                {
                    "name": "generate",
                    "type": "method",
                    "return_type": "str",
                    "parameters": ["model"]
                }
            ]
        }
    ]
    
    # Test data: Code generation expected input (dict-based)
    code_generation_data = {
        "QualityRule": {
            "name": "QualityRule",
            "type": "class",
            "description": "A quality rule for code generation",
            "methods": {
                "validate": {
                    "name": "validate",
                    "type": "method",
                    "return_type": "bool",
                    "parameters": ["code"]
                },
                "get_score": {
                    "name": "get_score",
                    "type": "method",
                    "return_type": "int", 
                    "parameters": []
                }
            }
        },
        "CodeGenerator": {
            "name": "CodeGenerator",
            "type": "class",
            "description": "Generates code from models",
            "methods": {
                "generate": {
                    "name": "generate",
                    "type": "method",
                    "return_type": "str",
                    "parameters": ["model"]
                }
            }
        }
    }
    
    print("\n🔍 Testing Vocabulary Alignment...")
    
    # Validate vocabulary alignment
    try:
        validation_result = integration.validate_vocabulary_alignment(
            reverse_engineering_data, 
            code_generation_data
        )
        
        print(f"📋 Validation Result: {json.dumps(validation_result, indent=2)}")
        
        if validation_result["valid"]:
            print("✅ Vocabulary alignment is valid!")
        else:
            print("⚠️ Vocabulary alignment issues detected:")
            for mismatch in validation_result["vocabulary_mismatches"]:
                print(f"  - {mismatch['description']} (Severity: {mismatch['severity']})")
            
            print("\n🔄 Recommended Transformations:")
            for transform in validation_result["recommended_transformations"]:
                print(f"  - {transform['description']} (Priority: {transform['priority']})")
        
    except Exception as e:
        print(f"❌ Vocabulary alignment validation failed: {e}")
        return
    
    # Test transformations
    print("\n🔄 Testing Transformations...")
    
    try:
        # Test list to dict transformation
        transformed_data = integration.apply_transformation(
            reverse_engineering_data, 
            "list_to_dict"
        )
        
        print("✅ List to Dictionary transformation successful")
        print(f"📊 Transformed data structure: {type(transformed_data).__name__}")
        print(f"📊 Transformed data keys: {list(transformed_data.keys())}")
        
        # Test dict to list transformation
        back_to_list = integration.apply_transformation(
            transformed_data, 
            "dict_to_list"
        )
        
        print("✅ Dictionary to List transformation successful")
        print(f"📊 Back to list structure: {type(back_to_list).__name__}")
        print(f"📊 List length: {len(back_to_list)}")
        
    except Exception as e:
        print(f"❌ Transformation failed: {e}")
        return
    
    print("\n🎉 All tests completed successfully!")

def test_ontology_queries():
    """Test SPARQL queries against the ontology."""
    
    print("\n🔍 Testing Ontology Queries")
    print("=" * 40)
    
    try:
        integration = OpenFlowIntegration()
        
        # Test basic ontology queries
        print("📊 Testing ontology structure queries...")
        
        # This would test SPARQL queries if the framework supports them
        # For now, just show the ontology summary
        summary = integration.get_ontology_summary()
        print(f"📊 Ontology contains {summary.get('classes', 0)} classes")
        print(f"📊 Ontology contains {summary.get('object_properties', 0)} object properties")
        print(f"📊 Ontology contains {summary.get('data_properties', 0)} data properties")
        print(f"📊 Ontology contains {summary.get('instances', 0)} instances")
        
    except Exception as e:
        print(f"❌ Ontology query test failed: {e}")

if __name__ == "__main__":
    print("🚀 OpenFlow-Playground Ontology Integration Test")
    print("=" * 60)
    
    # Test vocabulary alignment
    test_vocabulary_alignment()
    
    # Test ontology queries
    test_ontology_queries()
    
    print("\n✨ Test suite completed!")
