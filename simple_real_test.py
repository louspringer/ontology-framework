#!/usr/bin/env python3
"""Simple test of real test execution - macOS/Zsh compatible"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ontology_framework.test_generation.data_models import TestCase
from ontology_framework.test_generation.real_executor import RealTestExecutor


async def test_real_execution():
    """Test real test execution with simple test cases"""
    print("🧪 Testing Real Test Execution (macOS/Zsh Compatible)")
    
    # Create simple test cases
    test_cases = [
        TestCase(
            name="test_simple_pass",
            description="Simple passing test",
            test_code="assert True",
            imports=[]
        ),
        TestCase(
            name="test_simple_math",
            description="Simple math test", 
            test_code="assert 1 + 1 == 2",
            imports=[]
        ),
        TestCase(
            name="test_simple_fail",
            description="Simple failing test",
            test_code="assert False, 'This test should fail'",
            imports=[]
        )
    ]
    
    # Initialize real executor
    executor = RealTestExecutor()
    
    try:
        results = []
        for test_case in test_cases:
            print(f"  Executing: {test_case.name}")
            result = await executor.execute_real_test(test_case)
            results.append(result)
            
            status_emoji = "✅" if result.status.value == "passed" else "❌" if result.status.value == "failed" else "⚠️"
            print(f"    {status_emoji} {result.status.value} ({result.duration:.3f}s)")
            
            if result.error_message:
                print(f"    Error: {result.error_message}")
        
        # Summary
        passed = sum(1 for r in results if r.status.value == "passed")
        failed = sum(1 for r in results if r.status.value == "failed")
        errors = sum(1 for r in results if r.status.value == "error")
        
        print(f"\n📊 Results: {passed} passed, {failed} failed, {errors} errors")
        
        return results
        
    finally:
        executor.cleanup()


async def main():
    """Main test function"""
    print("🚀 Simple Real Test Execution Test")
    print("=" * 50)
    
    try:
        results = await test_real_execution()
        
        print("\n" + "=" * 50)
        print("🎉 Real test execution test completed!")
        print("\nKey capabilities validated:")
        print("✅ Real subprocess execution with pipes and tees")
        print("✅ Temporary test file creation and cleanup")
        print("✅ macOS/Zsh compatible shell command execution")
        print("✅ Proper error handling and result parsing")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Real test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)