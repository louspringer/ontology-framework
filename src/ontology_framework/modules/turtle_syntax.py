# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

"""
Module for fixing and validating Turtle syntax.
"""

from typing import Optional, Tuple, Union
from rdflib import Graph
from pyshacl import validate

def fix_turtle_syntax(content: str) -> str:
    """Fix common Turtle syntax issues.
    
    Args:
        content: The Turtle content to fix
        
    Returns:
        The fixed Turtle content
    """
    # Remove extra commas
    content = content.replace("  ,", ",")
    content = content.replace(",,", ",")
    
    # Fix missing dots at the end of statements
    lines = content.split("\n")
    fixed_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.endswith((".", ";")):
            line += " ."
        fixed_lines.append(line)
    
    return "\n".join(fixed_lines)

def validate_turtle(content: str) -> Tuple[bool, Optional[str]]:
    """Validate Turtle syntax."""
    try:
        g = Graph()
        g.parse(data=content, format='turtle')
        return True, None
    except Exception as e:
        return False, str(e)

def validate_shacl(data_graph: Graph, shapes_graph: Graph) -> Tuple[bool, Optional[str]]:
    """Validate a graph against SHACL shapes."""
    try:
        conforms, results_graph, results_text = validate(
            data_graph=data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs',
            abort_on_first=False
        )
        if not conforms:
            return False, results_text
        return True, None
    except Exception as e:
        return False, str(e)

def load_and_fix_turtle(content: str) -> Tuple[Graph, Optional[str]]:
    """Load and fix Turtle content.
    
    Args:
        content: The Turtle content to load and fix
        
    Returns:
        A tuple of (Graph, error_message)
        where error_message is None if successful
    """
    try:
        # Try loading as-is first
        g = Graph()
        g.parse(data=content, format="turtle")
        return g, None
    except Exception as e:
        # Try fixing and loading again
        try:
            fixed_content = fix_turtle_syntax(content)
            g = Graph()
            g.parse(data=fixed_content, format="turtle")
            return g, None
        except Exception as e2:
            return None, str(e2) 