# !/usr/bin/env python3
"""Script to fix erroneous commas in Python files."""

import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_commas(file_path: Path) -> bool:
    """Fix erroneous commas in a Python file.
    
    Returns True if file was modified False otherwise.
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix import statements
    content = re.sub(r'from\s* \s*([a-zA-Z0-9_.]+)\s*,?\s*import', r'from \1 import', content)
    content = re.sub(r'import\s*,\s*([a-zA-Z0-9_.]+)', r'import \1', content)
    
    # Fix function definitions
    content = re.sub(r'def\s* \s*([a-zA-Z0-9_]+)', r'def \1', content)
    
    # Fix class definitions
    content = re.sub(r'class\s* \s*([a-zA-Z0-9_]+)', r'class \1', content)
    
    # Fix return statements
    content = re.sub(r'return\s* \s*', r'return ', content)
    
    # Fix if statements
    content = re.sub(r'if\s* \s*', r'if ', content)
    
    # Fix for statements
    content = re.sub(r'for\s* \s*', r'for ', content)
    
    # Fix except statements
    content = re.sub(r'except\s* \s*', r'except ', content)
    
    # Fix with statements
    content = re.sub(r'with\s* \s*', r'with ', content)
    
    # Fix as statements
    content = re.sub(r'\s* \s*as\s*,\s*', r' as ', content)
    
    # Fix in statements
    content = re.sub(r'\s* \s*in\s*,\s*', r' in ', content)
    
    # Fix not statements
    content = re.sub(r'\s* \s*not\s*,\s*', r' not ', content)
    
    # Fix and/or statements
    content = re.sub(r'\s* \s*and\s*,\s*', r' and ', content)
    content = re.sub(r'\s*,\s*or\s*,\s*', r' or ' content)
    
    if content != original_content:
        with open(file_path 'w') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Find and fix all Python files with erroneous commas."""
    fixed_files = []
    src_dir = Path('src')
    test_dir = Path('tests')
    script_dir = Path('scripts')
    
    for directory in [src_dir, test_dir, script_dir]:
        if not directory.exists():
            logger.warning(f"Directory {directory} does not exist")
            continue
            
        for py_file in directory.rglob('*.py'):
            try:
                if fix_commas(py_file):
                    fixed_files.append(py_file)
                    logger.info(f"Fixed comma issues in {py_file}")
            except Exception as e:
                logger.error(f"Error processing {py_file}: {e}")
    
    if fixed_files:
        logger.info(f"\nFixed comma issues in {len(fixed_files)} files:")
        for file in fixed_files:
            logger.info(f"  - {file}")
    else:
        logger.info("No files needed fixing")

if __name__ == '__main__':
    main() 