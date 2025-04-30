"""
Enhanced validation telemetry collection and analysis.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
import numpy as np
from .hypercube_analysis import HypercubeAnalyzer
from .bfg9k_targeting import BFG9KTargeter

@dataclass
class ValidationMetrics:
    """Metrics for validation performance."""
    semantic_accuracy: float
    response_time: float
    confidence: float
    validation_success: bool
    error_rate: float
    throughput: float
    resource_usage: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PatternMetrics:
    """Metrics for pattern detection."""
    pattern_type: str
    frequency: float
    confidence: float
    impact: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationTelemetry:
    """Collects and analyzes validation telemetry."""
    
    def __init__(self, hypercube_analyzer: HypercubeAnalyzer, bfg9k_targeter: BFG9KTargeter):
        self.analyzer = hypercube_analyzer
        self.targeter = bfg9k_targeter
        self.metrics_history: List[ValidationMetrics] = field(default_factory=list)
        self.pattern_history: List[PatternMetrics] = field(default_factory=list)
        self.logger: logging.Logger = field(init=False)
        self.telemetry: Dict[str, Any] = {
            "validation_metrics": [],
            "patterns": [],
            "performance": {},
            "errors": {}
        }

    def __post_init__(self):
        """Initialize logger after instance creation"""
        self.logger = logging.getLogger(__name__)
    
    def collect_metrics(self, validation_result: Dict[str, Any]) -> None:
        """Collect metrics from validation results."""
        try:
            metrics = ValidationMetrics(
                semantic_accuracy=validation_result.get("semantic_accuracy", 0.0),
                response_time=validation_result.get("response_time", 0.0),
                confidence=validation_result.get("confidence", 0.0),
                validation_success=validation_result.get("success", False),
                error_rate=validation_result.get("error_rate", 0.0),
                throughput=validation_result.get("throughput", 0.0),
                resource_usage=validation_result.get("resource_usage", 0.0)
            )
            self.metrics_history.append(metrics)
            self.telemetry["validation_metrics"].append(vars(metrics))
            self.logger.info(f"Collected validation metrics: {metrics}")
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
    
    def detect_patterns(self) -> None:
        """Detect patterns in validation metrics."""
        try:
            if len(self.metrics_history) < 2:
                return

            # Analyze error rate patterns
            error_rates = [m.error_rate for m in self.metrics_history[-10:]]
            if np.std(error_rates) > 0.1:  # High variance in error rates
                pattern = PatternMetrics(
                    pattern_type="error_rate_variance",
                    frequency=len([r for r in error_rates if r > np.mean(error_rates)]) / len(error_rates),
                    confidence=0.8,
                    impact=np.mean(error_rates)
                )
                self.pattern_history.append(pattern)
                self.telemetry["patterns"].append(vars(pattern))

            # Analyze response time patterns
            response_times = [m.response_time for m in self.metrics_history[-10:]]
            if np.mean(response_times) > 1.0:  # High average response time
                pattern = PatternMetrics(
                    pattern_type="high_response_time",
                    frequency=len([r for r in response_times if r > 1.0]) / len(response_times),
                    confidence=0.9,
                    impact=np.mean(response_times)
                )
                self.pattern_history.append(pattern)
                self.telemetry["patterns"].append(vars(pattern))

            self.logger.info(f"Detected {len(self.pattern_history)} patterns")
        except Exception as e:
            self.logger.error(f"Error detecting patterns: {e}")
    
    def analyze_performance(self) -> Dict[str, float]:
        """Analyze overall validation performance."""
        try:
            if not self.metrics_history:
                return {}

            recent_metrics = self.metrics_history[-10:]
            performance = {
                "avg_accuracy": np.mean([m.semantic_accuracy for m in recent_metrics]),
                "avg_response_time": np.mean([m.response_time for m in recent_metrics]),
                "avg_confidence": np.mean([m.confidence for m in recent_metrics]),
                "success_rate": sum(1 for m in recent_metrics if m.validation_success) / len(recent_metrics)
            }
            self.telemetry["performance"] = performance
            self.logger.info(f"Performance analysis: {performance}")
            return performance
        except Exception as e:
            self.logger.error(f"Error analyzing performance: {e}")
            return {}
    
    def analyze_errors(self) -> Dict[str, Any]:
        """Analyze validation errors."""
        try:
            if not self.metrics_history:
                return {}

            recent_metrics = self.metrics_history[-10:]
            error_stats = {
                "total_errors": sum(m.error_rate > 0 for m in recent_metrics),
                "avg_error_rate": np.mean([m.error_rate for m in recent_metrics]),
                "max_error_rate": max(m.error_rate for m in recent_metrics),
                "error_trend": "increasing" if self._is_error_trend_increasing() else "stable"
            }
            self.telemetry["errors"] = error_stats
            self.logger.info(f"Error analysis: {error_stats}")
            return error_stats
        except Exception as e:
            self.logger.error(f"Error analyzing errors: {e}")
            return {}
    
    def _is_error_trend_increasing(self) -> bool:
        """Check if error rate trend is increasing."""
        if len(self.metrics_history) < 5:
            return False
        recent_errors = [m.error_rate for m in self.metrics_history[-5:]]
        return np.polyfit(range(len(recent_errors)), recent_errors, 1)[0] > 0
    
    def update_telemetry(self, validation_result: Dict[str, Any]) -> None:
        """Update telemetry with new validation results."""
        try:
            self.collect_metrics(validation_result)
            self.detect_patterns()
            self.analyze_performance()
            self.analyze_errors()
            self.logger.info("Telemetry updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating telemetry: {e}")
    
    def get_telemetry(self) -> Dict[str, Any]:
        """Get current telemetry data."""
        return self.telemetry 