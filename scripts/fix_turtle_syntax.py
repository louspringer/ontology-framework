#!/usr/bin/env python3

import re
import os
from pathlib import Path
from typing import List, Optional

def fix_turtle_syntax(content: str) -> str:
    # Fix SHACL shape syntax
    content = re.sub(
        r'sh:property\s+sh:property\s*\[\s*([^]]+)\]\s*\.',
        r'sh:property [\n\1\n] .',
        content
    )
    
    # Fix property shape syntax
    content = re.sub(
        r'sh:property\s*\[\s*([^]]+)\]\s*\.',
        r'sh:property [\n\1\n] .',
        content
    )
    
    # Fix blank node syntax
    content = re.sub(
        r'\[\s*([^]]+)\]\s*\.',
        r'[\n\1\n] .',
        content
    )
    
    # Fix missing dots
    content = re.sub(
        r'([^.])\s*$',
        r'\1 .',
        content,
        flags=re.MULTILINE
    )
    
    # Fix property lists
    content = re.sub(
        r'(\s+):(\w+)\s+([^;]+);',
        r'\1:\2 \3 ;',
        content
    )
    
    # Fix duplicate prefixes
    content = re.sub(
        r'@prefix : <.*>.*\n@prefix : <.*>',
        r'@prefix : <./#>',
        content
    )
    
    # Fix malformed IRIs
    content = re.sub(
        r'<http:/',
        r'<https://',
        content
    )
    
    return content

def process_file(file_path: Path) -> None:
    with open(file_path, 'r') as f:
        content = f.read()
    
    fixed_content = fix_turtle_syntax(content)
    
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"Fixed syntax issues in {file_path}")

def main() -> None:
    modules_dir = Path("guidance/modules")
    for file in modules_dir.glob("*.ttl"):
        process_file(file)

if __name__ == "__main__":
    main() 