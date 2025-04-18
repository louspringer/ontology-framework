import pytest
import requests
from unittest.mock import patch, MagicMock
from ontology_framework.api.boldo_explorer import BoldoAPIExplorer, BoldoAPIError

@pytest.fixture
def explorer():
    """Fixture providing a BoldoAPIExplorer instance with mocked API key."""
    with patch.object(BoldoAPIExplorer, '_get_api_key_from_1password', return_value="test_api_key"):
        return BoldoAPIExplorer()

@pytest.fixture
def mock_response():
    """Fixture providing a mock response object."""
    response = MagicMock()
    response.json.return_value = {"data": {}}
    response.raise_for_status.return_value = None
    return response

def test_init_with_api_key():
    """Test initialization with explicit API key."""
    explorer = BoldoAPIExplorer(api_key="test_key")
    assert explorer.api_key == "test_key"

def test_init_without_api_key():
    """Test initialization without API key."""
    with patch.object(BoldoAPIExplorer, '_get_api_key_from_1password', return_value="test_key"):
        explorer = BoldoAPIExplorer()
        assert explorer.api_key == "test_key"

def test_get_models(explorer):
    """Test getting all models."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"id": "1", "name": "Model 1"}]}
    mock_response.raise_for_status.return_value = None
    
    with patch.object(explorer.session, 'get', return_value=mock_response):
        models = explorer.get_models()
        assert len(models) == 1
        assert models[0]["id"] == "1"
        assert models[0]["name"] == "Model 1"

def test_get_models_error(explorer):
    """Test error handling when getting models fails."""
    with patch.object(explorer.session, 'get', side_effect=Exception("API Error")):
        with pytest.raises(BoldoAPIError):
            explorer.get_models()

def test_get_model(explorer):
    """Test getting a specific model."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"id": "1", "name": "Model 1"}}
    mock_response.raise_for_status.return_value = None
    
    with patch.object(explorer.session, 'get', return_value=mock_response):
        model = explorer.get_model("1")
        assert model["id"] == "1"
        assert model["name"] == "Model 1"

def test_get_model_error(explorer):
    """Test error handling when getting a model fails."""
    with patch.object(explorer.session, 'get', side_effect=Exception("API Error")):
        with pytest.raises(BoldoAPIError):
            explorer.get_model("1")

def test_create_model(explorer):
    """Test creating a new model."""
    model_data = {"name": "New Model"}
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"id": "2", "name": "New Model"}}
    mock_response.raise_for_status.return_value = None
    
    with patch.object(explorer.session, 'post', return_value=mock_response):
        model = explorer.create_model(model_data)
        assert model["id"] == "2"
        assert model["name"] == "New Model"

def test_create_model_error(explorer):
    """Test error handling when creating a model fails."""
    with patch.object(explorer.session, 'post', side_effect=Exception("API Error")):
        with pytest.raises(BoldoAPIError):
            explorer.create_model({"name": "New Model"})

def test_update_model(explorer):
    """Test updating an existing model."""
    model_data = {"name": "Updated Model"}
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"id": "1", "name": "Updated Model"}}
    mock_response.raise_for_status.return_value = None
    
    with patch.object(explorer.session, 'put', return_value=mock_response):
        model = explorer.update_model("1", model_data)
        assert model["id"] == "1"
        assert model["name"] == "Updated Model"

def test_update_model_error(explorer):
    """Test error handling when updating a model fails."""
    with patch.object(explorer.session, 'put', side_effect=Exception("API Error")):
        with pytest.raises(BoldoAPIError):
            explorer.update_model("1", {"name": "Updated Model"})

def test_delete_model(explorer):
    """Test deleting a model."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    
    with patch.object(explorer.session, 'delete', return_value=mock_response):
        explorer.delete_model("1")  # Should not raise an exception

def test_delete_model_error(explorer):
    """Test error handling when deleting a model fails."""
    with patch.object(explorer.session, 'delete', side_effect=Exception("API Error")):
        with pytest.raises(BoldoAPIError):
            explorer.delete_model("1")

def test_explore_endpoints(explorer, mock_response):
    """Test exploring available endpoints."""
    mock_response.json.return_value = {"data": {"endpoints": ["/models", "/users"]}}
    
    with patch.object(explorer.session, 'get', return_value=mock_response):
        endpoints = explorer.explore_endpoints()
        assert "endpoints" in endpoints

def test_list_resources(explorer, mock_response):
    """Test listing resources."""
    mock_response.json.return_value = {"data": [{"id": "1", "name": "Resource 1"}]}
    
    with patch.object(explorer.session, 'get', return_value=mock_response):
        resources = explorer.list_resources('users')
        assert len(resources) == 1

def test_get_resource_by_id(explorer, mock_response):
    """Test getting a resource by ID."""
    mock_response.json.return_value = {"data": {"id": "1", "name": "Resource 1"}}
    
    with patch.object(explorer.session, 'get', return_value=mock_response):
        resource = explorer.get_resource_by_id('users', 1)
        assert resource["id"] == "1"

def test_api_error_handling(explorer):
    """Test API error handling."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API Error")
    
    with patch.object(explorer.session, 'get', return_value=mock_response):
        with pytest.raises(BoldoAPIError):
            explorer.explore_endpoints()

def test_create_resource(explorer, mock_response):
    """Test creating a resource."""
    mock_response.json.return_value = {"data": {"id": "1", "name": "New Resource"}}
    
    with patch.object(explorer.session, 'post', return_value=mock_response):
        resource = explorer.create_resource('users', {'name': 'New Resource'})
        assert resource["name"] == "New Resource"

def test_update_resource(explorer, mock_response):
    """Test updating a resource."""
    mock_response.json.return_value = {"data": {"id": "1", "name": "Updated Resource"}}
    
    with patch.object(explorer.session, 'put', return_value=mock_response):
        resource = explorer.update_resource('users', 1, {'name': 'Updated Resource'})
        assert resource["name"] == "Updated Resource"

def test_delete_resource(explorer, mock_response):
    """Test deleting a resource."""
    with patch.object(explorer.session, 'delete', return_value=mock_response):
        explorer.delete_resource('users', 1)  # Should not raise an exception

def test_404_error_handling(explorer):
    """Test handling of 404 errors."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Resource not found")
    
    with patch.object(explorer.session, 'get', return_value=mock_response):
        with pytest.raises(BoldoAPIError, match="Resource not found: users/1"):
            explorer.get_resource_by_id('users', 1) 