from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from pyshacl import validate
import requests
import json
import logging
import os
from urllib.parse import urlparse
import io
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from pathlib import Path

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
BFG9K = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
SH = Namespace("http://www.w3.org/ns/shacl#")

logger = logging.getLogger(__name__)

load_dotenv()

class BFG9KManager:
    def __init__(self, config_path="bfg9k_config.ttl"):
        base_url = os.environ.get("GRAPHDB_URL")
        if base_url:
            parsed = urlparse(base_url)
            self.host = parsed.hostname
            self.port = parsed.port or 80
            self.base_url = base_url.rstrip("/")
        else:
            print(f"[DEBUG] BFG9KManager loading config from: {config_path}")
            self.config = Graph()
            self.config.parse(config_path, format="turtle")
            
            # Get server configuration
            server_config = self.config.value(predicate=RDF.type, object=BFG9K.ServerConfiguration)
            self.host = str(self.config.value(server_config, BFG9K.host))
            self.port = int(self.config.value(server_config, BFG9K.port))
            self.base_url = f"http://{self.host}:{self.port}"
        self.repository = os.environ.get("GRAPHDB_REPOSITORY", "ontologyframework")
        self.guidance_endpoint = f"{self.base_url}/repositories/{self.repository}/guidance#"
    
    def validate_ontology(self, ontology_path):
        """Validate ontology locally using pyshacl and check isomorphism. Also run OWLReady2 reasoning, with auto-correction if needed."""
        # Load the ontology
        g = Graph()
        g.parse(ontology_path, format="turtle")

        # SHACL validation (no shapes graph for now, just basic RDF/OWL checks)
        conforms, results_graph, results_text = validate(g, inference='rdfs', abort_on_first=False)

        # Isomorphism test: serialize and reload, then compare
        serialized = g.serialize(format="turtle")
        g2 = Graph()
        g2.parse(data=serialized, format="turtle")
        isomorphic = g.isomorphic(g2)

        # --- OWLReady2 Reasoner Validation (original) ---
        def try_owlready2(path):
            try:
                from owlready2 import get_ontology, sync_reasoner
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

        # Remove auto-correction logic: only report errors, do not attempt to fix

        return {
            "shacl_conforms": conforms,
            "shacl_results": results_text,
            "isomorphic": isomorphic,
            "owlready2_consistent": owlready2_consistent,
            "owlready2_inconsistencies": owlready2_inconsistencies
        }
    
    def query_ontology(self, query):
        """Query the ontology using SPARQL."""
        try:
            response = requests.post(
                f"{self.base_url}/repositories/{self.repository}/statements",
                data={"query": query},
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            if not response.text.strip():
                logger.warning("Empty response received from GraphDB")
                return {}
            
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response: {e}")
                logger.debug(f"Response content: {response.text}")
                return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query GraphDB: {e}")
            return {}
    
    def update_ontology(self, ontology_path):
        """Update ontology using GraphDB server (not /update endpoint)"""
        repo = os.environ.get("GRAPHDB_REPOSITORY", "guidance")
        username = os.environ.get("GRAPHDB_USERNAME")
        password = os.environ.get("GRAPHDB_PASSWORD")
        base_uri = os.environ.get("GRAPHDB_BASE_URI", "https://raw.githubusercontent.com/louspringer/ontology-framework/main")
        if not username or not password:
            raise RuntimeError("GRAPHDB_USERNAME and GRAPHDB_PASSWORD must be set in environment.")
        url = f"{self.base_url}/repositories/{repo}/statements"
        headers = {"Content-Type": "application/x-turtle"}
        logger.info(f"[update_ontology] POST {url} with file {ontology_path}")
        # Parse and serialize with base URI
        with open(ontology_path, "r") as f:
            raw_ttl = f.read()
        logger.debug(f"[update_ontology] Raw Turtle from file (first 500 chars): {raw_ttl[:500]}")
        g = Graph()
        g.parse(ontology_path, format="turtle", publicID=base_uri)
        logger.debug(f"[update_ontology] Parsed graph has {len(g)} triples")
        data = g.serialize(format="turtle", base=base_uri)
        logger.debug(f"[update_ontology] Serialized Turtle (first 500 chars): {data[:500]}")
        try:
            response = requests.post(url, headers=headers, data=data.encode("utf-8"), auth=HTTPBasicAuth(username, password))
            logger.info(f"[update_ontology] Response status: {response.status_code}")
            logger.debug(f"[update_ontology] Response headers: {response.headers}")
            logger.debug(f"[update_ontology] Response text: {response.text[:500]}")
            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            elif response.status_code == 204:
                return {"status": "success", "code": 204}
            else:
                return {"error": "Non-JSON response", "raw_response": response.text, "status_code": response.status_code}
        except Exception as e:
            logger.error(f"[update_ontology] Exception: {e}")
            logger.error(f"[update_ontology] Raw response: {getattr(response, 'text', '')}")
            return {"error": str(e), "raw_response": getattr(response, 'text', ''), "status_code": getattr(response, 'status_code', None)}
    
    def get_governance_rules(self):
        """Get governance rules from BFG9K server"""
        query = """
        PREFIX bfg9k: <https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#>
        SELECT ?rule ?label ?comment
        WHERE {
            ?rule a bfg9k:GovernanceRule ;
                  rdfs:label ?label ;
                  rdfs:comment ?comment .
        }
        """
        return self.query_ontology(query)
    
    def add_governance_rule(self, rule_uri, label, comment):
        """Add a new governance rule using BFG9K server"""
        update = f"""
        PREFIX bfg9k: <https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#>
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
        g.parse("guidance.ttl", format="turtle")
        
        # Create SHACL shapes for governance
        shapes_graph = Graph()
        
        # GovernanceRule shape
        governance_shape = BFG9K.GovernanceRuleShape
        shapes_graph.add((governance_shape, RDF.type, SH.NodeShape))
        shapes_graph.add((governance_shape, SH.targetClass, BFG9K.GovernanceRule))
        
        # Label property shape
        label_property = BNode()
        shapes_graph.add((governance_shape, SH.property, label_property))
        shapes_graph.add((label_property, SH.path, RDFS.label))
        shapes_graph.add((label_property, SH.minCount, Literal(1)))
        shapes_graph.add((label_property, SH.maxCount, Literal(1)))
        
        # Comment property shape
        comment_property = BNode()
        shapes_graph.add((governance_shape, SH.property, comment_property))
        shapes_graph.add((comment_property, SH.path, RDFS.comment))
        shapes_graph.add((comment_property, SH.minCount, Literal(1)))
        shapes_graph.add((comment_property, SH.maxCount, Literal(1)))
        
        # Validate
        conforms, results_graph, results_text = validate(
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
    print(json.dumps(validation_result, indent=2))
    
    # Get governance rules
    print("\nCurrent governance rules:")
    rules = manager.get_governance_rules()
    print(json.dumps(rules, indent=2))
    
    # Validate governance
    print("\nValidating governance rules...")
    governance_result = manager.validate_governance()
    print(json.dumps(governance_result, indent=2))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        manager = BFG9KManager()
        result = manager.clear_repository()
        print(result)
    else:
        main() 