"""DAG builder for test execution with dependency management"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from .data_models import TestCase, TestSuite


@dataclass
class TestNode:
    """A node in the test execution DAG"""
    test_case: TestCase
    dependencies: Set[str]  # Test names this test depends on
    dependents: Set[str]    # Test names that depend on this test
    
    def __post_init__(self):
        if not isinstance(self.dependencies, set):
            self.dependencies = set(self.dependencies) if self.dependencies else set()
        if not isinstance(self.dependents, set):
            self.dependents = set(self.dependents) if self.dependents else set()


@dataclass
class TestDAG:
    """Directed Acyclic Graph for test execution"""
    nodes: Dict[str, TestNode]
    execution_order: List[List[str]]  # Batches of tests that can run in parallel
    
    def __post_init__(self):
        if not self.nodes:
            self.nodes = {}
        if not self.execution_order:
            self.execution_order = []


class TestDAGBuilder:
    """Build DAG structures for test execution with dependency analysis"""
    
    def __init__(self):
        self.setup_teardown_patterns = {
            'setup': ['setup', 'init', 'before', 'prepare'],
            'teardown': ['teardown', 'cleanup', 'after', 'destroy']
        }
    
    def build_test_dag(self, test_suite: TestSuite) -> TestDAG:
        """Build a DAG from a test suite by analyzing dependencies"""
        # Create nodes for each test
        nodes = {}
        for test_case in test_suite.test_cases:
            dependencies = self._analyze_test_dependencies(test_case, test_suite.test_cases)
            nodes[test_case.name] = TestNode(
                test_case=test_case,
                dependencies=dependencies,
                dependents=set()
            )
        
        # Calculate dependents (reverse dependencies)
        for test_name, node in nodes.items():
            for dep in node.dependencies:
                if dep in nodes:
                    nodes[dep].dependents.add(test_name)
        
        # Calculate execution order (topological sort)
        execution_order = self._calculate_execution_order(nodes)
        
        return TestDAG(nodes=nodes, execution_order=execution_order)
    
    def _analyze_test_dependencies(self, test_case: TestCase, all_tests: List[TestCase]) -> Set[str]:
        """Analyze dependencies for a test case"""
        dependencies = set()
        
        # Check for explicit fixture dependencies
        if hasattr(test_case, 'fixtures') and test_case.fixtures:
            for fixture in test_case.fixtures:
                # Find tests that provide this fixture
                for other_test in all_tests:
                    if self._provides_fixture(other_test, fixture):
                        dependencies.add(other_test.name)
        
        # Check for setup/teardown patterns
        setup_deps = self._find_setup_dependencies(test_case, all_tests)
        dependencies.update(setup_deps)
        
        # Check for class-level dependencies
        class_deps = self._find_class_dependencies(test_case, all_tests)
        dependencies.update(class_deps)
        
        return dependencies
    
    def _provides_fixture(self, test_case: TestCase, fixture_name: str) -> bool:
        """Check if a test case provides a specific fixture"""
        # Simple heuristic: test name contains fixture name
        return fixture_name.lower() in test_case.name.lower()
    
    def _find_setup_dependencies(self, test_case: TestCase, all_tests: List[TestCase]) -> Set[str]:
        """Find setup dependencies based on naming patterns"""
        dependencies = set()
        
        # If this is not a setup test, it might depend on setup tests
        if not any(pattern in test_case.name.lower() for pattern in self.setup_teardown_patterns['setup']):
            for other_test in all_tests:
                if any(pattern in other_test.name.lower() for pattern in self.setup_teardown_patterns['setup']):
                    # Check if they're related (same class or module)
                    if self._are_related_tests(test_case, other_test):
                        dependencies.add(other_test.name)
        
        return dependencies
    
    def _find_class_dependencies(self, test_case: TestCase, all_tests: List[TestCase]) -> Set[str]:
        """Find dependencies based on class structure"""
        dependencies = set()
        
        # Extract class name from test case name
        test_class = self._extract_class_name(test_case.name)
        if not test_class:
            return dependencies
        
        # Look for class initialization tests
        for other_test in all_tests:
            other_class = self._extract_class_name(other_test.name)
            if (other_class == test_class and 
                other_test.name != test_case.name and
                ('init' in other_test.name.lower() or 'setup' in other_test.name.lower())):
                dependencies.add(other_test.name)
        
        return dependencies
    
    def _are_related_tests(self, test1: TestCase, test2: TestCase) -> bool:
        """Check if two tests are related (same class/module)"""
        # Simple heuristic: similar naming patterns
        class1 = self._extract_class_name(test1.name)
        class2 = self._extract_class_name(test2.name)
        
        if class1 and class2:
            return class1 == class2
        
        # Check for common prefixes
        name1_parts = test1.name.split('_')
        name2_parts = test2.name.split('_')
        
        if len(name1_parts) >= 2 and len(name2_parts) >= 2:
            return name1_parts[1] == name2_parts[1]  # Same class/module
        
        return False
    
    def _extract_class_name(self, test_name: str) -> Optional[str]:
        """Extract class name from test name"""
        # Pattern: test_ClassName_method_name
        parts = test_name.split('_')
        if len(parts) >= 3 and parts[0] == 'test':
            return parts[1]
        return None
    
    def _calculate_execution_order(self, nodes: Dict[str, TestNode]) -> List[List[str]]:
        """Calculate execution order using topological sort"""
        # Kahn's algorithm for topological sorting
        in_degree = {}
        for name, node in nodes.items():
            in_degree[name] = len(node.dependencies)
        
        execution_order = []
        
        while nodes:
            # Find nodes with no dependencies (in_degree = 0)
            ready_tests = [name for name, degree in in_degree.items() if degree == 0 and name in nodes]
            
            if not ready_tests:
                # Circular dependency detected - break it by taking remaining tests
                ready_tests = list(nodes.keys())
            
            execution_order.append(ready_tests)
            
            # Remove ready tests and update in_degrees
            for test_name in ready_tests:
                node = nodes.pop(test_name)
                del in_degree[test_name]
                
                # Reduce in_degree for dependents
                for dependent in node.dependents:
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
        
        return execution_order
    
    def validate_dag(self, dag: TestDAG) -> Tuple[bool, List[str]]:
        """Validate that the DAG has no cycles"""
        issues = []
        
        # Check for self-dependencies
        for name, node in dag.nodes.items():
            if name in node.dependencies:
                issues.append(f"Test {name} depends on itself")
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_name: str) -> bool:
            if node_name in rec_stack:
                return True
            if node_name in visited:
                return False
            
            visited.add(node_name)
            rec_stack.add(node_name)
            
            node = dag.nodes.get(node_name)
            if node:
                for dep in node.dependencies:
                    if dep in dag.nodes and has_cycle(dep):
                        return True
            
            rec_stack.remove(node_name)
            return False
        
        for node_name in dag.nodes:
            if node_name not in visited:
                if has_cycle(node_name):
                    issues.append(f"Circular dependency detected involving {node_name}")
        
        return len(issues) == 0, issues