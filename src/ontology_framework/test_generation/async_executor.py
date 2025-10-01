"""Async test executor for concurrent test execution"""

import asyncio
import time
import traceback
from typing import List, AsyncIterator, Optional
from concurrent.futures import ThreadPoolExecutor
from .data_models import TestCase, TestResult, TestSuite, TestSuiteResult, ProgressUpdate, TestStatus, ExecutionConfig
from ..core.enhanced_reflective_module import OntologyReflectiveModule
from .real_executor import RealTestExecutor


class AsyncTestExecutor(OntologyReflectiveModule):
    """Execute tests concurrently using asyncio and thread pools with comprehensive observability"""
    
    def __init__(self, config: Optional[ExecutionConfig] = None, environment: str = None):
        super().__init__(environment)
        self.config = config or ExecutionConfig()
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_tests)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.thread_pool_size)
        
        # Initialize real test executor for actual test execution
        self.real_executor = RealTestExecutor()
        
        # Store execution configuration in CMS
        self.store_content(
            content_id="test_execution_config",
            collection="configurations", 
            data=self.config.__dict__
        )
        
    async def execute_test_suite(self, test_suite: TestSuite) -> TestSuiteResult:
        """Execute all tests in a suite concurrently with full observability"""
        with self.trace_operation("execute_test_suite", test_count=len(test_suite.test_cases)) as trace:
            # Emit execution start observation
            self.emit_observation(
                f"Starting execution of {len(test_suite.test_cases)} tests in parallel",
                event_type="deployment",
                context={"suite_name": test_suite.name, "test_count": len(test_suite.test_cases)},
                emoji="⚡"
            )
            
            start_time = time.time()
            
            # Execute all tests concurrently
            tasks = [
                self._execute_single_test(test_case) 
                for test_case in test_suite.test_cases
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            test_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    test_results.append(TestResult(
                        test_name=test_suite.test_cases[i].name,
                        status=TestStatus.ERROR,
                        duration=0.0,
                        error_message=str(result),
                        stack_trace=traceback.format_exc()
                    ))
                else:
                    test_results.append(result)
            
            # Aggregate results
            total_duration = time.time() - start_time
            suite_result = self._aggregate_results(test_suite.name, test_results, total_duration)
            
            # Emit completion observation
            self.emit_observation(
                f"Completed test suite execution: {suite_result.passed_tests} passed, {suite_result.failed_tests} failed in {total_duration:.2f}s",
                event_type="success" if suite_result.failed_tests == 0 else "warning",
                context={
                    "total_tests": suite_result.total_tests,
                    "passed": suite_result.passed_tests,
                    "failed": suite_result.failed_tests,
                    "duration": total_duration
                },
                emoji="✅" if suite_result.failed_tests == 0 else "⚠️"
            )
            
            trace.output_result = {
                "total_tests": suite_result.total_tests,
                "passed": suite_result.passed_tests,
                "failed": suite_result.failed_tests,
                "duration": total_duration
            }
            
            return suite_result
    
    async def execute_with_progress(self, test_suite: TestSuite) -> AsyncIterator[ProgressUpdate]:
        """Execute tests with real-time progress updates"""
        start_time = time.time()
        completed = 0
        total = len(test_suite.test_cases)
        failed = 0
        
        # Create tasks for all tests
        tasks = [
            self._execute_single_test_with_callback(test_case, lambda: None)
            for test_case in test_suite.test_cases
        ]
        
        # Execute and yield progress updates
        for coro in asyncio.as_completed(tasks):
            result = await coro
            completed += 1
            if result.status in [TestStatus.FAILED, TestStatus.ERROR, TestStatus.TIMEOUT]:
                failed += 1
            
            elapsed = time.time() - start_time
            estimated_remaining = (elapsed / completed) * (total - completed) if completed > 0 else 0
            
            yield ProgressUpdate(
                completed_tests=completed,
                total_tests=total,
                current_test=result.test_name,
                elapsed_time=elapsed,
                estimated_remaining=estimated_remaining,
                failed_tests=failed
            )
    
    async def _execute_single_test(self, test_case: TestCase) -> TestResult:
        """Execute a single test case with concurrency control"""
        async with self.semaphore:
            return await self._run_test_case(test_case)
    
    async def _execute_single_test_with_callback(self, test_case: TestCase, callback) -> TestResult:
        """Execute a single test case with callback support"""
        async with self.semaphore:
            result = await self._run_test_case(test_case)
            callback()
            return result
    
    async def _run_test_case(self, test_case: TestCase) -> TestResult:
        """Run the actual test case logic"""
        start_time = time.time()
        
        try:
            # Simulate test execution (in real implementation, this would execute the actual test)
            if test_case.is_async:
                result = await self._execute_async_test(test_case)
            else:
                result = await self._execute_sync_test(test_case)
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name=test_case.name,
                status=result.get("status", TestStatus.PASSED),
                duration=duration,
                error_message=result.get("error"),
                output=result.get("output"),
                start_time=start_time,
                end_time=time.time()
            )
            
        except asyncio.TimeoutError:
            return TestResult(
                test_name=test_case.name,
                status=TestStatus.TIMEOUT,
                duration=test_case.timeout,
                error_message=f"Test timed out after {test_case.timeout} seconds",
                start_time=start_time,
                end_time=time.time()
            )
        except Exception as e:
            return TestResult(
                test_name=test_case.name,
                status=TestStatus.ERROR,
                duration=time.time() - start_time,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
                start_time=start_time,
                end_time=time.time()
            )
    
    async def _execute_async_test(self, test_case: TestCase) -> dict:
        """Execute an async test case using real test execution"""
        try:
            # Use real test executor for actual test execution
            result = await self.real_executor.execute_real_test(test_case)
            
            return {
                "status": result.status,
                "error": result.error_message,
                "output": result.output or f"Test {test_case.name} executed"
            }
        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "error": str(e),
                "output": f"Test {test_case.name} execution failed"
            }
    
    async def _execute_sync_test(self, test_case: TestCase) -> dict:
        """Execute a synchronous test case using real test execution"""
        try:
            # Use real test executor for actual test execution
            result = await self.real_executor.execute_real_test(test_case)
            
            return {
                "status": result.status,
                "error": result.error_message,
                "output": result.output or f"Test {test_case.name} executed"
            }
        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "error": str(e),
                "output": f"Test {test_case.name} execution failed"
            }
    
    def _aggregate_results(self, suite_name: str, results: List[TestResult], total_duration: float) -> TestSuiteResult:
        """Aggregate individual test results into suite result"""
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        error = sum(1 for r in results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)
        timeout = sum(1 for r in results if r.status == TestStatus.TIMEOUT)
        
        return TestSuiteResult(
            suite_name=suite_name,
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=failed,
            error_tests=error,
            skipped_tests=skipped,
            timeout_tests=timeout,
            total_duration=total_duration,
            test_results=results
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.thread_pool.shutdown(wait=True)