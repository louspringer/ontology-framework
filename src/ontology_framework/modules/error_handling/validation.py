from typing import Dict, Any, List, Callable
from .types import ValidationRule, ErrorSeverity, SecurityLevel, RiskLevel

class ValidationHandler:
    """Class for handling validation rules and checks."""
    
    def __init__(self) -> None:
        """Initialize validation handler with default rules."""
        self.validation_rules: Dict[ValidationRule, Callable[[Any], bool]] = {
            ValidationRule(
                description="Validate risk assessment",
                severity="HIGH",
                message_template="Risk validation failed: {message}",
                rule_type="risk"
            ): self._validate_risk,
            ValidationRule(
                description="Validate security measures",
                severity="HIGH",
                message_template="Security validation failed: {message}",
                rule_type="security"
            ): self._validate_security,
            ValidationRule(
                description="Validate sensitive data handling",
                severity="HIGH",
                message_template="Sensitive data validation failed: {message}",
                rule_type="sensitive_data"
            ): self._validate_sensitive_data
        }

    def validate(self, rule: ValidationRule, data: Any) -> bool:
        """Validate data against a specific rule."""
        if rule not in self.validation_rules:
            return False
        return bool(self.validation_rules[rule](data))

    def _validate_risk(self, data: Any) -> bool:
        """Validate risk level."""
        if not isinstance(data, dict):
            return False
        return 'risk_level' in data and isinstance(data['risk_level'], RiskLevel)

    def _validate_security(self, data: Any) -> bool:
        """Validate security level."""
        if not isinstance(data, dict):
            return False
        return 'security_level' in data and isinstance(data['security_level'], SecurityLevel)

    def _validate_sensitive_data(self, data: Any) -> bool:
        """Validate sensitive data handling."""
        if not isinstance(data, dict):
            return False
        return 'sensitive' in data and isinstance(data['sensitive'], bool) 