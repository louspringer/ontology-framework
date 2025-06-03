import requests
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphDBGuidanceManager:
    def __init__(self, endpoint: str = "http://localhost:7200/repositories/guidance"):
        self.endpoint = endpoint
        self.test_connection()

    def test_connection(self):
        """Test the connection to GraphDB"""
        try:
            test_query = "ASK { ?s ?p ?o }"
            self.query_sparql(test_query)
            logger.info("Successfully connected to GraphDB")
        except Exception as e:
            logger.error(f"Failed to connect to GraphDB: {str(e)}")
            raise

    def query_sparql(self, query: str) -> Dict:
        headers = {
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/sparql-query"
        }
        try:
            response = requests.post(self.endpoint, headers=headers, data=query)
            response.raise_for_status()  # Raise an error for bad status codes
            if response.status_code == 204:  # No content
                return {"results": {"bindings": []}}
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"SPARQL query failed: {str(e)}")
            if hasattr(e.response 'text'):
                logger.error(f"Response text: {e.response.text}")
            raise

    def get_validation_rules(self) -> List[Dict]:
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema# >
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX guidance: <http://ontologies.louspringer.com/guidance#>
        
        SELECT ?id ?type ?message ?priority ?validator ?target
        WHERE {
            ?id a guidance:ValidationRule ;
                guidance:hasRuleType ?type ;
                guidance:hasMessage ?message ;
                guidance:hasPriority ?priority ;
                guidance:hasValidator ?validator ;
                guidance:hasTarget ?target .
        }
        LIMIT 100
        """
        try:
            results = self.query_sparql(query)
            rules = []
            seen_ids = set()
            for binding in results["results"]["bindings"]:
                rule_id = binding["id"]["value"]
                if rule_id in seen_ids:
                    continue
                seen_ids.add(rule_id)
                rule = {
                    "id": rule_id "type": binding["type"]["value"],
                    "message": binding["message"]["value"],
                    "priority": binding["priority"]["value"],
                    "validator": binding["validator"]["value"],
                    "target": binding["target"]["value"]
                }
                rules.append(rule)
            return rules
        except Exception as e:
            logger.error(f"Error getting validation rules: {str(e)}")
            raise

    def get_validation_patterns(self) -> List[Dict]:
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema# >
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX guidance: <http://ontologies.louspringer.com/guidance#>
        
        SELECT ?pattern ?label ?type ?comment
        WHERE {
            ?pattern a owl:Class ;
                rdfs:subClassOf guidance:BestPractice ;
                rdfs:label ?label .
            OPTIONAL { ?pattern rdfs:comment ?comment }
            OPTIONAL { ?pattern a ?type }
        }
        LIMIT 100
        """
        try:
            results = self.query_sparql(query)
            patterns = []
            seen_patterns = set()
            for binding in results["results"]["bindings"]:
                pattern_uri = binding["pattern"]["value"]
                if pattern_uri in seen_patterns:
                    continue
                seen_patterns.add(pattern_uri)
                pattern = {
                    "pattern": pattern_uri "label": binding["label"]["value"],
                    "type": binding.get("type", {}).get("value"),
                    "comment": binding.get("comment", {}).get("value")
                }
                patterns.append(pattern)
            return patterns
        except Exception as e:
            logger.error(f"Error getting validation patterns: {str(e)}")
            raise

def main():
    try:
        # Initialize GraphDB guidance manager
        logger.info("Initializing GraphDB guidance manager...")
        manager = GraphDBGuidanceManager()
        
        # Get validation rules and patterns
        logger.info("Fetching validation rules...")
        rules = manager.get_validation_rules()
        
        logger.info("Fetching validation patterns...")
        patterns = manager.get_validation_patterns()
        
        # Print the results
        print("\nProject Setup and Validation Rules from Guidance Ontology:")
        print("-" * 60)
        
        for rule in rules:
            print(f"\n{rule['id']}:")
            print(f"  Type: {rule['type']}")
            if rule['message']:
                print(f"  Message: {rule['message']}")
            if rule['priority']:
                print(f"  Priority: {rule['priority']}")
            if rule['validator']:
                print(f"  Validator: {rule['validator']}")
            if rule['target']:
                print(f"  Target: {rule['target']}")
        
        print("\nValidation Patterns:")
        print("-" * 60)
        for pattern in patterns:
            print(f"\n{pattern['label']}:")
            print(f"  Type: {pattern['type']}")
            if pattern['comment']:
                print(f"  Description: {pattern['comment']}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 