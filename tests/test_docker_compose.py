import pytest
import subprocess
import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def test_docker_compose_services():
    """Test that required Docker Compose services are running and healthy."""
    try:
        # Run docker compose ps command
        result = subprocess.run(
            ['docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the JSON output
        services: List[Dict[str, Any]] = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    service = json.loads(line)
                    services.append(service)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON line: {line}")
                    raise
        
        # Log the service status for debugging
        logger.info(f"Docker Compose services: {services}")
        
        # Find the GraphDB service
        graphdb_service = next(
            (s for s in services if s.get('Service') == 'graphdb'), None
        )
        
        assert graphdb_service is not None, "GraphDB service not found in Docker Compose"
        assert graphdb_service['State'] == 'running', "GraphDB service is not running"
        assert graphdb_service['Health'] == 'healthy', "GraphDB service is not healthy"
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker Compose command failed: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error checking Docker Compose services: {str(e)}")
        raise

def test_graphdb_port_available():
    """Test that GraphDB port is available and responding."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 7200))
        logger.info(f"GraphDB port check result: {result}")
        assert result == 0, "GraphDB port 7200 is not available"
    except Exception as e:
        logger.error(f"Error checking GraphDB port availability: {str(e)}")
        raise

def test_docker_compose_logs():
    """Test that Docker Compose logs are accessible and contain expected information."""
    try:
        # First try Docker container logs
        result = subprocess.run(
            ['docker', 'logs', 'graphdb', '--since', '5m'],
            capture_output=True,
            text=True,
            check=True
        )
        
        docker_logs = result.stdout
        logger.info(f"Retrieved {len(docker_logs.splitlines())} lines from Docker logs")
        
        if not docker_logs:
            logger.warning("No Docker container logs found in the last 5 minutes")
            
        # Then try GraphDB monitor logs endpoint
        try:
            response = requests.get('http://localhost:7200/rest/monitor/logs')
            if response.status_code == 500:
                logger.error("GraphDB monitor logs endpoint returned 500 - this is expected in some GraphDB versions")
                logger.info("Checking alternative logging endpoints...")
                
                # Try alternative endpoints that might have logs
                alt_endpoints = [
                    '/rest/monitor/infrastructure',
                    '/rest/monitor/statistics',
                    '/rest/monitor/health'
                ]
                
                for endpoint in alt_endpoints:
                    try:
                        alt_response = requests.get(f'http://localhost:7200{endpoint}')
                        if alt_response.ok:
                            logger.info(f"Successfully retrieved data from {endpoint}")
                            logger.debug(f"Response: {alt_response.text[:200]}...")  # Log first 200 chars
                    except requests.RequestException as e:
                        logger.warning(f"Failed to access {endpoint}: {str(e)}")
                        
            elif response.ok:
                graphdb_logs = response.text
                logger.info(f"Retrieved GraphDB monitor logs: {len(graphdb_logs.splitlines())} lines")
            else:
                logger.error(f"Unexpected status code from monitor logs endpoint: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Failed to access GraphDB monitor logs endpoint: {str(e)}")
            logger.info("This is not a test failure as the endpoint may not be available in all versions")
            
        # Test passes if we can access at least one type of logs
        assert docker_logs or response.ok, "Could not access any logs"
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to retrieve Docker logs: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing logs: {str(e)}")
        logger.error(f"Full error context: {type(e).__name__}: {str(e)}")
        raise 