# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

from typing import Dict, Any, TypedDict
from datetime import datetime
import logging

class MetricsReport(TypedDict):
    metrics: Dict[str, Dict[str, Any]]
    thresholds: Dict[str, float]
    timestamp: str

class MetricsHandler:
    """Class for handling error metrics and monitoring."""
    
    def __init__(self) -> None:
        """Initialize metrics handler with default thresholds."""
        self.metrics: Dict[str, Dict[str, Any]] = {
            "error_counts": {},
            "detection_times": {},
            "error_matrix": {},
            "derived_metrics": {
                "mean_detection_time": 0.0,
                "error_rate": 0.0,
                "success_rate": 0.0
            }
        }
        self.thresholds: Dict[str, float] = {
            "max_detection_time": 1.0,  # seconds
            "max_error_rate": 0.1,      # 10%
            "min_success_rate": 0.9     # 90%
        }
        self.logger = logging.getLogger(__name__)

    def update_metrics(self, error_type: str, detection_time: float) -> None:
        """Update metrics for a specific error type."""
        if error_type not in self.metrics["error_counts"]:
            self.metrics["error_counts"][error_type] = 0
            self.metrics["detection_times"][error_type] = []
        
        self.metrics["error_counts"][error_type] += 1
        self.metrics["detection_times"][error_type].append(detection_time)
        
        if detection_time > self.thresholds["max_detection_time"]:
            self.logger.warning(f"Detection time {detection_time}s exceeds threshold for {error_type}")

    def update_error_matrix(self, error_type: str, is_resolved: bool) -> None:
        """Update error matrix with resolution status."""
        if error_type not in self.metrics["error_matrix"]:
            self.metrics["error_matrix"][error_type] = {
                "resolved": 0,
                "unresolved": 0
            }
        
        if is_resolved:
            self.metrics["error_matrix"][error_type]["resolved"] += 1
        else:
            self.metrics["error_matrix"][error_type]["unresolved"] += 1

    def calculate_derived_metrics(self) -> None:
        """Calculate derived metrics from raw data."""
        total_detection_time = 0.0
        total_errors = 0
        
        for error_type in self.metrics["detection_times"]:
            times = self.metrics["detection_times"][error_type]
            if times:
                total_detection_time += sum(times)
                total_errors += len(times)
        
        if total_errors > 0:
            self.metrics["derived_metrics"]["mean_detection_time"] = total_detection_time / total_errors
        
        total_attempts = sum(
            self.metrics["error_matrix"][error_type]["resolved"] +
            self.metrics["error_matrix"][error_type]["unresolved"]
            for error_type in self.metrics["error_matrix"]
        )
        
        if total_attempts > 0:
            total_resolved = sum(
                self.metrics["error_matrix"][error_type]["resolved"]
                for error_type in self.metrics["error_matrix"]
            )
            self.metrics["derived_metrics"]["error_rate"] = total_errors / total_attempts
            self.metrics["derived_metrics"]["success_rate"] = total_resolved / total_attempts

    def get_report(self) -> MetricsReport:
        """Generate a metrics report."""
        return {
            "metrics": self.metrics,
            "thresholds": self.thresholds,
            "timestamp": datetime.now().isoformat()
        } 