#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Docker is installed
if ! command_exists docker; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Check if Docker Compose is installed
if ! command_exists docker-compose; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Function to start services
start_services() {
    echo "Starting services..."
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 10
    echo "Services started. You can access:"
    echo "- BFG9K MCP server at http://localhost:8080"
    echo "- GraphDB at http://localhost:7200"
}

# Function to stop services
stop_services() {
    echo "Stopping services..."
    docker-compose down
    echo "Services stopped"
}

# Function to check service status
check_status() {
    echo "Checking service status..."
    docker-compose ps
}

# Function to view logs
view_logs() {
    if [ -z "$1" ]; then
        echo "Please specify a service (bfg9k-mcp, graphdb, or validation-service)"
        exit 1
    fi
    docker-compose logs -f "$1"
}

# Main script
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs "$2"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs [service]}"
        exit 1
        ;;
esac

exit 0 