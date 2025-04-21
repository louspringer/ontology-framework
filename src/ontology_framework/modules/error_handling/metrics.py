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
            "max_error_rate": 0.1,     # 10%
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

    def update_error_matrix(self, error_type: str, occurred: bool) -> None:
        """Update error occurrence matrix."""
        if error_type not in self.metrics["error_matrix"]:
            self.metrics["error_matrix"][error_type] = {"occurrences": 0, "total": 0}
        
        self.metrics["error_matrix"][error_type]["total"] += 1
        if occurred:
            self.metrics["error_matrix"][error_type]["occurrences"] += 1

    def calculate_derived_metrics(self) -> None:
        """Calculate derived metrics from raw data."""
        total_errors = sum(self.metrics["error_counts"].values())
        total_checks = sum(m["total"] for m in self.metrics["error_matrix"].values())
        
        if total_checks > 0:
            self.metrics["derived_metrics"]["error_rate"] = total_errors / total_checks
            self.metrics["derived_metrics"]["success_rate"] = 1 - self.metrics["derived_metrics"]["error_rate"]
            
            if self.metrics["derived_metrics"]["error_rate"] > self.thresholds["max_error_rate"]:
                self.logger.warning("Error rate exceeds threshold")
            
            if self.metrics["derived_metrics"]["success_rate"] < self.thresholds["min_success_rate"]:
                self.logger.warning("Success rate below threshold")

        # Calculate mean detection time
        all_times = [t for times in self.metrics["detection_times"].values() for t in times]
        if all_times:
            self.metrics["derived_metrics"]["mean_detection_time"] = sum(all_times) / len(all_times)

    def get_metrics_report(self) -> MetricsReport:
        """Get current metrics with thresholds."""
        return {
            "metrics": self.metrics,
            "thresholds": self.thresholds,
            "timestamp": datetime.now().isoformat()
        } 