from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from pyshacl import validate
import requests
import json

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
BFG9K = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
SH = Namespace("http://www.w3.org/ns/shacl#")

class BFG9KManager:
    def __init__(self, config_path="bfg9k_config.ttl"):
        self.config = Graph()
        self.config.parse(config_path, format="turtle")
        
        # Get server configuration
        server_config = self.config.value(predicate=RDF.type, object=BFG9K.ServerConfiguration)
        self.host = str(self.config.value(server_config, BFG9K.host))
        self.port = int(self.config.value(server_config, BFG9K.port))
        self.base_url = f"http://{self.host}:{self.port}"
    
    def validate_ontology(self, ontology_path):
        """Validate ontology using BFG9K server"""
        url = f"{self.base_url}/validate"
        with open(ontology_path, 'rb') as f:
            response = requests.post(url, files={'ontology': f})
        return response.json()
    
    def query_ontology(self, sparql_query):
        """Execute SPARQL query using BFG9K server"""
        url = f"{self.base_url}/query"
        response = requests.post(url, json={'query': sparql_query})
        return response.json()
    
    def update_ontology(self, ontology_path):
        """Update ontology using BFG9K server"""
        url = f"{self.base_url}/update"
        with open(ontology_path, 'rb') as f:
            response = requests.post(url, files={'ontology': f})
        return response.json()
    
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