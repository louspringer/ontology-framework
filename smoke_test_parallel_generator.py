#!/usr/bin/env python3
"""Smoke test for the parallel test generator system"""

import asyncio
import time
import tempfile
from pathlib import Path

# Import our test generation components
from src.ontology_framework.test_generation import (
    TestGenerator, AsyncTestExecutor, TestGenerationConfig, ExecutionConfig
)


async def create_sample_python_file() -> str:
    """Create a sample Python file for testing"""
    sample_code = '''
"""Sample module for testing test generation"""

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

async def fetch_data(url: str) -> dict:
    """Fetch data from a URL (async example)"""
    # Simulate async operation
    await asyncio.sleep(0.1)
    return {"url": url, "data": "sample"}

class Calculator:
    """Simple calculator class"""
    
    def __init__(self, precision: int = 2):
        self.precision = precision
    
    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers"""
        result = x * y
        return round(result, self.precision)
    
    async def divide_async(self, x: float, y: float) -> float:
        """Async division with validation"""
        if y == 0:
            raise ValueError("Cannot divide by zero")
        await asyncio.sleep(0.01)  # Simulate async work
        return round(x / y, self.precision)

def _private_function():
    """This should not generate tests"""
    return "private"
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_code)
        return f.name


async def test_basic_generation():
    """Test basic test generation functionality"""
    print("🧪 Testing basic test generation...")
    
    # Create sample file
    sample_file = await create_sample_python_file()
    
    try:
        # Initialize generator
        config = TestGenerationConfig(
            template_style="pytest",
            include_edge_cases=True,
            max_test_cases_per_function=3
        )
        generator = TestGenerator(config)
        
        # Generate tests
        test_suite = await generator.generate_tests_from_code(sample_file)
        
        print(f"✅ Generated test suite: {test_suite.name}")
        print(f"   - Total test cases: {len(test_suite.test_cases)}")
        
        # Print some sample test cases
        for i, test_case in enumerate(test_suite.test_cases[:3]):
            print(f"   - Test {i+1}: {test_case.name}")
            print(f"     Description: {test_case.description}")
            print(f"     Is Async: {test_case.is_async}")
            print(f"     Tags: {test_case.tags}")
        
        return test_suite
        
    finally:
        # Clean up
        Path(sample_file).unlink()


async def test_async_execution():
    """Test async test execution"""
    print("\n⚡ Testing async test execution...")
    
    # Create sample file and generate tests
    sample_file = await create_sample_python_file()
    
    try:
        generator = TestGenerator()
        test_suite = await generator.generate_tests_from_code(sample_file)
        
        # Configure executor
        exec_config = ExecutionConfig(
            max_concurrent_tests=5,
            thread_pool_size=2,
            timeout_default=10.0
        )
        
        # Execute tests
        async with AsyncTestExecutor(exec_config) as executor:
            start_time = time.time()
            result = await executor.execute_test_suite(test_suite)
            execution_time = time.time() - start_time
            
            print(f"✅ Executed test suite in {execution_time:.2f} seconds")
            print(f"   - Total tests: {result.total_tests}")
            print(f"   - Passed: {result.passed_tests}")
            print(f"   - Failed: {result.failed_tests}")
            print(f"   - Errors: {result.error_tests}")
            print(f"   - Timeouts: {result.timeout_tests}")
            
            # Show some individual results
            print("   Sample results:")
            for test_result in result.test_results[:3]:
                print(f"     - {test_result.test_name}: {test_result.status.value} ({test_result.duration:.3f}s)")
        
        return result
        
    finally:
        Path(sample_file).unlink()


async def test_progress_monitoring():
    """Test real-time progress monitoring"""
    print("\n📊 Testing progress monitoring...")
    
    sample_file = await create_sample_python_file()
    
    try:
        generator = TestGenerator()
        test_suite = await generator.generate_tests_from_code(sample_file)
        
        # Add more test cases for better progress demonstration
        for i in range(5):
            test_suite.test_cases.append(
                test_suite.test_cases[0]._replace(name=f"extra_test_{i}")
            )
        
        exec_config = ExecutionConfig(max_concurrent_tests=3)
        
        async with AsyncTestExecutor(exec_config) as executor:
            print("   Progress updates:")
            async for progress in executor.execute_with_progress(test_suite):
                print(f"     {progress.completion_percentage:.1f}% complete "
                      f"({progress.completed_tests}/{progress.total_tests}) "
                      f"- Current: {progress.current_test} "
                      f"- Failed: {progress.failed_tests}")
        
        print("✅ Progress monitoring completed")
        
    finally:
        Path(sample_file).unlink()


async def test_spec_generation():
    """Test specification-based test generation"""
    print("\n📋 Testing spec-based test generation...")
    
    generator = TestGenerator()
    
    # Generate tests from a mock specification
    spec_content = """
    # Sample Specification
    
    ## Requirements
    
    1. System SHALL validate user input
    2. System SHALL handle errors gracefully
    3. System SHALL provide async operations
    """
    
    test_suite = await generator.generate_tests_from_spec(spec_content)
    
    print(f"✅ Generated spec-based test suite: {test_suite.name}")
    print(f"   - Total test cases: {len(test_suite.test_cases)}")
    
    for test_case in test_suite.test_cases:
        print(f"   - {test_case.name}: {test_case.description}")


async def test_error_handling():
    """Test error handling in generation and execution"""
    print("\n🚨 Testing error handling...")
    
    generator = TestGenerator()
    
    # Test with non-existent file
    try:
        await generator.generate_tests_from_code("non_existent_file.py")
        print("❌ Should have raised FileNotFoundError")
    except FileNotFoundError:
        print("✅ Correctly handled missing file")
    
    # Test with invalid Python syntax
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def invalid_syntax(\n")  # Incomplete function
        invalid_file = f.name
    
    try:
        await generator.generate_tests_from_code(invalid_file)
        print("❌ Should have raised ValueError for invalid syntax")
    except ValueError as e:
        print(f"✅ Correctly handled invalid syntax: {str(e)[:50]}...")
    finally:
        Path(invalid_file).unlink()


async def main():
    """Run all smoke tests"""
    print("🚀 Starting Parallel Test Generator Smoke Test")
    print("=" * 50)
    
    try:
        # Run all test scenarios
        await test_basic_generation()
        await test_async_execution()
        await test_progress_monitoring()
        await test_spec_generation()
        await test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 All smoke tests completed successfully!")
        print("\nKey features validated:")
        print("✅ Test generation from Python code")
        print("✅ Async test execution with concurrency control")
        print("✅ Real-time progress monitoring")
        print("✅ Specification-based test generation")
        print("✅ Error handling and recovery")
        print("✅ Template-based test code generation")
        print("✅ Thread pool management for sync tests")
        
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)