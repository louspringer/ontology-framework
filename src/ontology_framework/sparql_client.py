from requests import Session
from requests.exceptions import RequestException
from .exceptions import SparqlClientError

class SparqlClient:
    def __init__(self, base_url: str, server_type: str):
        self.base_url = base_url
        self.server_type = server_type
        self.session = Session()

    def create_dataset(self, dataset: str) -> bool:
        """Create a new dataset.
        
        Args:
            dataset: Name of the dataset
            
        Returns:
            True if dataset was created successfully
            
        Raises:
            SparqlClientError: If dataset creation fails
        """
        try:
            # Check if dataset already exists
            if self.dataset_exists(dataset):
                return True
                
            if self.server_type == "graphdb":
                response = self.session.put(
                    f"{self.base_url}/rest/repositories/{dataset}",
                    headers={"Content-Type": "application/json"},
                    json={"id": dataset, "title": dataset, "type": "free"}
                )
            else:  # fuseki
                # For Fuseki, use the admin API to create a TDB2 dataset
                response = self.session.post(
                    f"{self.base_url}/$$/datasets",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "dbName": dataset,
                        "dbType": "tdb2",  # Use TDB2 for better performance and persistence
                        "ds.name": dataset  # Dataset name in the UI
                    }
                )
                
            if response.status_code == 405:  # Method not allowed
                raise SparqlClientError(f"Server does not support dataset creation via API. Status: {response.status_code}")
                
            response.raise_for_status()
            return True
        except RequestException as e:
            raise SparqlClientError(f"Failed to create dataset: {str(e)}")
        except Exception as e:
            raise SparqlClientError(f"Unexpected error creating dataset: {str(e)}")