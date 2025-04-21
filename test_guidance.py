from guidance import GuidanceOntology
from pathlib import Path

def main() -> None:
    # Initialize the guidance ontology
    guidance = GuidanceOntology()
    
    # Get and print all classes
    print("\n=== Classes ===")
    for cls in guidance.get_classes():
        print(f"\nClass: {cls.label}")
        print(f"  URI: {cls.uri}")
        print(f"  Comment: {cls.comment}")
    
    # Get and print all properties
    print("\n=== Properties ===")
    for prop in guidance.get_properties():
        print(f"\nProperty: {prop.label}")
        print(f"  URI: {prop.uri}")
        print(f"  Comment: {prop.comment}")
        if prop.domain:
            print(f"  Domain: {prop.domain}")
        if prop.range:
            print(f"  Range: {prop.range}")
    
    # Get and print all SHACL shapes
    print("\n=== SHACL Shapes ===")
    for shape in guidance.get_shacl_shapes():
        print(f"\nShape: {shape.label}")
        print(f"  URI: {shape.uri}")
        print(f"  Comment: {shape.comment}")
        print(f"  Target Class: {shape.target_class}")
        if shape.properties:
            print("  Properties:")
            for prop_dict in shape.properties:
                print(f"    - {prop_dict}")
    
    # Get and print all test protocols
    print("\n=== Test Protocols ===")
    for protocol in guidance.get_test_protocols():
        print(f"\nProtocol: {protocol.label}")
        print(f"  URI: {protocol.uri}")
        print(f"  Comment: {protocol.comment}")
    
    # Get and print all TODO items
    print("\n=== TODO Items ===")
    for todo in guidance.get_todo_items():
        print(f"\nTODO: {todo.label}")
        print(f"  URI: {todo.uri}")
        print(f"  Comment: {todo.comment}")
    
    # Get and print test requirements
    print("\n=== Test Requirements ===")
    requirements = guidance.get_test_requirements()
    for key, value in requirements.items():
        print(f"{key}: {value}")
    
    # Get and print conformance levels
    print("\n=== Conformance Levels ===")
    levels = guidance.get_conformance_levels()
    print("Valid levels:", levels)
    print("\nValidation tests:")
    for level in levels + ["INVALID"]:
        print(f"  {level}: {guidance.validate_conformance_level(level)}")
    
    # Test ontology emission
    print("\n=== Testing Ontology Emission ===")
    output_path = "guidance_emitted.ttl"
    guidance.emit_ontology(output_path)
    print(f"Ontology emitted to {output_path}")
    
    # Verify the emitted file exists and has content
    if Path(output_path).exists():
        with open(output_path, 'r') as f:
            content = f.read()
            print(f"\nEmitted ontology size: {len(content)} bytes")
            print("First few lines:")
            print("\n".join(content.splitlines()[:5]))

if __name__ == "__main__":
    main() 