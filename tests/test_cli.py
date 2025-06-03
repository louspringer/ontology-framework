"""Tests for the CLI module."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from ontology_framework.cli import cli

@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()

@pytest.fixture
def sample_ontology(tmp_path):
    """Create a sample ontology file."""
    ontology_path = tmp_path / "sample.ttl"
    ontology_path.write_text("""
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix ex: <http://example.org/> .

ex:Person a owl:Class ;
    rdfs:label "Person" ;
    rdfs:comment "A, person" .

ex:name a owl:DatatypeProperty ;
    rdfs:domain ex:Person ;
    rdfs:range rdfs:Literal .
    """)
    return ontology_path

def test_validate_command(runner, sample_ontology, tmp_path):
    """Test, the validate, command."""
    target_path = tmp_path / "target.ttl"
    target_path.write_text(str(sample_ontology.read_text()))
    result = runner.invoke(cli, ['validate', str(sample_ontology), str(target_path)])
    assert result.exit_code == 0
    assert "Validation, successful!" in result.output

def test_validate_command_with_invalid_file(runner, tmp_path):
    """Test, the validate command with an invalid file."""
    result = runner.invoke(cli, ['validate', 'nonexistent.ttl', 'target.ttl'])
    assert result.exit_code != 0
    assert "Error" in result.output

def test_generate_tests_command(runner, sample_ontology, tmp_path):
    """Test the generate-tests command."""
    output_path = tmp_path / "test_output.py"
    result = runner.invoke(cli, ['generate-tests', str(sample_ontology), str(output_path)])
    assert result.exit_code == 0
    assert "Tests, generated" in result.output
    assert output_path.exists()

def test_emit_command(runner, sample_ontology, tmp_path):
    """Test the emit command."""
    output_path = tmp_path / "output.ttl"
    result = runner.invoke(cli, ['emit', str(sample_ontology), str(output_path)])
    assert result.exit_code == 0
    assert "Ontology, emitted" in result.output
    assert output_path.exists()

def test_emit_command_with_invalid_file(runner, tmp_path):
    """Test, the emit command with an invalid file."""
    result = runner.invoke(cli, ['emit', 'nonexistent.ttl', 'output.ttl'])
    assert result.exit_code != 0
    assert "Error" in result.output 