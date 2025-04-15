import logging
import json
import os
import requests
from typing import Dict, List, Optional, Any, Union, cast
from ..exceptions import BoldoAPIError
from ..logging_config import OntologyFrameworkLogger
from ..config import get_api_token

# Configure basic logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class BoldoAPIExplorer:
    """Client for interacting with the Boldo API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Boldo API explorer.
        
        Args:
            api_key (Optional[str]): API key for authentication. If not provided, will attempt to get from environment.
        """
        self.logger = OntologyFrameworkLogger.get_logger("boldo_explorer")
        self.base_url = "https://api.boldo.com/v1"
        self.session = requests.Session()
        self.api_key = api_key or self._get_api_key_from_env()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _get_api_key_from_env(self) -> str:
        """Get the Boldo API key from environment variables.
        
        Returns:
            The API key as a string.
            
        Raises:
            BoldoAPIError: If the API key cannot be retrieved.
        """
        try:
            api_key = get_api_token()
            if not api_key:
                raise BoldoAPIError("BOLDO_API_TOKEN environment variable not set")
            return api_key
        except Exception as e:
            raise BoldoAPIError(f"Failed to get API key: {str(e)}")
    
    def _handle_request(self, method: str, endpoint: str, **kwargs) -> Union[Dict, List[Dict]]:
        """Handle API requests with proper error handling.
        
        Args:
            method: HTTP method (get, post, put, delete)
            endpoint: API endpoint
            **kwargs: Additional arguments for the request
            
        Returns:
            Response data as a dictionary or list of dictionaries
            
        Raises:
            BoldoAPIError: If the request fails
        """
        try:
            response = getattr(self.session, method)(f"{self.base_url}/{endpoint}", **kwargs)
            response.raise_for_status()
            return response.json().get("data", {})
        except requests.exceptions.RequestException as e:
            if response.status_code == 404:
                raise BoldoAPIError(f"Resource not found: {endpoint}")
            raise BoldoAPIError(f"API request failed: {str(e)}")
        except Exception as e:
            raise BoldoAPIError(f"Unexpected error: {str(e)}")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get all available models.
        
        Returns:
            List of model dictionaries
        """
        try:
            self.logger.info("Getting all models")
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            self.logger.error(f"Failed to get models: {str(e)}")
            raise BoldoAPIError(f"Failed to get models: {str(e)}")
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get a specific model by ID.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Model dictionary
        """
        try:
            self.logger.info(f"Getting model {model_id}")
            response = self.session.get(f"{self.base_url}/models/{model_id}")
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise BoldoAPIError(f"Model not found: {model_id}")
            raise BoldoAPIError(f"Failed to get model: {str(e)}")
        except Exception as e:
            self.logger.error(f"Failed to get model: {str(e)}")
            raise BoldoAPIError(f"Failed to get model: {str(e)}")
    
    def create_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new model.
        
        Args:
            data: Model data
            
        Returns:
            Created model dictionary
        """
        try:
            self.logger.info("Creating new model")
            response = self.session.post(f"{self.base_url}/models", json=data)
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            self.logger.error(f"Failed to create model: {str(e)}")
            raise BoldoAPIError(f"Failed to create model: {str(e)}")
    
    def update_model(self, model_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing model.
        
        Args:
            model_id: ID of the model
            data: Updated model data
            
        Returns:
            Updated model dictionary
        """
        try:
            self.logger.info(f"Updating model {model_id}")
            response = self.session.put(f"{self.base_url}/models/{model_id}", json=data)
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise BoldoAPIError(f"Model not found: {model_id}")
            raise BoldoAPIError(f"Failed to update model: {str(e)}")
        except Exception as e:
            self.logger.error(f"Failed to update model: {str(e)}")
            raise BoldoAPIError(f"Failed to update model: {str(e)}")
    
    def delete_model(self, model_id: str) -> None:
        """Delete a model.
        
        Args:
            model_id: ID of the model
        """
        try:
            self.logger.info(f"Deleting model {model_id}")
            response = self.session.delete(f"{self.base_url}/models/{model_id}")
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise BoldoAPIError(f"Model not found: {model_id}")
            raise BoldoAPIError(f"Failed to delete model: {str(e)}")
        except Exception as e:
            self.logger.error(f"Failed to delete model: {str(e)}")
            raise BoldoAPIError(f"Failed to delete model: {str(e)}")
    
    def explore_endpoints(self) -> Dict[str, Any]:
        """Explore available API endpoints.
        
        Returns:
            Dict containing available endpoints
        """
        try:
            self.logger.info("Exploring API endpoints")
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            self.logger.error(f"Failed to explore endpoints: {str(e)}")
            raise BoldoAPIError(f"Failed to explore endpoints: {str(e)}")
    
    def list_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        """List resources of a specific type.
        
        Args:
            resource_type: Type of resource to list
            
        Returns:
            List of resource dictionaries
        """
        try:
            self.logger.info(f"Listing {resource_type} resources")
            response = self.session.get(f"{self.base_url}/{resource_type}")
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            self.logger.error(f"Failed to list {resource_type} resources: {str(e)}")
            raise BoldoAPIError(f"Failed to list {resource_type} resources: {str(e)}")
    
    def get_resource_by_id(self, resource_type: str, resource_id: Union[str, int]) -> Dict[str, Any]:
        """Get a specific resource by ID.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            
        Returns:
            Resource dictionary
        """
        try:
            self.logger.info(f"Getting {resource_type} resource {resource_id}")
            response = self.session.get(f"{self.base_url}/{resource_type}/{resource_id}")
            # Check if response itself has status_code (for mocked responses)
            if getattr(response, 'status_code', None) == 404:
                raise BoldoAPIError(f"Resource not found: {resource_type}/{resource_id}")
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.HTTPError as e:
            # Check if error response has status_code
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                raise BoldoAPIError(f"Resource not found: {resource_type}/{resource_id}")
            raise BoldoAPIError(str(e))
        except Exception as e:
            self.logger.error(f"Failed to get resource: {str(e)}")
            raise BoldoAPIError(str(e))
    
    def create_resource(self, resource_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource.
        
        Args:
            resource_type: Type of resource to create
            data: Resource data
            
        Returns:
            Created resource dictionary
        """
        try:
            self.logger.info(f"Creating {resource_type} resource")
            response = self.session.post(f"{self.base_url}/{resource_type}", json=data)
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            self.logger.error(f"Failed to create resource: {str(e)}")
            raise BoldoAPIError(f"Failed to create resource: {str(e)}")
    
    def update_resource(self, resource_type: str, resource_id: Union[str, int], 
                       data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing resource.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            data: Updated resource data
            
        Returns:
            Updated resource dictionary
        """
        try:
            self.logger.info(f"Updating {resource_type} resource {resource_id}")
            response = self.session.put(f"{self.base_url}/{resource_type}/{resource_id}", json=data)
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            self.logger.error(f"Failed to update resource: {str(e)}")
            raise BoldoAPIError(f"Failed to update resource: {str(e)}")
    
    def delete_resource(self, resource_type: str, resource_id: Union[str, int]) -> None:
        """Delete a resource.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
        """
        try:
            self.logger.info(f"Deleting {resource_type} resource {resource_id}")
            response = self.session.delete(f"{self.base_url}/{resource_type}/{resource_id}")
            response.raise_for_status()
        except Exception as e:
            self.logger.error(f"Failed to delete resource: {str(e)}")
            raise BoldoAPIError(f"Failed to delete resource: {str(e)}") 