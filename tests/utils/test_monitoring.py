#!/usr/bin/env python3
"""Test monitoring utilities."""

import logging
import json
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import requests
from contextlib import contextmanager

class TestMonitor:
    """Monitor test execution and server logs."""
    
    def __init__(self, 
                 log_dir: Union[str, Path] = "logs",
                 graphdb_url: str = "http://localhost:7200"):
        """Initialize test monitor.
        
        Args:
            log_dir: Directory for test logs
            graphdb_url: GraphDB server URL
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.graphdb_url = graphdb_url
        self.logger = logging.getLogger(__name__)
        self.test_start_time: Optional[float] = None
        self.test_metrics: Dict[str, Any] = {}
        
    def _get_server_logs(self) -> List[Dict[str, Any]]:
        """Get recent server logs from GraphDB."""
        try:
            response = requests.get(
                f"{self.graphdb_url}/rest/monitor/logs",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get server logs: {e}")
            return []
            
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
    def monitor_test(self, test_name: str):
        """Monitor a test execution.
        
        Args:
            test_name: Name of the test being monitored
        """
        self.test_start_time = time.time()
        try:
            yield
            duration = time.time() - self.test_start_time
            self._log_test_metrics(test_name, "success", duration)
        except Exception as e:
            duration = time.time() - self.test_start_time
            self._log_test_metrics(test_name, "failure", duration, e)
            raise
        finally:
            self.test_start_time = None
            
    def get_test_metrics(self) -> Dict[str, Any]:
        """Get all test metrics."""
        return self.test_metrics
        
    def clear_metrics(self) -> None:
        """Clear stored test metrics."""
        self.test_metrics.clear()
        
    def get_failed_tests(self) -> List[Dict[str, Any]]:
        """Get metrics for failed tests."""
        return [
            metrics for metrics in self.test_metrics.values()
            if metrics["status"] == "failure"
        ]
        
    def get_slow_tests(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """Get metrics for tests that exceeded duration threshold.
        
        Args:
            threshold: Duration threshold in seconds
        """
        return [
            metrics for metrics in self.test_metrics.values()
            if metrics["duration"] > threshold
        ]
        
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test execution."""
        total_tests = len(self.test_metrics)
        failed_tests = len(self.get_failed_tests())
        slow_tests = len(self.get_slow_tests())
        
        return {
            "total_tests": total_tests,
            "failed_tests": failed_tests,
            "slow_tests": slow_tests,
            "success_rate": (total_tests - failed_tests) / total_tests if total_tests > 0 else 0,
            "average_duration": sum(m["duration"] for m in self.test_metrics.values()) / total_tests if total_tests > 0 else 0
        } 