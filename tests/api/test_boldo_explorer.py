import pytest
from unittest.mock import patch, MagicMock
from src.api.boldo_explorer import BoldoAPIExplorer, BoldoAPIError

@pytest.fixture
def mock_op():
    """Fixture to mock the 1Password CLI."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = "mock-api-key"
        yield mock_run

@pytest.fixture
def mock_requests():
    """Fixture to mock requests.Session."""
    with patch('requests.Session') as mock_session:
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        yield mock_session_instance

@pytest.fixture
def explorer(mock_op, mock_requests):
    """Fixture to create a BoldoAPIExplorer instance with mocked dependencies."""
    return BoldoAPIExplorer()

def test_get_api_key_from_1password(mock_op):
    """Test retrieving API key from 1Password."""
    explorer = BoldoAPIExplorer()
    assert explorer.api_key == "mock-api-key"
    mock_op.assert_called_once_with(
        ["op", "read", "op://Private/Baldo API Key/credential"],
        capture_output=True,
        text=True,
        check=True
    )

def test_get_api_key_from_1password_failure(mock_op):
    """Test handling 1Password CLI failure."""
    mock_op.side_effect = FileNotFoundError()
    with pytest.raises(RuntimeError, match="1Password CLI"):
        BoldoAPIExplorer()

def test_explore_endpoints(explorer, mock_requests):
    """Test exploring API endpoints."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"endpoints": ["users", "projects"]}
    mock_requests.request.return_value = mock_response
    
    endpoints = explorer.explore_endpoints()
    assert endpoints == {"endpoints": ["users", "projects"]}
    mock_requests.request.assert_called_once_with(
        "GET",
        "https://app.boldo.io/api/alpha/",
        headers={
            "Authorization": "Bearer mock-api-key",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )

def test_list_resources(explorer, mock_requests):
    """Test listing resources."""
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "1", "name": "Test"}]
    mock_requests.request.return_value = mock_response
    
    resources = explorer.list_resources("users")
    assert resources == [{"id": "1", "name": "Test"}]
    mock_requests.request.assert_called_once_with(
        "GET",
        "https://app.boldo.io/api/alpha/users",
        headers={
            "Authorization": "Bearer mock-api-key",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )

def test_get_resource_by_id(explorer, mock_requests):
    """Test getting a resource by ID."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "1", "name": "Test"}
    mock_requests.request.return_value = mock_response
    
    resource = explorer.get_resource_by_id("users", "1")
    assert resource == {"id": "1", "name": "Test"}
    mock_requests.request.assert_called_once_with(
        "GET",
        "https://app.boldo.io/api/alpha/users/1",
        headers={
            "Authorization": "Bearer mock-api-key",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )

def test_api_error_handling(explorer, mock_requests):
    """Test handling API errors."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API Error")
    mock_response.text = "Error details"
    mock_requests.request.return_value = mock_response
    
    with pytest.raises(BoldoAPIError) as exc_info:
        explorer.explore_endpoints()
    assert "API Error" in str(exc_info.value)
    assert "Error details" in str(exc_info.value)

def test_create_resource(explorer, mock_requests):
    """Test creating a resource."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "1", "name": "New Resource"}
    mock_requests.request.return_value = mock_response
    
    data = {"name": "New Resource"}
    result = explorer.create_resource("users", data)
    assert result == {"id": "1", "name": "New Resource"}
    mock_requests.request.assert_called_once_with(
        "POST",
        "https://app.boldo.io/api/alpha/users",
        headers={
            "Authorization": "Bearer mock-api-key",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json=data
    )

def test_update_resource(explorer, mock_requests):
    """Test updating a resource."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "1", "name": "Updated Resource"}
    mock_requests.request.return_value = mock_response
    
    data = {"name": "Updated Resource"}
    result = explorer.update_resource("users", "1", data)
    assert result == {"id": "1", "name": "Updated Resource"}
    mock_requests.request.assert_called_once_with(
        "PUT",
        "https://app.boldo.io/api/alpha/users/1",
        headers={
            "Authorization": "Bearer mock-api-key",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json=data
    )

def test_delete_resource(explorer, mock_requests):
    """Test deleting a resource."""
    mock_response = MagicMock()
    mock_requests.request.return_value = mock_response
    
    explorer.delete_resource("users", "1")
    mock_requests.request.assert_called_once_with(
        "DELETE",
        "https://app.boldo.io/api/alpha/users/1",
        headers={
            "Authorization": "Bearer mock-api-key",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    ) 