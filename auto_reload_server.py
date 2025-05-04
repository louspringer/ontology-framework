#!/usr/bin/env python3
"""
Auto-reloading web server for ontology visualization

Serves files from the current directory and automatically reloads
the page when the specified target file changes.
"""

import os
import sys
import argparse
from livereload import Server

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Start an auto-reloading web server")
    parser.add_argument("--port", type=int, default=8000, help="Port to serve on (default: 8000)")
    parser.add_argument("--watch", default="interactive_ontology.html", 
                        help="File to watch for changes (default: interactive_ontology.html)")
    parser.add_argument("--directory", default=".", help="Directory to serve (default: current directory)")
    return parser.parse_args()

def start_server(port, watch_file, directory):
    """Start a livereload server watching for file changes."""
    server = Server()
    
    # Watch the specified file for changes
    absolute_path = os.path.abspath(watch_file)
    server.watch(absolute_path)
    print(f"Watching for changes in: {absolute_path}")
    
    # Serve from the specified directory
    server_root = os.path.abspath(directory)
    print(f"Serving files from: {server_root}")
    
    # Start the server
    print(f"Server running at http://localhost:{port}")
    print("Auto-reload enabled - page will refresh when files change")
    print("Press Ctrl+C to stop the server")
    
    # Start the server with the specified port
    server.serve(port=port, root=server_root)

def main():
    """Main function."""
    args = parse_arguments()
    try:
        start_server(args.port, args.watch, args.directory)
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)

if __name__ == "__main__":
    main() 