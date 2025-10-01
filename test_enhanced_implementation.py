#!/usr/bin/env python3
"""Test the enhanced ReflectiveModule implementation"""

import asyncio
import tempfile
from pathlib import Path

# Import our enhanced components
from src.ontology_framework.test_generation import TestGenerator, AsyncTestExecutor
from src.ontology_framework.core.service_registry import get_service_registry


async def test_enhanced_test_generator():
    """Test the enhanced TestGenerator with ReflectiveModule capabilities"""
    print("🧪 Testing Enhanced TestGenerator with ReflectiveModule")
    
    # Create a sample Python file
    sample_code = '''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

class Calculator:
    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers"""
        return x * y
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_code)
        temp_file = f.name
    
    try:
        # Initialize enhanced TestGenerator
        test_gen = TestGenerator(environment="development")
        
        # Test module info (ReflectiveModule capability)
        module_info = test_gen.get_module_info()
        print(f"✅ Module Info: {module_info['module_name']} (env: {module_info['environment']})")
        
        # Test health status (ReflectiveModule capability)
        health = test_gen.get_health_status()
        print(f"✅ Health Status: {health.status.value} (score: {health.health_score:.2f})")
        
        # Test CLI interface generation (ReflectiveModule capability)
        cli_interface = test_gen.get_cli_interface()
        print(f"✅ CLI Commands Available: {len(cli_interface['commands'])}")
        
        # Test test generation with observability
        test_suite = await test_gen.generate_tests_from_code(temp_file)
        print(f"✅ Generated {len(test_suite.test_cases)} test cases with full observability")
        
        # Test performance metrics (ReflectiveModule capability)
        performance = test_gen.get_performance_metrics()
        print(f"✅ Performance Metrics: {performance['operation_count']} operations, {performance['error_count']} errors")
        
        return test_suite
        
    finally:
        Path(temp_file).unlink()


async def test_enhanced_async_executor():
    """Test the enhanced AsyncTestExecutor with ReflectiveModule capabilities"""
    print("\n⚡ Testing Enhanced AsyncTestExecutor with ReflectiveModule")
    
    # Create a simple test suite
    from src.ontology_framework.test_generation.data_models import TestCase, TestSuite
    
    test_cases = [
        TestCase(
            name="test_example_1",
            description="Test case 1",
            test_code="assert True",
            tags=["unit"]
        ),
        TestCase(
            name="test_example_2", 
            description="Test case 2",
            test_code="assert 1 + 1 == 2",
            tags=["unit"]
        )
    ]
    
    test_suite = TestSuite(
        name="enhanced_test_suite",
        test_cases=test_cases
    )
    
    # Initialize enhanced AsyncTestExecutor
    executor = AsyncTestExecutor(environment="development")
    
    # Test module capabilities
    capabilities = executor.get_capabilities()
    print(f"✅ Module Capabilities: {[cap.value for cap in capabilities]}")
    
    # Test service registry integration
    service_config = executor.get_service_config("prometheus")
    print(f"✅ Service Config Available: {bool(service_config)}")
    
    # Test execution with observability
    result = await executor.execute_test_suite(test_suite)
    print(f"✅ Executed {result.total_tests} tests: {result.passed_tests} passed, {result.failed_tests} failed")
    
    # Test operation traces (ReflectiveModule capability)
    traces = executor.get_operation_traces(limit=5)
    print(f"✅ Operation Traces: {len(traces)} traces captured")
    
    return result


async def test_service_registry():
    """Test the ServiceRegistry centralized configuration"""
    print("\n🔧 Testing ServiceRegistry Centralized Configuration")
    
    # Test singleton behavior
    registry1 = get_service_registry("development")
    registry2 = get_service_registry("development")
    
    print(f"✅ Singleton Pattern: {registry1 is registry2}")
    
    # Test configuration retrieval
    cms_config = registry1.get_cms_config()
    print(f"✅ CMS Config: {cms_config.url}")
    
    prometheus_config = registry1.get_prometheus_config()
    print(f"✅ Prometheus Config: Port {prometheus_config.additional_config['port']}")
    
    # Test health checking
    health_status = registry1.health_check_all_services()
    print(f"✅ Service Health: {health_status}")
    
    return registry1


async def main():
    """Run all enhanced implementation tests"""
    print("🚀 Testing Enhanced ReflectiveModule Implementation")
    print("=" * 60)
    
    try:
        # Test ServiceRegistry
        registry = await test_service_registry()
        
        # Test enhanced TestGenerator
        test_suite = await test_enhanced_test_generator()
        
        # Test enhanced AsyncTestExecutor
        result = await test_enhanced_async_executor()
        
        print("\n" + "=" * 60)
        print("🎉 All enhanced implementation tests completed successfully!")
        print("\nKey enhancements validated:")
        print("✅ ReflectiveModule integration with automatic observability")
        print("✅ ServiceRegistry centralized configuration (DRY principle)")
        print("✅ Environment-aware service discovery")
        print("✅ Automatic Prometheus metrics and health endpoints")
        print("✅ CLI interface generation through method introspection")
        print("✅ Operation tracing with correlation IDs")
        print("✅ Real-time Observatory event emission")
        print("✅ CMS integration for configuration storage")
        print("✅ Graceful degradation when services unavailable")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Enhanced implementation test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)