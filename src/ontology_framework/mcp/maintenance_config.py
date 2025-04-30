"""
Configuration for the MCP module.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import timedelta
import logging
from pathlib import Path
from .hypercube_analysis import HypercubeAnalyzer
from .bfg9k_targeting import BFG9KTargeter
from .validation_telemetry import ValidationTelemetry

logger = logging.getLogger(__name__)

@dataclass
class MaintenanceConfig:
    """Configuration for maintenance operations."""
    
    # Core settings from guidance.ttl
    conformance_level: str = "STRICT"
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    ontology_path: Path = field(default=Path("models/project_maintenance.ttl"))
    
    # Validation settings
    validation_interval: timedelta = field(default=timedelta(hours=24))
    validation_strategy: str = "SimilarityMatch"
    validation_path: Dict[str, Any] = field(default_factory=lambda: {
        "start_node": "ValidationRule",
        "intermediate_node": "ValidationPattern",
        "end_node": "ValidationTarget"
    })
    
    # Quality settings
    quality_threshold: float = 0.85
    required_metadata: List[str] = field(default_factory=lambda: [
        "hasMessage", "hasPriority", "hasTarget", "hasValidator"
    ])
    
    # Metrics settings
    metric_thresholds: Dict[str, float] = field(default_factory=dict)
    metric_update_interval: timedelta = field(default=timedelta(hours=1))
    
    # Reporting settings
    report_format: str = "markdown"
    report_interval: timedelta = field(default=timedelta(days=7))
    report_directory: str = "reports"
    
    # Model settings
    model_backup_interval: timedelta = field(default=timedelta(days=1))
    model_backup_directory: str = "backups"
    max_backup_count: int = 30
    
    # Hypercube settings
    hypercube_dimensions: Dict[str, Dict[str, float]] = field(default_factory=dict)
    trajectory_threshold: float = 0.1
    
    # BFG9K settings
    target_detection_threshold: float = 0.1
    elimination_confidence_threshold: float = 0.8
    
    def update(self, **kwargs: Any) -> None:
        """Update configuration settings.
        
        Args:
            **kwargs: Configuration key-value pairs to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")
                
    def get_validation_rule(self, rule_id: str) -> Dict[str, Any]:
        """Get a validation rule by ID.
        
        Args:
            rule_id: The ID of the validation rule
            
        Returns:
            The validation rule configuration
            
        Raises:
            KeyError: If the rule doesn't exist
        """
        if rule_id not in self.validation_rules:
            raise KeyError(f"Validation rule {rule_id} not found")
        return self.validation_rules[rule_id]
        
    def get_metric_threshold(self, metric_id: str) -> float:
        """Get a metric threshold by ID.
        
        Args:
            metric_id: The ID of the metric
            
        Returns:
            The metric threshold value
            
        Raises:
            KeyError: If the metric doesn't exist
        """
        if metric_id not in self.metric_thresholds:
            raise KeyError(f"Metric {metric_id} not found")
        return self.metric_thresholds[metric_id]

    def validate_config(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration against validation results."""
        try:
            # Check if validation result has required fields
            required_fields = ["target", "ordinance", "telemetry"]
            for field in required_fields:
                if field not in validation_result:
                    return {
                        "valid": False,
                        "error": f"Missing required field: {field}"
                    }
            
            # Validate ordinance structure
            ordinance = validation_result["ordinance"]
            if not isinstance(ordinance, dict):
                return {
                    "valid": False,
                    "error": "Ordinance must be a dictionary"
                }
            
            if "rules" not in ordinance or "config" not in ordinance:
                return {
                    "valid": False,
                    "error": "Ordinance must contain 'rules' and 'config'"
                }
            
            # Validate rules
            rules = ordinance["rules"]
            if not isinstance(rules, list):
                return {
                    "valid": False,
                    "error": "Rules must be a list"
                }
            
            # Validate that rules are strings
            for rule in rules:
                if not isinstance(rule, str):
                    return {
                        "valid": False,
                        "error": "Each rule must be a string"
                    }
            
            # Validate config
            config = ordinance["config"]
            if not isinstance(config, dict):
                return {
                    "valid": False,
                    "error": "Config must be a dictionary"
                }
            
            # Validate config structure
            required_config_fields = ["precision", "recall", "timeout"]
            for field in required_config_fields:
                if field not in config:
                    return {
                        "valid": False,
                        "error": f"Config missing required field: {field}"
                    }
                if not isinstance(config[field], (int, float)):
                    return {
                        "valid": False,
                        "error": f"Config field {field} must be a number"
                    }
            
            # Validate telemetry structure
            telemetry = validation_result["telemetry"]
            if not isinstance(telemetry, dict):
                return {
                    "valid": False,
                    "error": "Telemetry must be a dictionary"
                }
            
            # All checks passed
            return {
                "valid": True,
                "message": "Configuration validation successful"
            }
            
        except Exception as e:
            logger.error(f"Configuration validation error: {str(e)}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            } 