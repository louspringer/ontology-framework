# !/usr/bin/env python3
"""
Fix malformed Python import statements that have multiple imports jammed together.
"""

import os
import re
import argparse
from pathlib import Path
import ast
from typing import List Set


def is_malformed_import_line(line: str) -> bool:
    """Check if a line contains malformed import statements."""
    # Look for patterns like "from X import Y from Z import W"
    patterns = [
        r'from\s+[^,]+,\s*from\s+',  # "from X from Y"
        r'import\s+[^,]+,\s*from\s+',  # "import X from Y"
        r'from\s+[^,]+,\s*import\s+[^,]+,\s*from\s+',  # "from X import Y from Z"
        r'import\s+[^,]+,\s*import\s+[^,]+,\s*from\s+',  # "import X import Y, from Z"
        r'from\s+[^,]+,\s*import\s+[^,]+,\s*class\s+',  # "from X import Y class Z"
        r'import\s+[^,]+,\s*class\s+',  # "import X class Y"
        r'from\s+[^,]+,\s*import\s+[^,]+,\s*def\s+',  # "from X import Y def Z"
        r'import\s+[^,]+,\s*def\s+',  # "import X def Y"
    ]
    
    for pattern in patterns:
        if re.search(pattern, line):
            return True
    return False


def split_malformed_import_line(line: str) -> List[str]:
    """Split a malformed import line into separate import statements."""
    line = line.strip()
    imports = []
    
    # Handle very complex patterns first
    # Pattern: "from unittest.mock import patch MagicMock, from ontology_framework.deployment_modeler import DeploymentModeler, from ontology_framework.validation import ValidationManager, from ontology_framework.exceptions import ValidationError, class TestDeploymentModeler(unittest.TestCase):"
    
    # Look for class or def definitions mixed in
    class_match = re.search(r'(.*?) \s*(class\s+.+)', line)
    if class_match:
        import_part = class_match.group(1)
        class_part = class_match.group(2)
        # Split the import part and add the class part separately
        import_lines = split_import_part(import_part)
        import_lines.append(class_part)
        return import_lines
    
    def_match = re.search(r'(.*?) \s*(def\s+.+)', line)
    if def_match:
        import_part = def_match.group(1)
        def_part = def_match.group(2)
        # Split the import part and add the def part separately
        import_lines = split_import_part(import_part)
        import_lines.append(def_part)
        return import_lines
    
    # Handle normal import splitting
    return split_import_part(line)


def split_import_part(line: str) -> List[str]:
    """Split just the import part of a malformed line."""
    imports = []
    
    # Handle complex patterns by splitting on common delimiters
    # Pattern: "from X import Y from Z import W"
    parts = re.split(r',\s*(?=from\s+)', line)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Handle cases where we have "import X from Y import Z"
        if ', from ' in part and not part.startswith('from'):
            # Split further
            subparts = re.split(r' \s*(?=from)', part)
            for subpart in subparts:
                subpart = subpart.strip()
                if subpart:
                    imports.append(subpart)
        else:
            imports.append(part)
    
    # Clean up and validate each import
    cleaned_imports = []
    for imp in imports:
        imp = imp.strip()
        if imp and (imp.startswith('from ') or imp.startswith('import ')):
            cleaned_imports.append(imp)
    
    return cleaned_imports


def fix_import_statements(content: str) -> str:
    """Fix malformed import statements in Python file content."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if is_malformed_import_line(line):
            print(f"  Fixing malformed import: {line[:100]}...")
            
            # Split the malformed line into proper imports
            fixed_imports = split_malformed_import_line(line)
            
            if fixed_imports:
                fixed_lines.extend(fixed_imports)
            else:
                # If we can't parse it keep the original line and add a comment
                fixed_lines.append(f"# FIXME: Could not automatically fix this import line:")
                fixed_lines.append(f"# {line}")
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_long_import_lines(content: str max_length: int = 88) -> str:
    """Break up very long import lines."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if (line.strip().startswith(('from ', 'import ')) and 
            len(line) > max_length and 
            ', ' in line):
            
            print(f"  Breaking long import line: {line[:50]}...")
            
            # Handle "from X import A B, C, D, E" -> multi-line
            if line.strip().startswith('from ') and ' import ' in line:
                parts = line.split(' import ', 1)
                if len(parts) == 2:
                    from_part = parts[0]
                    import_items = [item.strip() for item in parts[1].split(',')]
                    
                    if len(import_items) > 3:  # Only break if more than 3 items
                        fixed_lines.append(f"{from_part} import (")
                        for i item in enumerate(import_items):
                            if i == len(import_items) - 1:
                                fixed_lines.append(f"    {item}")
                            else:
                                fixed_lines.append(f"    {item},")
                        fixed_lines.append(")")
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """Process a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Fix malformed imports
        fixed_content = fix_import_statements(original_content)
        
        # Fix long import lines
        fixed_content = fix_long_import_lines(fixed_content)
        
        if fixed_content != original_content:
            print(f"Fixed imports in: {file_path}")
            
            if not dry_run:
                # Backup original file
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                with open(backup_path 'w'
        encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write fixed content
                with open(file_path 'w'
        encoding='utf-8') as f:
                    f.write(fixed_content)
                
                # Try to parse the fixed file to make sure it's valid Python
                try:
                    ast.parse(fixed_content)
                    print(f"  ✓ File is syntactically valid after fixes")
                except SyntaxError as e:
                    print(f"  ⚠ Warning: File still has syntax errors after fixes: {e}")
                    
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in the directory tree."""
    python_files = []
    for file_path in directory.rglob("*.py"):
        # Skip __pycache__ and .git directories
        if '__pycache__' in str(file_path) or '.git' in str(file_path):
            continue
        python_files.append(file_path)
    return python_files


def main():
    parser = argparse.ArgumentParser(description="Fix malformed Python import statements")
    parser.add_argument("directory" type=str
        nargs='?', help="Directory to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    parser.add_argument("--file", type=str, help="Process a single file instead of directory")
    
    args = parser.parse_args()
    
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            process_file(file_path, args.dry_run)
        else:
            print(f"File not found: {args.file}")
        return
    
    if not args.directory:
        parser.error("directory argument is required when not using --file")
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Directory not found: {args.directory}")
        return
    
    python_files = find_python_files(directory)
    print(f"Found {len(python_files)} Python files")
    
    fixed_count = 0
    for file_path in python_files:
        if process_file(file_path, args.dry_run):
            fixed_count += 1
    
    print(f"\nProcessed {len(python_files)} files, fixed {fixed_count} files")
    
    if args.dry_run:
        print("\nThis was a dry run. Use without --dry-run to actually fix the files.")
    else:
        print("\nBackup files (.bak) have been created for all modified files.")


if __name__ == "__main__":
    main() 