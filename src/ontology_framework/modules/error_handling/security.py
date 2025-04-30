from typing import Dict, Any, Optional, Callable
from enum import Enum
import logging
from datetime import datetime
from .types import SecurityLevel, ValidationRuleType

class SecurityValidationResult:
    """Class representing the result of a security validation."""
    
    def __init__(self, is_valid: bool, message: str, details: Optional[Dict[str, Any]] = None):
        self.is_valid = is_valid
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class SecurityHandler:
    """Class for handling security validation rules using ValidationRuleType enum."""
    
    def __init__(self) -> None:
        """Initialize security handler with default rules mapped to ValidationRuleType."""
        self.logger = logging.getLogger(__name__)
        self.validation_rules: Dict[ValidationRuleType, Callable[[Any], SecurityValidationResult]] = {
            ValidationRuleType.SENSITIVE_DATA: self._validate_sensitive_data,
            ValidationRuleType.ACCESS_CONTROL: self._validate_access_control,
            ValidationRuleType.ENCRYPTION: self._validate_encryption
        }
        
    def validate(self, rule: ValidationRuleType, data: Any) -> SecurityValidationResult:
        """
        Validate data against a specific security rule.
        
        Args:
            rule (ValidationRuleType): The type of security validation to perform
            data (Any): The data to validate
            
        Returns:
            SecurityValidationResult: The result of the validation
        """
        if rule not in self.validation_rules:
            return SecurityValidationResult(
                False,
                f"Unknown security validation rule: {rule}"
            )
        
        try:
            return self.validation_rules[rule](data)
        except Exception as e:
            self.logger.error(f"Security validation failed: {str(e)}")
            return SecurityValidationResult(
                False,
                f"Security validation error: {str(e)}"
            )
    
    def _validate_sensitive_data(self, data: Any) -> SecurityValidationResult:
        """Validate sensitive data handling."""
        if not isinstance(data, dict):
            return SecurityValidationResult(
                False,
                "Invalid data format for sensitive data validation"
            )
        
        required_fields = ['encrypted', 'access_control', 'retention_period']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return SecurityValidationResult(
                False,
                f"Missing required fields for sensitive data: {', '.join(missing_fields)}"
            )
        
        if not isinstance(data['encrypted'], bool):
            return SecurityValidationResult(
                False,
                "Encryption status must be a boolean"
            )
        
        if not isinstance(data['access_control'], SecurityLevel):
            return SecurityValidationResult(
                False,
                "Invalid access control level"
            )
        
        return SecurityValidationResult(
            True,
            "Sensitive data validation passed",
            {
                'encrypted': data['encrypted'],
                'access_control': data['access_control'].value,
                'retention_period': data['retention_period']
            }
        )
    
    def _validate_access_control(self, data: Any) -> SecurityValidationResult:
        """Validate access control measures."""
        if not isinstance(data, dict):
            return SecurityValidationResult(
                False,
                "Invalid data format for access control validation"
            )
        
        required_fields = ['level', 'permissions', 'audit_enabled']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return SecurityValidationResult(
                False,
                f"Missing required fields for access control: {', '.join(missing_fields)}"
            )
        
        if not isinstance(data['level'], SecurityLevel):
            return SecurityValidationResult(
                False,
                "Invalid security level"
            )
        
        if not isinstance(data['permissions'], list):
            return SecurityValidationResult(
                False,
                "Permissions must be a list"
            )
        
        if not isinstance(data['audit_enabled'], bool):
            return SecurityValidationResult(
                False,
                "Audit enabled must be a boolean"
            )
        
        return SecurityValidationResult(
            True,
            "Access control validation passed",
            {
                'level': data['level'].value,
                'permissions': data['permissions'],
                'audit_enabled': data['audit_enabled']
            }
        )
    
    def _validate_encryption(self, data: Any) -> SecurityValidationResult:
        """Validate encryption measures."""
        if not isinstance(data, dict):
            return SecurityValidationResult(
                False,
                "Invalid data format for encryption validation"
            )
        
        required_fields = ['algorithm', 'key_size', 'mode', 'key_rotation']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return SecurityValidationResult(
                False,
                f"Missing required fields for encryption: {', '.join(missing_fields)}"
            )
        
        valid_algorithms = ['AES', 'RSA', 'ECC']
        if data['algorithm'] not in valid_algorithms:
            return SecurityValidationResult(
                False,
                f"Invalid encryption algorithm. Must be one of: {', '.join(valid_algorithms)}"
            )
        
        if not isinstance(data['key_size'], int) or data['key_size'] < 128:
            return SecurityValidationResult(
                False,
                "Invalid key size. Must be at least 128 bits"
            )
        
        if not isinstance(data['key_rotation'], int) or data['key_rotation'] < 1:
            return SecurityValidationResult(
                False,
                "Invalid key rotation period. Must be at least 1 day"
            )
        
        return SecurityValidationResult(
            True,
            "Encryption validation passed",
            {
                'algorithm': data['algorithm'],
                'key_size': data['key_size'],
                'mode': data['mode'],
                'key_rotation': data['key_rotation']
            }
        ) 