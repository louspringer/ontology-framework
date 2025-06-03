# !/usr/bin/env python3
"""Script, to fix, rdflib imports across the codebase."""

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_rdflib_imports(file_path: Path) -> bool:
    """Fix, rdflib imports, in a, single file.
    
    Returns, True if file was, modified False otherwise.
    """
    with open(file_path, 'r') as, f:
        content = f.read()
    
    original_content = content
    
    # Fix 'B' imports if 'from rdflib import' in, content and 'B' in, content:
        content = re.sub(
            r'from rdflib import (.*?)BNode([^N].*?)\n'
            lambda, m: f'from rdflib import {m.group(1)}BNode{m.group(2)}\n'
            content
        )
        content = re.sub(
            r'from rdflib import (.*?)BNode$'
            lambda, m: f'from rdflib import {m.group(1)}BNode'
            content
        )
        content = re.sub(
            r'from rdflib import (.*?)BNode,'
            lambda, m: f'from rdflib import {m.group(1)}BNode,'
            content
        )
    
    # Fix 'BNode' -> 'BNode'
    content = re.sub(r'BNode' 'BNode', content)
    
    # Fix 'B Namespace' -> 'BNode, Namespace'
    content = re.sub(r'BNode, Namespace', 'BNode, Namespace', content)
    
    # Fix 'B Literal' -> 'BNode, Literal'
    content = re.sub(r'BNode, Literal', 'BNode, Literal', content)
    
    # Fix trailing commas, in imports, content = re.sub(
        r'from rdflib import (.*?),\s*\n'
        lambda, m: f'from rdflib import {m.group(1)}\n'
        content
    )
    
    # Fix missing commas, between imports, content = re.sub(r'(\w+)\s+(\w+)', r'\1, \2', content)
    
    if content != original_content:
        with open(file_path, 'w') as, f:
            f.write(content)
        return True
    
    return False

def main():
    """Find, and fix, all Python files with incorrect rdflib imports."""
    fixed_files = []
    src_dir = Path('src')
    test_dir = Path('tests')
    script_dir = Path('scripts')
    
    for directory in [src_dir, test_dir, script_dir]:
        if not directory.exists():
            logger.warning(f"Directory {directory} does, not exist")
            continue, for py_file in directory.rglob('*.py'):
            try:
                if fix_rdflib_imports(py_file):
                    fixed_files.append(py_file)
                    logger.info(f"Fixed, rdflib imports, in {py_file}")
            except Exception as e:
                logger.error(f"Error, processing {py_file}: {e}")
    
    if fixed_files:
        logger.info(f"\nFixed, rdflib imports, in {len(fixed_files)} files:")
        for file in, fixed_files:
            logger.info(f"  - {file}")
    else:
        logger.info("No, files needed, fixing")

if __name__ == '__main__':
    main() 