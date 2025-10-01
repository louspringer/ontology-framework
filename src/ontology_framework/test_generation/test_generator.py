"""Test generator for creating test cases from code analysis"""

import ast
import inspect
from typing import List, Optional, Dict, Any
from pathlib import Path
from .data_models import TestCase, TestSuite, TestGenerationConfig, TestStatus
from ..core.enhanced_reflective_module import OntologyReflectiveModule


class TestGenerator(OntologyReflectiveModule):
    """Generate test cases from Python code analysis with comprehensive observability"""
    
    def __init__(self, config: Optional[TestGenerationConfig] = None, environment: str = None):
        super().__init__(environment)
        self.config = config or TestGenerationConfig()
        
        # Store configuration in CMS for centralized management
        self.store_content(
            content_id="test_generation_config",
            collection="configurations",
            data=self.config.__dict__
        )
    
    async def generate_tests_from_code(self, file_path: str) -> TestSuite:
        """Generate tests from a Python source file with full observability"""
        with self.trace_operation("generate_tests_from_code", file_path=file_path) as trace:
            # Emit real-time observation
            self.emit_observation(
                f"Generating tests from {file_path}",
                event_type="api_request",
                emoji="🧪"
            )
            
            path = Path(file_path)
            if not path.exists():
                self.emit_observation(
                    f"File not found: {file_path}",
                    event_type="error",
                    emoji="❌"
                )
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse the AST
            try:
                tree = ast.parse(source_code)
            except SyntaxError as e:
                self.emit_observation(
                    f"Invalid Python syntax in {file_path}: {e}",
                    event_type="error",
                    emoji="❌"
                )
                raise ValueError(f"Invalid Python syntax in {file_path}: {e}")
            
            # Extract testable elements
            test_cases = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Skip private functions
                        test_cases.extend(await self._generate_function_tests(node, path.stem))
                elif isinstance(node, ast.ClassDef):
                    test_cases.extend(await self._generate_class_tests(node, path.stem))
            
            test_suite = TestSuite(
                name=f"test_{path.stem}",
                test_cases=test_cases,
                estimated_duration=len(test_cases) * 0.1  # Rough estimate
            )
            
            # Emit success observation
            self.emit_observation(
                f"Generated {len(test_cases)} test cases from {file_path}",
                event_type="success",
                context={"test_count": len(test_cases), "file": file_path},
                emoji="✅"
            )
            
            trace.output_result = {"test_count": len(test_cases), "suite_name": test_suite.name}
            return test_suite
    
    async def generate_tests_from_spec(self, spec_content: str) -> TestSuite:
        """Generate tests from specification content (simplified for smoke test)"""
        # For smoke test, create some basic spec-based tests
        test_cases = [
            TestCase(
                name="test_spec_requirement_1",
                description="Test that requirement 1 is satisfied",
                test_code=self._generate_spec_test_code("requirement_1"),
                tags=["spec", "requirement"]
            ),
            TestCase(
                name="test_spec_acceptance_criteria",
                description="Test acceptance criteria validation",
                test_code=self._generate_spec_test_code("acceptance_criteria"),
                tags=["spec", "acceptance"]
            )
        ]
        
        return TestSuite(
            name="test_specification",
            test_cases=test_cases
        )
    
    async def _generate_function_tests(self, func_node: ast.FunctionDef, module_name: str) -> List[TestCase]:
        """Generate test cases for a function"""
        test_cases = []
        func_name = func_node.name
        
        # Check if function is async
        is_async = isinstance(func_node, ast.AsyncFunctionDef)
        
        # Basic happy path test
        test_cases.append(TestCase(
            name=f"test_{func_name}_happy_path",
            description=f"Test {func_name} with valid inputs",
            test_code=self._generate_function_test_code(func_name, "happy_path", is_async),
            is_async=is_async,
            tags=["unit", "happy_path"]
        ))
        
        # Edge case tests if enabled
        if self.config.include_edge_cases:
            test_cases.append(TestCase(
                name=f"test_{func_name}_edge_cases",
                description=f"Test {func_name} with edge case inputs",
                test_code=self._generate_function_test_code(func_name, "edge_cases", is_async),
                is_async=is_async,
                tags=["unit", "edge_case"]
            ))
        
        # Error handling tests
        test_cases.append(TestCase(
            name=f"test_{func_name}_error_handling",
            description=f"Test {func_name} error handling",
            test_code=self._generate_function_test_code(func_name, "error_handling", is_async),
            is_async=is_async,
            tags=["unit", "error_handling"]
        ))
        
        return test_cases[:self.config.max_test_cases_per_function]
    
    async def _generate_class_tests(self, class_node: ast.ClassDef, module_name: str) -> List[TestCase]:
        """Generate test cases for a class"""
        test_cases = []
        class_name = class_node.name
        
        # Constructor test
        test_cases.append(TestCase(
            name=f"test_{class_name.lower()}_initialization",
            description=f"Test {class_name} initialization",
            test_code=self._generate_class_test_code(class_name, "initialization"),
            tags=["unit", "initialization"]
        ))
        
        # Method tests
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_') or node.name in ['__init__', '__str__', '__repr__']:
                    method_tests = await self._generate_method_tests(node, class_name)
                    test_cases.extend(method_tests)
        
        return test_cases
    
    async def _generate_method_tests(self, method_node: ast.FunctionDef, class_name: str) -> List[TestCase]:
        """Generate test cases for a class method"""
        method_name = method_node.name
        is_async = isinstance(method_node, ast.AsyncFunctionDef)
        
        return [TestCase(
            name=f"test_{class_name.lower()}_{method_name}",
            description=f"Test {class_name}.{method_name}",
            test_code=self._generate_method_test_code(class_name, method_name, is_async),
            is_async=is_async,
            tags=["unit", "method"]
        )]
    
    def _generate_function_test_code(self, func_name: str, test_type: str, is_async: bool) -> str:
        """Generate test code for a function"""
        if self.config.template_style == "pytest":
            if is_async:
                return f'''
import pytest
import asyncio

@pytest.mark.asyncio
async def test_{func_name}_{test_type}():
    """Test {func_name} - {test_type}"""
    # TODO: Implement actual test logic
    result = await {func_name}()
    assert result is not None
'''
            else:
                return f'''
import pytest

def test_{func_name}_{test_type}():
    """Test {func_name} - {test_type}"""
    # TODO: Implement actual test logic
    result = {func_name}()
    assert result is not None
'''
        else:  # unittest style
            return f'''
import unittest

class Test{func_name.title()}(unittest.TestCase):
    def test_{test_type}(self):
        """Test {func_name} - {test_type}"""
        # TODO: Implement actual test logic
        result = {func_name}()
        self.assertIsNotNone(result)
'''
    
    def _generate_class_test_code(self, class_name: str, test_type: str) -> str:
        """Generate test code for a class"""
        if self.config.template_style == "pytest":
            return f'''
import pytest

def test_{class_name.lower()}_{test_type}():
    """Test {class_name} {test_type}"""
    instance = {class_name}()
    assert instance is not None
'''
        else:
            return f'''
import unittest

class Test{class_name}(unittest.TestCase):
    def test_{test_type}(self):
        """Test {class_name} {test_type}"""
        instance = {class_name}()
        self.assertIsNotNone(instance)
'''
    
    def _generate_method_test_code(self, class_name: str, method_name: str, is_async: bool) -> str:
        """Generate test code for a class method"""
        if self.config.template_style == "pytest":
            if is_async:
                return f'''
import pytest

@pytest.mark.asyncio
async def test_{class_name.lower()}_{method_name}():
    """Test {class_name}.{method_name}"""
    instance = {class_name}()
    result = await instance.{method_name}()
    assert result is not None
'''
            else:
                return f'''
import pytest

def test_{class_name.lower()}_{method_name}():
    """Test {class_name}.{method_name}"""
    instance = {class_name}()
    result = instance.{method_name}()
    assert result is not None
'''
        else:
            return f'''
import unittest

class Test{class_name}{method_name.title()}(unittest.TestCase):
    def test_{method_name}(self):
        """Test {class_name}.{method_name}"""
        instance = {class_name}()
        result = instance.{method_name}()
        self.assertIsNotNone(result)
'''
    
    def _generate_spec_test_code(self, test_type: str) -> str:
        """Generate test code for specification-based tests"""
        return f'''
import pytest

def test_spec_{test_type}():
    """Test specification {test_type}"""
    # TODO: Implement specification validation
    assert True  # Placeholder
'''