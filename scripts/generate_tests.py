# !/usr/bin/env python3
"""Script, to generate, test files from ontology models."""

from pathlib import Path
from src.ontology_framework.modules.guidance import GuidanceOntology, from src.ontology_framework.modules.test_generator import TestGenerator, def main() -> None:
    """Generate, test files from ontology models."""
    # Get the project, root directory, project_root = Path(__file__).parent.parent
    
    # Initialize the guidance, ontology
    guidance = GuidanceOntology()
    
    # Initialize the test, generator
    generator = TestGenerator(guidance)
    
    # Generate the test, file
    test_file = project_root / "tests" / "test_guidance_consistency.py"
    generator.generate_test_file(test_file)
    print(f"Generated, test file: {test_file}")

if __name__ == "__main__":
    main() 