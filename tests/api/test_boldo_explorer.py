import pytest
from unittest.mock import Mock, patch
from ontology_framework.api.boldo_explorer import BoldoAPIExplorer
from ontology_framework.exceptions import BoldoAPIError, AuthenticationError

@pytest.fixture
def explorer():
    return BoldoAPIExplorer("https://api.boldo.com", "test_api_key")

def test_init():
    explorer = BoldoAPIExplorer("https://api.boldo.com", "test_api_key")
    assert explorer.base_url == "https://api.boldo.com"
    assert explorer.api_key == "test_api_key"
    assert explorer.session.headers["Authorization"] == "Bearer test_api_key"
    assert explorer.session.headers["Content-Type"] == "application/json"

@patch('requests.Session')
def test_get_ontologies(mock_session, explorer):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": "1", "name": "Test Ontology"}]
    mock_session.return_value.request.return_value = mock_response
    
    result = explorer.get_ontologies()
    assert result == [{"id": "1", "name": "Test Ontology"}]
    mock_session.return_value.request.assert_called_once_with(
        'GET', 'https://api.boldo.com/ontologies'
    )

@patch('requests.Session')
def test_get_ontology(mock_session, explorer):
    mock_response = Mock()
    mock_response.json.return_value = {"id": "1", "name": "Test Ontology"}
    mock_session.return_value.request.return_value = mock_response
    
    result = explorer.get_ontology("1")
    assert result == {"id": "1", "name": "Test Ontology"}
    mock_session.return_value.request.assert_called_once_with(
        'GET', 'https://api.boldo.com/ontologies/1'
    )

@patch('requests.Session')
def test_search_ontologies(mock_session, explorer):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": "1", "name": "Test Ontology"}]
    mock_session.return_value.request.return_value = mock_response
    
    result = explorer.search_ontologies("test")
    assert result == [{"id": "1", "name": "Test Ontology"}]
    mock_session.return_value.request.assert_called_once_with(
        'GET', 'https://api.boldo.com/ontologies/search', params={'q': 'test'}
    )

@patch('requests.Session')
def test_authentication_error(mock_session, explorer):
    mock_response = Mock()
    mock_response.status_code = 401
    mock_session.return_value.request.return_value = mock_response
    
    with pytest.raises(AuthenticationError):
        explorer.get_ontologies()

@patch('requests.Session')
def test_api_error(mock_session, explorer):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_session.return_value.request.return_value = mock_response
    
    with pytest.raises(BoldoAPIError):
        explorer.get_ontologies() 