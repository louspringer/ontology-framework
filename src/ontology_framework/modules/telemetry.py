"""
Telemetry collection and analysis module for BFG9K validation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics that can be collected"""
    VALIDATION_TIME = "validation_time"
    SEMANTIC_ACCURACY = "semantic_accuracy"
    HIERARCHY_COMPLETENESS = "hierarchy_completeness"
    SHACL_COMPLIANCE = "shacl_compliance"
    RULE_COVERAGE = "rule_coverage"
    ERROR_RATE = "error_rate"

@dataclass
class TelemetryPoint:
    """A single telemetry data point"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]

class TelemetryCollector:
    """Collects and analyzes telemetry data"""
    
    def __init__(self):
        self.telemetry_data: List[TelemetryPoint] = []
        self.metric_thresholds = {
            MetricType.VALIDATION_TIME: 5.0,  # seconds
            MetricType.SEMANTIC_ACCURACY: 0.95,  # 95% accuracy
            MetricType.HIERARCHY_COMPLETENESS: 0.90,  # 90% complete
            MetricType.SHACL_COMPLIANCE: 0.95,  # 95% compliant
            MetricType.RULE_COVERAGE: 0.90,  # 90% coverage
            MetricType.ERROR_RATE: 0.05  # 5% error rate
        }
    
    def collect_metric(self, 
                      metric_type: MetricType,
                      value: float,
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """Collect a single metric"""
        point = TelemetryPoint(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.telemetry_data.append(point)
        logger.debug(f"Collected metric: {metric_type.value}={value}")
    
    def analyze_metrics(self) -> Dict[str, Any]:
        """Analyze collected metrics against thresholds"""
        analysis = {
            "status": "PASS",
            "violations": [],
            "summary": {}
        }
        
        for metric_type in MetricType:
            values = [p.value for p in self.telemetry_data 
                     if p.metric_type == metric_type]
            if not values:
                continue
                
            avg_value = sum(values) / len(values)
            threshold = self.metric_thresholds[metric_type]
            
            analysis["summary"][metric_type.value] = {
                "average": avg_value,
                "threshold": threshold,
                "status": "PASS" if avg_value >= threshold else "FAIL"
            }
            
            if avg_value < threshold:
                analysis["status"] = "FAIL"
                analysis["violations"].append({
                    "metric": metric_type.value,
                    "value": avg_value,
                    "threshold": threshold
                })
        
        return analysis
    
    def get_metric_history(self, metric_type: MetricType) -> List[Dict[str, Any]]:
        """Get historical data for a specific metric"""
        return [
            {
                "value": point.value,
                "timestamp": point.timestamp.isoformat(),
                "metadata": point.metadata
            }
            for point in self.telemetry_data
            if point.metric_type == metric_type
        ]
    
    def reset(self) -> None:
        """Reset all collected telemetry data"""
        self.telemetry_data = []
        logger.info("Telemetry data reset") 