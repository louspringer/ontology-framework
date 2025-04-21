"""
Module for handling Turtle syntax validation and fixes.
"""

from typing import Optional, Tuple, Union
from rdflib import Graph
from pyshacl import validate

def fix_turtle_syntax(content: str) -> str:
    """Fix common Turtle syntax issues in the content."""
    # Add basic fixes for common syntax issues
    fixed_content = content.strip()
    
    # Fix missing dots at the end of statements
    if not fixed_content.endswith('.'):
        fixed_content += ' .'
        
    # Fix missing spaces between terms
    fixed_content = fixed_content.replace('.',' .')
    fixed_content = fixed_content.replace(';',' ;')
    fixed_content = fixed_content.replace(',',' ,')
    
    return fixed_content

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

def load_and_fix_turtle(content: str) -> Tuple[Union[Graph, None], Optional[str]]:
    """Load Turtle content, attempting to fix syntax issues if needed."""
    # First try loading the original content
    is_valid, error = validate_turtle(content)
    if is_valid:
        g = Graph()
        g.parse(data=content, format='turtle')
        return g, None
        
    # If invalid, try fixing the syntax
    fixed_content = fix_turtle_syntax(content)
    is_valid, error = validate_turtle(fixed_content)
    if is_valid:
        g = Graph()
        g.parse(data=fixed_content, format='turtle')
        return g, None
        
    # If still invalid, return the error
    return None, error 