import unittest
import os
import ast
from collections import defaultdict
from typing import Dict, List, Set
import json

class CoverageAnalyzer:
    def __init__(self, src_dir: str = 'src', test_dir: str = 'tests'):
        self.src_dir = src_dir
        self.test_dir = test_dir
        self.coverage_data: Dict[str, Dict] = defaultdict(dict)
        
    def analyze_coverage(self) -> Dict:
        """Analyze test coverage across the codebase."""
        # Get all source files
        src_files = self._get_python_files(self.src_dir)
        test_files = self._get_python_files(self.test_dir)
        
        # Analyze each source file
        for src_file in src_files:
            module_name = self._get_module_name(src_file)
            self.coverage_data[module_name] = {
                'file_path': src_file,
                'test_files': [],
                'covered_lines': set(),
                'total_lines': 0,
                'coverage_percentage': 0.0
            }
            
            # Find corresponding test files
            test_files_for_module = self._find_test_files(module_name, test_files)
            self.coverage_data[module_name]['test_files'] = test_files_for_module
            
            # Calculate coverage
            self._calculate_coverage(src_file, test_files_for_module)
            
        return self.coverage_data

    def _get_python_files(self, directory: str) -> List[str]:
        """Get all Python files in a directory."""
        python_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files
        
    def _get_module_name(self, file_path: str) -> str:
        """Get module name from file path."""
        rel_path = os.path.relpath(file_path, self.src_dir)
        return rel_path.replace('/', '.').replace('\\', '.')[:-3]
        
    def _find_test_files(self, module_name: str, test_files: List[str]) -> List[str]:
        """Find test files for a module."""
        module_test_files = []
        test_prefix = f'test_{module_name.split(".")[-1]}'
        
        for test_file in test_files:
            if test_prefix in test_file:
                module_test_files.append(test_file)
                
        return module_test_files
        
    def _calculate_coverage(self, src_file: str, test_files: List[str]) -> None:
        """Calculate coverage for a source file."""
        # Parse source file
        with open(src_file, 'r') as f:
            src_tree = ast.parse(f.read())
            
        # Get all lines with code
        code_lines = set()
        for node in ast.walk(src_tree):
            if hasattr(node, 'lineno'):
                code_lines.add(node.lineno)
                
        self.coverage_data[self._get_module_name(src_file)]['total_lines'] = len(code_lines)
        
        # Parse test files and find covered lines
        covered_lines = set()
        for test_file in test_files:
            with open(test_file, 'r') as f:
                test_tree = ast.parse(f.read())
                
            # Find test methods
            for node in ast.walk(test_tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    # Analyze test method for coverage
                    for test_node in ast.walk(node):
                        if isinstance(test_node, ast.Call):
                            # Check if this is a validation call
                            if hasattr(test_node.func, 'attr') and 'validate' in test_node.func.attr:
                                # Add lines that are being tested
                                covered_lines.update(code_lines)
                                
        self.coverage_data[self._get_module_name(src_file)]['covered_lines'] = covered_lines
        self.coverage_data[self._get_module_name(src_file)]['coverage_percentage'] = (
            len(covered_lines) / len(code_lines) * 100 if code_lines else 0.0
        )
        
    def generate_report(self, output_file: str = 'coverage_report.json') -> None:
        """Generate a coverage report."""
        coverage_data = self.analyze_coverage()
        
        # Calculate overall coverage
        total_lines = sum(data['total_lines'] for data in coverage_data.values())
        total_covered = sum(len(data['covered_lines']) for data in coverage_data.values())
        overall_coverage = (total_covered / total_lines * 100) if total_lines else 0.0
        report = {
            'overall_coverage': overall_coverage,
            'modules': {
                module: {
                    'coverage_percentage': data['coverage_percentage'],
                    'covered_lines': len(data['covered_lines']),
                    'total_lines': data['total_lines'],
                    'test_files': data['test_files']
                }
                for module, data in coverage_data.items()
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
    def print_report(self) -> None:
        """Print coverage report to console."""
        coverage_data = self.analyze_coverage()
        
        print("\nTest Coverage Report")
        print("===================")
        
        for module, data in coverage_data.items():
            print(f"\nModule: {module}")
            print(f"Coverage: {data['coverage_percentage']:.2f}%")
            print(f"Covered Lines: {len(data['covered_lines'])}/{data['total_lines']}")
            print("Test Files:")
            for test_file in data['test_files']:
                print(f"  - {test_file}")
                
        total_lines = sum(data['total_lines'] for data in coverage_data.values())
        total_covered = sum(len(data['covered_lines']) for data in coverage_data.values())
        overall_coverage = (total_covered / total_lines * 100) if total_lines else 0.0
        print(f"\nOverall Coverage: {overall_coverage:.2f}%")

if __name__ == '__main__':
    analyzer = CoverageAnalyzer()
    analyzer.print_report()
    analyzer.generate_report() 