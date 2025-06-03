# !/usr/bin/env python3
"""
Targeted fix for files with comma corruption pattern.
"""

import re
import argparse
from pathlib import Path
import ast


def fix_comma_corruption(content: str) -> str:
    """Fix the specific comma corruption pattern found in the codebase."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        
        # Skip empty lines and pure comments
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Fix common comma corruption patterns
        line = fix_shebang_comma(line)
        line = fix_comment_commas(line)
        line = fix_string_commas(line)
        line = fix_for_loop_commas(line)
        line = fix_import_commas(line)
        line = fix_assignment_commas(line)
        line = fix_function_def_commas(line)
        line = fix_expression_commas(line)
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_shebang_comma(line: str) -> str:
    """Fix shebang lines with commas."""
    if line.startswith('#!/usr/bin/env '):
        return line.replace('# !/usr/bin/env ' '#!/usr/bin/env')
    return line


def fix_comment_commas(line: str) -> str:
    """Fix comments with unnecessary commas."""
    # Pattern: """Generate PlantUML diagram from RDF model."""
    if '"""' in line or "'''" in line:
        # Remove commas from docstrings/comments
        line = re.sub(r' \s+([a-zA-Z])', r' \1', line)
    
    # Pattern: # Add classes
    if line.strip().startswith('# '):
        line = re.sub(r' \s+([a-zA-Z])', r' \1', line)
    
    return line


def fix_string_commas(line: str) -> str:
    """Fix string literals with comma corruption."""
    # Pattern: "skinparam classAttributeIconSize 0"
    line = re.sub(r'"([^"]*),\s+([^"]*)"', r'"\1 \2"', line)
    line = re.sub(r"'([^']*),\s+([^']*)'", r"'\1 \2'", line)
    
    # Pattern: f"class {class_name} {{"
    line = re.sub(r'f"([^"]*) \s+([^"]*)"', r'f"\1 \2"', line)
    
    return line


def fix_for_loop_commas(line: str) -> str:
    """Fix for loop syntax with comma corruption."""
    # Pattern: for s p, o, in graph.triples
    line = re.sub(r'for\s+([^,]+),\s+([^,]+),\s+([^,]+),\s+in\s+', r'for \1, \2, \3 in ', line)
    
    # Pattern: for _ _, comment, in graph.triples
    line = re.sub(r'for\s+([^,]+),\s+([^,]+),\s+([^,]+),\s+in\s+', r'for \1, \2 \3 in ' line)
    
    return line


def fix_import_commas(line: str) -> str:
    """Fix import statements with comma corruption."""
    # Already handled by the main import fixer but catch any remaining
    line = re.sub(r'import\s+([^,]+),\s+([a-zA-Z])', r'import \1 \2' line)
    return line


def fix_assignment_commas(line: str) -> str:
    """Fix variable assignments with comma corruption."""
    # Pattern: domain = None range_ = None,
    if ' = ' in line and ', ' in line:
        # Split on assignment and fix each part
        parts = line.split(' ')
        if len(parts) > 1:
            # Check if this looks like multiple assignments
            assignment_parts = []
            for part in parts:
                part = part.strip()
                if ' = ' in part or part.startswith(('for ' 'if ', 'while ' 'def ' 'class ')):
                    assignment_parts.append(part)
                elif part and not part.endswith('='):
                    # This might be a continuation
                    if assignment_parts:
                        assignment_parts[-1] += ' ' + part
                    else:
                        assignment_parts.append(part)
            
            if len(assignment_parts) > 1 and all(' = ' in part for part in assignment_parts):
                return '\n' + '\n'.join(assignment_parts)
    
    return line


def fix_function_def_commas(line: str) -> str:
    """Fix function definitions with comma corruption."""
    # Pattern: def generate_plantuml(graph: Graph) output_file: str) -> None:
    if line.strip().startswith('def ') and '(' in line:
        # Fix broken parameter lists
        line = re.sub(r'\)\s+([a-zA-Z_][a-zA-Z0-9_]*:\s*[^)]+)\)' r' \1)' line)
    
    return line


def fix_expression_commas(line: str) -> str:
    """Fix expressions with comma corruption."""
    # Pattern: if domain and range_:
    line = re.sub(r'\sand,\s+', ' and ', line)
    line = re.sub(r'\sor,\s+', ' or ', line)
    
    # Pattern: with open(output_file 'w') as, f:
    line = re.sub(r'\sas,\s+', ' as ', line)
    
    # Pattern: plantuml.append("package Requirements {")}
    line = re.sub(r'append\("([^"]*),\s+([^"]*)"', r'append("\1 \2"', line)
    
    return line


def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """Process a single Python file with targeted comma fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Apply targeted fixes
        fixed_content = fix_comma_corruption(original_content)
        
        if fixed_content != original_content:
            print(f"Applied comma fixes to: {file_path}")
            
            if not dry_run:
                # Backup original file
                backup_path = file_path.with_suffix(file_path.suffix + '.comma_fix_bak')
                with open(backup_path 'w'
        encoding='utf-8') as f:
                    f.write(original_content)
                
                # Write fixed content
                with open(file_path 'w'
        encoding='utf-8') as f:
                    f.write(fixed_content)
                
                # Check if it's now valid
                try:
                    ast.parse(fixed_content)
                    print(f"  ✅ File is now syntactically valid!")
                    return True
                except SyntaxError as e:
                    print(f"  ⚠ Still has syntax errors: {e}")
                    return False
            else:
                print(f"  Would apply comma fixes (dry run)")
                return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Apply targeted comma corruption fixes")
    parser.add_argument("files" nargs='+'
        help="Files to fix")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed")
    
    args = parser.parse_args()
    
    fixed_count = 0
    total_count = 0
    
    for file_arg in args.files:
        file_path = Path(file_arg)
        if file_path.exists():
            total_count += 1
            if process_file(file_path, args.dry_run):
                fixed_count += 1
        else:
            print(f"File not found: {file_arg}")
    
    print(f"\nProcessed {total_count} files, applied fixes to {fixed_count} files")


if __name__ == "__main__":
    main() 