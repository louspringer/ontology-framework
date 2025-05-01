from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
import json
import os

# Define namespaces
MCP = Namespace("http://example.org/mcp#")
BFG9K = Namespace("http://example.org/bfg9k#")
SH = Namespace("http://www.w3.org/ns/shacl#")

def update_mcp_config():
    # Load the guidance ontology
    guidance_graph = Graph()
    guidance_graph.parse("guidance.ttl", format="turtle")
    
    # Create a new graph for MCP configuration
    mcp_graph = Graph()
    
    # Add MCP server configuration
    mcp_server = BNode()
    mcp_graph.add((mcp_server, RDF.type, MCP.MCPServer))
    mcp_graph.add((mcp_server, MCP.serverType, Literal("BFG9K")))
    mcp_graph.add((mcp_server, MCP.port, Literal(8080, datatype=XSD.integer)))
    mcp_graph.add((mcp_graph, MCP.host, Literal("localhost")))
    mcp_graph.add((mcp_graph, MCP.ontologyPath, Literal("guidance.ttl")))
    
    # Add validation rules
    validation_rules = BNode()
    mcp_graph.add((validation_rules, RDF.type, MCP.ValidationRules))
    
    # Add ontology structure validation
    ontology_structure = BNode()
    mcp_graph.add((ontology_structure, RDF.type, MCP.OntologyStructure))
    mcp_graph.add((ontology_structure, MCP.requiredClasses, Literal("ValidationRule,ValidationPattern,ConsistencyRule,SemanticRule,SyntaxRule,SecurityRule,ComplianceRule")))
    mcp_graph.add((ontology_structure, MCP.requiredProperties, Literal("hasMessage,hasPriority,hasTarget,hasValidator,hasSecurityLevel,hasComplianceLevel")))
    mcp_graph.add((ontology_structure, MCP.requiredShapes, Literal("ValidationPatternShape,ValidationRuleShape,SecurityRuleShape,ComplianceRuleShape")))
    
    # Add BFG9K validation pattern
    bfg9k_pattern = BNode()
    mcp_graph.add((bfg9k_pattern, RDF.type, MCP.ValidationPattern))
    mcp_graph.add((bfg9k_pattern, MCP.patternType, Literal("BFG9K")))
    mcp_graph.add((bfg9k_pattern, MCP.message, Literal("Big Friendly Giant 9000 validation pattern")))
    mcp_graph.add((bfg9k_pattern, MCP.priority, Literal("HIGH")))
    mcp_graph.add((bfg9k_pattern, MCP.validator, Literal("validateBFG9K")))
    
    # Add validation strategy
    strategy = BNode()
    mcp_graph.add((strategy, RDF.type, MCP.ValidationStrategy))
    
    # Add strategy steps
    exact_match = BNode()
    mcp_graph.add((exact_match, RDF.type, MCP.StrategyStep))
    mcp_graph.add((exact_match, MCP.stepType, Literal("ExactMatch")))
    mcp_graph.add((exact_match, MCP.message, Literal("Check for exact matches in validation rules")))
    mcp_graph.add((exact_match, MCP.priority, Literal("HIGH")))
    
    similarity_match = BNode()
    mcp_graph.add((similarity_match, RDF.type, MCP.StrategyStep))
    mcp_graph.add((similarity_match, MCP.stepType, Literal("SimilarityMatch")))
    mcp_graph.add((similarity_match, MCP.message, Literal("Check for similar patterns in validation rules")))
    mcp_graph.add((similarity_match, MCP.priority, Literal("MEDIUM")))
    
    llm_select = BNode()
    mcp_graph.add((llm_select, RDF.type, MCP.StrategyStep))
    mcp_graph.add((llm_select, MCP.stepType, Literal("LLMSelect")))
    mcp_graph.add((llm_select, MCP.message, Literal("Use LLM for complex pattern matching")))
    mcp_graph.add((llm_select, MCP.priority, Literal("LOW")))
    
    # Add security rules
    security = BNode()
    mcp_graph.add((security, RDF.type, MCP.SecurityRules))
    mcp_graph.add((security, MCP.enabled, Literal(True, datatype=XSD.boolean)))
    
    # Add compliance rules
    compliance = BNode()
    mcp_graph.add((compliance, RDF.type, MCP.ComplianceRules))
    mcp_graph.add((compliance, MCP.enabled, Literal(True, datatype=XSD.boolean)))
    
    # Save the MCP configuration
    mcp_config = {
        "core": {
            "validation": {
                "enabled": True,
                "requirePhaseOrder": True,
                "requireContext": True,
                "requireServerConfig": True,
                "dryRun": False,
                "backupEnabled": True
            },
            "validationRules": {
                "ontologyStructure": {
                    "requiredClasses": ["ValidationRule", "ValidationPattern", "ConsistencyRule", "SemanticRule", "SyntaxRule", "SecurityRule", "ComplianceRule"],
                    "requiredProperties": ["hasMessage", "hasPriority", "hasTarget", "hasValidator", "hasSecurityLevel", "hasComplianceLevel"],
                    "requiredShapes": ["ValidationPatternShape", "ValidationRuleShape", "SecurityRuleShape", "ComplianceRuleShape"]
                }
            }
        },
        "adapters": {
            "ide": {
                "servers": {
                    "bfg9k": {
                        "url": "http://localhost:8080",
                        "type": "bfg9k"
                    }
                }
            }
        },
        "metadata": {
            "project": "ontology-framework",
            "version": "1.0.0",
            "description": "Unified MCP Configuration with BFG9K",
            "timestamp": "2024-03-21T10:00:00Z",
            "author": "ontology-framework-team"
        },
        "logging": {
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": ".cursor/mcp.log"
        },
        "mcpServers": {
            "bfg9k": {
                "url": "http://localhost:8080",
                "type": "bfg9k"
            }
        }
    }
    
    # Save the configuration
    with open(".cursor/mcp.json", "w") as f:
        json.dump(mcp_config, f, indent=2)
    
    # Save the BFG9K-specific configuration
    with open(".cursor/mcp_bfg9k.json", "w") as f:
        json.dump(mcp_config, f, indent=2)

if __name__ == "__main__":
    update_mcp_config() 