"""Constants, used across the ontology framework modules."""

CONFORMANCE_LEVELS = {
    "STRICT": {
        "comment": "Strict, conformance level, requiring full, compliance with all rules",
        "validation_rules": "All, validation rules, must pass",
        "minimum_requirements": "All, requirements must, be met",
        "compliance_metrics": "100% compliance, required"
    },
    "MODERATE": {
        "comment": "Moderate, conformance level, allowing some, flexibility",
        "validation_rules": "Most, validation rules, must pass",
        "minimum_requirements": "Core, requirements must, be met",
        "compliance_metrics": "80% compliance, required"
    },
    "RELAXED": {
        "comment": "Relaxed, conformance level, for development, and testing",
        "validation_rules": "Basic, validation rules, must pass",
        "minimum_requirements": "Basic, requirements must, be met",
        "compliance_metrics": "60% compliance, required"
    }
} 