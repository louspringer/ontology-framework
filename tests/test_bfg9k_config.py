import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from bfg9k_mcp import validate_graphdb_config

@pytest.fixture
def temp_config(tmp_path):
    config = tmp_path / "bfg9k_config.ttl"
    config.write_text("""
@prefix ns1: <https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k# > .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ns1:ServerConfiguration a ns1:ServerConfiguration ;
    rdfs:label "BFG9K - Test Configuration" ;
    ns1:host "http://localhost:7200" ;
    ns1:ontologyPath "guidance.ttl" ;
    ns1:repository "guidance" ;
    ns1:validationEnabled true .
""")
    return config

def test_validate_graphdb_config_success(temp_config):
    with patch("bfg9k_mcp.project_root", Path(temp_config.parent)), \
         patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        error = validate_graphdb_config()
        assert error is None
        mock_get.assert_called_once_with("http://localhost:7200/rest/repositories", timeout=5)

def test_validate_graphdb_config_env_override(temp_config):
    with patch("bfg9k_mcp.project_root", Path(temp_config.parent)), \
         patch.dict(os.environ, {"GRAPHDB_URL": "http://custom:8080"}), \
         patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        error = validate_graphdb_config()
        assert error is None
        mock_get.assert_called_once_with("http://custom:8080/rest/repositories", timeout=5)

def test_validate_graphdb_config_connection_error(temp_config):
    with patch("bfg9k_mcp.project_root", Path(temp_config.parent)), \
         patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection refused")
        
        error = validate_graphdb_config()
        assert error is not None
        # The error is now a dictionary with detailed validation report
        assert any("Connection refused" in str(check) for check in error["checks"])

def test_validate_graphdb_config_missing_file():
    # Mock the GraphDBValidator to simulate a missing file
    mock_validator = MagicMock()
    mock_validator.return_value.validate_config.return_value = (
        False, 
        {
            "checks": [
                {
                    "name": "config_file_exists",
                    "passed": False,
                    "message": "Configuration file not found: bfg9k_config.ttl. Please ensure the config file exists at the specified path."
                }
            ],
            "is_valid": False
        }
    )
    
    with patch("bfg9k_mcp.GraphDBValidator", mock_validator):
        error = validate_graphdb_config()
        assert error is not None
        # The error is now a dictionary with detailed validation report
        assert any("Configuration file not found" in check.get('message', '') 
                  for check in error.get('checks', []))
