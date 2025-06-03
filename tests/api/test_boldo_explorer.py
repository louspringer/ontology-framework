import pytest
from unittest.mock import Mock
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

def test_get_ontologies(explorer, mocker):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": "1", "name": "Test Ontology"}]
    mock_response.raise_for_status.return_value = None
    mocker.patch.object(explorer.session, "request", return_value=mock_response)

    result = explorer.get_ontologies()
    assert result == [{"id": "1", "name": "Test Ontology"}]
    explorer.session.request.assert_called_once_with(
        'GET', 'https://api.boldo.com/ontologies'
    )

def test_get_ontology(explorer, mocker):
    mock_response = Mock()
    mock_response.json.return_value = {"id": "1", "name": "Test Ontology"}
    mock_response.raise_for_status.return_value = None
    mocker.patch.object(explorer.session, "request", return_value=mock_response)

    result = explorer.get_ontology("1")
    assert result == {"id": "1", "name": "Test Ontology"}
    explorer.session.request.assert_called_once_with(
        'GET', 'https://api.boldo.com/ontologies/1'
    )

def test_search_ontologies(explorer, mocker):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": "1", "name": "Test Ontology"}]
    mock_response.raise_for_status.return_value = None
    mocker.patch.object(explorer.session, "request", return_value=mock_response)

    result = explorer.search_ontologies("test")
    assert result == [{"id": "1", "name": "Test Ontology"}]
    explorer.session.request.assert_called_once_with(
        'GET', 'https://api.boldo.com/ontologies/search', params={'q': 'test'}
    )

def test_authentication_error(explorer, mocker):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("401 Client Error: Unauthorized for url")
    mocker.patch.object(explorer.session, "request", return_value=mock_response)

    with pytest.raises(Exception):  # Should be AuthenticationError if you want to test your custom error
        explorer.get_ontologies()

def test_api_error(explorer, mocker):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("500 Server Error: Internal Server Error for url")
    mocker.patch.object(explorer.session, "request", return_value=mock_response)

    with pytest.raises(Exception):  # Should be BoldoAPIError if you want to test your custom error
        explorer.get_ontologies()
