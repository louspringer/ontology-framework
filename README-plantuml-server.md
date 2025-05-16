# PlantUML Server

This is a PlantUML server implementation for the ontology framework project. It provides a web service that renders PlantUML diagrams on-the-fly.

## Overview

PlantUML is an open-source tool that allows users to create UML diagrams from a simple text language. This server enables rendering PlantUML diagrams via an HTTP API, which can be used by various tools and applications.

## Installation Options

### Option 1: Using Docker Compose (Recommended)

This is the easiest way to get started:

```bash
# Build and start the server
docker-compose -f docker-compose.plantuml.yml up -d
```

The server will be available at http://localhost:20075

### Option 2: Using the Install Script

For a direct installation on your system:

```bash
# Make the script executable if not already
chmod +x install_plantuml_server.sh

# Run the installation script with sudo
sudo ./install_plantuml_server.sh
```

This will:
- Download the PlantUML JAR file
- Install necessary dependencies (Java, GraphViz)
- Create a system user
- Set up and start a systemd service

### Option 3: Manual Installation

1. Ensure you have Java 11+ and GraphViz installed
2. Download the PlantUML JAR
3. Run it with:
   ```bash
   java -jar plantuml.jar -picoweb:20075
   ```

## Usage

### Basic Usage

To render a diagram, use either of these methods:

1. **Text input**: Visit http://localhost:20075 and enter your PlantUML code in the text area
2. **URL-encoded**: http://localhost:20075/plantuml/png/SyfFKj2rKt3CoKnELR1Io4ZDoSa70000
3. **GET request**: http://localhost:20075/plantuml/png?uml=> **Note:** The SVG below is rendered from the PlantUML diagram for GitHub compatibility.

![Diagram](README-plantuml-server_diagram_1.svg)

[View PlantUML source](README-plantuml-server_diagram_1.puml)


### Output Formats

The server supports multiple output formats:
- PNG: Use `/plantuml/png/...` or `/plantuml/png?uml=...`
- SVG: Use `/plantuml/svg/...` or `/plantuml/svg?uml=...`
- PDF: Use `/plantuml/pdf/...` or `/plantuml/pdf?uml=...`
- TXT: Use `/plantuml/txt/...` or `/plantuml/txt?uml=...`

### Examples

**Sequence Diagram:**
```
> **Note:** The SVG below is rendered from the PlantUML diagram for GitHub compatibility.

![Diagram](alice__.svg)

[View PlantUML source](alice__.puml)

```

**Class Diagram:**
```
> **Note:** The SVG below is rendered from the PlantUML diagram for GitHub compatibility.

![Diagram](class_car.svg)

[View PlantUML source](class_car.puml)

```

## Integration

### With Markdown Files

You can integrate with Markdown by using image links:

```markdown
![My Diagram](http://localhost:20075/plantuml/png?uml=@startuml%0A%0AAlice%20-%3E%20Bob%3A%20Hello%0A%0A@enduml)
```

### With Visual Studio Code

Use the "PlantUML" extension and configure it to use your local server:

1. Install the PlantUML extension
2. Configure it with:
   ```json
   "plantuml.server": "http://localhost:20075"
   ```

### With Jupyter Notebooks

You can use the `%plantuml` magic command with IPython:

```python
%load_ext plantuml_magic
%plantuml_config url="http://localhost:20075/plantuml/png"
%plantuml
> **Note:** The SVG below is rendered from the PlantUML diagram for GitHub compatibility.

![Diagram](alice__.svg)

[View PlantUML source](alice__.puml)

```

## Troubleshooting

- If the server doesn't start, check if port 20075 is already in use
- For rendering issues, ensure GraphViz is properly installed
- For memory issues, adjust the Java heap size using the `-Xmx` flag

## Security Considerations

The PlantUML server is configured with the `INTERNET` security profile, which allows:
- HTTP/HTTPS connections to standard ports (80/443)
- No local file access
- No execution of external commands

For different security requirements, modify the `PLANTUML_SECURITY_PROFILE` environment variable in the configuration. 