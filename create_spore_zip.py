# !/usr/bin/env python3
"""
Script to create spore_integration_files.zip with updated TTL files
Run this to create the zip file that Claude/Cursor will process
"""

import zipfile
import os
from pathlib import Path

# Updated guidance.ttl content
guidance_ttl = '''@prefix guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

rdf:type rdfs:label "22-rdf-syntax-ns#type" ;
    rdfs:comment "Description of 22-rdf-syntax-ns#type" ;
    rdfs:domain owl:Thing ;
    rdfs:range owl:Thing ;
    owl:versionInfo "1.0.0" .

rdfs:subClassOf rdfs:label "rdf-schema#subClassOf" ;
    rdfs:comment "Description of rdf-schema#subClassOf" ;
    rdfs:domain owl:Thing ;
    rdfs:range owl:Thing ;
    owl:versionInfo "1.0.0" .

guidance: a owl:Ontology ;
    rdfs:label "Guidance Ontology"@en ;
    rdfs:comment "Ontology for managing guidance and validation rules"@en ;
    owl:imports <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/collaboration#> <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/core#>,
        <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/model# > <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/security#>,
        <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation# > <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#> ;
    owl:versionInfo "1.0.0" .

guidance:ClassHierarchyCheck a guidance:ConsistencyRule ;
    guidance:hasMessage "Check for cycles in class hierarchy" ;
    guidance:hasPriority "HIGH" ;
    guidance:hasTarget "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ClassHierarchyCheck"^^xsd:anyURI ;
    guidance:hasValidator "validate_consistency" .

guidance:IntegrationRequirement a owl:Class ;
    rdfs:label "Integration Requirement"@en ;
    rdfs:comment "Requirements for integrating validation components"@en .

guidance:LegacySupportInstance a guidance:LegacySupport ;
    guidance:hasLegacyMapping <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/collaboration#> <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/core#>,
        <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/model# > <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/security#>,
        <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation# > <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#> .

guidance:ModuleRegistryInstance a guidance:ModuleRegistry ;
    guidance:registeredModule <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/collaboration# > <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/core#>,
        <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/model# > <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/security#>,
        <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation# > <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#> .

guidance:SHACLValidation a owl:Class ;
    rdfs:label "SHACL Validation"@en ;
    rdfs:comment "Rules and patterns for SHACL validation"@en .

guidance:SPORERule a owl:Class ;
    rdfs:subClassOf guidance:ValidationRule ;
    owl:equivalentClass <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores# SPOREMessage> ;
    rdfs:label "SPORE Rule"@en ;
    rdfs:comment "Legacy alias for SPORE Message - use spores:SPOREMessage for new instances"@en ;
    owl:deprecated true ;
    owl:versionInfo "1.0.0" .

guidance:SemanticRule a owl:Class ;
    rdfs:subClassOf guidance:ValidationRule .

guidance:SyntaxRule a owl:Class ;
    rdfs:subClassOf guidance:ValidationRule .

guidance:TODO a owl:Class ;
    rdfs:label "Future Improvements" ;
    rdfs:comment "Items for future development and enhancement" .

guidance:ValidationPattern a owl:Class ;
    rdfs:label "Validation Pattern"@en ;
    rdfs:comment "Pattern for implementing validation rules"@en .

guidance:ValidationRuleShape a sh:NodeShape ;
    sh:property [ sh:datatype xsd:anyURI ;
            sh:maxCount 1 ;
            sh:minCount 1 ;
            sh:path guidance:hasTarget ] [ sh:datatype xsd:string ;
            sh:maxCount 1 ;
            sh:minCount 1 ;
            sh:path guidance:hasPriority ],
        [ sh:datatype xsd:string ;
            sh:maxCount 1 ;
            sh:minCount 1 ;
            sh:path guidance:hasValidator ],
        [ sh:datatype xsd:string ;
            sh:maxCount 1 ;
            sh:minCount 1 ;
            sh:path guidance:hasMessage ] ;
    sh:targetClass guidance:ValidationRule .

guidance:hasLegacyMapping a owl:ObjectProperty ;
    rdfs:label "has legacy mapping"@en ;
    rdfs:comment "Maps to legacy system concepts"@en ;
    rdfs:domain guidance:LegacySupport ;
    rdfs:range owl:Thing ;
    owl:versionInfo "1.0.0" .

guidance:registeredModule a owl:ObjectProperty ;
    rdfs:label "registered module"@en ;
    rdfs:comment "Links to a registered module"@en ;
    rdfs:domain guidance:ModuleRegistry ;
    rdfs:range owl:Ontology ;
    owl:versionInfo "1.0.0" .

guidance:ConsistencyRule a owl:Class ;
    rdfs:subClassOf guidance:ValidationRule .

guidance:hasMessage a owl:DatatypeProperty ;
    rdfs:domain guidance:ValidationRule .

guidance:hasPriority a owl:DatatypeProperty ;
    rdfs:domain guidance:ValidationRule .

guidance:hasTarget a owl:DatatypeProperty ;
    rdfs:domain guidance:ValidationRule .

guidance:hasValidator a owl:DatatypeProperty ;
    rdfs:domain guidance:ValidationRule .

guidance:LegacySupport a owl:Class ;
    rdfs:label "Legacy Support"@en ;
    rdfs:comment "Support for legacy system mappings"@en ;
    owl:versionInfo "1.0.0" .

guidance:ModuleRegistry a owl:Class ;
    rdfs:label "Module Registry"@en ;
    rdfs:comment "Registry of all ontology modules"@en ;
    owl:versionInfo "1.0.0" .

owl:DatatypeProperty rdfs:subClassOf rdf:Property .

guidance:ValidationRule a owl:Class .

owl:Class rdfs:subClassOf rdfs:Class .

# BFG9K MCP Architecture Classes
guidance:BFG9KArchitecture a owl:Class ;
    rdfs:label "BFG9K Architecture"@en ;
    rdfs:comment "Core architecture class for BFG9K MCP system"@en ;
    owl:versionInfo "1.0.0" .

guidance:ContainerInstance a owl:Class ;
    rdfs:label "Container Instance"@en ;
    rdfs:comment "Azure Container Instance configuration"@en ;
    rdfs:subClassOf guidance:BFG9KArchitecture ;
    owl:versionInfo "1.0.0" .

guidance:NetworkConfiguration a owl:Class ;
    rdfs:label "Network Configuration"@en ;
    rdfs:comment "Network settings for container instances"@en ;
    rdfs:subClassOf guidance:BFG9KArchitecture ;
    owl:versionInfo "1.0.0" .

guidance:EnvironmentVariable a owl:Class ;
    rdfs:label "Environment Variable"@en ;
    rdfs:comment "Environment variable configuration"@en ;
    rdfs:subClassOf guidance:BFG9KArchitecture ;
    owl:versionInfo "1.0.0" .

# BFG9K MCP Properties
guidance:hasContainerName a owl:DatatypeProperty ;
    rdfs:label "has container name"@en ;
    rdfs:comment "Specifies the container name"@en ;
    rdfs:domain guidance:ContainerInstance ;
    rdfs:range xsd:string ;
    owl:versionInfo "1.0.0" .

guidance:hasNetworkType a owl:DatatypeProperty ;
    rdfs:label "has network type"@en ;
    rdfs:comment "Specifies the network type (public/private)"@en ;
    rdfs:domain guidance:NetworkConfiguration ;
    rdfs:range xsd:string ;
    owl:versionInfo "1.0.0" .

guidance:hasEnvironmentVariable a owl:ObjectProperty ;
    rdfs:label "has environment variable"@en ;
    rdfs:comment "Links to environment variable configuration"@en ;
    rdfs:domain guidance:ContainerInstance ;
    rdfs:range guidance:EnvironmentVariable ;
    owl:versionInfo "1.0.0" .

# BFG9K MCP Individuals
guidance:BFG9KMCPServer a guidance:ContainerInstance ;
    guidance:hasContainerName "bfg9k-mcp-server" ;
    guidance:hasEnvironmentVariable guidance:ServerConfig .

guidance:ServerConfig a guidance:EnvironmentVariable ;
    rdfs:label "Server Configuration"@en ;
    rdfs:comment "Environment variables for server configuration"@en .

guidance:PublicNetwork a guidance:NetworkConfiguration ;
    guidance:hasNetworkType "public" ;
    rdfs:label "Public Network"@en ;
    rdfs:comment "Public network configuration"@en .

# SHACL Validation Rules
guidance:ContainerInstanceShape a sh:NodeShape ;
    sh:targetClass guidance:ContainerInstance ;
    sh:property [
        sh:path guidance:hasContainerName ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string
    ] .

guidance:NetworkConfigurationShape a sh:NodeShape ;
    sh:targetClass guidance:NetworkConfiguration ;
    sh:property [
        sh:path guidance:hasNetworkType ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:in ("public" "private")
    ] .

# TODO Section
guidance:BFG9KEnhancements a guidance:TODO ;
    rdfs:label "BFG9K Future Enhancements"@en ;
    rdfs:comment "Future improvements for BFG9K MCP architecture"@en ;
    guidance:hasPriority "MEDIUM" ;
    guidance:hasTargetDate "2024-Q3" .

# SPORE Integration - New Additions

# SPORE-specific validation instances
guidance:SPOREValidationInstance a guidance:SPORERule ;
    guidance:hasMessage "Validate SPORE message structure and routing" ;
    guidance:hasPriority "HIGH" ;
    guidance:hasTarget "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#SPOREMessage"^^xsd:anyURI ;
    guidance:hasValidator "validate_spore_message" .

guidance:SPOREChannelValidationInstance a guidance:ValidationRule ;
    guidance:hasMessage "Validate SPORE communication channels" ;
    guidance:hasPriority "MEDIUM" ;
    guidance:hasTarget "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#SPOREChannel"^^xsd:anyURI ;
    guidance:hasValidator "validate_spore_channel" .

guidance:SPOREAgentValidationInstance a guidance:ValidationRule ;
    guidance:hasMessage "Validate SPORE agent configuration" ;
    guidance:hasPriority "MEDIUM" ;
    guidance:hasTarget "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#SPOREAgent"^^xsd:anyURI ;
    guidance:hasValidator "validate_spore_agent" .

# SPORE-specific TODO items
guidance:SPOREEnhancements a guidance:TODO ;
    rdfs:label "SPORE Future Enhancements"@en ;
    rdfs:comment "Future improvements for SPORE inter-LLM communication system"@en ;
    guidance:hasPriority "HIGH" ;
    guidance:hasTargetDate "2024-Q4" ;
    guidance:hasMessage "Implement advanced SPORE routing message queuing, and semantic validation" .

# SPORE integration requirements
guidance:SPOREIntegrationRequirement a guidance:IntegrationRequirement ;
    rdfs:label "SPORE Integration Requirement"@en ;
    rdfs:comment "Requirements for integrating SPORE communication into existing validation framework"@en ;
    guidance:hasValidator "validate_spore_integration" ;
    guidance:hasPriority "HIGH" .

# SPORE-specific SHACL validation shape
guidance:SPOREMessageValidationShape a sh:NodeShape ;
    sh:targetClass <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#SPOREMessage> ;
    sh:property [ sh:path <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#hasSourceAgent> ;
            sh:minCount 1 ;
            sh:maxCount 1 ;
            sh:class <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#SPOREAgent> ] [ sh:path <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#hasTargetAgent> ;
            sh:maxCount 1 ;
            sh:class <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores# SPOREAgent> ] [ sh:path <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#hasPayload> ;
            sh:minCount 1 ;
            sh:maxCount 1 ;
            sh:class <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores# SPOREPayload> ] [ sh:path <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#hasChannel> ;
            sh:minCount 1 ;
            sh:maxCount 1 ;
            sh:class <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores# SPOREChannel> ] .
'''

# SPORE module content
spores_ttl = '''@prefix : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .
@prefix validation: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

: a owl:Ontology ;
    rdfs:label "SPORE Validation Module"@en ;
    rdfs:comment "Module for SPORE (Semantic Packet Ontology Rule Exchange) inter-LLM communication"@en ;
    owl:versionInfo "1.0.0" ;
    owl:imports <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation#> .

# Core SPORE Classes
:SPOREMessage a owl:Class ;
    rdfs:subClassOf validation:ValidationRule ;
    rdfs:label "SPORE Message"@en ;
    rdfs:comment "TTL-encoded message for inter-LLM communication and workflow automation"@en ;
    owl:versionInfo "1.0.0" .

:SPOREPayload a owl:Class ;
    rdfs:label "SPORE Payload"@en ;
    rdfs:comment "Structured TTL payload containing message data and metadata"@en ;
    owl:versionInfo "1.0.0" .

:SPOREChannel a owl:Class ;
    rdfs:label "SPORE Channel"@en ;
    rdfs:comment "Communication channel for SPORE message routing"@en ;
    owl:versionInfo "1.0.0" .

:SPOREAgent a owl:Class ;
    rdfs:label "SPORE Agent"@en ;
    rdfs:comment "LLM agent capable of sending/receiving SPORE messages"@en ;
    owl:versionInfo "1.0.0" .

# SPORE Message Types
:WorkflowSPORE a owl:Class ;
    rdfs:subClassOf :SPOREMessage ;
    rdfs:label "Workflow SPORE"@en ;
    rdfs:comment "SPORE message for workflow coordination between LLMs"@en .

:DataSPORE a owl:Class ;
    rdfs:subClassOf :SPOREMessage ;
    rdfs:label "Data SPORE"@en ;
    rdfs:comment "SPORE message containing structured data exchange"@en .

:ValidationSPORE a owl:Class ;
    rdfs:subClassOf :SPOREMessage ;
    rdfs:label "Validation SPORE"@en ;
    rdfs:comment "SPORE message for validation rule propagation"@en .

:SemanticSPORE a owl:Class ;
    rdfs:subClassOf :SPOREMessage ;
    rdfs:label "Semantic SPORE"@en ;
    rdfs:comment "SPORE message for semantic web integration and GraphDB operations"@en .

# Agent Types for Multi-LLM Workflows
:ClaudeAgent a owl:Class ;
    rdfs:subClassOf :SPOREAgent ;
    rdfs:label "Claude Agent"@en ;
    rdfs:comment "Anthropic Claude LLM agent in SPORE network"@en .

:ChatGPTAgent a owl:Class ;
    rdfs:subClassOf :SPOREAgent ;
    rdfs:label "ChatGPT Agent"@en ;
    rdfs:comment "OpenAI ChatGPT agent in SPORE network"@en .

:CursorAgent a owl:Class ;
    rdfs:subClassOf :SPOREAgent ;
    rdfs:label "Cursor IDE Agent"@en ;
    rdfs:comment "Cursor IDE integrated agent for development workflows"@en .

# SPORE Properties
:hasPayload a owl:ObjectProperty ;
    rdfs:domain :SPOREMessage ;
    rdfs:range :SPOREPayload ;
    rdfs:label "has payload"@en ;
    rdfs:comment "Links SPORE message to its structured payload"@en .

:hasSourceAgent a owl:ObjectProperty ;
    rdfs:domain :SPOREMessage ;
    rdfs:range :SPOREAgent ;
    rdfs:label "has source agent"@en ;
    rdfs:comment "Agent that originated the SPORE message"@en .

:hasTargetAgent a owl:ObjectProperty ;
    rdfs:domain :SPOREMessage ;
    rdfs:range :SPOREAgent ;
    rdfs:label "has target agent"@en ;
    rdfs:comment "Intended recipient agent for SPORE message"@en .

:hasChannel a owl:ObjectProperty ;
    rdfs:domain :SPOREMessage ;
    rdfs:range :SPOREChannel ;
    rdfs:label "has channel"@en ;
    rdfs:comment "Communication channel for message routing"@en .

:hasTTLContent a owl:DatatypeProperty ;
    rdfs:domain :SPOREPayload ;
    rdfs:range xsd:string ;
    rdfs:label "has TTL content"@en ;
    rdfs:comment "TTL-formatted content of the payload"@en .

:hasMessageType a owl:DatatypeProperty ;
    rdfs:domain :SPOREMessage ;
    rdfs:range xsd:string ;
    rdfs:label "has message type"@en ;
    rdfs:comment "Type classification of SPORE message"@en .

:hasWorkflowStep a owl:DatatypeProperty ;
    rdfs:domain :WorkflowSPORE ;
    rdfs:range xsd:string ;
    rdfs:label "has workflow step"@en ;
    rdfs:comment "Workflow step identifier for coordination"@en .

:hasTimestamp a owl:DatatypeProperty ;
    rdfs:domain :SPOREMessage ;
    rdfs:range xsd:dateTime ;
    rdfs:label "has timestamp"@en ;
    rdfs:comment "Message creation timestamp"@en .

:hasSessionId a owl:DatatypeProperty ;
    rdfs:domain :SPOREMessage ;
    rdfs:range xsd:string ;
    rdfs:label "has session ID"@en ;
    rdfs:comment "Session identifier for message correlation"@en .

# Communication Channels
:ClipboardChannel a owl:Class ;
    rdfs:subClassOf :SPOREChannel ;
    rdfs:label "Clipboard Channel"@en ;
    rdfs:comment "Clipboard-based message passing channel"@en .

:BrowserExtensionChannel a owl:Class ;
    rdfs:subClassOf :SPOREChannel ;
    rdfs:label "Browser Extension Channel"@en ;
    rdfs:comment "Browser extension mediated communication"@en .

:FileSystemChannel a owl:Class ;
    rdfs:subClassOf :SPOREChannel ;
    rdfs:label "File System Channel"@en ;
    rdfs:comment "File-based message exchange channel"@en .

:GraphDBChannel a owl:Class ;
    rdfs:subClassOf :SPOREChannel ;
    rdfs:label "GraphDB Channel"@en ;
    rdfs:comment "GraphDB-mediated semantic message exchange"@en .

# SHACL Shapes for Validation
:SPOREMessageShape a sh:NodeShape ;
    sh:targetClass :SPOREMessage ;
    sh:property [
        sh:path :hasSourceAgent ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:class :SPOREAgent
    ]  [
        sh:path :hasPayload ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:class :SPOREPayload
    ] ,
    [
        sh:path :hasTimestamp ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:dateTime
    ] ,
    [
        sh:path :hasMessageType ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string
    ] .

:SPOREPayloadShape a sh:NodeShape ;
    sh:targetClass :SPOREPayload ;
    sh:property [
        sh:path :hasTTLContent ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^@prefix.*\\\\.$"
    ] .

# Example SPORE Instances
:ExampleWorkflowSPORE a :WorkflowSPORE ;
    rdfs:label "Example Workflow Coordination"@en ;
    rdfs:comment "Example SPORE for multi-LLM workflow coordination"@en ;
    :hasSourceAgent :ExampleClaudeAgent ;
    :hasTargetAgent :ExampleChatGPTAgent ;
    :hasChannel :ExampleClipboardChannel ;
    :hasWorkflowStep "code_generation" ;
    :hasMessageType "workflow_coordination" ;
    :hasPayload :ExampleWorkflowPayload .

:ExampleSemanticSPORE a :SemanticSPORE ;
    rdfs:label "Example Semantic Web Integration"@en ;
    rdfs:comment "Example SPORE for GraphDB integration"@en ;
    :hasSourceAgent :ExampleCursorAgent ;
    :hasTargetAgent :ExampleClaudeAgent ;
    :hasChannel :ExampleGraphDBChannel ;
    :hasMessageType "semantic_integration" ;
    :hasPayload :ExampleSemanticPayload .

# Example Agents and Channels
:ExampleClaudeAgent a :ClaudeAgent ;
    rdfs:label "Example Claude Web Interface"@en .

:ExampleChatGPTAgent a :ChatGPTAgent ;
    rdfs:label "Example ChatGPT Professional"@en .

:ExampleCursorAgent a :CursorAgent ;
    rdfs:label "Example Cursor IDE Instance"@en .

:ExampleClipboardChannel a :ClipboardChannel ;
    rdfs:label "System Clipboard Bridge"@en .

:ExampleGraphDBChannel a :GraphDBChannel ;
    rdfs:label "Local GraphDB Instance"@en .

# Example Payloads
:ExampleWorkflowPayload a :SPOREPayload ;
    :hasTTLContent """@prefix workflow: <http://example.org/workflow#> .
workflow:task_001 a workflow:CodeGenerationTask ;
    workflow:language "python" ;
    workflow:requirements "pandas data analysis" ;
    workflow:priority "high" .""" .

:ExampleSemanticPayload a :SPOREPayload ;
    :hasTTLContent """@prefix data: <http://example.org/data#> .
data:dataset_001 a data:AnalysisDataset ;
    data:source "web_scraping" ;
    data:format "csv" ;
    data:requires_validation true .""" .

# Test Cases for SPORE Validation
:SPOREMessageValidationTest a validation:TestCase ;
    rdfs:label "SPORE Message Validation Test"@en ;
    rdfs:comment "Tests SPORE message structure and content validation"@en ;
    validation:hasExpectedResult "All SPORE messages should have valid structure"@en ;
    validation:hasTestQuery """
    PREFIX spore: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?message ?source ?target ?payload WHERE {
        ?message rdf:type spore:SPOREMessage ;
                 spore:hasSourceAgent ?source ;
                 spore:hasTargetAgent ?target ;
                 spore:hasPayload ?payload .
        ?payload spore:hasTTLContent ?content .
        FILTER NOT EXISTS {
            ?message spore:hasTimestamp ?timestamp
        }
    }""" .

:SPOREChannelTest a validation:TestCase ;
    rdfs:label "SPORE Channel Test"@en ;
    rdfs:comment "Tests SPORE communication channel functionality"@en ;
    validation:hasExpectedResult "All SPORE channels should be properly configured"@en ;
    validation:hasTestQuery """
    PREFIX spore: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?message ?channel WHERE {
        ?message rdf:type spore:SPOREMessage ;
                 spore:hasChannel ?channel .
        ?channel rdf:type spore:SPOREChannel .
    }""" .
'''

def create_spore_zip():
    """Create zip file with SPORE integration files"""
    
    # Create Downloads directory if it doesn't exist
    downloads_dir = Path.home() / "Downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    zip_path = downloads_dir / "spore_integration_files.zip"
    
    # Create the zip file
    with zipfile.ZipFile(zip_path 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add guidance.ttl
        zipf.writestr("guidance.ttl" guidance_ttl)
        
        # Add spores.ttl with proper directory structure
        zipf.writestr("guidance/modules/validation/spores.ttl" spores_ttl)
        
        # Add README with instructions
        readme_content = """# SPORE Integration Files

This zip contains:
1. guidance.ttl - Updated main ontology with SPORE integration
2. guidance/modules/validation/spores.ttl - New SPORE module

## Integration Steps:
1. Backup existing guidance.ttl
2. Replace guidance.ttl with the updated version
3. Create directory structure: guidance/modules/validation/
4. Add spores.ttl to the validation directory
5. Test with: rapper -i turtle guidance.ttl
6. Validate SHACL constraints if available

## SPORE Message Format:
See the SPORE Integration Message artifact for the complete workflow instructions.
"""
        zipf.writestr("README.md" readme_content)
    
    print(f"Created SPORE integration zip file: {zip_path}")
    print(f"File size: {zip_path.stat().st_size} bytes")
    
    return zip_path

if __name__ == "__main__":
    create_spore_zip()