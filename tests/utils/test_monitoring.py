#!/usr/bin/env python3
"""Test monitoring utilities."""

import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Generator, TypedDict
from datetime import datetime
from pathlib import Path
import requests
from contextlib import contextmanager
from dataclasses import dataclass, field

class LogEntry(TypedDict):
    """Structure of a log entry."""
    message: str
    level: str
    timestamp: str

@dataclass
class TestExecution:
    """Information about a test execution."""
    name: str
    duration: float = 0.0
    status: str = "pending"
    error: Optional[str] = None
    server_logs: List[LogEntry] = field(default_factory=list)

class TestMonitor:
    """Monitor test execution and collect metrics."""

    def __init__(self, graphdb_url: str = "http://localhost:7200") -> None:
        """Initialize the test monitor.
        
        Args:
            graphdb_url: URL of the GraphDB server
        """
        self.graphdb_url = graphdb_url
        self.executions: Dict[str, TestExecution] = {}
        self.total_tests = 0
        self.failed_tests = 0
        self.slow_tests = 0
        self.slow_threshold = 1.0  # seconds
        self.logger = logging.getLogger(__name__)
        self.test_start_time: Optional[float] = None
        self.test_metrics: Dict[str, Dict[str, Any]] = {}
        self.current_test: Optional[str] = None
        self.log_dir = Path("test_logs")
        self.log_dir.mkdir(exist_ok=True)
        
    def _get_server_logs(self) -> List[LogEntry]:
        """Get logs from the GraphDB server.
        
        Returns:
            List of log entries as dictionaries
        """
        try:
            response = requests.get(f"{self.graphdb_url}/rest/monitor/logs")
            response.raise_for_status()
            return response.json().get("logs", [])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get server logs: {e}")
            return []
    
    def _get_log_messages(self, logs: List[LogEntry]) -> List[str]:
        """Extract log messages from structured log entries.
        
        Args:
            logs: List of structured log entries
            
        Returns:
            List of log messages
        """
        return [log["message"] for log in logs]
    
    def check_logs_for_message(self, message: str) -> bool:
        """Check if a message exists in the server logs.
        
        Args:
            message: Message to search for
            
        Returns:
            True if message found, False otherwise
            
        Example:
            >>> monitor.check_logs_for_message("Repository 'test_repo' created")
            True
        """
        logs = self._get_server_logs()
        messages = self._get_log_messages(logs)
        return any(message in log_msg for log_msg in messages)
    
    def check_logs_for_error(self, error_message: str) -> bool:
        """Check if an error message exists in the server logs.
        
        Args:
            error_message: Error message to search for
            
        Returns:
            True if error found, False otherwise
            
        Example:
            >>> monitor.check_logs_for_error("Error executing query")
            True
        """
        logs = self._get_server_logs()
        error_logs = [log for log in logs if log["level"] == "ERROR"]
        messages = self._get_log_messages(error_logs)
        return any(error_message in log_msg for log_msg in messages)
    
    def check_logs_for_slow_query(self, query_message: str = "") -> bool:
        """Check if any slow queries were detected.
        
        Args:
            query_message: Optional specific query message to search for
            
        Returns:
            True if slow query found, False otherwise
            
        Example:
            >>> monitor.check_logs_for_slow_query("Query executed")
            True
        """
        logs = self._get_server_logs()
        warn_logs = [log for log in logs if log["level"] == "WARN"]
        messages = self._get_log_messages(warn_logs)
        if query_message:
            return any("Slow query" in log_msg and query_message in log_msg for log_msg in messages)
        return any("Slow query" in log_msg for log_msg in messages)
    
    def _log_test_metrics(self, 
                         test_name: str,
                         status: str,
                         duration: float,
                         error: Optional[Exception] = None) -> None:
        """Log test execution metrics."""
        metrics = {
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "server_logs": self._get_server_logs(),
            "error": str(error) if error else None
        }
        
        log_file = self.log_dir / f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(metrics, f, indent=2)
            
        self.test_metrics[test_name] = metrics
        
    @contextmanager
    def monitor_test(self, test_name: str) -> Generator[None, None, None]:
        """Context manager to monitor a test execution.
        
        Args:
            test_name: Name of the test being monitored
        """
        execution = TestExecution(name=test_name)
        self.executions[test_name] = execution
        self.total_tests += 1
        self.current_test = test_name
        
        start_time = time.time()
        
        try:
            yield
            execution.status = "success"
        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            self.failed_tests += 1
            raise
        finally:
            duration = time.time() - start_time
            execution.duration = duration
            if duration > self.slow_threshold:
                self.slow_tests += 1
            execution.server_logs = self._get_server_logs()
            self._log_test_metrics(test_name, execution.status, duration, 
                                Exception(execution.error) if execution.error else None)
            self.current_test = None

    def get_server_logs(self) -> List[LogEntry]:
        """Get server logs for the current test.
        
        Returns:
            List of server log entries.
        """
        if not self.current_test:
            return []
        execution = self.executions.get(self.current_test)
        return execution.server_logs if execution else []

    def print_summary(self) -> None:
        """Print a summary of test execution results."""
        print("\nTest Execution Summary:")
        print(f"Total tests: {self.total_tests}")
        print(f"Failed tests: {self.failed_tests}")
        print(f"Slow tests: {self.slow_tests}")
        
        if self.failed_tests > 0:
            print("\nFailed Tests:")
            for name, execution in self.executions.items():
                if execution.status == "failed":
                    print(f"  {name}: {execution.error}")
        
        if self.slow_tests > 0:
            print("\nSlow Tests:")
            for name, execution in self.executions.items():
                if execution.duration > self.slow_threshold:
                    print(f"  {name}: {execution.duration:.2f}s")

    def get_test_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all test metrics."""
        return self.test_metrics

    def clear_metrics(self) -> None:
        """Clear all test metrics."""
        self.test_metrics.clear()
        self.executions.clear()
        self.total_tests = 0
        self.failed_tests = 0
        self.slow_tests = 0

    def get_failed_tests(self) -> List[str]:
        """Get list of failed test names."""
        return [name for name, execution in self.executions.items()
                if execution.status == "failed"]

    def get_slow_tests(self, threshold: float = 1.0) -> List[str]:
        """Get list of slow test names.
        
        Args:
            threshold: Duration threshold in seconds
            
        Returns:
            List of test names that exceeded the threshold
        """
        return [name for name, execution in self.executions.items()
                if execution.duration > threshold]

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test execution metrics.
        
        Returns:
            Dictionary containing test summary metrics
        """
        total_tests = len(self.test_metrics)
        failed_tests = sum(1 for m in self.test_metrics.values() if m["status"] == "failed")
        slow_tests = sum(1 for m in self.test_metrics.values() if m["duration"] > 1.0)
        
        return {
            "total_tests": total_tests,
            "failed_tests": failed_tests,
            "slow_tests": slow_tests,
            "failed_test_names": self.get_failed_tests(),
            "slow_test_names": self.get_slow_tests(),
            "tests": self.test_metrics
        } 