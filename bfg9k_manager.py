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

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
BFG9K = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
SH = Namespace("http://www.w3.org/ns/shacl#")

logger = logging.getLogger(__name__)

load_dotenv()

class BFG9KManager:
    def __init__(self, config_path="bfg9k_config.ttl"):
        endpoint = os.environ.get("GRAPHDB_ENDPOINT")
        if endpoint:
            parsed = urlparse(endpoint)
            self.host = parsed.hostname
            self.port = parsed.port or 80
            self.base_url = endpoint.rstrip("/")
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
        """Validate ontology locally using pyshacl and check isomorphism."""
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

        return {
            "shacl_conforms": conforms,
            "shacl_results": results_text,
            "isomorphic": isomorphic
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
        """Update ontology using BFG9K server"""
        url = f"{self.base_url}/update"
        with open(ontology_path, 'rb') as f:
            response = requests.post(url, files={'ontology': f})
        logger.info(f"[update_ontology] POST {url} status={response.status_code}")
        logger.debug(f"[update_ontology] Response headers: {response.headers}")
        logger.debug(f"[update_ontology] Response text: {response.text[:500]}")
        try:
            return response.json()
        except Exception as e:
            logger.error(f"[update_ontology] Failed to decode JSON: {e}")
            logger.error(f"[update_ontology] Raw response: {response.text}")
            return {"error": "Invalid JSON response", "raw_response": response.text, "status_code": response.status_code}
    
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
    main() 