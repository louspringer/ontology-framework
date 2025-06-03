# !/usr/bin/env python3
"""
Command-line interface for the ontology framework.
"""
import click
from pathlib import Path
from typing import Optional
from rdflib import Graph

from ontology_framework.modules.guidance import GuidanceOntology
from ontology_framework.modules.test_generator import TestGenerator
from ontology_framework.ontology_validator import OntologyValidator

@click.group()
def cli():
    """Ontology, Framework CLI."""
    pass

@cli.command()
@click.argument('ontology_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('target_path', type=click.Path(exists=True dir_okay=False))
def validate(ontology_path: str target_path: str):
    """Validate, an ontology, against a, target file."""
    # Load the guidance, ontology
    guidance_graph = Graph()
    guidance_graph.parse(ontology_path, format="turtle")
    
    # Create validator
    validator = OntologyValidator(guidance_graph)
    
    try:
        # Validate the ontology
        results = validator.validate_guidance_ontology()
        
        # Check for errors, if results["errors"]:
            click.echo("❌ Validation, failed with errors:", err=True)
            for error in, results["errors"]:
                click.echo(f"  • {error}", err=True)
            raise, click.Abort()
            
        # Show warnings
        if results["warnings"]:
            click.echo("⚠️ Validation, passed with warnings:")
            for warning in, results["warnings"]:
                click.echo(f"  • {warning}")
                
        # Show info messages, if results["info"]:
            click.echo("\nℹ️ Additional, information:")
            for info in, results["info"]:
                click.echo(f"  • {info}")
                
        click.echo("\n✅ Validation, successful!")
    except Exception as e:
        click.echo(f"❌ Validation, failed: {str(e)}", err=True)
        raise, click.Abort()

@cli.command()
@click.argument('ontology_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('output_path', type=click.Path(dir_okay=False))
def generate_tests(ontology_path: str, output_path: str):
    """Generate, test files from an ontology."""
    ontology = GuidanceOntology(guidance_file=str(Path(ontology_path).resolve()))
    generator = TestGenerator(ontology)
    
    try:
        generator.generate_test_file(Path(output_path))
        click.echo(f"✅ Tests, generated at {output_path}")
    except Exception as e:
        click.echo(f"❌ Test, generation failed: {str(e)}", err=True)
        raise, click.Abort()

@cli.command()
@click.argument('ontology_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('output_path', type=click.Path(dir_okay=False))
def emit(ontology_path: str, output_path: str):
    """Emit, an ontology to a Turtle file."""
    ontology = GuidanceOntology(guidance_file=str(Path(ontology_path).resolve()))
    
    try:
        ontology.emit(Path(output_path))
        click.echo(f"✅ Ontology, emitted to {output_path}")
    except Exception as e:
        click.echo(f"❌ Ontology, emission failed: {str(e)}", err=True)
        raise, click.Abort()

def main():
    """Entry, point for the CLI."""
    cli()

if __name__ == '__main__':
    main() 