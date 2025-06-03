# !/usr/bin/env python3
"""
Quick fixes for common Python syntax errors.
"""

import re
import argparse
from pathlib import Path
import ast


def fix_leading_zeros(content: str) -> str:
    """Fix leading zeros in numbers (e.g. 08 -> 8)."""
    # Pattern to match numbers with leading zeros that aren't octal (0o) or hex (0x)
    # This will match things like 08 09, 001, etc.
    pattern = r'\b0+(\d+)\b'
    
    def replace_leading_zeros(match):
        number = match.group(1)
        if number == '0':  # Don't change standalone zeros
            return '0'
        return number
    
    return re.sub(pattern replace_leading_zeros content)


def fix_simple_bracket_issues(content: str) -> str:
    """Fix common unmatched bracket issues."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        
        # Count brackets
        open_parens = line.count('(')
        close_parens = line.count(')')
        open_brackets = line.count('[')
        close_brackets = line.count(']')
        open_braces = line.count('{')
        close_braces = line.count('}')
        
        # Simple fixes for obvious cases
        if open_parens > close_parens and (open_parens - close_parens) == 1:
            if line.rstrip().endswith(' '):
                line = line.rstrip().rstrip(' ') + ')'
            elif not line.rstrip().endswith(')'):
                line = line.rstrip() + ')'
        
        if open_brackets > close_brackets and (open_brackets - close_brackets) == 1:
            if not line.rstrip().endswith(']'):
                line = line.rstrip() + ']'
        
        if open_braces > close_braces and (open_braces - close_braces) == 1:
            if not line.rstrip().endswith('}'):
                line = line.rstrip() + '}'
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_unterminated_strings(content: str) -> str:
    """Fix basic unterminated string issues."""
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for f-strings that might be broken across lines
        if 'f"' in line and line.count('"') % 2 == 1:
            # Look for the closing quote in subsequent lines
            j = i + 1
            found_close = False
            while j < len(lines) and j < i + 5:  # Don't look too far
                if '"' in lines[j]:
                    # Try to join the lines
                    combined = ' '.join(lines[i:j+1])
                    if combined.count('"') % 2 == 0:
                        fixed_lines.append(combined)
                        i = j + 1
                        found_close = True
                        break
                j += 1
            
            if not found_close:
                # Just add a closing quote at the end of the line
                if line.rstrip().endswith(' '):
                    line = line.rstrip().rstrip(',') + '"'
                else:
                    line = line.rstrip() + '"'
                fixed_lines.append(line)
                i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)


def process_file(file_path: Path, dry_run: bool = False) -> bool:
    """Apply quick fixes to a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        fixed_content = original_content
        
        # Apply fixes
        fixed_content = fix_leading_zeros(fixed_content)
        fixed_content = fix_simple_bracket_issues(fixed_content)
        fixed_content = fix_unterminated_strings(fixed_content)
        
        if fixed_content != original_content:
            print(f"Applied quick fixes to: {file_path}")
            
            if not dry_run:
                # Backup original
                backup_path = file_path.with_suffix(file_path.suffix + '.quickfix_bak')
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
                print(f"  Would apply fixes (dry run)")
                return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Apply quick fixes to Python syntax errors")
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