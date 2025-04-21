"""Mock GraphDB server for testing."""

import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Type
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from threading import Thread
from urllib.parse import urlparse, parse_qs
import socket

def find_free_port() -> int:
    """Find a free port to use for the server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port: int = int(s.getsockname()[1])
    return port

class MockGraphDBServer:
    """Mock GraphDB server for testing."""
    
    def __init__(self, host: str = "localhost", port: Optional[int] = None) -> None:
        """Initialize the mock server.
        
        Args:
            host: The host to bind to
            port: Optional port to use. If None, a random free port will be used.
        """
        self.host = host
        self.port = port if port is not None else find_free_port()
        self.url = f"http://{host}:{self.port}"
        self.logs: list[Dict[str, Any]] = []  # Changed to store structured log entries
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start the mock server."""
        def create_handler(server: "MockGraphDBServer") -> Type[BaseHTTPRequestHandler]:
            """Create a handler class with a reference to the server."""
            class Handler(BaseHTTPRequestHandler):
                """Handler for mock GraphDB server requests."""
                
                mock_server = server  # Class attribute to store server reference
                
                def do_GET(self) -> None:
                    """Handle GET requests."""
                    parsed_path = urlparse(self.path)
                    
                    if parsed_path.path == "/rest/monitor/logs":
                        self._handle_logs()
                    elif parsed_path.path.startswith("/repositories/"):
                        self._handle_query(parse_qs(parsed_path.query))
                    else:
                        self.send_error(404, "Not Found")
                
                def do_POST(self) -> None:
                    """Handle POST requests."""
                    if self.path == "/rest/repositories":
                        self._handle_create_repository()
                    elif self.path.endswith("/statements"):
                        self._handle_import_data()
                    else:
                        self.send_error(404, "Not Found")
                
                def _send_json_response(self, data: Dict[str, Any], status: int = 200) -> None:
                    """Send a JSON response."""
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                
                def _handle_logs(self) -> None:
                    """Handle server log requests."""
                    logs = self.mock_server.get_logs()
                    self._send_json_response({"logs": logs})
                
                def _handle_query(self, params: Dict[str, List[str]]) -> None:
                    """Handle SPARQL query requests."""
                    query = params.get("query", [""])[0]
                    if not query:
                        self.send_error(400, "Missing query parameter")
                        return
                        
                    if "error" in query.lower() or "invalid" in query.lower():
                        self.mock_server.add_log("Error executing query", level="ERROR")
                        self.send_error(400, "Invalid SPARQL query")
                        return
                        
                    # Simulate slow query
                    if "WHERE" in query and not "LIMIT" in query:
                        time.sleep(1.5)  # Sleep for 1.5 seconds to simulate slow query
                        self.mock_server.add_log("Slow query detected", level="WARN")
                        
                    result = {
                        "head": {"vars": ["s", "p", "o"]},
                        "results": {
                            "bindings": [
                                {
                                    "s": {"type": "uri", "value": "http://example.org/TestClass"},
                                    "p": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                                    "o": {"type": "uri", "value": "http://www.w3.org/2000/01/rdf-schema#Class"}
                                }
                            ]
                        }
                    }
                    self.mock_server.add_log("Query executed", level="INFO")
                    self._send_json_response(result)
                
                def _handle_create_repository(self) -> None:
                    """Handle repository creation requests."""
                    content_length = int(self.headers.get("Content-Length", 0))
                    if content_length:
                        config = self.rfile.read(content_length).decode()
                        self.mock_server.add_log("Repository 'test_repo' created", level="INFO")
                    self._send_json_response({"status": "success"})
                
                def _handle_import_data(self) -> None:
                    """Handle data import requests."""
                    content_length = int(self.headers.get("Content-Length", 0))
                    if content_length:
                        data = self.rfile.read(content_length).decode()
                        # Get the file path from the Content-Disposition header
                        content_disposition = self.headers.get("Content-Disposition", "")
                        filename = content_disposition.split("filename=")[-1].strip('"')
                        self.mock_server.add_log(f"Data imported from {filename}", level="INFO")
                    self._send_json_response({"status": "success"})
                    
            return Handler
            
        handler = create_handler(self)
        self.server = HTTPServer((self.host, self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def stop(self) -> None:
        """Stop the mock server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def add_log(self, message: str, level: str = "INFO") -> None:
        """Add a message to the server logs.
        
        Args:
            message: The log message
            level: Log level (INFO, WARN, ERROR)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "logger": "MockGraphDB"
        }
        self.logs.append(log_entry)
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all server logs as a list of structured log entries."""
        return self.logs
    
    def clear_logs(self) -> None:
        """Clear all server logs."""
        self.logs.clear()

    def __enter__(self) -> "MockGraphDBServer":
        """Start server when entering context."""
        self.start()
        return self
        
    def __exit__(self, exc_type: Optional[Type[BaseException]], 
                exc_val: Optional[BaseException], 
                exc_tb: Optional[Any]) -> None:
        """Stop server when exiting context."""
        self.stop()