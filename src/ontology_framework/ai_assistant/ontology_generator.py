"""AI-powered ontology generation from natural language descriptions"""

from typing import Dict, List, Optional, Set
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
from ..prefix_map import default_prefix_map
import re


class OntologyGenerator:
    """Generate ontology scaffolds from natural language descriptions"""
    
    def __init__(self):
        self.graph = Graph()
        self.base_namespace = Namespace("http://example.org/ontology/")
        self._bind_prefixes()
    
    def generate_from_description(self, description: str, domain: str = "general") -> Dict[str, any]:
        """Generate ontology from natural language description"""
        # Parse the description to extract concepts and relationships
        concepts = self._extract_concepts(description)
        relationships = self._extract_relationships(description)
        
        # Create the ontology graph
        ontology_uri = self.base_namespace[f"{domain}_ontology"]
        self._create_ontology_header(ontology_uri, description, domain)
        
        # Add classes
        class_uris = {}
        for concept in concepts:
            class_uri = self._create_class(concept)
            class_uris[concept] = class_uri
        
        # Add properties
        property_uris = {}
        for rel in relationships:
            prop_uri = self._create_property(rel, class_uris)
            property_uris[rel["name"]] = prop_uri
        
        return {
            "ontology_uri": str(ontology_uri),
            "graph": self.graph,
            "turtle": self.graph.serialize(format="turtle"),
            "classes": class_uris,
            "properties": property_uris,
            "summary": {
                "classes_count": len(concepts),
                "properties_count": len(relationships),
                "description": description
            }
        }
    
    def generate_class_hierarchy(self, concepts: List[str]) -> Graph:
        """Generate class hierarchy from list of concepts"""
        hierarchy_graph = Graph()
        
        # Create classes
        class_uris = {}
        for concept in concepts:
            class_uri = self.base_namespace[self._to_class_name(concept)]
            hierarchy_graph.add((class_uri, RDF.type, OWL.Class))
            hierarchy_graph.add((class_uri, RDFS.label, Literal(concept)))
            class_uris[concept] = class_uri
        
        # Infer hierarchy based on naming patterns
        for concept in concepts:
            parent = self._infer_parent_class(concept, concepts)
            if parent and parent != concept:
                child_uri = class_uris[concept]
                parent_uri = class_uris[parent]
                hierarchy_graph.add((child_uri, RDFS.subClassOf, parent_uri))
        
        return hierarchy_graph
    
    def generate_properties_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract and generate properties from descriptive text"""
        properties = []
        
        # Pattern for "X has Y" relationships
        has_patterns = re.findall(r'(\w+)\s+has\s+(\w+)', text, re.IGNORECASE)
        for subject, obj in has_patterns:
            properties.append({
                "name": f"has{obj.capitalize()}",
                "domain": subject,
                "range": obj,
                "type": "ObjectProperty"
            })
        
        # Pattern for "X is Y" relationships
        is_patterns = re.findall(r'(\w+)\s+is\s+(?:a\s+)?(\w+)', text, re.IGNORECASE)
        for subject, obj in is_patterns:
            properties.append({
                "name": f"is{obj.capitalize()}",
                "domain": subject,
                "range": obj,
                "type": "ObjectProperty"
            })
        
        # Pattern for attributes
        attr_patterns = re.findall(r'(\w+)\s+(?:with|having)\s+(\w+)', text, re.IGNORECASE)
        for subject, attr in attr_patterns:
            properties.append({
                "name": attr,
                "domain": subject,
                "range": "string",
                "type": "DatatypeProperty"
            })
        
        return properties
    
    def create_spore_pattern(self, pattern_name: str, description: str) -> Dict[str, any]:
        """Create a spore transformation pattern"""
        spore_uri = self.base_namespace[f"spore_{pattern_name}"]
        meta_ns = default_prefix_map.get_namespace("meta")
        
        # Create spore as transformation pattern
        self.graph.add((spore_uri, RDF.type, meta_ns.TransformationPattern))
        self.graph.add((spore_uri, RDFS.label, Literal(pattern_name)))
        self.graph.add((spore_uri, RDFS.comment, Literal(description)))
        
        # Add governance properties
        self.graph.add((spore_uri, meta_ns.distributesPatch, Literal(True)))
        self.graph.add((spore_uri, meta_ns.supportsValidation, Literal(True)))
        
        return {
            "spore_uri": str(spore_uri),
            "pattern_name": pattern_name,
            "description": description,
            "turtle": self.graph.serialize(format="turtle")
        }
    
    def _extract_concepts(self, description: str) -> List[str]:
        """Extract potential concepts/classes from description"""
        # Simple noun extraction - could be enhanced with NLP
        words = re.findall(r'\b[A-Z][a-z]+\b', description)
        
        # Common concept indicators
        concept_words = []
        for word in words:
            if word.lower() not in ["the", "and", "or", "but", "with", "from", "this", "that"]:
                concept_words.append(word)
        
        # Remove duplicates while preserving order
        seen = set()
        concepts = []
        for word in concept_words:
            if word.lower() not in seen:
                concepts.append(word)
                seen.add(word.lower())
        
        return concepts[:10]  # Limit to reasonable number
    
    def _extract_relationships(self, description: str) -> List[Dict[str, str]]:
        """Extract relationships from description"""
        relationships = []
        
        # Look for verb patterns that indicate relationships
        verb_patterns = [
            r'(\w+)\s+(has|contains|includes)\s+(\w+)',
            r'(\w+)\s+(is|are)\s+(?:a\s+)?(\w+)',
            r'(\w+)\s+(belongs to|part of)\s+(\w+)',
            r'(\w+)\s+(uses|requires|needs)\s+(\w+)'
        ]
        
        for pattern in verb_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                subject, verb, obj = match
                prop_name = self._verb_to_property(verb)
                relationships.append({
                    "name": prop_name,
                    "domain": subject,
                    "range": obj,
                    "verb": verb
                })
        
        return relationships
    
    def _create_ontology_header(self, ontology_uri: URIRef, description: str, domain: str):
        """Create ontology metadata"""
        self.graph.add((ontology_uri, RDF.type, OWL.Ontology))
        self.graph.add((ontology_uri, RDFS.label, Literal(f"{domain.title()} Ontology")))
        self.graph.add((ontology_uri, RDFS.comment, Literal(description)))
        self.graph.add((ontology_uri, OWL.versionInfo, Literal("1.0.0")))
    
    def _create_class(self, concept: str) -> URIRef:
        """Create OWL class from concept"""
        class_name = self._to_class_name(concept)
        class_uri = self.base_namespace[class_name]
        
        self.graph.add((class_uri, RDF.type, OWL.Class))
        self.graph.add((class_uri, RDFS.label, Literal(concept)))
        self.graph.add((class_uri, RDFS.comment, Literal(f"Class representing {concept}")))
        
        return class_uri
    
    def _create_property(self, relationship: Dict[str, str], class_uris: Dict[str, URIRef]) -> URIRef:
        """Create OWL property from relationship"""
        prop_name = self._to_property_name(relationship["name"])
        prop_uri = self.base_namespace[prop_name]
        
        # Determine property type
        if relationship.get("range") in class_uris:
            self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
        else:
            self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        
        self.graph.add((prop_uri, RDFS.label, Literal(relationship["name"])))
        
        # Add domain and range if available
        if relationship.get("domain") in class_uris:
            self.graph.add((prop_uri, RDFS.domain, class_uris[relationship["domain"]]))
        
        if relationship.get("range") in class_uris:
            self.graph.add((prop_uri, RDFS.range, class_uris[relationship["range"]]))
        
        return prop_uri
    
    def _to_class_name(self, concept: str) -> str:
        """Convert concept to valid class name"""
        return ''.join(word.capitalize() for word in concept.split())
    
    def _to_property_name(self, name: str) -> str:
        """Convert name to valid property name"""
        words = name.split()
        if len(words) > 1:
            return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        return name.lower()
    
    def _verb_to_property(self, verb: str) -> str:
        """Convert verb to property name"""
        verb_map = {
            "has": "has",
            "contains": "contains",
            "includes": "includes",
            "is": "is",
            "are": "is",
            "belongs to": "belongsTo",
            "part of": "partOf",
            "uses": "uses",
            "requires": "requires",
            "needs": "needs"
        }
        return verb_map.get(verb.lower(), verb.lower())
    
    def _infer_parent_class(self, concept: str, all_concepts: List[str]) -> Optional[str]:
        """Infer parent class based on naming patterns"""
        concept_lower = concept.lower()
        
        # Look for more general terms
        for other in all_concepts:
            other_lower = other.lower()
            if (other_lower in concept_lower and 
                other_lower != concept_lower and 
                len(other_lower) < len(concept_lower)):
                return other
        
        return None
    
    def _bind_prefixes(self):
        """Bind common prefixes to the graph"""
        default_prefix_map.bind_to_graph(self.graph)