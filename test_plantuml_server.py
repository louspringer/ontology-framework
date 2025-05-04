#!/usr/bin/env python3
"""
Test the PlantUML server by generating and saving a simple diagram.
"""

import urllib.request
import urllib.parse
import sys
import os
import time
import subprocess
import tempfile
import webbrowser
from pathlib import Path


def encode_plantuml(uml_text):
    """Encode the PlantUML text for URL transmission using the PlantUML text encoding."""
    # This is a simplified encoding - PlantUML server handles this internally
    return urllib.parse.quote(uml_text)


def test_plantuml_server(host="localhost", port=20075):
    """Test if the PlantUML server is running and can generate diagrams."""
    # Simple PlantUML diagram
    test_diagram = """
@startuml
Alice -> Bob: Hello
Bob --> Alice: Hi there!
@enduml
"""
    
    # Encode for URL
    encoded_diagram = encode_plantuml(test_diagram)
    
    # URLs for different formats
    png_url = f"http://{host}:{port}/plantuml/png?uml={encoded_diagram}"
    svg_url = f"http://{host}:{port}/plantuml/svg?uml={encoded_diagram}"
    
    # Create test directory if it doesn't exist
    test_dir = Path("test_plantuml")
    test_dir.mkdir(exist_ok=True)
    
    # Try to download the PNG
    png_file = test_dir / "test_diagram.png"
    svg_file = test_dir / "test_diagram.svg"
    
    try:
        # Check if server is reachable
        server_url = f"http://{host}:{port}"
        urllib.request.urlopen(server_url, timeout=5)
        print(f"✅ PlantUML server is running at {server_url}")
        
        # Try to generate PNG
        urllib.request.urlretrieve(png_url, png_file)
        print(f"✅ Successfully generated PNG diagram: {png_file}")
        
        # Try to generate SVG
        urllib.request.urlretrieve(svg_url, svg_file)
        print(f"✅ Successfully generated SVG diagram: {svg_file}")
        
        # Try to open the diagrams in the browser
        print("\nOpening diagrams in browser...")
        webbrowser.open(png_file.absolute().as_uri())
        time.sleep(1)  # Add a short delay
        webbrowser.open(svg_file.absolute().as_uri())
        
        return True
        
    except urllib.error.URLError as e:
        print(f"❌ Cannot connect to PlantUML server: {e}")
        print(f"   Make sure the server is running at {host}:{port}")
        return False
    except Exception as e:
        print(f"❌ Error testing PlantUML server: {e}")
        return False


def start_server_if_needed():
    """Start the PlantUML server if it's not already running."""
    try:
        # Check if server is already running
        urllib.request.urlopen("http://localhost:20075", timeout=2)
        print("PlantUML server is already running")
        return None  # Server is already running
    except urllib.error.URLError:
        # Server not running, try to start it
        print("PlantUML server not running, attempting to start...")
        
        # Check if JAR file exists
        if not os.path.exists("plantuml.jar"):
            print("Downloading PlantUML JAR...")
            try:
                urllib.request.urlretrieve(
                    "https://github.com/plantuml/plantuml/releases/download/v1.2024.4/plantuml-1.2024.4.jar",
                    "plantuml.jar"
                )
            except Exception as e:
                print(f"Failed to download PlantUML JAR: {e}")
                return None
        
        # Start server in a separate process
        try:
            process = subprocess.Popen(
                ["java", "-jar", "plantuml.jar", "-picoweb:20075"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            print("Waiting for server to start...")
            for _ in range(10):  # Try for 10 seconds
                try:
                    urllib.request.urlopen("http://localhost:20075", timeout=1)
                    print("Server started successfully")
                    return process
                except urllib.error.URLError:
                    time.sleep(1)
            
            print("Server didn't start in time, stopping...")
            process.terminate()
            return None
            
        except Exception as e:
            print(f"Failed to start PlantUML server: {e}")
            return None


if __name__ == "__main__":
    process = None
    try:
        # Try to start server if needed
        process = start_server_if_needed()
        
        # Run the test
        if test_plantuml_server():
            print("\n✅ PlantUML server test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ PlantUML server test failed!")
            sys.exit(1)
    finally:
        # Clean up if we started the server
        if process:
            print("Stopping PlantUML server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill() 