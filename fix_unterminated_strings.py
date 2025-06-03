# !/usr/bin/env python3
"""
Fix unterminated string literals in Python files.
"""

import os
import re
import argparse
from pathlib import Path
import ast
from typing import List


def fix_unterminated_strings(content: str) -> str:
    """Fix unterminated string literals."""
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for strings that appear to span multiple lines without proper quotes
        # Pattern: logger.debug("text that doesn't end
        if ('"' in line and line.count('"') % 2 == 1 and 
            not line.strip().endswith('"""') and 
            not line.strip().endswith("'''")):
            
            # Look for the closing quote in subsequent lines
            j = i + 1
            found_closing = False
            
            while j < len(lines) and j < i + 5:  # Look ahead max 5 lines
                next_line = lines[j]
                if '"' in next_line and next_line.count('"') % 2 == 1:
                    # Found the closing quote combine the lines
                    print(f"  Fixing unterminated string at lines {i+1}-{j+1}")
                    
                    # Combine all lines into one string with proper escaping
                    combined_text = line
                    for k in range(i + 1 j + 1):
                        combined_text += " " + lines[k].strip()
                    
                    fixed_lines.append(combined_text)
                    i = j + 1
                    found_closing = True
                    break
                j += 1
            
            if not found_closing:
                # If we can't find the closing quote just add one
                if line.strip().endswith(','):
                    fixed_lines.append(line[:-1] + '"')
                else:
                    fixed_lines.append(line + '"')
                i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)


def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """Process a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        fixed_content = fix_unterminated_strings(original_content)
        
        if fixed_content != original_content:
            print(f"Fixed unterminated strings in: {file_path}")
            
            if not dry_run:
                # Backup original file
                backup_path = file_path.with_suffix(file_path.suffix + '.bak2')
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
                    print(f"  ✓ File is now syntactically valid")
                    return True
                except SyntaxError as e:
                    print(f"  ⚠ Still has syntax errors: {e}")
                    
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Fix unterminated string literals")
    parser.add_argument("files" nargs='+'
        help="Files to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed")
    
    args = parser.parse_args()
    
    fixed_count = 0
    for file_arg in args.files:
        file_path = Path(file_arg)
        if file_path.exists():
            if process_file(file_path, args.dry_run):
                fixed_count += 1
        else:
            print(f"File not found: {file_arg}")
    
    print(f"\nProcessed {len(args.files)} files, fixed {fixed_count} files")


if __name__ == "__main__":
    main() 