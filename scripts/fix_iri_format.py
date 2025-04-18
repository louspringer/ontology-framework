#!/usr/bin/env python3

import re
import os
from pathlib import Path
from typing import Match

def fix_iri_format(content: str) -> str:
    """Fix IRI format by replacing single forward slashes with double forward slashes in protocol parts
    and converting absolute IRIs to relative ones where appropriate."""
    # Remove any existing base declarations and duplicate prefix declarations
    content = re.sub(r'@base.*?\.\n+', '', content)
    content = re.sub(r'(@prefix\s+:\s+<[^>]+>\s+\.\n+)(?=@prefix\s+:\s+<)', '', content)
    
    # Fix protocol slashes
    content = re.sub(r'(https?:/)(?!/)', r'\1/', content)
    
    # Convert absolute IRIs to relative ones for example instances
    content = re.sub(
        r'<http://ontologies\.louspringer\.com/guidance/modules/[^#>]+#([^>]+)>',
        r':\1',
        content
    )
    
    # Convert absolute IRIs to relative ones for imports
    content = re.sub(
        r'<https://raw\.githubusercontent\.com/louspringer/ontology-framework/main/guidance/modules/([^>]+)>',
        r'<./\1>',
        content
    )
    
    # Convert prefix declarations to use GitHub URLs
    content = re.sub(
        r'@prefix ([^:]+): <http://ontologies\.louspringer\.com/guidance/([^>]+)>',
        r'@prefix \1: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/\2>',
        content
    )
    
    # Replace blank nodes in SHACL shapes with explicit identifiers
    blank_node_count = 0
    def replace_blank_node(match: Match[str]) -> str:
        nonlocal blank_node_count
        blank_node_count += 1
        return f":shape{blank_node_count}"
    
    # First, handle top-level blank nodes
    content = re.sub(r'\[\s*(?=a\s+sh:NodeShape)', lambda m: replace_blank_node(m), content)
    
    # Then, handle nested blank nodes in sh:property
    def replace_property_blank_node(match: Match[str]) -> str:
        nonlocal blank_node_count
        blank_node_count += 1
        return f":shape{blank_node_count}"
    
    # Replace property blank nodes and fix their syntax
    content = re.sub(r'sh:property\s+\[\s*', lambda m: f"sh:property {replace_property_blank_node(m)} .\n        {replace_property_blank_node(m)} ", content)
    content = re.sub(r'\s*\](?=\s*[,;])', '', content)
    content = re.sub(r',\s*(?=:shape\d+\s+sh:)', ' .\n        ', content)
    
    # Fix any remaining blank node syntax
    content = re.sub(r'\[\s*sh:', r':shape1 sh:', content)
    content = re.sub(r'\s*\](?=\s*[,;])', '', content)
    
    # Fix property list syntax
    content = re.sub(r';\s*(?=:shape\d+\s+sh:)', ' .\n        ', content)
    content = re.sub(r'\.\s*(?=:shape\d+\s+sh:)', ' .\n        ', content)
    
    return content

def add_base_uri(content: str, file_path: Path) -> str:
    """Add base URI declaration to the content."""
    module_name = file_path.stem
    base_uri = f"@base <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/{module_name}#> .\n\n"
    # Add prefix for the current module
    prefix = f"@prefix : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/{module_name}#> .\n"
    return base_uri + prefix + content

def process_file(file_path: Path) -> None:
    """Process a single file to fix IRI formats and add base URI."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    fixed_content = fix_iri_format(content)
    fixed_content = add_base_uri(fixed_content, file_path)
    
    if content != fixed_content:
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        print(f"Fixed IRI formats and added base URI in {file_path}")

def main() -> None:
    """Process all .ttl files in the guidance/modules directory."""
    modules_dir = Path("guidance/modules")
    for file_path in modules_dir.glob("*.ttl"):
        process_file(file_path)

if __name__ == "__main__":
    main() 