#!/bin/bash

set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

# Create directory structure
mkdir -p /opt/plantuml

# Download the latest PlantUML JAR
echo "Downloading PlantUML JAR..."
wget -O /opt/plantuml/plantuml.jar https://github.com/plantuml/plantuml/releases/download/v1.2024.4/plantuml-1.2024.4.jar

# Install dependencies
echo "Installing dependencies..."
if command -v apt-get &> /dev/null; then
  apt-get update
  apt-get install -y openjdk-11-jre-headless graphviz fonts-dejavu
elif command -v dnf &> /dev/null; then
  dnf install -y java-11-openjdk-headless graphviz dejavu-sans-fonts
elif command -v yum &> /dev/null; then
  yum install -y java-11-openjdk-headless graphviz dejavu-sans-fonts
else
  echo "Unsupported package manager. Please install Java 11, GraphViz, and DejaVu fonts manually."
  exit 1
fi

# Create user
echo "Creating plantuml user..."
if ! id -u plantuml &>/dev/null; then
  useradd -r -m -d /opt/plantuml -s /bin/false plantuml
fi

# Copy service file
echo "Setting up systemd service..."
cp plantuml-server.service /etc/systemd/system/

# Set permissions
chown -R plantuml:plantuml /opt/plantuml
chmod 755 /opt/plantuml
chmod 644 /opt/plantuml/plantuml.jar

# Start and enable service
systemctl daemon-reload
systemctl enable plantuml-server
systemctl start plantuml-server

echo "PlantUML server has been installed and started on port 20075"
echo "You can access it at http://localhost:20075" 