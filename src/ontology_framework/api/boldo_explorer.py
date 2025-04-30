import requests
from typing import Dict, List, Optional, Any, Union, cast
from ..exceptions import BoldoAPIError, AuthenticationError, APIRequestError, ResourceNotFoundError

class BoldoAPIExplorer:
    """Class for exploring and interacting with the Boldo API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize the explorer.
        
        Args:
            base_url: Base URL for the Boldo API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        self.session.headers["Content-Type"] = "application/json"
            
    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Get a resource by ID.
        
        Args:
            resource_id: ID of the resource to retrieve
            
        Returns:
            The resource data
            
        Raises:
            AuthenticationError: If authentication fails
            ResourceNotFoundError: If the resource doesn't exist
            APIRequestError: If the API request fails
        """
        url = f"{self.base_url}/resources/{resource_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            elif e.response.status_code == 404:
                raise ResourceNotFoundError(f"Resource {resource_id} not found")
            else:
                raise APIRequestError(f"API request failed: {str(e)}", e.response.status_code)
        except Exception as e:
            raise BoldoAPIError(f"Unexpected error: {str(e)}")
            
    def search_resources(self, query: str) -> List[Dict[str, Any]]:
        """Search for resources.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching resources
            
        Raises:
            AuthenticationError: If authentication fails
            APIRequestError: If the API request fails
        """
        url = f"{self.base_url}/search"
        try:
            response = self.session.get(url, params={'q': query})
            response.raise_for_status()
            return cast(List[Dict[str, Any]], response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            else:
                raise APIRequestError(f"API request failed: {str(e)}", e.response.status_code)
        except Exception as e:
            raise BoldoAPIError(f"Unexpected error: {str(e)}")
            
    def create_resource(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource.
        
        Args:
            data: Resource data to create
            
        Returns:
            The created resource
            
        Raises:
            AuthenticationError: If authentication fails
            APIRequestError: If the API request fails
        """
        url = f"{self.base_url}/resources"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            else:
                raise APIRequestError(f"API request failed: {str(e)}", e.response.status_code)
        except Exception as e:
            raise BoldoAPIError(f"Unexpected error: {str(e)}")
            
    def update_resource(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a resource.
        
        Args:
            resource_id: ID of the resource to update
            data: Updated resource data
            
        Returns:
            The updated resource
            
        Raises:
            AuthenticationError: If authentication fails
            ResourceNotFoundError: If the resource doesn't exist
            APIRequestError: If the API request fails
        """
        url = f"{self.base_url}/resources/{resource_id}"
        try:
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return cast(Dict[str, Any], response.json())
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            elif e.response.status_code == 404:
                raise ResourceNotFoundError(f"Resource {resource_id} not found")
            else:
                raise APIRequestError(f"API request failed: {str(e)}", e.response.status_code)
        except Exception as e:
            raise BoldoAPIError(f"Unexpected error: {str(e)}")
            
    def delete_resource(self, resource_id: str) -> None:
        """Delete a resource.
        
        Args:
            resource_id: ID of the resource to delete
            
        Raises:
            AuthenticationError: If authentication fails
            ResourceNotFoundError: If the resource doesn't exist
            APIRequestError: If the API request fails
        """
        url = f"{self.base_url}/resources/{resource_id}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            elif e.response.status_code == 404:
                raise ResourceNotFoundError(f"Resource {resource_id} not found")
            else:
                raise APIRequestError(f"API request failed: {str(e)}", e.response.status_code)
        except Exception as e:
            raise BoldoAPIError(f"Unexpected error: {str(e)}")

    def get_ontologies(self) -> list[dict]:
        """Get all ontologies."""
        url = f"{self.base_url}/ontologies"
        response = self.session.request('GET', url)
        response.raise_for_status()
        return response.json()

    def get_ontology(self, ontology_id: str) -> dict:
        """Get a single ontology by ID."""
        url = f"{self.base_url}/ontologies/{ontology_id}"
        response = self.session.request('GET', url)
        response.raise_for_status()
        return response.json()

    def search_ontologies(self, query: str) -> list[dict]:
        """Search ontologies by query string."""
        url = f"{self.base_url}/ontologies/search"
        response = self.session.request('GET', url, params={'q': query})
        response.raise_for_status()
        return response.json()