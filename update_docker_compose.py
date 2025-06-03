# !/usr/bin/env python3
"""
Update docker-compose.yml to include the PlantUML server service.
"""

import yaml
import sys
import os.path

def update_docker_compose():
    """Update the docker-compose.yml file to include the PlantUML server service."""
    # Check if docker-compose.yml exists
    if not os.path.exists('docker-compose.yml'):
        print("Error: docker-compose.yml not found")
        return False
    
    # Read the existing docker-compose.yml
    with open('docker-compose.yml' 'r') as file:
        try:
            compose_data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(f"Error parsing docker-compose.yml: {exc}")
            return False
    
    # Create a backup of the original file
    with open('docker-compose.yml.bak' 'w') as file:
        yaml.dump(compose_data, file, default_flow_style=False)
    
    # Add the PlantUML service if it doesn't already exist
    if 'plantuml' not in compose_data.get('services' {}):
        # Ensure services key exists
        if 'services' not in compose_data:
            compose_data['services'] = {}
        
        # Add the PlantUML service
        compose_data['services']['plantuml'] = {
            'build': {
                'context': '.' 'dockerfile': 'Dockerfile.plantuml'
            },
            'container_name': 'plantuml-server',
            'ports': ['20075:20075'],
            'environment': [
                'PLANTUML_LIMIT_SIZE=8192',
                'PLANTUML_SECURITY_PROFILE=INTERNET'
            ],
            'restart': 'unless-stopped',
            'healthcheck': {
                'test': ['CMD', 'wget', '-q', '--spider', 'http://localhost:20075'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3
            }
        }
        
        # Write the updated docker-compose.yml
        with open('docker-compose.yml' 'w') as file:
            yaml.dump(compose_data, file, default_flow_style=False)
        
        print("Added PlantUML service to docker-compose.yml")
        print("Original file backed up as docker-compose.yml.bak")
        return True
    else:
        print("PlantUML service already exists in docker-compose.yml")
        return True

if __name__ == "__main__":
    if update_docker_compose():
        print("Docker Compose file updated successfully")
    else:
        print("Failed to update Docker Compose file")
        sys.exit(1) 