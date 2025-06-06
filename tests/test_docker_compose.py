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
        
        # Wait for GraphDB to become healthy, as it can take time
        # A more robust solution would poll, but a sleep is simpler for now.
        # The healthcheck in docker-compose.yml has a start_period of 40s.
        logger.info("Waiting for GraphDB service to become healthy...")
        import time
        time.sleep(45) # Wait longer than the start_period

        # Re-fetch service status after waiting
        result_after_wait = subprocess.run(
            ['docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True, text=True, check=True
        )
        services_after_wait: List[Dict[str, Any]] = []
        for line_after_wait in result_after_wait.stdout.strip().split('\n'):
            if line_after_wait:
                services_after_wait.append(json.loads(line_after_wait))
        
        graphdb_service_after_wait = next(
            (s for s in services_after_wait if s.get('Service') == 'graphdb'), None
        )
        assert graphdb_service_after_wait is not None, "GraphDB service not found after waiting"
        logger.info(f"GraphDB service status after waiting: {graphdb_service_after_wait}")
        assert graphdb_service_after_wait['Health'] == 'healthy', f"GraphDB service is not healthy. Status: {graphdb_service_after_wait.get('Status')}, Health: {graphdb_service_after_wait.get('Health')}"
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker Compose command failed: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error checking Docker Compose services: {str(e)}")
        raise

def test_graphdb_port_available():
    """Test that GraphDB port is available and responding by making an HTTP request."""
    health_check_url = "http://localhost:7200/rest/repositories"
    try:
        # Attempt a connection similar to how GraphDBClient might or how health checks are done.
        # Need to handle potential auth if the mock server or real server requires it for this endpoint.
        # For now, assume no auth for a basic reachability test to this common endpoint.
        response = requests.get(health_check_url, timeout=10, headers={"Accept": "application/json"})
        response.raise_for_status() # Check for HTTP errors
        logger.info(f"GraphDB endpoint {health_check_url} is responding with status {response.status_code}.")
        assert response.status_code == 200, f"GraphDB port 7200 not responding as expected to {health_check_url}. Status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking GraphDB port availability via HTTP to {health_check_url}: {str(e)}")
        pytest.fail(f"Error checking GraphDB port availability via HTTP to {health_check_url}: {str(e)}")
    except Exception as e: # Catch any other unexpected error
        logger.error(f"Unexpected error during GraphDB port availability check: {str(e)}")
        pytest.fail(f"Unexpected error during GraphDB port availability check: {str(e)}")

def test_docker_compose_logs():
    """Test that Docker Compose logs are accessible and contain expected information."""
    try:
        # Get the actual container name for the graphdb service
        ps_result = subprocess.run(
            ['docker', 'compose', 'ps', '--format', 'json'],
            capture_output=True, text=True, check=True
        )
        services_data: List[Dict[str, Any]] = []
        for line in ps_result.stdout.strip().split('\n'):
            if line:
                services_data.append(json.loads(line))
        
        graphdb_container_name = None
        for service_info in services_data:
            if service_info.get('Service') == 'graphdb':
                graphdb_container_name = service_info.get('Name')
                break
        
        assert graphdb_container_name, "Could not determine GraphDB container name from 'docker compose ps'"
        logger.info(f"Found GraphDB container name: {graphdb_container_name}")

        # First try Docker container logs using the actual container name
        result = subprocess.run(
            ['docker', 'logs', graphdb_container_name, '--since', '5m'],
            capture_output=True,
            text=True,
            check=True
        )
        
        docker_logs = result.stdout
        logger.info(f"Retrieved {len(docker_logs.splitlines())} lines from Docker logs")
        
        if not docker_logs:
            logger.warning("No Docker container logs found in the last 5 minutes")
            
        # Then try GraphDB monitor logs endpoint
        response = None # Initialize response
        try:
            response = requests.get('http://localhost:7200/rest/monitor/logs', timeout=10)
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
        http_log_accessible = False
        if response and response.ok:
            http_log_accessible = True
        else: # Check alternative endpoints if the main one failed or returned 500
            # This part already logs success/warnings, we just need to know if any were okay.
            # Re-checking here for assertion clarity.
            for alt_ep in alt_endpoints:
                try:
                    # Use a new response variable for clarity
                    temp_alt_response = requests.get(f'http://localhost:7200{alt_ep}', timeout=5)
                    if temp_alt_response.ok:
                        http_log_accessible = True
                        break 
                except requests.RequestException:
                    pass # Already logged by the test

        assert docker_logs or http_log_accessible, "Could not access any logs (neither Docker CLI logs nor any HTTP monitor/log endpoint)"
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to retrieve Docker logs: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing logs: {str(e)}")
        logger.error(f"Full error context: {type(e).__name__}: {str(e)}")
        raise
