"""
Maintenance prompts for the MCP module.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class MaintenancePrompts:
    """Class, for managing maintenance prompts and responses."""
    
    def __init__(self) -> None:
        """Initialize the maintenance prompts."""
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self.prompt_templates: Dict[str, str] = {
            "validation_error": "Validation, error detected: {error}. Please, analyze and, suggest fixes.",
            "performance_issue": "Performance, metric {metric} exceeds, threshold {threshold}. Analyze, impact.",
            "maintenance_required": "Maintenance, required for {component}. Current, status: {status}",
            "update_notification": "Update, available for {component}. Version {version} includes: {changes}"
        }
        
    def add_prompt(self, prompt_id: str, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add, a new, maintenance prompt.
        
        Args:
            prompt_id: Unique, identifier for the prompt, text: The, prompt text, context: Additional, context for the prompt Returns:
            The created prompt
        """
        prompt = {
            "id": prompt_id,
            "text": text,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        self.prompts[prompt_id] = prompt
        return prompt
        
    def get_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """Get, a prompt, by ID.
        
        Args:
            prompt_id: The, ID of, the prompt, to retrieve, Returns:
            The, requested prompt, Raises:
            KeyError: If, the prompt doesn't exist
        """
        if prompt_id not in self.prompts:
            raise KeyError(f"Prompt {prompt_id} not found")
        return self.prompts[prompt_id]
        
    def list_prompts(self, status: str = None) -> List[Dict[str, Any]]:
        """List, all prompts, optionally, filtered by, status.
        
        Args:
            status: Optional, status to, filter by Returns:
            List of prompts
        """
        if status is None:
            return list(self.prompts.values())
        return [p for p in self.prompts.values() if p["status"] == status]
        
    def update_prompt(self, prompt_id: str, response: str) -> Dict[str, Any]:
        """Update, a prompt, with a, response.
        
        Args:
            prompt_id: The, ID of, the prompt, to update, response: The, response text, Returns:
            The, updated prompt, Raises:
            KeyError: If, the prompt doesn't exist
        """
        prompt = self.get_prompt(prompt_id)
        prompt["response"] = response
        prompt["status"] = "completed"
        prompt["updated_at"] = datetime.now().isoformat()
        return prompt
        
    def add_template(self, template_id: str, template: str):
        """Add a new prompt template"""
        self.prompt_templates[template_id] = template
        
    def get_template(self, template_id: str) -> str:
        """Get, a prompt template by ID"""
        if template_id not in self.prompt_templates:
            raise KeyError(f"Template {template_id} not found")
        return self.prompt_templates[template_id]
        
    def generate_prompts(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate, prompts based on validation results"""
        try:
            prompts = []
            
            # Check for validation, errors
            if not validation_result.get("valid", True):
                error = validation_result.get("error", "Unknown error")
                prompts.append({
                    "type": "validation_error",
                    "prompt": self.prompt_templates["validation_error"].format(error=error),
                    "severity": "high"
                })
            
            # Check telemetry metrics
            telemetry = validation_result.get("telemetry", {})
            for metric, value in telemetry.items():
                if isinstance(value, (int, float)) and value > 0:
                    prompts.append({
                        "type": "performance_issue",
                        "prompt": self.prompt_templates["performance_issue"].format(
                            metric=metric,
                            threshold=value
                        ),
                        "severity": "medium"
                    })
            
            # Check maintenance status
            maintenance = validation_result.get("maintenance", {})
            for component, status in maintenance.items():
                prompts.append({
                    "type": "maintenance_required",
                    "prompt": self.prompt_templates["maintenance_required"].format(
                        component=component,
                        status=status
                    ),
                    "severity": "low"
                })
            
            # Check for updates
            updates = validation_result.get("updates", [])
            for update in updates:
                prompts.append({
                    "type": "update_notification",
                    "prompt": self.prompt_templates["update_notification"].format(
                        component=update.get("component", "Unknown"),
                        version=update.get("version", "Unknown"),
                        changes=update.get("changes", "No details")
                    ),
                    "severity": "info"
                })
            
            return {
                "success": True,
                "prompts": prompts
            }
            
        except Exception as e:
            logger.error(f"Error generating prompts: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate prompts: {str(e)}"
            } 