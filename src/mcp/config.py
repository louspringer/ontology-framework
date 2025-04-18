from mcp import Config

class MaintenanceConfig(Config):
    # Server configuration
    HOST = "localhost"
    PORT = 8000
    
    # Model configuration
    MODEL_PATH = "models/project_maintenance.ttl"
    MODEL_FORMAT = "turtle"
    
    # Resource configuration
    RESOURCES = [
        "get_maintenance_model",
        "get_validation_rules",
        "get_maintenance_metrics"
    ]
    
    # Tool configuration
    TOOLS = [
        "validate_artifact",
        "track_change",
        "update_metric"
    ]
    
    # Prompt configuration
    PROMPTS = [
        "validate_artifact_prompt",
        "track_change_prompt",
        "update_metrics_prompt",
        "maintenance_report_prompt"
    ]
    
    # Validation configuration
    VALIDATION_RULES = {
        "ontology": "maint:OntologyValidation",
        "change_tracking": "maint:ChangeTrackingValidation",
        "reference": "maint:ReferenceValidation"
    }
    
    # Metrics configuration
    METRICS = {
        "validation_coverage": "maint:ValidationCoverage",
        "change_tracking_completeness": "maint:ChangeTrackingCompleteness"
    }
    
    # Schedule configuration
    SCHEDULES = {
        "validation": "DAILY",
        "change_tracking": "REAL_TIME"
    } 