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

# Standalone utility function
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
        self.host = host
        self.port = port if port is not None else find_free_port()
        self.url = f"http://{host}:{self.port}"
        self.logs: List[Dict[str, Any]] = []
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.repository_data: Dict[str, Any] = {} # Basic data store

    def start(self) -> None:
        server_instance = self # Pass the instance of MockGraphDBServer

        class Handler(BaseHTTPRequestHandler):
            mock_server_ref = server_instance # Store reference to the MockGraphDBServer instance

            def _send_json_response(self, data: Dict[str, Any], status: int = 200) -> None:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

            def _handle_logs(self) -> None:
                logs = self.mock_server_ref.get_logs()
                self._send_json_response({"logs": logs})

            def _handle_query(self, params: Dict[str, List[str]]) -> None:
                query_list = params.get("query")
                if not query_list or not query_list[0]:
                    self.send_error(400, "Missing query parameter")
                    return
                query = query_list[0]
                
                if "error" in query.lower() or "invalid" in query.lower():
                    self.mock_server_ref.add_log("Error executing query", level="ERROR")
                    self.send_error(400, "Invalid SPARQL query")
                    return
                
                if "WHERE" in query and "LIMIT" not in query: # Simulate slow query
                    time.sleep(0.1) # Reduced sleep time
                    self.mock_server_ref.add_log("Slow query detected", level="WARN")
                
                # Fixed response for SPARQL Client tests
                result = {
                    "head": {"vars": ["s", "p", "o"]},
                    "results": {
                        "bindings": [{
                            "s": {"type": "uri", "value": "http://example.org/TestClass"},
                            "p": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
                            "o": {"type": "uri", "value": "http://www.w3.org/2000/01/rdf-schema#Class"}
                        }]}}
                self.mock_server_ref.add_log(f"Query executed: {query[:100]}...", level="INFO")
                self._send_json_response(result)

            def _handle_create_repository(self) -> None:
                # Minimal implementation for repository creation
                self.mock_server_ref.add_log("Repository creation endpoint hit.", level="INFO")
                self._send_json_response({"message": "Repository endpoint."}, status=200)


            def _handle_sparql_update(self, update_query_str: Optional[str] = None) -> None:
                if update_query_str is None:
                    content_length = int(self.headers.get("Content-Length", 0))
                    if not content_length:
                        self.send_error(400, "Missing update query in body")
                        return
                    update_query_str = self.rfile.read(content_length).decode()
                
                self.mock_server_ref.add_log(f"SPARQL update received: {update_query_str[:100]}...", level="INFO")
                self.send_response(204) # No Content for successful SPARQL UPDATE
                self.end_headers()

            def _handle_import_data(self) -> None: # For direct RDF upload
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length:
                    data = self.rfile.read(content_length).decode()
                    self.mock_server_ref.add_log(f"Data import received (first 100 chars): {data[:100]}", level="INFO")
                self.send_response(204) 
                self.end_headers()

            def do_GET(self) -> None:
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                
                # Endpoint for SPARQLClient.check_server_status()
                if parsed_path.path == "/rest/repositories":
                     # Wrap the list in a dictionary to match _send_json_response signature
                     # Or adjust _send_json_response to handle List[Dict] if preferred for this endpoint
                     repo_list = [{"id": "mock_repo", "title": "Mock Repository", "uri": f"{self.mock_server_ref.url}/repositories/mock_repo", "readable": True, "writable": True}]
                     self._send_json_response({"repositories": repo_list}) 
                     return

                if parsed_path.path == "/rest/monitor/logs":
                    self._handle_logs()
                # General query endpoint (can be /sparql, /query, or repo specific)
                elif parsed_path.path.startswith("/repositories/") or \
                     parsed_path.path in ["/sparql", "/query"] or \
                     "query" in query_params:
                    self._handle_query(query_params)
                else:
                    self.send_error(404, "Not Found")

            def do_POST(self) -> None:
                parsed_path = urlparse(self.path)
                content_type = self.headers.get("Content-Type", "")
                
                # SPARQL Update endpoint (can be repo specific or general)
                if parsed_path.path.endswith("/statements") or \
                   parsed_path.path in ["/sparql", "/update"]:
                    if "application/sparql-update" in content_type:
                        self._handle_sparql_update()
                    elif "application/x-www-form-urlencoded" in content_type:
                        content_length = int(self.headers.get("Content-Length", 0))
                        post_data = self.rfile.read(content_length).decode()
                        params = parse_qs(post_data)
                        if "update" in params:
                            self._handle_sparql_update(params["update"][0])
                        elif "query" in params: # Query via POST form
                            self._handle_query({"query": params["query"]})
                        else:
                            self.send_error(400, "Bad Request: Missing update or query parameter")
                    elif "text/turtle" in content_type or "application/n-triples" in content_type:
                         self._handle_import_data()
                    else:
                        self.send_error(415, f"Unsupported Media Type for {parsed_path.path}: {content_type}")
                elif parsed_path.path == "/rest/repositories": # Keep repo creation
                    self._handle_create_repository()
                else:
                    self.send_error(404, "Not Found")

        self.server = HTTPServer((self.host, self.port), Handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join(timeout=1)


    def add_log(self, message: str, level: str = "INFO") -> None:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "logger": "MockGraphDB"
        }
        self.logs.append(log_entry)

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs

    def clear_logs(self) -> None:
        self.logs.clear()

    def __enter__(self) -> "MockGraphDBServer":
        self.start()
        return self
    
    def __exit__(self, exc_type: Optional[Type[BaseException]], 
                exc_val: Optional[BaseException], 
                exc_tb: Optional[Any]) -> None:
        self.stop()
