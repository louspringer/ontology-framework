"""
Maintenance prompts for the MCP module.
"""

from typing import Dict, Any, List
from datetime import datetime

class MaintenancePrompts:
    """Class for managing maintenance prompts and responses."""
    
    def __init__(self) -> None:
        """Initialize the maintenance prompts."""
        self.prompts: Dict[str, Dict[str, Any]] = {}
        
    def add_prompt(self, prompt_id: str, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new maintenance prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            text: The prompt text
            context: Additional context for the prompt
            
        Returns:
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
        """Get a prompt by ID.
        
        Args:
            prompt_id: The ID of the prompt to retrieve
            
        Returns:
            The requested prompt
            
        Raises:
            KeyError: If the prompt doesn't exist
        """
        if prompt_id not in self.prompts:
            raise KeyError(f"Prompt {prompt_id} not found")
        return self.prompts[prompt_id]
        
    def list_prompts(self, status: str = None) -> List[Dict[str, Any]]:
        """List all prompts, optionally filtered by status.
        
        Args:
            status: Optional status to filter by
            
        Returns:
            List of prompts
        """
        if status is None:
            return list(self.prompts.values())
        return [p for p in self.prompts.values() if p["status"] == status]
        
    def update_prompt(self, prompt_id: str, response: str) -> Dict[str, Any]:
        """Update a prompt with a response.
        
        Args:
            prompt_id: The ID of the prompt to update
            response: The response text
            
        Returns:
            The updated prompt
            
        Raises:
            KeyError: If the prompt doesn't exist
        """
        prompt = self.get_prompt(prompt_id)
        prompt["response"] = response
        prompt["status"] = "completed"
        prompt["updated_at"] = datetime.now().isoformat()
        return prompt 