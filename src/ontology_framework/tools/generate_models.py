"""Script to generate models for Python files."""

import argparse
from pathlib import Path
from model_generator import ModelGenerator

def main():
    """Main entry point for model generation."""
    parser = argparse.ArgumentParser(description="Generate models for Python files")
    parser.add_argument("directory", help="Directory containing Python files")
    parser.add_argument("--output", "-o", default="models.ttl", help="Output file for models")
    parser.add_argument("--pattern", "-p", default="*.py", help="File pattern to match")
    args = parser.parse_args()
    
    generator = ModelGenerator()
    models = generator.generate_models_for_directory(args.directory, args.pattern)
    generator.save_models(args.output)
    
    print(f"Generated {len(models)} models")
    print(f"Models saved to {args.output}")
    
if __name__ == "__main__":
    main() 