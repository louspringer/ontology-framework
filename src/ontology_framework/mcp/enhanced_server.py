"""Enhanced MCP server with all AI-assisted capabilities"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import logging

from ..ai_assistant.ontology_chat import OntologyChat
from ..ai_assistant.sparql_assistant import SPARQLAssistant
from ..ai_assistant.ontology_generator import OntologyGenerator
from ..validation.advanced_validator import AdvancedValidator
from ..collaboration.change_impact import ChangeImpactAnalyzer
from ..integration.ci_cd_pipeline import CICDPipeline
from ..developer_experience.code_generator import CodeGenerator
from ..sparql_client import SPARQLClient


class EnhancedOntologyMCPServer:
    """Enhanced MCP server with comprehensive ontology development capabilities"""
    
    def __init__(self, sparql_client: Optional[SPARQLClient] = None):
        self.server = Server("enhanced-ontology-mcp")
        self.sparql_client = sparql_client
        
        # Initialize AI assistants
        self.ontology_chat = OntologyChat(sparql_client) if sparql_client else None
        self.sparql_assistant = SPARQLAssistant(sparql_client) if sparql_client else None
        self.ontology_generator = OntologyGenerator()
        self.advanced_validator = AdvancedValidator(sparql_client)
        self.change_analyzer = ChangeImpactAnalyzer(sparql_client)
        self.ci_cd_pipeline = CICDPipeline()
        self.code_generator = CodeGenerator()
        
        self._register_tools()
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        # AI Assistant Tools
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="ontology_chat",
                    description="Ask natural language questions about ontology structure and content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "Natural language question about the ontology"}
                        },
                        "required": ["question"]
                    }
                ),
                Tool(
                    name="generate_sparql",
                    description="Generate SPARQL queries from natural language descriptions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "Natural language description of desired query"}
                        },
                        "required": ["description"]
                    }
                ),
                Tool(
                    name="optimize_sparql",
                    description="Analyze and optimize SPARQL query performance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SPARQL query to optimize"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="explain_sparql",
                    description="Explain what a SPARQL query does in natural language",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SPARQL query to explain"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="generate_ontology",
                    description="Generate ontology scaffold from natural language description",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "Natural language description of the domain"},
                            "domain": {"type": "string", "description": "Domain name for the ontology", "default": "general"}
                        },
                        "required": ["description"]
                    }
                ),
                Tool(
                    name="create_spore_pattern",
                    description="Create a spore transformation pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern_name": {"type": "string", "description": "Name of the spore pattern"},
                            "description": {"type": "string", "description": "Description of what the pattern does"}
                        },
                        "required": ["pattern_name", "description"]
                    }
                ),
                Tool(
                    name="validate_ontology_advanced",
                    description="Run advanced semantic validation beyond basic SHACL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ontology_file": {"type": "string", "description": "Path to ontology file to validate"}
                        },
                        "required": ["ontology_file"]
                    }
                ),
                Tool(
                    name="analyze_performance",
                    description="Analyze ontology design for query performance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ontology_file": {"type": "string", "description": "Path to ontology file to analyze"}
                        },
                        "required": ["ontology_file"]
                    }
                ),
                Tool(
                    name="analyze_change_impact",
                    description="Analyze the impact of ontology changes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "old_file": {"type": "string", "description": "Path to old ontology version"},
                            "new_file": {"type": "string", "description": "Path to new ontology version"}
                        },
                        "required": ["old_file", "new_file"]
                    }
                ),
                Tool(
                    name="predict_query_impact",
                    description="Predict how ontology changes will affect existing queries",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "old_file": {"type": "string", "description": "Path to old ontology version"},
                            "new_file": {"type": "string", "description": "Path to new ontology version"},
                            "sample_queries": {"type": "array", "items": {"type": "string"}, "description": "Sample SPARQL queries to test"}
                        },
                        "required": ["old_file", "new_file", "sample_queries"]
                    }
                ),
                Tool(
                    name="run_ci_cd_pipeline",
                    description="Run CI/CD pipeline for ontology validation and deployment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ontology_files": {"type": "array", "items": {"type": "string"}, "description": "List of ontology files to process"},
                            "branch": {"type": "string", "description": "Git branch name", "default": "main"}
                        },
                        "required": ["ontology_files"]
                    }
                ),
                Tool(
                    name="generate_python_classes",
                    description="Generate Python classes from ontology definitions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ontology_file": {"type": "string", "description": "Path to ontology file"},
                            "output_dir": {"type": "string", "description": "Output directory for generated code", "default": "generated"}
                        },
                        "required": ["ontology_file"]
                    }
                ),
                Tool(
                    name="generate_pydantic_models",
                    description="Generate Pydantic models from ontology",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ontology_file": {"type": "string", "description": "Path to ontology file"},
                            "output_file": {"type": "string", "description": "Output file for models", "default": "models.py"}
                        },
                        "required": ["ontology_file"]
                    }
                ),
                Tool(
                    name="generate_rest_api",
                    description="Generate REST API endpoints for ontology",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ontology_file": {"type": "string", "description": "Path to ontology file"},
                            "output_dir": {"type": "string", "description": "Output directory for API code", "default": "api"}
                        },
                        "required": ["ontology_file"]
                    }
                ),
                Tool(
                    name="create_github_workflow",
                    description="Generate GitHub Actions workflow for ontology CI/CD",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {"type": "string", "description": "Path to project root"}
                        },
                        "required": ["project_path"]
                    }
                ),
                Tool(
                    name="coverage_analysis",
                    description="Analyze ontology completeness for domain requirements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ontology_file": {"type": "string", "description": "Path to ontology file"},
                            "requirements": {"type": "array", "items": {"type": "string"}, "description": "List of domain requirements"}
                        },
                        "required": ["ontology_file", "requirements"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "ontology_chat":
                    return await self._handle_ontology_chat(arguments)
                elif name == "generate_sparql":
                    return await self._handle_generate_sparql(arguments)
                elif name == "optimize_sparql":
                    return await self._handle_optimize_sparql(arguments)
                elif name == "explain_sparql":
                    return await self._handle_explain_sparql(arguments)
                elif name == "generate_ontology":
                    return await self._handle_generate_ontology(arguments)
                elif name == "create_spore_pattern":
                    return await self._handle_create_spore_pattern(arguments)
                elif name == "validate_ontology_advanced":
                    return await self._handle_validate_ontology_advanced(arguments)
                elif name == "analyze_performance":
                    return await self._handle_analyze_performance(arguments)
                elif name == "analyze_change_impact":
                    return await self._handle_analyze_change_impact(arguments)
                elif name == "predict_query_impact":
                    return await self._handle_predict_query_impact(arguments)
                elif name == "run_ci_cd_pipeline":
                    return await self._handle_run_ci_cd_pipeline(arguments)
                elif name == "generate_python_classes":
                    return await self._handle_generate_python_classes(arguments)
                elif name == "generate_pydantic_models":
                    return await self._handle_generate_pydantic_models(arguments)
                elif name == "generate_rest_api":
                    return await self._handle_generate_rest_api(arguments)
                elif name == "create_github_workflow":
                    return await self._handle_create_github_workflow(arguments)
                elif name == "coverage_analysis":
                    return await self._handle_coverage_analysis(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
            except Exception as e:
                logging.error(f"Error in tool {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _handle_ontology_chat(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle ontology chat requests"""
        if not self.ontology_chat:
            return [TextContent(type="text", text="Ontology chat requires SPARQL client connection")]
        
        question = arguments["question"]
        response = self.ontology_chat.ask_question(question)
        
        return [TextContent(type="text", text=json.dumps(response, indent=2))]
    
    async def _handle_generate_sparql(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle SPARQL generation requests"""
        if not self.sparql_assistant:
            return [TextContent(type="text", text="SPARQL assistant requires SPARQL client connection")]
        
        description = arguments["description"]
        query_result = self.sparql_assistant.generate_query(description)
        
        return [TextContent(type="text", text=json.dumps(query_result, indent=2))]
    
    async def _handle_optimize_sparql(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle SPARQL optimization requests"""
        if not self.sparql_assistant:
            return [TextContent(type="text", text="SPARQL assistant requires SPARQL client connection")]
        
        query = arguments["query"]
        optimization_result = self.sparql_assistant.optimize_query(query)
        
        return [TextContent(type="text", text=json.dumps(optimization_result, indent=2))]
    
    async def _handle_explain_sparql(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle SPARQL explanation requests"""
        if not self.sparql_assistant:
            return [TextContent(type="text", text="SPARQL assistant requires SPARQL client connection")]
        
        query = arguments["query"]
        explanation = self.sparql_assistant.explain_query(query)
        
        return [TextContent(type="text", text=json.dumps(explanation, indent=2))]
    
    async def _handle_generate_ontology(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle ontology generation requests"""
        description = arguments["description"]
        domain = arguments.get("domain", "general")
        
        result = self.ontology_generator.generate_from_description(description, domain)
        
        return [TextContent(type="text", text=f"Generated ontology with {result['summary']['classes_count']} classes and {result['summary']['properties_count']} properties.\n\nTurtle output:\n{result['turtle']}")]
    
    async def _handle_create_spore_pattern(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle spore pattern creation"""
        pattern_name = arguments["pattern_name"]
        description = arguments["description"]
        
        result = self.ontology_generator.create_spore_pattern(pattern_name, description)
        
        return [TextContent(type="text", text=f"Created spore pattern '{pattern_name}':\n\n{result['turtle']}")]
    
    async def _handle_validate_ontology_advanced(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle advanced ontology validation"""
        ontology_file = arguments["ontology_file"]
        
        try:
            from rdflib import Graph
            graph = Graph()
            graph.parse(ontology_file)
            
            validation_result = self.advanced_validator.semantic_consistency_check(graph)
            
            return [TextContent(type="text", text=json.dumps(validation_result, indent=2))]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Validation failed: {str(e)}")]
    
    async def _handle_analyze_performance(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle performance analysis"""
        ontology_file = arguments["ontology_file"]
        
        try:
            from rdflib import Graph
            graph = Graph()
            graph.parse(ontology_file)
            
            performance_result = self.advanced_validator.performance_analysis(graph)
            
            return [TextContent(type="text", text=json.dumps(performance_result, indent=2))]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Performance analysis failed: {str(e)}")]
    
    async def _handle_analyze_change_impact(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle change impact analysis"""
        old_file = arguments["old_file"]
        new_file = arguments["new_file"]
        
        try:
            from rdflib import Graph
            
            old_graph = Graph()
            old_graph.parse(old_file)
            
            new_graph = Graph()
            new_graph.parse(new_file)
            
            impact_result = self.change_analyzer.analyze_change_impact(old_graph, new_graph)
            
            return [TextContent(type="text", text=json.dumps(impact_result, indent=2))]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Change impact analysis failed: {str(e)}")]
    
    async def _handle_predict_query_impact(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle query impact prediction"""
        old_file = arguments["old_file"]
        new_file = arguments["new_file"]
        sample_queries = arguments["sample_queries"]
        
        try:
            from rdflib import Graph
            
            old_graph = Graph()
            old_graph.parse(old_file)
            
            new_graph = Graph()
            new_graph.parse(new_file)
            
            changes = self.change_analyzer._detect_changes(old_graph, new_graph)
            query_impact = self.change_analyzer.predict_query_impact(changes, sample_queries)
            
            return [TextContent(type="text", text=json.dumps(query_impact, indent=2))]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Query impact prediction failed: {str(e)}")]
    
    async def _handle_run_ci_cd_pipeline(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle CI/CD pipeline execution"""
        ontology_files = arguments["ontology_files"]
        branch = arguments.get("branch", "main")
        
        pipeline_result = self.ci_cd_pipeline.run_pipeline(ontology_files, branch)
        
        return [TextContent(type="text", text=json.dumps(pipeline_result, indent=2))]
    
    async def _handle_generate_python_classes(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle Python class generation"""
        ontology_file = arguments["ontology_file"]
        output_dir = arguments.get("output_dir", "generated")
        
        result = self.code_generator.generate_python_classes(ontology_file, output_dir)
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _handle_generate_pydantic_models(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle Pydantic model generation"""
        ontology_file = arguments["ontology_file"]
        output_file = arguments.get("output_file", "models.py")
        
        result_file = self.code_generator.generate_pydantic_models(ontology_file, output_file)
        
        return [TextContent(type="text", text=f"Generated Pydantic models in: {result_file}")]
    
    async def _handle_generate_rest_api(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle REST API generation"""
        ontology_file = arguments["ontology_file"]
        output_dir = arguments.get("output_dir", "api")
        
        result = self.code_generator.generate_rest_api(ontology_file, output_dir)
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _handle_create_github_workflow(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle GitHub workflow creation"""
        project_path = arguments["project_path"]
        
        workflow_path = self.ci_cd_pipeline.generate_github_workflow(project_path)
        
        return [TextContent(type="text", text=f"Generated GitHub workflow at: {workflow_path}")]
    
    async def _handle_coverage_analysis(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle coverage analysis"""
        ontology_file = arguments["ontology_file"]
        requirements = arguments["requirements"]
        
        try:
            from rdflib import Graph
            graph = Graph()
            graph.parse(ontology_file)
            
            coverage_result = self.advanced_validator.coverage_analysis(graph, requirements)
            
            return [TextContent(type="text", text=json.dumps(coverage_result, indent=2))]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Coverage analysis failed: {str(e)}")]
    
    async def run(self, host: str = "localhost", port: int = 8080):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


async def main():
    """Main entry point for the enhanced MCP server"""
    server = EnhancedOntologyMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())