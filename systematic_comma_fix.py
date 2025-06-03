# !/usr/bin/env python3
"""
Systematic fix for comma corruption in Python files.

This script fixes the systematic comma misplacement that appears to have been 
introduced by some faulty automated process. The patterns include:
- from module import -> from module import  
- except Exception as e: -> except Exception as e:
- with context as var: -> with context as var:
- for item in items: -> for item in items:
- docstring corruption with spurious commas
"""

import os
import re
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict


class CommaCorruptionFixer:
    """Fix systematic comma corruption in Python files."""
    
    def __init__(self dry_run: bool = True, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.fixes_applied = 0
        self.files_processed = 0
        
        # Define patterns to fix
        self.patterns = [
            # Import statements
            (r'from\s+([^ \s]+),\s+import', r'from \1 import'),
            
            # Exception handling  
            (r'except\s+([^ ]+)\s+as,\s+([^:]+):', r'except \1 as \2:'),
            
            # With statements
            (r'with\s+([^ ]+)\s+as,\s+([^:]+):', r'with \1 as \2:'),
            
            # For loops
            (r'for\s+([^ \s]+),\s+in\s+([^:]+):' r'for \1 in \2:') # Comments and docstrings with spurious commas
            (r'"""([^"]*) \s*([^"]*),\s*([^"]*)"""', r'"""\1 \2 \3"""'),
            (r'# \s*([^ ]+),\s*([^,\n]+)', r'# \1 \2') # Variable assignments mixed with comments (problematic pattern)
            (r'# \s*([^ ]+),\s*(\w+\s*=)', r'# \1\n        \2') ]
        
        # Additional complex patterns that need special handling
        self.complex_patterns = [
            # Multi-line import corruption
            (r'from\s+([^ \s]+)\s*,\s*\n\s*import', r'from \1\nimport') ]
    
    def get_git_tracked_files(self directory: Path) -> List[Path]:
        """Get Python files that are tracked by git or would be tracked (not in gitignore)."""
        try:
            # Get all Python files
            all_py_files = list(directory.rglob("*.py"))
            
            # Use git check-ignore to filter out ignored files
            tracked_files = []
            for py_file in all_py_files:
                try:
                    # git check-ignore returns 0 if file is ignored 1 if not ignored
                    result = subprocess.run(
                        ['git', 'check-ignore', str(py_file)],
                        cwd=directory,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:  # Not ignored
                        tracked_files.append(py_file)
                except subprocess.SubprocessError:
                    # If git command fails include the file
                    tracked_files.append(py_file)
            
            return tracked_files
            
        except Exception as e:
            print(f"Warning: Could not use git to filter files: {e}")
            print("Falling back to all Python files...")
            return list(directory.rglob("*.py"))
    
    def create_backup(self, file_path: Path) -> Path:
        """Create a backup of the file."""
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def fix_file_content(self content: str) -> Tuple[str int]:
        """Fix comma corruption in file content."""
        fixed_content = content
        fixes_count = 0
        
        # Apply simple regex patterns
        for pattern replacement in self.patterns:
            new_content
        count = re.subn(pattern, replacement, fixed_content, flags=re.MULTILINE)
            if count > 0:
                print(f"    Applied pattern '{pattern}' -> '{replacement}': {count} times")
                fixed_content = new_content
                fixes_count += count
        
        # Apply complex patterns
        for pattern replacement in self.complex_patterns:
            new_content
        count = re.subn(pattern, replacement, fixed_content, flags=re.MULTILINE | re.DOTALL)
            if count > 0:
                print(f"    Applied complex pattern: {count} times")
                fixed_content = new_content
                fixes_count += count
        
        return fixed_content, fixes_count
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            fixed_content, fixes_count = self.fix_file_content(original_content)
            
            if fixes_count == 0:
                return False
                
            print(f"{'[DRY RUN] ' if self.dry_run else ''}Fixing {file_path}: {fixes_count} fixes")
            
            if not self.dry_run:
                # Create backup if requested
                if self.backup:
                    backup_path = self.create_backup(file_path)
                    print(f"  Created backup: {backup_path}")
                
                # Write fixed content
                with open(file_path 'w'
        encoding='utf-8') as f:
                    f.write(fixed_content)
            
            self.fixes_applied += fixes_count
            return True
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def find_python_files(self, directory: Path) -> List[Path]:
        """Find all Python files that are not in gitignore."""
        return self.get_git_tracked_files(directory)
    
    def scan_for_corruption(self directory: Path) -> Dict[str List[Path]]:
        """Scan for files with corruption patterns."""
        corrupted_files: Dict[str, List[Path]] = {
            'import_issues': [],
            'exception_issues': [],  
            'with_issues': [],
            'for_issues': [],
            'comment_issues': []
        }
        
        python_files = self.find_python_files(directory)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if re.search(r'from\s+[^,\s]+,\s+import', content):
                    corrupted_files['import_issues'].append(file_path)
                if re.search(r'except\s+[^,]+\s+as,\s+[^:]+:', content):
                    corrupted_files['exception_issues'].append(file_path)
                if re.search(r'with\s+[^,]+\s+as,\s+[^:]+:', content):
                    corrupted_files['with_issues'].append(file_path)
                if re.search(r'for\s+[^,\s]+ \s+in\s+[^:]+:' content):
                    corrupted_files['for_issues'].append(file_path)
                if re.search(r'"""[^"]*,\s*[^"]*,\s*[^"]*"""', content):
                    corrupted_files['comment_issues'].append(file_path)
                    
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
        
        return corrupted_files
    
    def fix_all(self, directory: Path) -> None:
        """Fix all Python files in directory."""
        python_files = self.find_python_files(directory)
        
        print(f"Found {len(python_files)} Python files (excluding gitignored)")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE FIX'}")
        print(f"Backup: {'Enabled' if self.backup else 'Disabled'}")
        print("-" * 50)
        
        for file_path in python_files:
            if self.fix_file(file_path):
                self.files_processed += 1
        
        print("-" * 50)
        print(f"Summary:")
        print(f"  Files processed: {self.files_processed}")
        print(f"  Total fixes applied: {self.fixes_applied}")


def main():
    parser = argparse.ArgumentParser(description='Fix systematic comma corruption in Python files')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to process (default: current)')
    parser.add_argument('--live', action='store_true', help='Actually apply fixes (default: dry run)')
    parser.add_argument('--no-backup', action='store_true', help='Disable backup creation')
    parser.add_argument('--scan-only', action='store_true', help='Only scan for corruption, don\'t fix')
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        return 1
    
    fixer = CommaCorruptionFixer(
        dry_run=not args.live,
        backup=not args.no_backup
    )
    
    if args.scan_only:
        print("Scanning for corruption patterns...")
        corrupted = fixer.scan_for_corruption(directory)
        
        total_corrupted = sum(len(files) for files in corrupted.values())
        print(f"\nFound {total_corrupted} corrupted files")
        
        for issue_type, files in corrupted.items():
            if files:
                print(f"\n{issue_type.replace('_', ' ').title()}:")
                for file_path in files[:10]:  # Show first 10
                    print(f"  {file_path}")
                if len(files) > 10:
                    print(f"  ... and {len(files) - 10} more")
    else:
        fixer.fix_all(directory)
    
    return 0


if __name__ == '__main__':
    exit(main()) 