"""Core data models for test generation and execution"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, AsyncIterator
from enum import Enum
import time


class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class CoverageLevel(Enum):
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    EXHAUSTIVE = "exhaustive"


@dataclass
class TestCase:
    """Individual test case with all necessary information"""
    name: str
    description: str
    test_code: str
    imports: List[str] = field(default_factory=list)
    fixtures: List[str] = field(default_factory=list)
    parameters: Optional[List[Dict[str, Any]]] = None
    expected_outcome: TestStatus = TestStatus.PASSED
    tags: List[str] = field(default_factory=list)
    timeout: float = 30.0
    is_async: bool = False


@dataclass
class TestSuite:
    """Collection of related test cases"""
    name: str
    test_cases: List[TestCase]
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0


@dataclass
class TestResult:
    """Result of executing a single test case"""
    test_name: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    output: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None


@dataclass
class TestSuiteResult:
    """Aggregated results from executing a test suite"""
    suite_name: str
    total_tests: int
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    skipped_tests: int = 0
    timeout_tests: int = 0
    total_duration: float = 0.0
    test_results: List[TestResult] = field(default_factory=list)


@dataclass
class ProgressUpdate:
    """Real-time progress information during test execution"""
    completed_tests: int
    total_tests: int
    current_test: Optional[str] = None
    elapsed_time: float = 0.0
    estimated_remaining: float = 0.0
    failed_tests: int = 0
    
    @property
    def completion_percentage(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.completed_tests / self.total_tests) * 100


@dataclass
class TestGenerationConfig:
    """Configuration for test generation behavior"""
    template_style: str = "pytest"  # pytest, unittest, custom
    coverage_level: CoverageLevel = CoverageLevel.COMPREHENSIVE
    include_edge_cases: bool = True
    generate_property_tests: bool = False
    max_test_cases_per_function: int = 5
    async_test_support: bool = True
    max_concurrent_tests: int = 10
    default_timeout: float = 30.0
    fail_fast: bool = False


@dataclass
class ExecutionConfig:
    """Configuration for test execution behavior"""
    max_concurrent_tests: int = 10
    thread_pool_size: int = 4
    timeout_default: float = 30.0
    timeout_max: float = 300.0
    capture_output: bool = True
    verbose_reporting: bool = True
    fail_fast: bool = False