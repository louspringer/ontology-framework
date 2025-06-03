# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

"""Compliance handler module for error handling."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .types import ComplianceLevel, ComplianceRule, ComplianceResult

class ComplianceHandler:
    """Handler for compliance-related operations."""
    
    def __init__(self):
        """Initialize compliance handler."""
        self.rules: Dict[str, ComplianceRule] = {}
        self.results: List[ComplianceResult] = []
        self.current_level = ComplianceLevel.STANDARD
    
    def add_rule(self, rule: ComplianceRule) -> None:
        """Add a compliance rule."""
        self.rules[rule.id] = rule
    
    def remove_rule(self, rule_id: str) -> None:
        """Remove a compliance rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
    
    def set_compliance_level(self, level: ComplianceLevel) -> None:
        """Set the compliance level."""
        self.current_level = level
    
    def check_compliance(self, data: Dict[str, Any]) -> ComplianceResult:
        """Check compliance against current rules."""
        result = ComplianceResult(
            timestamp=datetime.utcnow(),
            level=self.current_level,
            is_compliant=True,
            violations=[]
        )
        
        for rule in self.rules.values():
            if not rule.validate(data):
                result.is_compliant = False
                result.violations.append({
                    "rule_id": rule.id,
                    "description": rule.description,
                    "severity": rule.severity
                })
        
        self.results.append(result)
        return result
    
    def get_compliance_history(self) -> List[ComplianceResult]:
        """Get compliance check history."""
        return self.results
    
    def get_active_rules(self) -> Dict[str, ComplianceRule]:
        """Get currently active compliance rules."""
        return self.rules
    
    def clear_history(self) -> None:
        """Clear compliance check history."""
        self.results = []
    
    def export_compliance_report(self) -> Dict[str, Any]:
        """Export compliance report."""
        return {
            "level": self.current_level.value,
            "total_rules": len(self.rules),
            "total_checks": len(self.results),
            "latest_result": self.results[-1] if self.results else None,
            "rules": {
                rule_id: {
                    "description": rule.description,
                    "severity": rule.severity,
                    "enabled": rule.enabled
                }
                for rule_id, rule in self.rules.items()
            }
        } 