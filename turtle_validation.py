import re
from typing import List, Dict, Optional
from pathlib import Path
import rdflib
import requests
from dotenv import load_dotenv
import os
from src.ontology_framework.graphdb_client import GraphDBClient, GraphDBError

def check_relative_prefixes(turtle_content: str) -> List[Dict]:
    pattern = re.compile(r'@prefix\s+([^:]+):\s*<\./([^>#]+)#>')
    results = []
    for i, line in enumerate(turtle_content.splitlines(), 1):
        m = pattern.search(line)
        if m:
            prefix, frag = m.group(1), m.group(2)
            results.append({
                'type': 'error',
                'line': i,
                'message': f"Relative prefix detected: {prefix}: <./{frag}#>",
                'suggestion': f"Use absolute IRI, e.g., <https://your-base-uri/{frag}#>"
            })
    return results

def check_malformed_iris(turtle_content: str) -> List[Dict]:
    pattern = re.compile(r'(<http:/)([^/])')
    results = []
    for i, line in enumerate(turtle_content.splitlines(), 1):
        if pattern.search(line):
            results.append({
                'type': 'error',
                'line': i,
                'message': f"Malformed IRI detected: {line.strip()}",
                'suggestion': "Use 'http://' instead of 'http:/'"
            })
    return results

def check_duplicate_prefixes(turtle_content: str) -> List[Dict]:
    pattern = re.compile(r'@prefix\s+([^:]+):')
    seen = {}
    results = []
    for i, line in enumerate(turtle_content.splitlines(), 1):
        m = pattern.match(line.strip())
        if m:
            prefix = m.group(1)
            if prefix in seen:
                results.append({
                    'type': 'warning',
                    'line': i,
                    'message': f"Duplicate prefix declaration: {prefix}",
                    'suggestion': f"Remove duplicate, keep only the first at line {seen[prefix]}"
                })
            else:
                seen[prefix] = i
    return results

def check_undeclared_prefixes(turtle_content: str) -> List[Dict]:
    # Find all declared prefixes
    declared = set()
    prefix_decl = re.compile(r'@prefix\s+([^:]+):')
    for line in turtle_content.splitlines():
        m = prefix_decl.match(line.strip())
        if m:
            declared.add(m.group(1))
    # Find all used prefixes
    used = set()
    # Whitelist for common datatypes
    datatype_whitelist = {
        'xsd', 'rdf', 'rdfs', 'owl', 'sh', 'dc', 'dct', 'skos', 'foaf', 'prov', 'schema', 'void', 'qb', 'time', 'geo', 'vann', 'doap', 'cc', 'org', 'gr', 'sioc', 'bibo', 'obo', 'oboInOwl', 'swrl', 'swrlb', 'swrla', 'vs', 'ex', 'meta', 'problem', 'solution', 'conversation', 'guidance', 'validation', 'api_doc', 'mu', 'repo', 'security', 'collaboration', 'model'
    }
    triple_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*):([a-zA-Z_][a-zA-Z0-9_\-]*)')
    for line in turtle_content.splitlines():
        for m in triple_pattern.finditer(line):
            prefix = m.group(1)
            local = m.group(2)
            # Ignore if prefix is whitelisted
            if prefix in datatype_whitelist:
                continue
            # Ignore if looks like a date/time literal (e.g., 2024-04-12T00:00:00)
            if re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', f"{prefix}:{local}"):
                continue
            used.add(prefix)
    undeclared = used - declared
    results = []
    for prefix in undeclared:
        results.append({
            'type': 'error',
            'line': None,
            'message': f"Prefix '{prefix}:' used in triples but not declared.",
            'suggestion': f"Add a @prefix declaration for '{prefix}:' at the top of the file."
        })
    return results

def check_syntax(turtle_content: str) -> List[Dict]:
    results = []
    try:
        g = rdflib.Graph()
        g.parse(data=turtle_content, format="turtle")
    except Exception as e:
        results.append({
            'type': 'error',
            'line': None,
            'message': f"Turtle syntax error: {e}",
            'suggestion': "Check the reported error and fix the syntax."
        })
    return results

def check_encoding(turtle_path: str) -> List[Dict]:
    results = []
    try:
        with open(turtle_path, 'r', encoding='utf-8') as f:
            f.read()
    except UnicodeDecodeError as e:
        results.append({
            'type': 'error',
            'line': None,
            'message': f"File encoding error: {e}",
            'suggestion': "Save the file as UTF-8."
        })
    return results

def check_prefix_iri_reachability(turtle_content: str) -> List[Dict]:
    pattern = re.compile(r'@prefix\s+([^:]+):\s*<([^>#]+)#>')
    results = []
    for i, line in enumerate(turtle_content.splitlines(), 1):
        m = pattern.search(line)
        if m:
            prefix, iri = m.group(1), m.group(2)
            # Only check http(s) IRIs
            if iri.startswith('http://') or iri.startswith('https://'):
                try:
                    resp = requests.head(iri, timeout=2)
                    if resp.status_code >= 400:
                        results.append({
                            'type': 'warning',
                            'line': i,
                            'message': f"Declared prefix '{prefix}:' points to IRI '{iri}' which is not reachable (status {resp.status_code}).",
                            'suggestion': f"Check the IRI or use a resolvable namespace."
                        })
                except Exception as e:
                    results.append({
                        'type': 'warning',
                        'line': i,
                        'message': f"Declared prefix '{prefix}:' points to IRI '{iri}' which could not be reached ({e.__class__.__name__}).",
                        'suggestion': f"Check the IRI or use a resolvable namespace."
                    })
    return results

def check_unused_prefixes(turtle_content: str) -> List[Dict]:
    # Find all declared prefixes
    declared = set()
    prefix_decl = re.compile(r'@prefix\s+([^:]+):')
    for line in turtle_content.splitlines():
        m = prefix_decl.match(line.strip())
        if m:
            declared.add(m.group(1))
    # Find all used prefixes
    used = set()
    triple_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*):([a-zA-Z_][a-zA-Z0-9_\-]*)')
    for line in turtle_content.splitlines():
        for m in triple_pattern.finditer(line):
            used.add(m.group(1))
    unused = declared - used
    results = []
    for prefix in unused:
        results.append({
            'type': 'warning',
            'line': None,
            'message': f"Declared prefix '{prefix}:' is never used in the file.",
            'suggestion': f"Remove unused prefix declaration."
        })
    return results

def check_graphdb_consistency(turtle_content: str) -> List[Dict]:
    load_dotenv()
    base_url = os.environ.get("GRAPHDB_URL", "http://localhost:7200")
    repository = os.environ.get("GRAPHDB_REPOSITORY", "ontologyframework")
    results = []
    try:
        client = GraphDBClient(base_url, repository)
        graph_uris = set(client.list_graphs())
    except Exception as e:
        results.append({
            'type': 'warning',
            'line': None,
            'message': f"Could not connect to GraphDB ({e.__class__.__name__}: {e})",
            'suggestion': "Check your .env configuration and GraphDB status."
        })
        return results
    # Find all declared prefixes and their IRIs
    prefix_pattern = re.compile(r'@prefix\s+([^:]+):\s*<([^>#]+)#>')
    for i, line in enumerate(turtle_content.splitlines(), 1):
        m = prefix_pattern.search(line)
        if m:
            prefix, iri = m.group(1), m.group(2)
            # Only check http(s) IRIs
            if iri.startswith('http://') or iri.startswith('https://'):
                if iri not in graph_uris:
                    results.append({
                        'type': 'warning',
                        'line': i,
                        'message': f"Declared prefix '{prefix}:' IRI '{iri}' not present as a named graph in GraphDB.",
                        'suggestion': f"Load the corresponding ontology into GraphDB or check the IRI."
                    })
    return results

def validate_all(turtle_path: str) -> List[Dict]:
    # Read file content
    with open(turtle_path, encoding='utf-8') as f:
        content = f.read()
    results = []
    results.extend(check_relative_prefixes(content))
    results.extend(check_malformed_iris(content))
    results.extend(check_duplicate_prefixes(content))
    results.extend(check_undeclared_prefixes(content))
    results.extend(check_syntax(content))
    results.extend(check_encoding(turtle_path))
    results.extend(check_prefix_iri_reachability(content))
    results.extend(check_unused_prefixes(content))
    results.extend(check_graphdb_consistency(content))
    return results 