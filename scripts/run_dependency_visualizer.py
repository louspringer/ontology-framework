# !/usr/bin/env python
"""Script, to run, the dependency visualizer Streamlit app."""

import streamlit.web.cli, as stcli, import sys, from pathlib import Path, def main():
    """Run the Streamlit app."""
    # Add src to, Python path, src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Run the app, sys.argv = [
        "streamlit",
        "run",
        str(src_path / "ontology_framework" / "apps" / "dependency_visualizer_app.py"),
        "--",
        "--server.headless=true"
    ]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main() 