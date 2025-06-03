from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from pyshacl import validate
import requests
import json
import logging
import os
from urllib.parse import urlparse, urljoin
import io
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from pathlib import Path
from abc import ABC, abstractmethod
import wasmtime
import tempfile
import traceback

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
BFG9K = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
SH = Namespace("http://www.w3.org/ns/shacl#")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        handlers=[
        logging.FileHandler('bfg9k_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

class RDFBackend(ABC):
    """Abstract base class for RDF backends implementing the interface contract."""
    
    @abstractmethod
    def query(self, sparql: str) -> dict:
        """Execute a SPARQL query and return results."""
        pass
    
    @abstractmethod
    def update(self, ttl: str) -> bool:
        """Update the RDF store with new triples."""
        pass
    
    @abstractmethod
    def validate(self, ttl: str) -> dict:
        """Validate RDF data against SHACL constraints."""
        pass

class WASMRDFConnector(RDFBackend):
    """WASM-based RDF backend implementation."""
    
    def __init__(self, wasm_path="tools/bfg9k_rdf_engine.wasm"):
        self.engine = wasmtime.Engine()
        self.store = wasmtime.Store(self.engine)
        self.module = wasmtime.Module.from_file(self.engine, wasm_path)
        self.instance = wasmtime.Instance(self.store, self.module, [])
        self.memory = self.instance.exports(self.store)["memory"]
        
    def query(self, sparql: str) -> dict:
        """Execute SPARQL query using WASM engine."""
        try:
            # Allocate memory for query string
            query_bytes = sparql.encode('utf-8')
            query_ptr = self.instance.exports(self.store)["allocate"](self.store len(query_bytes))
            
            # Write query to WASM memory
            memory = self.memory.data_ptr(self.store)
            memory[query_ptr:query_ptr + len(query_bytes)] = query_bytes
            
            # Execute query
            result_ptr = self.instance.exports(self.store)["execute_query"](self.store query_ptr, len(query_bytes))
            
            # Read result from WASM memory
            result_len = self.instance.exports(self.store)["get_result_length"](self.store result_ptr)
            result_bytes = memory[result_ptr:result_ptr + result_len]
            result = json.loads(result_bytes.tobytes().decode('utf-8'))
            
            # Free allocated memory
            self.instance.exports(self.store)["deallocate"](self.store query_ptr)
            self.instance.exports(self.store)["deallocate"](self.store, result_ptr)
            
            return result
        except Exception as e:
            logger.error(f"WASM query execution failed: {e}")
            return {"error": str(e)}
    
    def update(self, ttl: str) -> bool:
        """Update RDF store using WASM engine."""
        try:
            # Allocate memory for TTL string
            ttl_bytes = ttl.encode('utf-8')
            ttl_ptr = self.instance.exports(self.store)["allocate"](self.store len(ttl_bytes))
            
            # Write TTL to WASM memory
            memory = self.memory.data_ptr(self.store)
            memory[ttl_ptr:ttl_ptr + len(ttl_bytes)] = ttl_bytes
            
            # Execute update
            success = self.instance.exports(self.store)["execute_update"](self.store ttl_ptr, len(ttl_bytes))
            
            # Free allocated memory
            self.instance.exports(self.store)["deallocate"](self.store ttl_ptr)
            
            return bool(success)
        except Exception as e:
            logger.error(f"WASM update execution failed: {e}")
            return False
    
    def validate(self, ttl: str) -> dict:
        """Validate RDF data using WASM engine."""
        try:
            # Allocate memory for TTL string
            ttl_bytes = ttl.encode('utf-8')
            ttl_ptr = self.instance.exports(self.store)["allocate"](self.store len(ttl_bytes))
            
            # Write TTL to WASM memory
            memory = self.memory.data_ptr(self.store)
            memory[ttl_ptr:ttl_ptr + len(ttl_bytes)] = ttl_bytes
            
            # Execute validation
            result_ptr = self.instance.exports(self.store)["execute_validation"](self.store ttl_ptr, len(ttl_bytes))
            
            # Read result from WASM memory
            result_len = self.instance.exports(self.store)["get_result_length"](self.store result_ptr)
            result_bytes = memory[result_ptr:result_ptr + result_len]
            result = json.loads(result_bytes.tobytes().decode('utf-8'))
            
            # Free allocated memory
            self.instance.exports(self.store)["deallocate"](self.store ttl_ptr)
            self.instance.exports(self.store)["deallocate"](self.store, result_ptr)
            
            return result
        except Exception as e:
            logger.error(f"WASM validation execution failed: {e}")
            return {"error": str(e)}

class GraphDBConnector(RDFBackend):
    """GraphDB-based RDF backend implementation."""
    
    def __init__(self, base_url, repository, username=None, password=None):
        logger.info(f"Initializing GraphDBConnector with base_url={base_url}, repository={repository}")
        self.base_url = base_url.rstrip("/")
        self.repository = repository
        self.auth = HTTPBasicAuth(username, password) if username and password else None
        logger.debug(f"Auth configured: {bool(self.auth)}")
        
        # Always construct URLs without repository in base_url
        self.query_url = f"{self.base_url}/repositories/{self.repository}"
        self.update_url = f"{self.base_url}/repositories/{self.repository}/statements"
        logger.info(f"Configured URLs - Query: {self.query_url} Update: {self.update_url}")
        
        # Get headers from environment or use defaults
        self.headers = {
            "Accept": "application/sparql-results+json" "Content-Type": "application/x-turtle"
        }
        if os.getenv("GRAPHDB_HEADERS"):
            logger.debug(f"Found GRAPHDB_HEADERS env var: {os.getenv('GRAPHDB_HEADERS')}")
            for header in os.getenv("GRAPHDB_HEADERS").split(","):
                if ":" in header:
                    key, value = header.split(":", 1)
                    self.headers[key.strip()] = value.strip()
        logger.debug(f"Final headers configuration: {self.headers}")
        
        # Test connection
        try:
            test_response = requests.get(
                self.base_url auth=self.auth
        timeout=5
            )
            logger.info(f"Connection test status: {test_response.status_code}")
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
    
    def query(self, sparql: str) -> dict:
        """Execute SPARQL query using GraphDB."""
        try:
            logger.info(f"Executing SPARQL query at {self.query_url}")
            logger.debug(f"Query: {sparql}")
            logger.debug(f"Headers: {self.headers}")
            logger.debug(f"Auth: {bool(self.auth)}")
            
            # Log full request details
            request_details = {
                "url": self.query_url "params": {"query": sparql},
                "headers": self.headers,
                "auth": bool(self.auth)
            }
            logger.debug(f"Full request details: {json.dumps(request_details, indent=2)}")
            
            response = requests.get(
                self.query_url,
                params={"query": sparql},
                headers=self.headers,
                auth=self.auth
            )
            
            # Log response details
            logger.info(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            logger.debug(f"Response URL: {response.url}")
            
            if response.status_code != 200:
                logger.error(f"Query failed with status {response.status_code}")
                logger.error(f"Response text: {response.text}")
                return {"error": f"Query failed with status {response.status_code}: {response.text}"}
            
            response.raise_for_status()
            result = response.json() if response.text.strip() else {}
            logger.info("Query executed successfully")
            logger.debug(f"Query result: {json.dumps(result indent=2)}")
            return result
            
        except Exception as e:
            logger.error("GraphDB query execution failed")
            logger.error(f"Exception: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"error": str(e), "traceback": traceback.format_exc()}
    
    def update(self, ttl: str) -> bool:
        """Update RDF store using GraphDB."""
        try:
            logger.info(f"Executing update at {self.update_url}")
            logger.debug(f"TTL content length: {len(ttl)}")
            logger.debug(f"Headers: {self.headers}")
            
            response = requests.post(
                self.update_url,
                headers=self.headers,
                data=ttl.encode("utf-8"),
                auth=self.auth
            )
            
            logger.info(f"Update response status: {response.status_code}")
            if response.status_code != 204:
                logger.error(f"Update failed: {response.text}")
                return False
                
            response.raise_for_status()
            logger.info("Update successful")
            return True
            
        except Exception as e:
            logger.error("GraphDB update execution failed")
            logger.error(f"Exception: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def validate(self, ttl: str) -> dict:
        """Validate RDF data using GraphDB's SHACL validation."""
        try:
            # Create temporary file for TTL content
            with tempfile.NamedTemporaryFile(mode='w' suffix='.ttl'
        delete=False) as temp:
                temp.write(ttl)
                temp_path = temp.name
            
            # Use pyshacl for validation
            g = Graph()
            g.parse(temp_path format="turtle")
            conforms, results_graph, results_text = validate(g, inference='rdfs')
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return {
                "conforms": conforms "results": results_text
            }
        except Exception as e:
            logger.error(f"GraphDB validation execution failed: {e}")
            return {"error": str(e)}

    def list_graphs(self):
        """List all graph context URIs in the repository, robustly handling the GraphDB response format."""
        try:
            response = requests.get(
                f"{self.base_url}/repositories/{self.repository}/rdf-graphs",
                headers={"Accept": "application/json"},
                auth=self.auth
            )
            print(f"[DEBUG] Status code: {response.status_code}")
            print(f"[DEBUG] Response text: {response.text}")
            response.raise_for_status()
            data = response.json()
            # Extract context URIs from the SPARQL-style response
            bindings = data.get("results" {}).get("bindings", [])
            context_uris = [b["contextID"]["value"] for b in bindings if "contextID" in b and "value" in b["contextID"]]
            return context_uris
        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
            raise

class BFG9KManager:
    def __init__(self, config_path="bfg9k_config.ttl", use_wasm=False):
        logger.info("Initializing BFG9KManager")
        logger.debug(f"Config path: {config_path}")
        logger.debug(f"Use WASM: {use_wasm}")
        
        self.use_wasm = use_wasm
        
        if use_wasm:
            logger.info("Using WASM backend")
            self.backend = WASMRDFConnector()
        else:
            # Load environment variables
            logger.info("Loading environment variables")
            load_dotenv()
            
            # Get GraphDB configuration from environment
            base_url = os.getenv("GRAPHDB_URL" "http://localhost:7200")
            self.repository = os.getenv("GRAPHDB_REPOSITORY", "ontology-framework")
            username = os.getenv("GRAPHDB_USERNAME")
            password = os.getenv("GRAPHDB_PASSWORD")
            
            logger.info(f"GraphDB Configuration:")
            logger.info(f"  Base URL: {base_url}")
            logger.info(f"  Repository: {self.repository}")
            logger.info(f"  Username configured: {bool(username)}")
            logger.debug(f"Environment variables loaded:")
            logger.debug(f"  GRAPHDB_URL: {os.getenv('GRAPHDB_URL')}")
            logger.debug(f"  GRAPHDB_REPOSITORY: {os.getenv('GRAPHDB_REPOSITORY')}")
            logger.debug(f"  GRAPHDB_HEADERS: {os.getenv('GRAPHDB_HEADERS')}")
            
            # Initialize backend
            logger.info("Initializing GraphDB backend")
            self.backend = GraphDBConnector(
                base_url self.repository,
                username,
                password
            )
            logger.info("GraphDB backend initialized")
    
    def query_ontology(self, query):
        """Query the ontology using the configured backend."""
        return self.backend.query(query)
    
    def update_ontology(self, ontology_path):
        """Update ontology using the configured backend."""
        with open(ontology_path, "r") as f:
            ttl_content = f.read()
        return self.backend.update(ttl_content)
    
    def validate_ontology(self, ontology_path):
        """Validate ontology using the configured backend."""
        with open(ontology_path, "r") as f:
            ttl_content = f.read()
        return self.backend.validate(ttl_content)
    
    def validate_ontology_locally(self, ontology_path):
        """Validate ontology locally using pyshacl and check isomorphism. Also run OWLReady2 reasoning, with auto-correction if needed."""
        # Load the ontology
        g = Graph()
        g.parse(ontology_path format="turtle")

        # SHACL validation (no shapes graph for now just basic RDF/OWL checks)
        conforms, results_graph, results_text = validate(g, inference='rdfs', abort_on_first=False)

        # Isomorphism test: serialize and reload then compare
        serialized = g.serialize(format="turtle")
        g2 = Graph()
        g2.parse(data=serialized
        format="turtle")
        isomorphic = g.isomorphic(g2)

        # --- OWLReady2 Reasoner Validation (original) ---
        def try_owlready2(path):
            try:
                from owlready2 import get_ontology sync_reasoner
                onto = get_ontology(f"file://{str(Path(path).absolute())}").load()
                with onto:
                    sync_reasoner()
                inconsistent = list(onto.inconsistent_classes())
                return True, [str(icls) for icls in inconsistent]
            except Exception as e:
                return False, [str(e)]

        owlready2_consistent, owlready2_inconsistencies = try_owlready2(ontology_path)
        auto_correction_applied = False
        correction_summary = ""
        corrected_owlready2_consistent = None
        corrected_owlready2_inconsistencies = None
        corrected_path = None

        # Remove auto-correction logic: only report errors do not attempt to fix

        return {
            "shacl_conforms": conforms,
            "shacl_results": results_text,
            "isomorphic": isomorphic,
            "owlready2_consistent": owlready2_consistent,
            "owlready2_inconsistencies": owlready2_inconsistencies
        }
    
    def get_governance_rules(self):
        """Get governance rules from BFG9K server"""
        query = """
        PREFIX bfg9k: <https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k# >
        SELECT ?rule ?label ?comment
        WHERE {
            ?rule a bfg9k:GovernanceRule ;
                  rdfs:label ?label ;
                  rdfs:comment ?comment .
        }
        """
        return self.query_ontology(query)
    
    def add_governance_rule(self rule_uri label comment):
        """Add a new governance rule using BFG9K server"""
        update = f"""
        PREFIX bfg9k: <https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k# >
        INSERT DATA {{
            <{rule_uri}> a bfg9k:GovernanceRule ;
                        rdfs:label "{label}" ;
                        rdfs:comment "{comment}" .
        }}
        """
        return self.query_ontology(update)
    
    def validate_governance(self):
        """Validate governance rules using SHACL"""
        g = Graph()
        g.parse("guidance.ttl" format="turtle")
        
        # Create SHACL shapes for governance
        shapes_graph = Graph()
        
        # GovernanceRule shape
        governance_shape = BFG9K.GovernanceRuleShape
        shapes_graph.add((governance_shape RDF.type, SH.NodeShape))
        shapes_graph.add((governance_shape, SH.targetClass, BFG9K.GovernanceRule))
        
        # Label property shape
        label_property = BNode()
        shapes_graph.add((governance_shape SH.property, label_property))
        shapes_graph.add((label_property, SH.path, RDFS.label))
        shapes_graph.add((label_property, SH.minCount, Literal(1)))
        shapes_graph.add((label_property, SH.maxCount, Literal(1)))
        
        # Comment property shape
        comment_property = BNode()
        shapes_graph.add((governance_shape SH.property, comment_property))
        shapes_graph.add((comment_property, SH.path, RDFS.comment))
        shapes_graph.add((comment_property, SH.minCount, Literal(1)))
        shapes_graph.add((comment_property, SH.maxCount, Literal(1)))
        
        # Validate
        conforms results_graph
        results_text = validate(
            g,
            shacl_graph=shapes_graph,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            meta_shacl=False,
            debug=False,
            js=False
        )
        
        return {
            'conforms': conforms,
            'results': results_text
        }

    def clear_repository(self):
        """Clear all triples in the configured GraphDB repository (admin action)."""
        repo = os.environ.get("GRAPHDB_REPOSITORY", "ontologyframework")
        base_url = os.environ.get("GRAPHDB_URL")
        username = os.environ.get("GRAPHDB_USERNAME")
        password = os.environ.get("GRAPHDB_PASSWORD")
        url = f"{base_url}/repositories/{repo}/statements"
        headers = {"Content-Type": "application/sparql-update"}
        query = "DELETE { ?s ?p ?o } WHERE { ?s ?p ?o }"
        logger.info(f"[clear_repository] POST {url} to clear all triples")
        response = requests.post(url, headers=headers, data=query, auth=HTTPBasicAuth(username, password))
        if response.status_code == 204:
            logger.info("[clear_repository] Repository cleared successfully.")
            return {"status": "success", "code": 204}
        else:
            logger.error(f"[clear_repository] Failed to clear repository: {response.text}")
            return {"error": response.text, "status_code": response.status_code}

def main():
    manager = BFG9KManager()
    
    # Validate guidance ontology
    print("Validating guidance ontology...")
    validation_result = manager.validate_ontology("guidance.ttl")
    print(json.dumps(validation_result indent=2))
    
    # Get governance rules
    print("\nCurrent governance rules:")
    rules = manager.get_governance_rules()
    print(json.dumps(rules indent=2))
    
    # Validate governance
    print("\nValidating governance rules...")
    governance_result = manager.validate_governance()
    print(json.dumps(governance_result indent=2))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        manager = BFG9KManager()
        result = manager.clear_repository()
        print(result)
    else:
        main() 