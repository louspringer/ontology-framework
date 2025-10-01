"""Natural language interface for ontology exploration"""

from typing import Dict, List, Optional, Any
from rdflib import Graph, Namespace, URIRef
from ..sparql_client import SPARQLClient
from ..prefix_map import default_prefix_map


class OntologyChat:
    """AI-powered chat interface for ontology queries"""
    
    def __init__(self, sparql_client: SPARQLClient):
        self.sparql_client = sparql_client
        self.graph = Graph()
        self._load_ontologies()
    
    def _load_ontologies(self):
        """Load available ontologies into memory"""
        # Load from GraphDB or local files
        pass
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Process natural language question about ontology"""
        # Parse question intent
        intent = self._parse_intent(question)
        
        if intent == "structure":
            return self._get_structure_info(question)
        elif intent == "relationships":
            return self._get_relationship_info(question)
        elif intent == "concepts":
            return self._get_concept_info(question)
        else:
            return self._general_query(question)
    
    def _parse_intent(self, question: str) -> str:
        """Determine the type of question being asked"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["structure", "hierarchy", "classes"]):
            return "structure"
        elif any(word in question_lower for word in ["related", "connects", "properties"]):
            return "relationships"
        elif any(word in question_lower for word in ["what is", "define", "concept"]):
            return "concepts"
        else:
            return "general"
    
    def _get_structure_info(self, question: str) -> Dict[str, Any]:
        """Get ontology structure information"""
        query = """
        SELECT ?class ?superClass ?label WHERE {
            ?class a owl:Class .
            OPTIONAL { ?class rdfs:subClassOf ?superClass }
            OPTIONAL { ?class rdfs:label ?label }
        }
        LIMIT 50
        """
        
        results = self.sparql_client.execute_query(query)
        return {
            "type": "structure",
            "classes": self._format_class_hierarchy(results),
            "summary": f"Found {len(results)} classes in the ontology"
        }
    
    def _get_relationship_info(self, question: str) -> Dict[str, Any]:
        """Get relationship information between concepts"""
        query = """
        SELECT ?property ?domain ?range ?label WHERE {
            ?property a owl:ObjectProperty .
            OPTIONAL { ?property rdfs:domain ?domain }
            OPTIONAL { ?property rdfs:range ?range }
            OPTIONAL { ?property rdfs:label ?label }
        }
        LIMIT 50
        """
        
        results = self.sparql_client.execute_query(query)
        return {
            "type": "relationships",
            "properties": self._format_properties(results),
            "summary": f"Found {len(results)} object properties"
        }
    
    def _get_concept_info(self, question: str) -> Dict[str, Any]:
        """Get information about specific concepts"""
        # Extract concept name from question
        concept = self._extract_concept(question)
        
        query = f"""
        SELECT ?predicate ?object WHERE {{
            <{concept}> ?predicate ?object .
        }}
        UNION {{
            ?subject ?predicate <{concept}> .
        }}
        LIMIT 20
        """
        
        results = self.sparql_client.execute_query(query)
        return {
            "type": "concept",
            "concept": concept,
            "properties": results,
            "summary": f"Information about {concept}"
        }
    
    def _general_query(self, question: str) -> Dict[str, Any]:
        """Handle general queries"""
        return {
            "type": "general",
            "response": "I can help you explore ontology structure, relationships, and concepts. Try asking about classes, properties, or specific concepts.",
            "suggestions": [
                "What classes are in this ontology?",
                "Show me the relationships between concepts",
                "What is the definition of [concept]?"
            ]
        }
    
    def _format_class_hierarchy(self, results: List[Dict]) -> List[Dict]:
        """Format class hierarchy results"""
        formatted = []
        for result in results:
            formatted.append({
                "class": str(result.get("class", "")),
                "superClass": str(result.get("superClass", "")),
                "label": str(result.get("label", ""))
            })
        return formatted
    
    def _format_properties(self, results: List[Dict]) -> List[Dict]:
        """Format property results"""
        formatted = []
        for result in results:
            formatted.append({
                "property": str(result.get("property", "")),
                "domain": str(result.get("domain", "")),
                "range": str(result.get("range", "")),
                "label": str(result.get("label", ""))
            })
        return formatted
    
    def _extract_concept(self, question: str) -> str:
        """Extract concept URI from question"""
        # Simple extraction - could be enhanced with NLP
        words = question.split()
        for word in words:
            if ":" in word:  # Likely a prefixed URI
                return default_prefix_map.expand_curie(word)
        return ""