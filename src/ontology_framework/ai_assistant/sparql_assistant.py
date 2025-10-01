"""AI-powered SPARQL query generation and optimization"""

from typing import Dict, List, Optional, Tuple
import re
from ..sparql_client import SPARQLClient
from ..prefix_map import default_prefix_map


class SPARQLAssistant:
    """Generate and optimize SPARQL queries from natural language"""
    
    def __init__(self, sparql_client: SPARQLClient):
        self.sparql_client = sparql_client
        self.common_patterns = self._load_query_patterns()
    
    def generate_query(self, description: str) -> Dict[str, str]:
        """Generate SPARQL query from natural language description"""
        query_type = self._identify_query_type(description)
        
        if query_type == "select":
            return self._generate_select_query(description)
        elif query_type == "construct":
            return self._generate_construct_query(description)
        elif query_type == "ask":
            return self._generate_ask_query(description)
        else:
            return self._generate_describe_query(description)
    
    def optimize_query(self, query: str) -> Dict[str, any]:
        """Analyze and optimize SPARQL query performance"""
        analysis = {
            "original_query": query,
            "optimizations": [],
            "estimated_performance": "unknown",
            "suggestions": []
        }
        
        # Check for common performance issues
        if "OPTIONAL" in query and "FILTER" in query:
            analysis["optimizations"].append("Move FILTER inside OPTIONAL for better performance")
        
        if query.count("?") > 20:
            analysis["suggestions"].append("Consider reducing the number of variables")
        
        if "UNION" in query:
            analysis["suggestions"].append("Check if UNION can be replaced with more specific patterns")
        
        # Add prefixes if missing
        optimized_query = self._add_missing_prefixes(query)
        if optimized_query != query:
            analysis["optimizations"].append("Added missing prefixes")
            analysis["optimized_query"] = optimized_query
        
        return analysis
    
    def explain_query(self, query: str) -> Dict[str, any]:
        """Explain what a SPARQL query does in natural language"""
        explanation = {
            "query_type": self._get_query_type(query),
            "description": "",
            "patterns": [],
            "filters": [],
            "complexity": "low"
        }
        
        # Parse query components
        if "SELECT" in query.upper():
            variables = re.findall(r'\?(\w+)', query)
            explanation["description"] = f"Selects {len(variables)} variables: {', '.join(variables)}"
        
        # Identify triple patterns
        patterns = re.findall(r'\?(\w+)\s+(\S+)\s+\?(\w+)', query)
        explanation["patterns"] = [f"{p[0]} {p[1]} {p[2]}" for p in patterns]
        
        # Identify filters
        filters = re.findall(r'FILTER\s*\([^)]+\)', query, re.IGNORECASE)
        explanation["filters"] = filters
        
        # Estimate complexity
        if len(patterns) > 5 or len(filters) > 2 or "UNION" in query:
            explanation["complexity"] = "high"
        elif len(patterns) > 2 or len(filters) > 0:
            explanation["complexity"] = "medium"
        
        return explanation
    
    def suggest_improvements(self, query: str, execution_time: Optional[float] = None) -> List[str]:
        """Suggest improvements for a SPARQL query"""
        suggestions = []
        
        # Performance-based suggestions
        if execution_time and execution_time > 5.0:
            suggestions.append("Query is slow - consider adding more specific patterns")
            suggestions.append("Use LIMIT to reduce result set size")
        
        # Pattern-based suggestions
        if "SELECT *" in query:
            suggestions.append("Specify exact variables instead of SELECT *")
        
        if query.count("OPTIONAL") > 3:
            suggestions.append("Too many OPTIONAL clauses may impact performance")
        
        if not any(prefix in query for prefix in ["PREFIX", "@prefix"]):
            suggestions.append("Add PREFIX declarations for better readability")
        
        return suggestions
    
    def _identify_query_type(self, description: str) -> str:
        """Identify the type of SPARQL query needed"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ["find", "get", "list", "show"]):
            return "select"
        elif any(word in desc_lower for word in ["create", "build", "construct"]):
            return "construct"
        elif any(word in desc_lower for word in ["exists", "is there", "check"]):
            return "ask"
        else:
            return "describe"
    
    def _generate_select_query(self, description: str) -> Dict[str, str]:
        """Generate SELECT query from description"""
        # Simple pattern matching - could be enhanced with NLP
        query = "SELECT ?subject ?predicate ?object WHERE {\n"
        query += "  ?subject ?predicate ?object .\n"
        
        # Add filters based on description
        if "class" in description.lower():
            query += "  ?subject a owl:Class .\n"
        elif "property" in description.lower():
            query += "  ?subject a owl:ObjectProperty .\n"
        
        query += "}\nLIMIT 100"
        
        return {
            "query": query,
            "type": "SELECT",
            "description": f"Generated SELECT query for: {description}"
        }
    
    def _generate_construct_query(self, description: str) -> Dict[str, str]:
        """Generate CONSTRUCT query from description"""
        query = "CONSTRUCT {\n"
        query += "  ?subject ?predicate ?object .\n"
        query += "} WHERE {\n"
        query += "  ?subject ?predicate ?object .\n"
        query += "}"
        
        return {
            "query": query,
            "type": "CONSTRUCT",
            "description": f"Generated CONSTRUCT query for: {description}"
        }
    
    def _generate_ask_query(self, description: str) -> Dict[str, str]:
        """Generate ASK query from description"""
        query = "ASK {\n"
        query += "  ?subject ?predicate ?object .\n"
        query += "}"
        
        return {
            "query": query,
            "type": "ASK",
            "description": f"Generated ASK query for: {description}"
        }
    
    def _generate_describe_query(self, description: str) -> Dict[str, str]:
        """Generate DESCRIBE query from description"""
        query = "DESCRIBE ?resource WHERE {\n"
        query += "  ?resource ?predicate ?object .\n"
        query += "}\nLIMIT 10"
        
        return {
            "query": query,
            "type": "DESCRIBE",
            "description": f"Generated DESCRIBE query for: {description}"
        }
    
    def _get_query_type(self, query: str) -> str:
        """Extract query type from SPARQL query"""
        query_upper = query.upper().strip()
        
        if query_upper.startswith("SELECT"):
            return "SELECT"
        elif query_upper.startswith("CONSTRUCT"):
            return "CONSTRUCT"
        elif query_upper.startswith("ASK"):
            return "ASK"
        elif query_upper.startswith("DESCRIBE"):
            return "DESCRIBE"
        else:
            return "UNKNOWN"
    
    def _add_missing_prefixes(self, query: str) -> str:
        """Add missing prefix declarations to query"""
        prefixes_needed = set()
        
        # Find prefixed names in query
        prefixed_names = re.findall(r'(\w+):', query)
        for prefix in prefixed_names:
            if prefix not in ["http", "https", "ftp"]:  # Skip URLs
                prefixes_needed.add(prefix)
        
        # Add prefix declarations
        prefix_declarations = ""
        for prefix in prefixes_needed:
            if prefix in default_prefix_map.prefixes:
                namespace = default_prefix_map.get_namespace(prefix)
                prefix_declarations += f"PREFIX {prefix}: <{namespace}>\n"
        
        if prefix_declarations:
            return prefix_declarations + "\n" + query
        
        return query
    
    def _load_query_patterns(self) -> Dict[str, str]:
        """Load common SPARQL query patterns"""
        return {
            "all_classes": """
                SELECT ?class ?label WHERE {
                    ?class a owl:Class .
                    OPTIONAL { ?class rdfs:label ?label }
                }
            """,
            "class_hierarchy": """
                SELECT ?class ?superClass WHERE {
                    ?class rdfs:subClassOf ?superClass .
                }
            """,
            "object_properties": """
                SELECT ?property ?domain ?range WHERE {
                    ?property a owl:ObjectProperty .
                    OPTIONAL { ?property rdfs:domain ?domain }
                    OPTIONAL { ?property rdfs:range ?range }
                }
            """
        }