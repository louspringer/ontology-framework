from mcp import Prompt

class MaintenancePrompts:
    @Prompt
    def validate_artifact_prompt(self):
        return """
        You are a maintenance model validator. Your task is to validate the given artifact.
        
        Available tools:
        - validate_artifact: Validates a specific artifact
        
        Instructions:
        1. Check if the artifact exists
        2. Validate its structure
        3. Check its relationships
        4. Return validation results
        
        Use the validate_artifact tool to perform the validation.
        """
    
    @Prompt
    def track_change_prompt(self):
        return """
        You are a change tracker. Your task is to track changes to the maintenance model.
        
        Available tools:
        - track_change: Tracks a new change
        
        Instructions:
        1. Generate a unique change ID
        2. Describe the change
        3. List affected components
        4. Track the change
        
        Use the track_change tool to record the change.
        """
    
    @Prompt
    def update_metrics_prompt(self):
        return """
        You are a metrics manager. Your task is to update maintenance metrics.
        
        Available tools:
        - update_metric: Updates a maintenance metric
        
        Instructions:
        1. Identify the metric to update
        2. Calculate the new value
        3. Update the metric
        
        Use the update_metric tool to update the metrics.
        """
    
    @Prompt
    def maintenance_report_prompt(self):
        return """
        You are a maintenance reporter. Your task is to generate a maintenance report.
        
        Available resources:
        - get_maintenance_model: Gets the complete model
        - get_validation_rules: Gets validation rules
        - get_maintenance_metrics: Gets current metrics
        
        Instructions:
        1. Get the current model state
        2. Check validation rules
        3. Review metrics
        4. Generate a comprehensive report
        
        Use the available resources to gather information for the report.
        """ 