"""
Configuration for the MCP module.
"""

from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import timedelta

@dataclass
class MaintenanceConfig:
    """Configuration for maintenance operations."""
    
    # Validation settings
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    validation_interval: timedelta = field(default=timedelta(hours=24))
    
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