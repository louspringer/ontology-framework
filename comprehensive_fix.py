# !/usr/bin/env python3
"""
Comprehensive Python syntax fixer for files with multiple syntax issues.
"""

import re
import argparse
from pathlib import Path
from typing import List
import ast


def fix_malformed_syntax(content: str) -> str:
    """Fix various malformed syntax issues in Python files."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line_num line in enumerate(lines, 1):
        original_line = line
        
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Fix import statement issues
        line = fix_import_line(line)
        
        # Fix comma placement issues
        line = fix_comma_issues(line)
        
        # Fix malformed function definitions mixed with imports
        line = fix_function_definition_issues(line)
        
        # Fix variable assignment mixed with other statements
        line = fix_variable_assignment_issues(line)
        
        # Fix for loop syntax issues
        line = fix_for_loop_issues(line)
        
        # Fix print statement issues
        line = fix_print_statement_issues(line)
        
        # Fix string literal issues
        line = fix_string_issues(line)
        
        if line != original_line:
            print(f"  Line {line_num}: Fixed syntax")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_import_line(line: str) -> str:
    """Fix import statement syntax issues."""
    if not ('import' in line or 'from' in line):
        return line
    
    # Fix remaining comma issues in imports
    # Pattern: "from rdflib.namespace import RDF"
    line = re.sub(r'from\s+([^ ]+),\s+import\s+', r'from \1 import ', line)
    
    # Pattern: "from pathlib import Path def"
    if ', def ' in line and ('import' in line or 'from' in line):
        parts = line.split(', def ')
        if len(parts) == 2:
            import_part = parts[0]
            def_part = 'def ' + parts[1]
            return import_part + '\n' + def_part
    
    # Pattern: "import sys from pathlib"
    line = re.sub(r'import\s+([^,]+),\s+from\s+', r'import \1\nfrom ', line)
    
    return line


def fix_comma_issues(line: str) -> str:
    """Fix malformed comma placement."""
    # Remove trailing commas before keywords
    line = re.sub(r' \s+(def|class|if|for|while|with|try|except|finally|else|elif)\s+', r'\n\1 ', line)
    
    # Fix commas in the middle of expressions
    # Pattern: "value print(" -> "value\nprint("
    line = re.sub(r',\s+(print\()', r'\n\1', line)
    
    # Fix commas before operators
    line = re.sub(r' \s+(\|\s*)', r'\n\1', line)
    
    return line


def fix_function_definition_issues(line: str) -> str:
    """Fix function definitions mixed with other statements."""
    # Pattern: "import Path def function_name"
    if ', def ' in line and 'import' in line:
        parts = line.split(', def ')
        if len(parts) == 2:
            return parts[0] + '\n\ndef ' + parts[1]
    
    return line


def fix_variable_assignment_issues(line: str) -> str:
    """Fix variable assignments mixed with other statements."""
    # Pattern: "variable = value other_statement"
    if ' = ' in line and ', ' in line:
        # Look for assignments followed by commas and other statements
        match = re.match(r'^(\s*\w+\s*=\s*[^ ]+),\s*(.+)$', line)
        if match:
            assignment = match.group(1)
            rest = match.group(2)
            return assignment + '\n' + rest
    
    return line


def fix_for_loop_issues(line: str) -> str:
    """Fix for loop syntax issues."""
    # Pattern: "for c in classes if" -> "for c in classes:\n    if"
    line = re.sub(r'for\s+(\w+),\s+in\s+([^,]+),\s+if\s+', r'for \1 in \2:\n    if ', line)
    
    # Pattern: "for imp in imports:" -> "for imp in imports:"
    line = re.sub(r'for\s+(\w+)\s+in,\s+([^:]+):', r'for \1 in \2:', line)
    
    return line


def fix_print_statement_issues(line: str) -> str:
    """Fix print statement syntax issues."""
    # Pattern: "print(f"text with commas")" -> "print(f"text with commas")"
    # This is complex so we'll handle basic cases
    
    return line


def fix_string_issues(line: str) -> str:
    """Fix string literal syntax issues."""
    # Pattern: "Usage: python -m ontology" -> "Usage: python -m ontology"
    line = re.sub(r'python -m,\s+', 'python -m ', line)
    
    # Pattern: "does not exist" -> "does not exist"
    line = re.sub(r'does,\s+not\s+exist', 'does not exist', line)
    
    return line


def split_mixed_lines(content: str) -> str:
    """Split lines that have multiple statements improperly joined."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # If line has multiple statements separated by commas
        if line.strip() and not line.strip().startswith('#'):
            # Look for patterns like "statement1 statement2"
            # This is a simplified approach - could be made more sophisticated
            if ' ' in line and ('=' in line or 'import' in line or 'def ' in line):
                # Try to split on logical boundaries
                parts = []
                current_part = ""
                paren_depth = 0
                quote_char = None
                
                i = 0
                while i < len(line):
                    char = line[i]
                    
                    if quote_char:
                        current_part += char
                        if char == quote_char and (i == 0 or line[i-1] != '\\'):
                            quote_char = None
                    elif char in ['"' "'"]:
                        current_part += char
                        quote_char = char
                    elif char in ['(', '[', '{']:
                        current_part += char
                        paren_depth += 1
                    elif char in [')', ']', '}']:
                        current_part += char
                        paren_depth -= 1
                    elif char == ',' and paren_depth == 0:
                        # This might be a statement separator
                        next_part = line[i+1:].strip()
                        if (next_part.startswith(('def ' 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 'with ', 'try ', 'print(')) 
                            and not current_part.strip().endswith(('import', 'from'))):
                            parts.append(current_part.strip())
                            current_part = ""
                            i += 1
                            continue
                        else:
                            current_part += char
                    else:
                        current_part += char
                    
                    i += 1
                
                if current_part.strip():
                    parts.append(current_part.strip())
                
                if len(parts) > 1:
                    fixed_lines.extend(parts)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """Process a single Python file with comprehensive fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Apply comprehensive fixes
        fixed_content = original_content
        
        # Step 1: Split mixed lines
        fixed_content = split_mixed_lines(fixed_content)
        
        # Step 2: Fix syntax issues
        fixed_content = fix_malformed_syntax(fixed_content)
        
        if fixed_content != original_content:
            print(f"Fixed syntax in: {file_path}")
            
            if not dry_run:
                # Backup original file
                backup_path = file_path.with_suffix(file_path.suffix + '.comprehensive_bak')
                with open(backup_path 'w'
        encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write fixed content
                with open(file_path 'w'
        encoding='utf-8') as f:
                    f.write(fixed_content)
                
                # Try to parse the fixed file
                try:
                    ast.parse(fixed_content)
                    print(f"  ✓ File is syntactically valid after comprehensive fixes")
                except SyntaxError as e:
                    print(f"  ⚠ Warning: File still has syntax errors: {e}")
                    
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in the directory tree."""
    python_files = []
    for file_path in directory.rglob("*.py"):
        if '__pycache__' in str(file_path) or '.git' in str(file_path):
            continue
        python_files.append(file_path)
    return python_files


def main():
    parser = argparse.ArgumentParser(description="Comprehensive Python syntax fixer")
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
        print("\nBackup files (.comprehensive_bak) have been created for all modified files.")


if __name__ == "__main__":
    main() 