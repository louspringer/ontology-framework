import os
import sys
import logging
import json
from typing import Optional, Dict, Any, List, Union, Set, cast
import requests
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BoldoAPIError(Exception):
    """Custom exception for Boldo API errors."""
    pass

class BoldoAPIExplorer:
    """A secure explorer for the Boldo API."""
    
    BASE_URL = "https://app.boldo.io/api/alpha/"
    FAILURE_LOG_FILE = "failed_endpoints.log"
    MAX_FAILURES = 3
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Boldo API explorer.
        
        Args:
            api_key: Optional API key. If not provided, will attempt to get from 1Password.
        """
        self.api_key = api_key or self._get_api_key_from_1password()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self._endpoint_cache: Dict[str, Any] = {}
        self._failure_count: int = 0
        self._failed_endpoints: Set[str] = set()
    
    def _get_api_key_from_1password(self) -> str:
        """Securely retrieve the API key from 1Password.
        
        Returns:
            str: The API key
            
        Raises:
            RuntimeError: If the API key cannot be retrieved
        """
        try:
            # Use op CLI to get the credential
            import subprocess
            result = subprocess.run(
                ["op", "read", "op://Private/Baldo API Key/credential"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to retrieve API key from 1Password: {e}")
            raise RuntimeError("Could not retrieve API key from 1Password")
        except FileNotFoundError:
            logger.error("1Password CLI (op) not found")
            raise RuntimeError("1Password CLI (op) is required but not installed")
    
    def _log_failed_endpoint(self, endpoint: str, status_code: int, error_msg: str) -> None:
        """Log a failed endpoint to the failure log file.
        
        Args:
            endpoint: The endpoint that failed
            status_code: HTTP status code
            error_msg: Error message
        """
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} - {endpoint} - Status: {status_code} - Error: {error_msg}\n"
        
        with open(self.FAILURE_LOG_FILE, 'a') as f:
            f.write(log_entry)
            
        self._failed_endpoints.add(endpoint)
        self._failure_count += 1
        
        if self._failure_count >= self.MAX_FAILURES:
            logger.error(f"Maximum number of failures ({self.MAX_FAILURES}) reached. Exiting.")
            logger.error(f"Failed endpoints: {', '.join(self._failed_endpoints)}")
            sys.exit(1)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Union[Dict[str, Any], str]:
        """Make an authenticated request to the Boldo API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Dict containing the JSON response or str if response is not JSON
            
        Raises:
            BoldoAPIError: If the request fails
        """
        url = f"{self.BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(method, url, **kwargs)
            
            # Log the full response for debugging
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            logger.debug(f"Response content: {response.text[:1000]}...")  # First 1000 chars
            
            # Specifically handle 404 responses
            if response.status_code == 404:
                logger.warning(f"Endpoint not found (404): {url}")
                logger.warning(f"Response content: {response.text}")
                self._log_failed_endpoint(endpoint, 404, "Endpoint not found")
                response.raise_for_status()
            
            response.raise_for_status()
            
            # Try to parse as JSON, but don't fail if it's not JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus: {e.response.status_code}"
                error_msg += f"\nHeaders: {dict(e.response.headers)}"
                error_msg += f"\nResponse: {e.response.text}"
                # Log 404s at warning level, others at error
                if e.response.status_code == 404:
                    logger.warning(error_msg)
                else:
                    logger.error(error_msg)
                    
                self._log_failed_endpoint(endpoint, e.response.status_code, error_msg)
            else:
                logger.error(error_msg)
                self._log_failed_endpoint(endpoint, status_code or 0, error_msg)
                
            raise BoldoAPIError(error_msg)
    
    def explore_endpoints(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Explore available API endpoints.
        
        Args:
            force_refresh: If True, ignore cache and fetch fresh data
            
        Returns:
            Dict containing information about available endpoints
            
        Note:
            This method assumes the root endpoint returns JSON. If it doesn't,
            the type checker will flag an error, but the runtime behavior is handled
            by _make_request.
        """
        if not force_refresh and self._endpoint_cache:
            logger.info("Using cached endpoint data")
            return self._endpoint_cache
            
        logger.info("Fetching fresh endpoint data")
        # Cast to Dict[str, Any] since we know the root endpoint returns JSON
        self._endpoint_cache = cast(Dict[str, Any], self._make_request("GET", ""))
        return self._endpoint_cache
    
    def get_resource(self, resource_path: str) -> Dict[str, Any]:
        """Get a specific resource from the API.
        
        Args:
            resource_path: Path to the resource
            
        Returns:
            Dict containing the resource data
            
        Note:
            This method assumes the resource endpoint returns JSON. If it doesn't,
            the type checker will flag an error, but the runtime behavior is handled
            by _make_request.
        """
        return cast(Dict[str, Any], self._make_request("GET", resource_path))
    
    def list_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        """List all resources of a specific type.
        
        Args:
            resource_type: Type of resource to list
            
        Returns:
            List of resource dictionaries
            
        Note:
            This method handles both list and single resource responses,
            ensuring the return type is always List[Dict[str, Any]].
        """
        response = self._make_request("GET", resource_type)
        if isinstance(response, list):
            return response
        # Cast to Dict[str, Any] since we know it's a single resource
        return [cast(Dict[str, Any], response)]
    
    def get_resource_by_id(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """Get a specific resource by its ID.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            
        Returns:
            Dict containing the resource data
            
        Note:
            This method assumes the resource endpoint returns JSON. If it doesn't,
            the type checker will flag an error, but the runtime behavior is handled
            by _make_request.
        """
        return cast(Dict[str, Any], self._make_request("GET", f"{resource_type}/{resource_id}"))
    
    def create_resource(self, resource_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource.
        
        Args:
            resource_type: Type of resource to create
            data: Resource data
            
        Returns:
            Dict containing the created resource
            
        Note:
            This method assumes the resource endpoint returns JSON. If it doesn't,
            the type checker will flag an error, but the runtime behavior is handled
            by _make_request.
        """
        return cast(Dict[str, Any], self._make_request("POST", resource_type, json=data))
    
    def update_resource(self, resource_type: str, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing resource.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            data: Updated resource data
            
        Returns:
            Dict containing the updated resource
            
        Note:
            This method assumes the resource endpoint returns JSON. If it doesn't,
            the type checker will flag an error, but the runtime behavior is handled
            by _make_request.
        """
        return cast(Dict[str, Any], self._make_request("PUT", f"{resource_type}/{resource_id}", json=data))
    
    def delete_resource(self, resource_type: str, resource_id: str) -> None:
        """Delete a resource.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
        """
        self._make_request("DELETE", f"{resource_type}/{resource_id}")

def main():
    """Main entry point for the Boldo API explorer."""
    try:
        explorer = BoldoAPIExplorer()
        
        # Common OpenAPI/Swagger documentation paths
        doc_paths = [
            "",  # root
            "/docs",
            "/swagger",
            "/swagger.json",
            "/swagger.yaml",
            "/openapi.json",
            "/openapi.yaml",
            "/api-docs",
            "/api-docs/swagger.json",
            "/api-docs/swagger.yaml",
            "/v3/api-docs",
            "/v3/api-docs/swagger.json",
            "/v3/api-docs/swagger.yaml",
            "/.well-known/openapi",
            "/.well-known/openapi.json",
            "/.well-known/openapi.yaml",
            "/api/v1/docs",
            "/api/v2/docs",
            "/api/v3/docs",
            "/api/v1/swagger",
            "/api/v2/swagger",
            "/api/v3/swagger",
            "/api/v1/openapi",
            "/api/v2/openapi",
            "/api/v3/openapi",
            "/api/alpha/docs",  # Since we're using alpha API
            "/api/alpha/swagger",
            "/api/alpha/openapi"
        ]
        
        logger.info("Checking common OpenAPI/Swagger documentation locations...")
        
        for path in doc_paths:
            try:
                logger.info(f"Trying path: {path}")
                # First check headers for documentation links
                url = f"{explorer.BASE_URL.rstrip('/')}/{path.lstrip('/')}"
                response = explorer.session.head(url)
                
                # Check for documentation links in headers
                doc_headers = [
                    'Link',
                    'X-API-Documentation',
                    'X-Swagger-Version',
                    'X-OpenAPI-Version'
                ]
                
                for header in doc_headers:
                    if header in response.headers:
                        logger.info(f"Found documentation link in {header}: {response.headers[header]}")
                
                # Now try to get the actual content
                response = explorer.get_resource(path)
                
                # Check if this looks like OpenAPI/Swagger documentation
                if isinstance(response, dict):
                    if "openapi" in response or "swagger" in response:
                        logger.info(f"Found OpenAPI/Swagger documentation at {path}")
                        logger.info("-" * 80)
                        print(json.dumps(response, indent=2))
                        break
                    elif "paths" in response or "definitions" in response:
                        logger.info(f"Found API documentation at {path}")
                        logger.info("-" * 80)
                        print(json.dumps(response, indent=2))
                        break
                    else:
                        logger.info(f"Found JSON response at {path}")
                        logger.info("Full response:")
                        print(json.dumps(response, indent=2))
                        logger.info("\nResponse structure:")
                        print(json.dumps({k: type(v).__name__ for k, v in response.items()}, indent=2))
                else:
                    logger.info(f"Unexpected response format at {path}")
                    logger.info(f"Response type: {type(response)}")
                    logger.info(f"Response content: {response}")
                    
            except BoldoAPIError as e:
                logger.info(f"No documentation found at {path}: {str(e)}")
                continue
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 