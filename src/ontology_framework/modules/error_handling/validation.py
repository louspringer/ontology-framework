from typing import Dict, Any, List, Callable, Optional, Union, Tuple
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, SH
from ...ontology_types import (
    ValidationRule, ErrorSeverity, SecurityLevel, RiskLevel,
    ComplianceLevel
)
from ..validation.bfg9k_pattern import BFG9KPattern
from datetime import datetime
import json
import csv
import io
import re
from .types import ErrorType

class ValidationHandler:
    """Handler for validation rules and history tracking."""
    
    class CustomRule:
        """Custom validation rule."""
        def __init__(self, name: str, message: Optional[str] = None, priority: str = "LOW",
                     target: str = "data", validator: str = "custom_validator"):
            self.name = name
            self.message = message if message is not None else f"Custom validation rule: {name}"
            self.priority = priority
            self.target = target
            self.validator = validator
            self.validator_func: Optional[Callable[[Dict[str, Any]], bool]] = None  # Store the actual validator function

    def __init__(self):
        """Initialize validation handler."""
        self._validation_history = []
        self._validation_thresholds: Dict[str, Tuple[float, Callable[[float], bool]]] = {}
        self._custom_rules = {}
        self._validation_rules = {
            ValidationRule.RISK: self._validate_risk,
            ValidationRule.SECURITY: self._validate_security,
            ValidationRule.COMPLIANCE: self._validate_compliance,
            ValidationRule.PERFORMANCE: self._validate_performance,
            ValidationRule.SENSITIVE_DATA: self._validate_sensitive_data,
            ValidationRule.RELIABILITY: self._validate_reliability,
            ValidationRule.AVAILABILITY: self._validate_availability,
            ValidationRule.SCALABILITY: self._validate_scalability,
            ValidationRule.MAINTAINABILITY: self._validate_maintainability,
            ValidationRule.SEVERITY: self._validate_severity,
            ValidationRule.STEP_ORDER: self._validate_step_order,
            ValidationRule.SPORE: self._validate_spore,
            ValidationRule.SEMANTIC: self._validate_semantic,
            ValidationRule.SYNTAX: self._validate_syntax,
            ValidationRule.MATRIX: self._validate_matrix,
            ValidationRule.BFG9K: self._validate_bfg9k_pattern
        }
        self._graph = Graph()
        self._load_shacl_shapes()
        self.validation_rules = {
            ValidationRule.MATRIX: {
                "required_fields": ["matrix_id", "matrix_type", "matrix_level"],
                "field_types": {
                    "matrix_id": str,
                    "matrix_type": str,
                    "matrix_level": str
                },
                "constraints": {
                    "matrix_id": r"^[A-Za-z0-9_-]+$",
                    "matrix_type": ["access", "risk", "compliance"],
                    "matrix_level": ["low", "medium", "high", "critical"]
                }
            },
            ValidationRule.SEMANTIC: {
                "required_fields": ["ontology_id", "ontology_type"],
                "field_types": {
                    "ontology_id": str,
                    "ontology_type": str
                },
                "constraints": {
                    "ontology_id": r"^[A-Za-z0-9_-]+$",
                    "ontology_type": ["owl", "rdfs", "skos"]
                }
            },
            ValidationRule.SPORE: {
                "required_fields": ["pattern_id", "pattern_type"],
                "field_types": {
                    "pattern_id": str,
                    "pattern_type": str
                },
                "constraints": {
                    "pattern_id": r"^[A-Za-z0-9_-]+$",
                    "pattern_type": ["structural", "behavioral", "creational"]
                }
            }
        }

    def _load_shacl_shapes(self):
        """Load SHACL shapes from guidance.ttl"""
        self._graph.parse("guidance.ttl", format="turtle")

    def validate(self, rule: ValidationRule, data: Dict[str, Any], conformance_level: Optional[str] = None) -> bool:
        """Validate data against a rule."""
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
            
        if rule not in self._validation_rules and rule not in self._custom_rules:
            raise ValueError(f"Rule {rule} not found in validation rules")
            
        if conformance_level and conformance_level not in ["STRICT", "LENIENT", "MODERATE"]:
            raise ValueError(f"Invalid conformance level: {conformance_level}")
            
        validator = self._validation_rules.get(rule) or self._custom_rules.get(rule)
        result = validator(data)
        error_message = None
        
        # Check against threshold if configured
        rule_name = rule.value if isinstance(rule, ValidationRule) else rule.name
        if rule_name in self._validation_thresholds:
            threshold, check = self._validation_thresholds[rule_name]
            threshold_result = check(result) and result >= threshold
            if not threshold_result:
                error_message = f"Failed threshold check: value {result} does not meet threshold {threshold}"
            result = threshold_result
        
        # Get validation-specific error message if validation failed
        if not result and not error_message:
            if hasattr(validator, '__name__'):
                error_message = f"Validation failed for rule {validator.__name__}"
            else:
                error_message = "Validation failed"
                
        self._log_validation_attempt(rule, data, result, error_message)
        return result

    def _convert_to_rdf(self, data: Dict[str, Any]) -> Graph:
        """Convert dictionary data to RDF graph for validation."""
        g = Graph()
        ex = Namespace("http://example.org/")
        
        # Create BFG9K pattern instance
        pattern = ex[data['ontology_id']]
        g.add((pattern, RDF.type, ex.BFG9KPattern))
        
        # Add basic properties
        g.add((pattern, ex.ontologyId, data['ontology_id']))
        g.add((pattern, ex.validationType, data['validation_type']))
        g.add((pattern, ex.securityLevel, data['security_level']))
        g.add((pattern, ex.patternType, data['pattern_type']))
        
        # Add pattern elements
        for element in data['pattern_elements']:
            g.add((pattern, ex.hasPatternElement, element))
            
        # Add constraints
        constraints = ex[f"{data['ontology_id']}_constraints"]
        g.add((pattern, ex.hasConstraints, constraints))
        g.add((constraints, ex.minScore, data['constraints']['min_score']))
        
        # Add relationships
        for rel in data['relationships']:
            g.add((pattern, ex.hasRelationship, rel))
        
        # Add LLM config
        llm_config = ex[f"{data['ontology_id']}_llm_config"]
        g.add((pattern, ex.hasLLMConfig, llm_config))
        g.add((llm_config, ex.modelType, data['llm_config']['model_type']))
        g.add((llm_config, ex.temperature, data['llm_config']['temperature']))
        g.add((llm_config, ex.maxTokens, data['llm_config']['max_tokens']))
        
        return g

    def _validate_with_shacl(self, data_graph: Graph) -> bool:
        """Validate data graph against SHACL shapes."""
        from pyshacl import validate
        
        conforms, _, _ = validate(data_graph, shacl_graph=self._graph)
        return conforms

    def get_validation_history(self) -> List[Dict[str, Any]]:
        """Get the validation history."""
        return self._validation_history.copy()

    def _validate_matrix(self, data: Dict[str, Any]) -> bool:
        """Validate matrix data."""
        required_fields = ['security_level', 'authentication_method', 'authorization_level', 'data_classification']
        if not all(field in data for field in required_fields):
            return False
            
        if not isinstance(data['security_level'], SecurityLevel):
            return False
            
        if not isinstance(data['authentication_method'], str) or not data['authentication_method']:
            return False
            
        if not isinstance(data['authorization_level'], str) or not data['authorization_level']:
            return False
            
        if not isinstance(data['data_classification'], str) or not data['data_classification']:
            return False
            
        return True

    def _validate_semantic(self, data: Dict[str, Any]) -> bool:
        """Validate semantic data."""
        required_fields = ['ontology_id', 'validation_type']
        if not all(field in data for field in required_fields):
            return False
            
        if not isinstance(data['ontology_id'], str) or not data['ontology_id']:
            return False
            
        if not isinstance(data['validation_type'], str) or not data['validation_type']:
            return False
            
        return True

    def _validate_syntax(self, data: Dict[str, Any]) -> bool:
        """Validate syntax data."""
        required_fields = ['syntax_type', 'content', 'format']
        if not all(field in data for field in required_fields):
            return False
            
        if not isinstance(data['syntax_type'], str) or not data['syntax_type']:
            return False
            
        if not isinstance(data['content'], str) or not data['content']:
            return False
            
        if not isinstance(data['format'], str) or not data['format']:
            return False
            
        return True

    def _validate_compliance(self, data: Dict[str, Any]) -> bool:
        """Validate compliance data.
        
        Args:
            data: A dictionary containing compliance data with the following structure:
                {
                    'compliance_level': str,  # The compliance level (e.g., 'HIGH', 'MEDIUM', 'LOW')
                    'status': str,  # The current status (e.g., 'COMPLIANT', 'NON_COMPLIANT')
                    'requirements': List[str],  # List of compliance requirements
                    'review_date': str,  # Optional, format: YYYY-MM-DD
                    'evidence': Dict[str, str]  # Optional, mapping of requirement IDs to evidence
                }
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        required_fields = ['compliance_level', 'status', 'requirements']
        
        # Check required fields exist and are not None
        if not all(field in data and data[field] is not None for field in required_fields):
            return False
            
        # Validate compliance_level is a non-empty string
        if not isinstance(data['compliance_level'], str) or not data['compliance_level'].strip():
            return False
            
        # Validate status is a non-empty string
        if not isinstance(data['status'], str) or not data['status'].strip():
            return False
            
        # Validate requirements is a non-empty list of strings
        if not isinstance(data['requirements'], list) or not data['requirements']:
            return False
        if not all(isinstance(req, str) and req.strip() for req in data['requirements']):
            return False
            
        # Validate optional review_date if present
        if 'review_date' in data:
            if not isinstance(data['review_date'], str):
                return False
            try:
                datetime.strptime(data['review_date'], '%Y-%m-%d')
            except ValueError:
                return False
                
        # Validate optional evidence if present
        if 'evidence' in data:
            if not isinstance(data['evidence'], dict):
                return False
            if not all(isinstance(k, str) and isinstance(v, str) for k, v in data['evidence'].items()):
                return False
                
        return True

    def _validate_performance(self, data: Dict[str, Any]) -> bool:
        """Validate performance data.
        
        Args:
            data: Dictionary containing performance metrics and thresholds
                Required fields:
                - metrics: Dict[str, float] - Performance metrics (e.g., latency, throughput)
                - thresholds: Dict[str, float] - Acceptable thresholds for each metric
                Optional fields:
                - resource_usage: Dict[str, float] - Resource utilization (0-1 range)
                - timestamp: str - ISO format timestamp of measurement
                
        Returns:
            bool: True if validation passes, False otherwise
        """
        # Check required fields
        required_fields = ['metrics', 'thresholds']
        if not all(field in data for field in required_fields):
            return False
            
        # Validate metrics
        if not isinstance(data['metrics'], dict):
            return False
        for metric, value in data['metrics'].items():
            if not isinstance(value, (int, float)):
                return False
                
        # Validate thresholds
        if not isinstance(data['thresholds'], dict):
            return False
        for threshold, value in data['thresholds'].items():
            if not isinstance(value, (int, float)):
                return False
                
        # Validate optional resource usage
        if 'resource_usage' in data:
            if not isinstance(data['resource_usage'], dict):
                return False
            for resource, usage in data['resource_usage'].items():
                if not isinstance(usage, (int, float)) or not 0 <= usage <= 1:
                    return False
                    
        # Validate optional timestamp
        if 'timestamp' in data:
            if not isinstance(data['timestamp'], str):
                return False
            try:
                datetime.fromisoformat(data['timestamp'])
            except ValueError:
                return False
        
        return True

    def _validate_spore(self, data: Dict[str, Any]) -> bool:
        """Validate SPORE pattern data."""
        required_fields = ['pattern_type', 'pattern_elements', 'constraints']
        if not all(field in data for field in required_fields):
            return False
            
        if not isinstance(data['pattern_type'], str) or not data['pattern_type']:
            return False
            
        if not isinstance(data['pattern_elements'], list) or not data['pattern_elements']:
            return False
            
        if not isinstance(data['constraints'], dict) or not data['constraints']:
            return False
            
        return True

    def _validate_individual_type(self, data: Dict[str, Any]) -> bool:
        """Validate individual type data."""
        required_fields = ['individual_uri', 'type_assertions', 'property_values']
        if not all(field in data for field in required_fields):
            return False
            
        if not isinstance(data['individual_uri'], str) or not data['individual_uri']:
            return False
            
        if not isinstance(data['type_assertions'], list) or not data['type_assertions']:
            return False
            
        if not isinstance(data['property_values'], dict):
            return False
            
        return True

    def _log_validation_attempt(self, rule: ValidationRule, data: Any, result: bool, message: Optional[str] = None) -> None:
        """Log validation attempt with enhanced metadata."""
        timestamp = datetime.now().isoformat()
        entry = {
            "rule": rule.value,
            "message": rule.message,
            "priority": rule.priority,
            "target": rule.target,
            "validator": rule.validator,
            "data": str(data),
            "result": result,
            "timestamp": timestamp
        }
        if message:
            entry["error_message"] = message
        self._validation_history.append(entry)

    def _get_security_level(self, rule: ValidationRule) -> str:
        """Get security level for a validation rule."""
        security_levels = {
            ValidationRule.MATRIX: "HIGH",
            ValidationRule.SEMANTIC: "MEDIUM",
            ValidationRule.SYNTAX: "MEDIUM",
            ValidationRule.COMPLIANCE: "HIGH",
            ValidationRule.PERFORMANCE: "LOW"
        }
        return security_levels.get(rule, "MEDIUM")

    def _get_validation_requirements(self, rule: ValidationRule) -> Dict[str, Any]:
        """Get validation requirements for a rule."""
        return {
            'required_fields': self._get_required_fields(rule),
            'field_types': self._get_field_types(rule),
            'constraints': self._get_constraints(rule),
            'security_requirements': self._get_security_requirements(rule)
        }

    def _get_field_types(self, rule: ValidationRule) -> Dict[str, Any]:
        """Get field types for a rule."""
        return {
            ValidationRule.MATRIX: {
                'security_level': SecurityLevel,
                'authentication_method': str,
                'authorization_level': str,
                'data_classification': str
            },
            ValidationRule.SEMANTIC: {
                'ontology_id': str,
                'validation_type': str,
                'security_level': SecurityLevel,
                'data_format': str
            }
        }.get(rule, {})

    def _get_required_fields(self, rule: ValidationRule) -> Dict[str, Any]:
        """Get required fields for a validation rule."""
        field_requirements: Dict[ValidationRule, Dict[str, Any]] = {
            ValidationRule.MATRIX: {
                'security_level': SecurityLevel,
                'authentication_method': str,
                'authorization_level': str,
                'data_classification': str
            },
            ValidationRule.SEMANTIC: {
                'ontology_id': str,
                'validation_type': str,
                'security_level': SecurityLevel,
                'data_format': str
            }
        }
        return field_requirements.get(rule, {})

    def _get_constraints(self, rule: ValidationRule) -> Dict[str, Any]:
        """Get constraints for a rule."""
        constraints: Dict[ValidationRule, Dict[str, Any]] = {
            ValidationRule.MATRIX: {
                'min_password_length': 12,
                'required_encryption': True,
                'audit_trail_required': True
            },
            ValidationRule.SEMANTIC: {
                'min_similarity_score': 0.85,
                'required_phases': ['initialization', 'exact_match', 'similarity_match', 'llm_selection', 'final_validation']
            }
        }
        return constraints.get(rule, {})

    def _get_security_requirements(self, rule: ValidationRule) -> Dict[str, Any]:
        """Get security requirements for a rule."""
        requirements: Dict[ValidationRule, Dict[str, Any]] = {
            ValidationRule.MATRIX: {
                'encryption_required': True,
                'access_control': 'STRICT',
                'audit_level': 'HIGH'
            },
            ValidationRule.SEMANTIC: {
                'encryption_required': True,
                'access_control': 'STRICT',
                'audit_level': 'HIGH',
                'authentication_required': True
            }
        }
        return requirements.get(rule, {})

    def _validate_bfg9k_pattern(self, validation_data: Dict[str, Any]) -> bool:
        """Validate data using BFG9K pattern.
        
        Args:
            validation_data: Dictionary containing validation metadata and data
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Initialize BFG9K pattern validator
            bfg9k = BFG9KPattern(self._graph)
            
            # Extract data for BFG9K validation
            data = {
                "ontology_id": f"validation_{validation_data['timestamp']}",
                "validation_type": validation_data.get("conformance_level", "STRICT"),
                "security_level": "HIGH",  # Default to high security
                "pattern_type": "BFG9K",
                "pattern_elements": [validation_data["rule"]],
                "constraints": {
                    "min_score": 0.85,
                    "max_iterations": 100
                },
                "relationships": ["validates", "depends_on"],
                "llm_config": {
                    "model_type": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
            
            # Validate using BFG9K pattern
            result = bfg9k.validate(data, validation_data.get("conformance_level", "STRICT"))
            return result.is_valid
            
        except Exception as e:
            return False

    def filter_validation_history(self, rule: Optional[Union[ValidationRule, str]] = None,
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None,
                                result: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Filter validation history by criteria.
        
        Args:
            rule: Optional rule to filter by
            start_date: Optional start date (ISO format)
            end_date: Optional end date (ISO format) 
            result: Optional result to filter by
            
        Returns:
            List of filtered history entries
        """
        filtered = self._validation_history.copy()
        
        if rule:
            rule_str = rule.value if isinstance(rule, ValidationRule) else str(rule)
            filtered = [h for h in filtered if h["rule"] == rule_str]
            
        if start_date:
            filtered = [h for h in filtered if h["timestamp"] >= start_date]
            
        if end_date:
            filtered = [h for h in filtered if h["timestamp"] <= end_date]
            
        if result is not None:
            filtered = [h for h in filtered if h["result"] == result]
            
        return filtered

    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics."""
        total = len(self._validation_history)
        if total == 0:
            return {
                "total_validations": 0,
                "success_rate": 0.0,
                "failure_rate": 0.0,
                "by_rule": {},
                "by_priority": {},
                "by_target": {}
            }
            
        successes = sum(1 for entry in self._validation_history if entry["result"])
        
        # Calculate statistics by rule
        by_rule = {}
        for entry in self._validation_history:
            rule = entry["rule"]
            if rule not in by_rule:
                by_rule[rule] = {"total": 0, "successes": 0}
            by_rule[rule]["total"] += 1
            if entry["result"]:
                by_rule[rule]["successes"] += 1
                
        # Calculate statistics by priority
        by_priority = {}
        for entry in self._validation_history:
            priority = entry.get("priority", "MEDIUM")
            if priority not in by_priority:
                by_priority[priority] = {"total": 0, "successes": 0}
            by_priority[priority]["total"] += 1
            if entry["result"]:
                by_priority[priority]["successes"] += 1
                
        # Calculate statistics by target
        by_target = {}
        for entry in self._validation_history:
            target = entry.get("target", "data")
            if target not in by_target:
                by_target[target] = {"total": 0, "successes": 0}
            by_target[target]["total"] += 1
            if entry["result"]:
                by_target[target]["successes"] += 1
                
        return {
            "total_validations": total,
            "success_rate": successes / total,
            "failure_rate": (total - successes) / total,
            "by_rule": by_rule,
            "by_priority": by_priority,
            "by_target": by_target
        }

    def add_custom_rule(self, name: str, validator_func: Callable[[Dict[str, Any]], bool],
                       message: Optional[str] = None, priority: str = "MEDIUM", target: str = "data") -> None:
        """
        Add a custom validation rule.
        
        Args:
            name: Name of the custom rule
            validator_func: Function that validates data
            message: Validation message
            priority: Rule priority level
            target: Target data type
        """
        custom_rule = self.CustomRule(name=name, message=message, priority=priority,
                                    target=target, validator=validator_func.__name__)
        custom_rule.validator_func = validator_func  # Store the validator function
        self._custom_rules[name] = custom_rule

    def configure_validation_threshold(self, rule: Union[ValidationRule, 'ValidationHandler.CustomRule'],
                                    threshold: float,
                                    check_func: Optional[Callable[[float], bool]] = None) -> None:
        """
        Configure validation threshold for a rule.
        
        Args:
            rule: ValidationRule or CustomRule to configure threshold for
            threshold: Threshold value between 0 and 1
            check_func: Optional function to check threshold value (default: greater than or equal)
        
        Raises:
            ValueError: If threshold not between 0 and 1
            TypeError: If rule is not ValidationRule or CustomRule
        """
        if not (isinstance(rule, ValidationRule) or isinstance(rule, self.CustomRule)):
            raise TypeError("Rule must be a ValidationRule enum or CustomRule")
            
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
            
        # Default check function is greater than or equal
        if check_func is None:
            check_func = lambda x: x >= threshold
            
        # Use rule name as key for both ValidationRule and CustomRule
        rule_name = rule.value if isinstance(rule, ValidationRule) else rule.name
        self._validation_thresholds[rule_name] = (threshold, check_func)

    def export_validation_history(self, format: str = "json") -> str:
        """Export validation history in specified format."""
        if format not in ["json", "csv"]:
            raise ValueError("Format must be 'json' or 'csv'")
            
        if format == "json":
            return json.dumps(self._validation_history, indent=2)
        else:
            if not self._validation_history:
                return ""
                
            # Get all possible fields
            fields = set()
            for entry in self._validation_history:
                fields.update(entry.keys())
                
            # Create CSV header
            header = list(fields)
            rows = [header]
            
            # Add data rows
            for entry in self._validation_history:
                row = [entry.get(field, "") for field in header]
                rows.append(row)
                
            # Convert to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(rows)
            return output.getvalue()

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        stats = self.get_validation_statistics()
        
        report = {
            "summary": {
                "total_validations": stats["total_validations"],
                "success_rate": stats["success_rate"],
                "failure_rate": stats["failure_rate"]
            },
            "by_rule": stats["by_rule"],
            "by_priority": stats["by_priority"],
            "by_target": stats["by_target"],
            "recent_failures": [],
            "threshold_violations": []
        }
        
        # Add recent failures
        recent_failures = self.filter_validation_history(result=False)
        if recent_failures:
            report["recent_failures"] = recent_failures[-5:]  # Last 5 failures
            
        # Check threshold violations
        for rule_name, (threshold, check) in self._validation_thresholds.items():
            rule_stats = stats["by_rule"].get(rule_name, {"total": 0, "successes": 0})
            if rule_stats["total"] > 0:
                success_rate = rule_stats["successes"] / rule_stats["total"]
                if not check(success_rate):
                    report["threshold_violations"].append({
                        "rule": rule_name,
                        "threshold": threshold,
                        "actual_rate": success_rate
                    })
                    
        return report

    def _validate_risk(self, data: Dict[str, Any]) -> bool:
        """Validate risk data."""
        required_fields = ['risk_level', 'risk_type', 'impact', 'probability']
        if not all(field in data for field in required_fields):
            return False
        if not isinstance(data['risk_level'], RiskLevel):
            return False
        return True

    def _validate_security(self, data: Dict[str, Any]) -> bool:
        """Validate security data."""
        required_fields = ['security_level', 'security_controls', 'threat_model']
        if not all(field in data for field in required_fields):
            return False
        if not isinstance(data['security_level'], SecurityLevel):
            return False
        return True

    def _validate_sensitive_data(self, data: Dict[str, Any]) -> bool:
        """Validate sensitive data."""
        required_fields = ['data_type', 'classification', 'encryption_level']
        if not all(field in data for field in required_fields):
            return False
        return True

    def _validate_reliability(self, data: Dict[str, Any]) -> bool:
        """Validate reliability data."""
        required_fields = ['reliability_score', 'failure_rate', 'mtbf']
        if not all(field in data for field in required_fields):
            return False
        return True

    def _validate_availability(self, data: Dict[str, Any]) -> bool:
        """Validate availability data."""
        required_fields = ['availability_percentage', 'downtime', 'recovery_time']
        if not all(field in data for field in required_fields):
            return False
        return True

    def _validate_scalability(self, data: Dict[str, Any]) -> bool:
        """Validate scalability data."""
        required_fields = ['scaling_factor', 'load_capacity', 'resource_efficiency']
        if not all(field in data for field in required_fields):
            return False
        return True

    def _validate_maintainability(self, data: Dict[str, Any]) -> bool:
        """Validate maintainability data."""
        required_fields = ['maintainability_index', 'code_complexity', 'documentation_coverage']
        if not all(field in data for field in required_fields):
            return False
        return True

    def _validate_severity(self, data: Dict[str, Any]) -> bool:
        """Validate severity data."""
        required_fields = ['severity_level', 'impact_scope', 'urgency']
        if not all(field in data for field in required_fields):
            return False
        if not isinstance(data['severity_level'], ErrorSeverity):
            return False
        return True

    def _validate_step_order(self, data: Dict[str, Any]) -> bool:
        """Validate step order data."""
        required_fields = ['steps', 'dependencies', 'execution_order']
        if not all(field in data for field in required_fields):
            return False
        if not isinstance(data['steps'], list) or not data['steps']:
            return False
        return True

__all__ = ['ValidationHandler'] 