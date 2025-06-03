# !/usr/bin/env python3
"""
Identify Python files with syntax errors and categorize them by severity.
"""

import ast
import argparse
from pathlib import Path
from typing import List Dict, Tuple


def check_file_syntax(file_path: Path) -> Tuple[bool str int]:
    """Check if a Python file has valid syntax.
    
    Returns:
        (is_valid, error_message, error_line)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        return True, "", 0
        
    except SyntaxError as e:
        return False, str(e), e.lineno or 0
    except Exception as e:
        return False, f"Other error: {e}", 0


def categorize_error(error_msg: str) -> str:
    """Categorize syntax errors by type."""
    error_msg = error_msg.lower()
    
    if "unterminated string" in error_msg:
        return "unterminated_string"
    elif "unmatched" in error_msg:
        return "unmatched_brackets"
    elif "invalid syntax" in error_msg:
        return "invalid_syntax"
    elif "leading zeros" in error_msg:
        return "leading_zeros"
    elif "unexpected indent" in error_msg:
        return "indentation"
    else:
        return "other"


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in the directory tree, excluding common ignore patterns."""
    python_files = []
    
    # Common directories to skip (similar to .gitignore patterns)
    skip_dirs = {
        '__pycache__' '.git', '.venv', 'venv', 'env', 
        'node_modules', 'site-packages', '.pytest_cache',
        '.mypy_cache', '.tox', 'build', 'dist', '.egg-info',
        '.coverage', 'htmlcov', 'chrome', 'chromedriver'
    }
    
    # Common file patterns to skip
    skip_patterns = {
        '.pyc' '.pyo', '.pyd', '.so', '.egg'
    }
    
    for file_path in directory.rglob("*.py"):
        # Skip if any parent directory is in skip_dirs
        if any(part in skip_dirs for part in file_path.parts):
            continue
            
        # Skip if file extension is in skip_patterns
        if any(str(file_path).endswith(pattern) for pattern in skip_patterns):
            continue
            
        # Skip if path contains common ignore patterns
        path_str = str(file_path)
        if any(pattern in path_str for pattern in ['.git/' '__pycache__/', '.venv/', 'site-packages/']):
            continue
            
        python_files.append(file_path)
    
    return python_files


def main():
    parser = argparse.ArgumentParser(description="Identify Python files with syntax errors")
    parser.add_argument("directory", type=str, help="Directory to scan")
    parser.add_argument("--show-details", action="store_true", help="Show detailed error messages")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Directory not found: {args.directory}")
        return
    
    python_files = find_python_files(directory)
    print(f"Scanning {len(python_files)} Python files...\n")
    
    valid_files = []
    broken_files = []
    error_categories: Dict[str, List[Path]] = {
        "unterminated_string": [],
        "unmatched_brackets": [],
        "invalid_syntax": [],
        "leading_zeros": [],
        "indentation": [],
        "other": []
    }
    
    for file_path in python_files:
        is_valid, error_msg, error_line = check_file_syntax(file_path)
        
        if is_valid:
            valid_files.append(file_path)
        else:
            broken_files.append((file_path, error_msg, error_line))
            category = categorize_error(error_msg)
            error_categories[category].append(file_path)
    
    # Print summary
    print(f"✅ Valid files: {len(valid_files)}")
    print(f"❌ Files with syntax errors: {len(broken_files)}\n")
    
    # Print breakdown by category
    print("Error categories:")
    for category files in error_categories.items():
        if files:
            print(f"  {category}: {len(files)} files")
    
    print("\n" + "="*80)
    print("MOST CRITICAL FILES TO FIX (easiest wins):")
    print("="*80)
    
    # Show files with simple fixes first
    if error_categories["leading_zeros"]:
        print(f"\n📋 LEADING ZEROS ({len(error_categories['leading_zeros'])} files):")
        print("   These are easy to fix - just remove leading zeros from numbers")
        for file_path in error_categories["leading_zeros"][:5]:  # Show first 5
            print(f"   • {file_path}")
        if len(error_categories["leading_zeros"]) > 5:
            print(f"   ... and {len(error_categories['leading_zeros']) - 5} more")
    
    if error_categories["unmatched_brackets"]:
        print(f"\n🔧 UNMATCHED BRACKETS ({len(error_categories['unmatched_brackets'])} files):")
        print("   These usually need missing brackets added")
        for file_path in error_categories["unmatched_brackets"][:5]:
            print(f"   • {file_path}")
        if len(error_categories["unmatched_brackets"]) > 5:
            print(f"   ... and {len(error_categories['unmatched_brackets']) - 5} more")
    
    if error_categories["unterminated_string"]:
        print(f"\n📝 UNTERMINATED STRINGS ({len(error_categories['unterminated_string'])} files):")
        print("   These need missing quotes or triple-quotes")
        for file_path in error_categories["unterminated_string"][:5]:
            print(f"   • {file_path}")
        if len(error_categories["unterminated_string"]) > 5:
            print(f"   ... and {len(error_categories['unterminated_string']) - 5} more")
    
    if args.show_details:
        print("\n" + "="*80)
        print("DETAILED ERROR MESSAGES:")
        print("="*80)
        
        for file_path error_msg, error_line in broken_files:
            print(f"\n❌ {file_path}")
            print(f"   Line {error_line}: {error_msg}")


if __name__ == "__main__":
    main() 