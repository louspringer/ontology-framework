# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

import logging
import os
import requests
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from datetime import datetime
import json
import tempfile
import uuid
import time
import traceback

logger = logging.getLogger(__name__)

# Utility for TTL-safe string escaping
def ttl_escape(s: str) -> str:
    """Escape a string for safe inclusion in TTL literals."""
    return s.replace('"', '\"').replace('\\', '\\\\')

class GraphDBValidator:
    """Validator for GraphDB configuration and connectivity."""
    
    def __init__(self, config_file: str = "bfg9k_config.ttl"):
        """Initialize the validator with config file path."""
        self.config_file = Path(config_file)
        self.validation_history = []
        self.validation_graph = Graph()
        self._setup_logging()
        self._load_validation_patterns()
        self.debug_flag = os.environ.get('BFG9K_DEBUG', 'false').lower() == 'true'
        self.debug_dump_file = Path("logs/graphdb_validator_debug.log")
        if self.debug_flag:
            self.debug_dump_file.parent.mkdir(exist_ok=True)
    
    def _setup_logging(self):
        """Setup enhanced logging for validation."""
        self.log_file = Path("logs/graphdb_validation.log")
        self.log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
    
    def _load_validation_patterns(self):
        """Load validation patterns from guidance files."""
        try:
            guidance_dir = Path("guidance/modules")
            pattern_files = [
                "validation.ttl",
                "ontology_tracking.ttl",
                "transformed_validation.ttl"
            ]
            for pattern_file in pattern_files:
                pattern_path = guidance_dir / pattern_file
                if pattern_path.exists():
                    self.validation_graph.parse(pattern_path, format="turtle")
                else:
                    logger.warning(f"Validation pattern file not found: {pattern_path}")
        except Exception as e:
            logger.error(f"Failed to load validation patterns: {e}")
    
    def _log_request(self, method, url, **kwargs):
        request_id = str(uuid.uuid4())
        debug_mode = os.environ.get('BFG9K_DEBUG', 'false').lower() == 'true'
        logger.debug(f"[GraphDBValidator][{request_id}] {method} {url}")
        for k, v in kwargs.items():
            if k in ('headers', 'params', 'json', 'data') and debug_mode:
                logger.debug(f"[GraphDBValidator][{request_id}] {k}: {v}")
        logger.debug(f"[GraphDBValidator][{request_id}] Timestamp: {datetime.now().isoformat()}")
        return request_id

    def _log_response(self, request_id, response, start_time):
        debug_mode = os.environ.get('BFG9K_DEBUG', 'false').lower() == 'true'
        elapsed = time.perf_counter() - start_time
        logger.debug(f"[GraphDBValidator][{request_id}] Response status: {response.status_code}")
        if debug_mode:
            logger.debug(f"[GraphDBValidator][{request_id}] Response headers: {dict(response.headers)}")
            if hasattr(response, 'text') and len(response.text) < 10000:
                logger.debug(f"[GraphDBValidator][{request_id}] Response body: {response.text}")
        logger.debug(f"[GraphDBValidator][{request_id}] Elapsed: {elapsed:.4f}s")
    
    def validate_config(self) -> Tuple[bool, Dict]:
        """Validate GraphDB configuration file and connectivity.
        
        Returns:
            Tuple[bool Dict]: (is_valid validation_report)
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'config_file': str(self.config_file),
            'checks': [],
            'is_valid': True,
            'environment': self._get_environment_info(),
            'ttl_findings': []  # TTL snippets for findings
        }
        def log_debug_dump(msg):
            if self.debug_flag:
                with open(self.debug_dump_file, 'a') as f:
                    f.write(f"{datetime.now().isoformat()} - {msg}\n")
        try:
            # Check config file existence
            if not self.config_file.exists():
                msg = f"Configuration file not found: {self.config_file}. Please ensure the config file exists at the specified path."
                self._add_check(report, 'config_file_exists', False, msg)
                ttl_snippet = f"""@prefix error: <http://example.org/error# > .\n[] a error:ValidationError ;\n   error:type \"ConfigFileMissing\" ;\n   error:message \"{ttl_escape(msg)}\" ;\n   error:severity \"CRITICAL\" ;\n   error:timestamp \"{datetime.now().isoformat()}\" ."""
                report['ttl_findings'].append(ttl_snippet)
                log_debug_dump(f"Config file missing: {msg}")
                return False, report
            
            # Parse and validate TTL syntax
            g = Graph()
            try:
                g.parse(self.config_file, format="turtle")
                self._add_check(report, 'ttl_syntax', True, "TTL syntax is valid")
            except Exception as e:
                msg = f"Invalid TTL syntax: {str(e)}. Please check the configuration file for syntax errors."
                self._add_check(report, 'ttl_syntax', False, msg)
                ttl_snippet = f"""@prefix error: <http://example.org/error# > .\n[] a error:ValidationError ;\n   error:type \"TTLSyntaxError\" ;\n   error:message \"{ttl_escape(msg)}\" ;\n   error:severity \"CRITICAL\" ;\n   error:timestamp \"{datetime.now().isoformat()}\" ."""
                report['ttl_findings'].append(ttl_snippet)
                log_debug_dump(f"TTL syntax error: {traceback.format_exc()}")
                return False, report
            
            # Extract and validate GraphDB endpoint
            host_query = """
            PREFIX ns1: <https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#>
            SELECT ?host WHERE {
                ?s ns1:host ?host .
            }
            """
            try:
                results = g.query(host_query)
                host = next(iter(results))[0].value
            except Exception as e:
                msg = f"Failed to extract host from config: {str(e)}. Please ensure the config contains a valid ns1:host property."
                self._add_check(report, 'host_extraction', False, msg)
                ttl_snippet = f"""@prefix error: <http://example.org/error# > .\n[] a error:ValidationError ;\n   error:type \"HostExtractionError\" ;\n   error:message \"{ttl_escape(msg)}\" ;\n   error:severity \"CRITICAL\" ;\n   error:timestamp \"{datetime.now().isoformat()}\" ."""
                report['ttl_findings'].append(ttl_snippet)
                log_debug_dump(f"Host extraction error: {traceback.format_exc()}")
                return False, report
            
            # Check if host is overridden by environment
            graphdb_url = os.environ.get("GRAPHDB_URL", host)
            self._add_check(report, 'graphdb_url', True, 
                          f"Using GraphDB endpoint: {graphdb_url}")
            
            # Validate endpoint connectivity with retry
            max_retries = 3
            retry_delay = 1  # seconds
            for attempt in range(max_retries):
                try:
                    url = f"{graphdb_url}/rest/repositories"
                    request_id = self._log_request('GET', url)
                    start = time.perf_counter()
                    response = requests.get(url,
                                          timeout=5)
                    self._log_response(request_id, response, start)
                    response.raise_for_status()
                    self._add_check(report, 'endpoint_connectivity', True,
                                  "Successfully connected to GraphDB endpoint")
                    break
                except requests.exceptions.RequestException as e:
                    msg = f"Failed to connect to GraphDB endpoint ({url}): {str(e)}. Please check the endpoint URL and network connectivity."
                    logger.error(f"[GraphDBValidator][endpoint_connectivity] Exception: {msg}", exc_info=True)
                    log_debug_dump(f"Endpoint connectivity error (attempt {attempt+1}): {traceback.format_exc()}")
                    if attempt == max_retries - 1:
                        self._add_check(report, 'endpoint_connectivity', False, msg)
                        ttl_snippet = f"""@prefix error: <http://example.org/error# > .\n[] a error:ValidationError ;\n   error:type \"EndpointConnectivityError\" ;\n   error:message \"{ttl_escape(msg)}\" ;\n   error:severity \"CRITICAL\" ;\n   error:timestamp \"{datetime.now().isoformat()}\" ."""
                        report['ttl_findings'].append(ttl_snippet)
                        return False, report
                    logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
                    time.sleep(retry_delay)
            
            # Validate against guidance patterns
            try:
                validation_results = self._validate_against_patterns(g)
                for result in validation_results:
                    self._add_check(report, result['name'], result['passed'], result['message'])
            except Exception as e:
                msg = f"Guidance pattern validation failed: {str(e)}. Please check the config and guidance patterns."
                self._add_check(report, 'guidance_pattern_validation', False, msg)
                ttl_snippet = f"""@prefix error: <http://example.org/error# > .\n[] a error:ValidationError ;\n   error:type \"GuidancePatternValidationError\" ;\n   error:message \"{ttl_escape(msg)}\" ;\n   error:severity \"CRITICAL\" ;\n   error:timestamp \"{datetime.now().isoformat()}\" ."""
                report['ttl_findings'].append(ttl_snippet)
                log_debug_dump(f"Guidance pattern validation error: {traceback.format_exc()}")
                return False, report
            
            # Store validation history
            self.validation_history.append(report)
            
            # Export validation report
            self._export_validation_report(report)
            
            return report['is_valid'], report
            
        except Exception as e:
            # Always emit actionable non-mysterious error messages
            msg = f"Unexpected error during validation: {str(e)}. Please check the stack trace for details."
            trace = traceback.format_exc()
            self._add_check(report, 'unexpected_error', False, msg)
            ttl_snippet = f"""@prefix error: <http://example.org/error# > .\n[] a error:ValidationError ;\n   error:type \"UnexpectedError\" ;\n   error:message \"{ttl_escape(msg)}\" ;\n   error:trace \"{ttl_escape(trace)}\" ;\n   error:severity \"CRITICAL\" ;\n   error:timestamp \"{datetime.now().isoformat()}\" ."""
            report['ttl_findings'].append(ttl_snippet)
            log_debug_dump(f"Unexpected error: {trace}")
            return False, report
    
    def _get_environment_info(self) -> Dict:
        """Get current environment information."""
        return {
            'graphdb_url': os.environ.get('GRAPHDB_URL', 'Not set'),
            'graphdb_repository': os.environ.get('GRAPHDB_REPOSITORY', 'Not set'),
            'debug_mode': os.environ.get('BFG9K_DEBUG', 'false').lower() == 'true'
        }
    
    def _validate_against_patterns(self, config_graph: Graph) -> List[Dict]:
        """Validate configuration against guidance patterns."""
        results = []
        
        # Example validation: Check for required properties
        required_props = [
            ('ns1:host', 'GraphDB host'),
            ('ns1:repository', 'Repository name'),
            ('ns1:ontologyPath', 'Ontology path')
        ]
        
        ns1 = Namespace('https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k# ')
        for prop, label in required_props:
            query = f"""
            ASK {{
                ?config a ns1:ServerConfiguration ;
                    {prop} ?value .
            }}
            """
            if not config_graph.query(query).askAnswer:
                results.append({
                    'name': f'required_property_{prop.split(":")[-1]}',
                    'passed': False,
                    'message': f"Missing required property: {label}"
                })
            else:
                results.append({
                    'name': f'required_property_{prop.split(":")[-1]}',
                    'passed': True,
                    'message': f"Found required property: {label}"
                })
        
        return results
    
    def _add_check(self, report: Dict, check_name: str, passed: bool, message: str):
        """Add a check result to the validation report."""
        report['checks'].append({
            'name': check_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        if not passed:
            report['is_valid'] = False
        logger.info(f"Validation check '{check_name}': {message}")
    
    def _export_validation_report(self, report: Dict):
        """Export validation report in multiple formats."""
        try:
            # Create reports directory
            reports_dir = Path("logs/validation_reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Export as JSON
            json_path = reports_dir / f"validation_{timestamp}.json"
            with open(json_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Export as TTL
            ttl_path = reports_dir / f"validation_{timestamp}.ttl"
            g = Graph()
            
            # Add namespaces
            g.bind('spore', URIRef('https://raw.githubusercontent.com/louspringer/spore-ontology/main#'))
            g.bind('bfg', URIRef('https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k# '))
            
            # Create validation report node
            report_uri = URIRef(f"https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#ValidationReport_{timestamp}")
            g.add((report_uri, RDF.type, URIRef('https://raw.githubusercontent.com/louspringer/spore-ontology/main#ValidationReport')))
            g.add((report_uri, RDFS.label, Literal(f"Validation Report {timestamp}")))
            
            # Add checks
            for check in report['checks']:
                check_uri = URIRef(f"{report_uri}#Check_{check['name']}")
                g.add((check_uri, RDF.type, URIRef('https://raw.githubusercontent.com/louspringer/spore-ontology/main# ValidationCheck')))
                g.add((check_uri, RDFS.label, Literal(check['name'])))
                g.add((check_uri, URIRef('https://raw.githubusercontent.com/louspringer/spore-ontology/main#status'), Literal('passed' if check['passed'] else 'failed')))
                g.add((check_uri, RDFS.comment, Literal(check['message'])))
                g.add((check_uri, URIRef('https://raw.githubusercontent.com/louspringer/spore-ontology/main#timestamp'), Literal(check['timestamp'])))
            
            # Add TTL findings
            for snippet in report['ttl_findings']:
                snippet_uri = URIRef(f"{report_uri}#TTLFinding_{uuid.uuid4()}")
                g.add((snippet_uri, RDF.type, URIRef('https://raw.githubusercontent.com/louspringer/spore-ontology/main# TTLFinding')))
                g.add((snippet_uri, RDFS.label, Literal(snippet)))
            
            g.serialize(destination=str(ttl_path), format='turtle')
            
            logger.info(f"Validation report exported to {json_path} and {ttl_path}")
            
        except Exception as e:
            logger.error(f"Failed to export validation report: {e}")
    
    def get_validation_history(self) -> List[Dict]:
        """Get the history of validation checks."""
        return self.validation_history
