#!/usr/bin/env python3
"""
Command-line interface for the ontology framework.
"""
import click
from pathlib import Path
from typing import Optional

from ontology_framework.modules.guidance import GuidanceOntology
from ontology_framework.modules.test_generator import TestGenerator

@click.group()
def cli():
    """Ontology Framework CLI."""
    pass

@cli.command()
@click.argument('ontology_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('target_path', type=click.Path(exists=True, dir_okay=False))
def validate(ontology_path: str, target_path: str):
    """Validate an ontology against a target file."""
    ontology = GuidanceOntology(Path(ontology_path))
    target = Path(target_path)
    
    try:
        ontology.validate(target)
        click.echo("✅ Validation successful!")
    except Exception as e:
        click.echo(f"❌ Validation failed: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('ontology_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('output_path', type=click.Path(dir_okay=False))
def generate_tests(ontology_path: str, output_path: str):
    """Generate test files from an ontology."""
    ontology = GuidanceOntology(Path(ontology_path))
    generator = TestGenerator(ontology)
    
    try:
        generator.generate_test_file(Path(output_path))
        click.echo(f"✅ Tests generated at {output_path}")
    except Exception as e:
        click.echo(f"❌ Test generation failed: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('ontology_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('output_path', type=click.Path(dir_okay=False))
def emit(ontology_path: str, output_path: str):
    """Emit an ontology to a Turtle file."""
    ontology = GuidanceOntology(Path(ontology_path))
    
    try:
        ontology.emit(Path(output_path))
        click.echo(f"✅ Ontology emitted to {output_path}")
    except Exception as e:
        click.echo(f"❌ Ontology emission failed: {str(e)}", err=True)
        raise click.Abort()

def main():
    """Entry point for the CLI."""
    cli() 