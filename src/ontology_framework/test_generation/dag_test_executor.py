"""DAG-aware test executor for intelligent parallel execution"""

import asyncio
import time
from typing import List, Dict, Set
from .data_models import TestSuite, TestSuiteResult, TestResult, TestStatus, ProgressUpdate
from .async_executor import AsyncTestExecutor
from .test_dag_builder import TestDAGBuilder, TestDAG
from ..core.enhanced_reflective_module import OntologyReflectiveModule


class DAGTestExecutor(OntologyReflectiveModule):
    """Execute tests using DAG orchestration for optimal parallelism"""
    
    def __init__(self, environment: str = None):
        super().__init__(environment)
        self.dag_builder = TestDAGBuilder()
        self.base_executor = AsyncTestExecutor(environment=environment)
    
    async def execute_test_suite_with_dag(self, test_suite: TestSuite) -> TestSuiteResult:
        """Execute test suite using DAG orchestration"""
        with self.trace_operation("execute_dag_optimized_suite", test_count=len(test_suite.test_cases)) as trace:
            # Build DAG from test suite
            self.emit_observation(
                f"Building DAG for {len(test_suite.test_cases)} tests",
                event_type="api_request",
                emoji="🔗"
            )
            
            dag = self.dag_builder.build_test_dag(test_suite)
            
            # Validate DAG
            is_valid, issues = self.dag_builder.validate_dag(dag)
            if not is_valid:
                self.emit_observation(
                    f"DAG validation failed: {'; '.join(issues)}",
                    event_type="error",
                    emoji="❌"
                )
                # Fallback to regular execution
                return await self.base_executor.execute_test_suite(test_suite)
            
            # Calculate parallelization benefit
            total_batches = len(dag.execution_order)
            max_parallel = max(len(batch) for batch in dag.execution_order) if dag.execution_order else 1
            parallelization_factor = len(test_suite.test_cases) / total_batches if total_batches > 0 else 1
            
            self.emit_observation(
                f"DAG analysis complete: {total_batches} execution batches, {parallelization_factor:.1f}x parallelization factor",
                event_type="performance",
                context={
                    "total_tests": len(test_suite.test_cases),
                    "execution_batches": total_batches,
                    "max_parallel": max_parallel,
                    "parallelization_factor": parallelization_factor
                },
                emoji="🚀"
            )
            
            # Execute DAG in batches
            start_time = time.time()
            all_results = []
            completed_tests = set()
            
            for batch_index, batch in enumerate(dag.execution_order):
                batch_start = time.time()
                
                self.emit_observation(
                    f"Executing batch {batch_index + 1}/{total_batches}: {len(batch)} tests in parallel",
                    event_type="deployment",
                    context={"batch_tests": batch},
                    emoji="⚡"
                )
                
                # Execute tests in current batch concurrently
                batch_results = await self._execute_test_batch(batch, dag, completed_tests)
                all_results.extend(batch_results)
                
                # Update completed tests
                for result in batch_results:
                    if result.status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.SKIPPED]:
                        completed_tests.add(result.test_name)
                
                batch_duration = time.time() - batch_start
                self.emit_observation(
                    f"Batch {batch_index + 1} completed in {batch_duration:.2f}s",
                    event_type="success",
                    context={"batch_duration": batch_duration, "completed_count": len(completed_tests)},
                    emoji="✅"
                )
            
            # Aggregate results
            total_duration = time.time() - start_time
            suite_result = self._aggregate_dag_results(test_suite.name, all_results, total_duration)
            
            # Calculate efficiency metrics
            sequential_estimate = len(test_suite.test_cases) * 0.1  # Rough estimate
            efficiency = (sequential_estimate / total_duration) if total_duration > 0 else 1.0
            
            self.emit_observation(
                f"DAG execution complete: {suite_result.passed_tests} passed, {suite_result.failed_tests} failed, {efficiency:.1f}x speedup",
                event_type="success",
                context={
                    "total_duration": total_duration,
                    "efficiency": efficiency,
                    "parallelization_factor": parallelization_factor
                },
                emoji="🎉"
            )
            
            trace.output_result = {
                "total_tests": suite_result.total_tests,
                "passed": suite_result.passed_tests,
                "failed": suite_result.failed_tests,
                "duration": total_duration,
                "parallelization_factor": parallelization_factor,
                "efficiency": efficiency
            }
            
            return suite_result
    
    async def _execute_test_batch(self, batch: List[str], dag: TestDAG, completed_tests: Set[str]) -> List[TestResult]:
        """Execute a batch of tests concurrently"""
        # Get test cases for this batch
        test_cases = []
        for test_name in batch:
            if test_name in dag.nodes:
                test_cases.append(dag.nodes[test_name].test_case)
        
        if not test_cases:
            return []
        
        # Create a mini test suite for this batch
        from .data_models import TestSuite
        batch_suite = TestSuite(
            name=f"batch_{len(batch)}_tests",
            test_cases=test_cases
        )
        
        # Execute using base executor
        batch_result = await self.base_executor.execute_test_suite(batch_suite)
        
        return batch_result.test_results
    
    def _aggregate_dag_results(self, suite_name: str, results: List[TestResult], total_duration: float) -> TestSuiteResult:
        """Aggregate DAG execution results"""
        from .data_models import TestSuiteResult
        
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        error = sum(1 for r in results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)
        timeout = sum(1 for r in results if r.status == TestStatus.TIMEOUT)
        
        return TestSuiteResult(
            suite_name=f"{suite_name}_dag_optimized",
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=failed,
            error_tests=error,
            skipped_tests=skipped,
            timeout_tests=timeout,
            total_duration=total_duration,
            test_results=results
        )
    
    async def analyze_test_dependencies(self, test_suite: TestSuite) -> Dict[str, any]:
        """Analyze test dependencies and return DAG information"""
        with self.trace_operation("analyze_test_dependencies", test_count=len(test_suite.test_cases)) as trace:
            dag = self.dag_builder.build_test_dag(test_suite)
            is_valid, issues = self.dag_builder.validate_dag(dag)
            
            analysis = {
                "total_tests": len(test_suite.test_cases),
                "execution_batches": len(dag.execution_order),
                "max_parallel_tests": max(len(batch) for batch in dag.execution_order) if dag.execution_order else 0,
                "dependency_count": sum(len(node.dependencies) for node in dag.nodes.values()),
                "is_valid_dag": is_valid,
                "issues": issues,
                "parallelization_factor": len(test_suite.test_cases) / len(dag.execution_order) if dag.execution_order else 1,
                "execution_plan": dag.execution_order
            }
            
            self.emit_observation(
                f"Dependency analysis: {analysis['parallelization_factor']:.1f}x parallelization possible",
                event_type="info",
                context=analysis,
                emoji="📊"
            )
            
            trace.output_result = analysis
            return analysis
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get DAG executor capabilities"""
        from ..core.enhanced_reflective_module import ModuleCapability
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]