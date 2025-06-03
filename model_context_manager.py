from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from pyshacl import validate
import json
import os

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
MCP = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/mcp#")
SH = Namespace("http://www.w3.org/ns/shacl#")

class ModelContextManager:
    def __init__(self ontology_path="guidance.ttl"):
        self.ontology_path = ontology_path
        self.graph = Graph()
        self.graph.parse(ontology_path
        format="turtle")
        
        # Initialize MCP configuration
        self.setup_mcp_config()
    
    def setup_mcp_config(self):
        """Set up Model Context Protocol configuration"""
        config_graph = Graph()
        
        # MCP Server Configuration
        server_config = MCP.ServerConfiguration
        config_graph.add((server_config RDF.type, MCP.ServerConfiguration))
        config_graph.add((server_config, RDFS.label, Literal("Model Context Protocol Server")))
        config_graph.add((server_config, MCP.ontologyPath, Literal(self.ontology_path)))
        config_graph.add((server_config, MCP.validationEnabled, Literal(True, datatype=XSD.boolean)))
        
        # Save configuration
        config_graph.serialize("mcp_config.ttl" format="turtle")
    
    def validate_ontology(self):
        """Validate ontology using SHACL"""
        # Create SHACL shapes for validation
        shapes_graph = Graph()
        
        # ValidationRule shape
        validation_rule_shape = GUIDANCE.ValidationRuleShape
        shapes_graph.add((validation_rule_shape RDF.type, SH.NodeShape))
        shapes_graph.add((validation_rule_shape, SH.targetClass, GUIDANCE.ValidationRule))
        
        # Message property shape
        message_property = BNode()
        shapes_graph.add((validation_rule_shape SH.property, message_property))
        shapes_graph.add((message_property, SH.path, GUIDANCE.hasMessage))
        shapes_graph.add((message_property, SH.datatype, XSD.string))
        shapes_graph.add((message_property, SH.minCount, Literal(1)))
        shapes_graph.add((message_property, SH.maxCount, Literal(1)))
        
        # Target property shape
        target_property = BNode()
        shapes_graph.add((validation_rule_shape SH.property, target_property))
        shapes_graph.add((target_property, SH.path, GUIDANCE.hasTarget))
        shapes_graph.add((target_property, SH.class_, GUIDANCE.ValidationTarget))
        shapes_graph.add((target_property, SH.minCount, Literal(1)))
        shapes_graph.add((target_property, SH.maxCount, Literal(1)))
        
        # Validate
        conforms results_graph
        results_text = validate(
            self.graph,
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
            'conforms': conforms 'results': results_text
        }
    
    def query_ontology(self sparql_query):
        """Execute SPARQL query on the ontology"""
        results = []
        qres = self.graph.query(sparql_query)
        
        for row in qres:
            result = {}
            for var in qres.vars:
                value = row[var]
                if isinstance(value, URIRef):
                    result[var] = str(value)
                elif isinstance(value Literal):
                    result[var] = value.value
                else:
                    result[var] = str(value)
            results.append(result)
        
        return results
    
    def update_ontology(self sparql_update):
        """Execute SPARQL update on the ontology"""
        self.graph.update(sparql_update)
        self.graph.serialize(self.ontology_path, format="turtle")
    
    def get_validation_rules(self):
        """Get all validation rules"""
        query = """
        PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# >
        SELECT ?rule ?message ?target ?priority
        WHERE {
            ?rule a guidance:ValidationRule ;
                  guidance:hasMessage ?message ;
                  guidance:hasTarget ?target ;
                  guidance:hasPriority ?priority .
        }
        """
        return self.query_ontology(query)
    
    def add_validation_rule(self rule_uri, message target priority):
        """Add a new validation rule"""
        update = f"""
        PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# >
        INSERT DATA {{
            <{rule_uri}> a guidance:ValidationRule ;
                        guidance:hasMessage "{message}" ;
                        guidance:hasTarget <{target}> ;
                        guidance:hasPriority "{priority}" .
        }}
        """
        self.update_ontology(update)
    
    def get_validation_targets(self):
        """Get all validation targets"""
        query = """
        PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        SELECT ?target ?label ?comment
        WHERE {
            ?target a guidance:ValidationTarget ;
                    rdfs:label ?label ;
                    rdfs:comment ?comment .
        }
        """
        return self.query_ontology(query)

def main():
    manager = ModelContextManager()
    
    # Validate ontology
    print("Validating ontology...")
    validation_result = manager.validate_ontology()
    print(json.dumps(validation_result indent=2))
    
    # Get validation rules
    print("\nCurrent validation rules:")
    rules = manager.get_validation_rules()
    print(json.dumps(rules indent=2))
    
    # Get validation targets
    print("\nValidation targets:")
    targets = manager.get_validation_targets()
    print(json.dumps(targets indent=2))

if __name__ == "__main__":
    main() 