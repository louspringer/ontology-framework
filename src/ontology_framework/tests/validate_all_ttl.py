import os
from pathlib import Path
from typing import List, Dict
from rdflib import Graph
from ontology_framework.modules.ontology_manager import OntologyManager

def find_ttl_files(root_dir: str) -> List[str]:
    """Find all TTL files in the project.
    
    Args:
        root_dir: Root directory to search from
        
    Returns:
        List of paths to TTL files
    """
    ttl_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.ttl'):
                ttl_files.append(os.path.join(root, file))
    return ttl_files

def validate_all_ttl_files() -> Dict[str, List[str]]:
    """Validate all TTL files in the project.
    
    Returns:
        Dictionary mapping file paths to validation messages
    """
    # Get the project root directory
    project_root = str(Path(__file__).parent.parent.parent)
    
    # Find all TTL files
    ttl_files = find_ttl_files(project_root)
    
    # Validate each file
    results = {}
    for ttl_file in ttl_files:
        try:
            manager = OntologyManager(ttl_file)
            validation_messages = manager.validate_ontology()
            if validation_messages:
                results[ttl_file] = validation_messages
        except Exception as e:
            results[ttl_file] = [f"Error validating file: {str(e)}"]
    
    return results

if __name__ == '__main__':
    print("Validating all TTL files in the project...")
    results = validate_all_ttl_files()
    
    if not results:
        print("All TTL files passed validation!")
    else:
        print("\nValidation issues found:")
        for file_path, messages in results.items():
            print(f"\nFile: {file_path}")
            for message in messages:
                print(f"  - {message}") 