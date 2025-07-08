#!/usr/bin/env python3
"""
Property Graph Integration Example for Ontology Framework

This module demonstrates how property graphs can be integrated into the existing
ontology framework to provide performance benefits for specific use cases while
maintaining compatibility with the existing RDF/OWL infrastructure.
"""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging
from datetime import datetime

# RDF/OWL imports
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, OWL, XSD, SH
from rdflib.namespace import NamespaceManager

# Property Graph imports (Neo4j)
try:
    from neo4j import GraphDatabase
    from neo4j.exceptions import ServiceUnavailable
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logging.warning("Neo4j driver not available. Property graph features will be disabled.")

# Framework imports
from src.ontology_framework.modules.ontology import Ontology
from src.ontology_framework.modules.validation import ValidationModule
from src.ontology_framework.namespace import NAMESPACES

logger = logging.getLogger(__name__)


class PropertyGraphIntegration:
    """
    Integration layer between RDF/OWL ontologies and property graphs.
    
    This class provides bidirectional synchronization and performance optimization
    for specific use cases while maintaining the formal rigor of RDF/OWL.
    """
    
    def __init__(self, neo4j_uri: str = "bolt://localhost:7687", 
                 username: str = "neo4j", password: str = "password"):
        """Initialize the property graph integration.
        
        Args:
            neo4j_uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        self.ontology = Ontology("http://example.org/ontology#")
        self.validation_module = ValidationModule()
        
        # Initialize Neo4j connection
        if NEO4J_AVAILABLE:
            try:
                self.driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
                self._test_connection()
                logger.info("Neo4j connection established")
            except ServiceUnavailable:
                logger.warning("Neo4j not available, running in RDF-only mode")
                self.driver = None
        else:
            logger.warning("Neo4j driver not available, running in RDF-only mode")
            self.driver = None
    
    def _test_connection(self):
        """Test Neo4j connection."""
        with self.driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
    
    def sync_ontology_to_property_graph(self, ontology_uri: str) -> bool:
        """Sync an ontology from RDF to property graph format.
        
        Args:
            ontology_uri: URI of the ontology to sync
            
        Returns:
            True if sync successful, False otherwise
        """
        if not self.driver:
            logger.warning("Neo4j not available, skipping sync")
            return False
        
        try:
            with self.driver.session() as session:
                # Clear existing data for this ontology
                session.run("""
                    MATCH (n:Ontology {uri: $uri})
                    DETACH DELETE n
                """, uri=ontology_uri)
                
                # Create ontology node
                session.run("""
                    CREATE (o:Ontology {
                        uri: $uri,
                        name: $name,
                        version: $version,
                        synced_at: datetime()
                    })
                """, uri=ontology_uri, name=self._extract_ontology_name(ontology_uri), version="1.0")
                
                # Sync classes
                self._sync_classes(session, ontology_uri)
                
                # Sync properties
                self._sync_properties(session, ontology_uri)
                
                # Sync relationships
                self._sync_relationships(session, ontology_uri)
                
                logger.info(f"Successfully synced ontology {ontology_uri} to property graph")
                return True
                
        except Exception as e:
            logger.error(f"Failed to sync ontology {ontology_uri}: {e}")
            return False
    
    def _sync_classes(self, session, ontology_uri: str):
        """Sync ontology classes to property graph."""
        # Query classes from RDF
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?class ?label ?comment
        WHERE {
            ?class a owl:Class .
            FILTER(STRSTARTS(STR(?class), ?ontology))
            OPTIONAL { ?class rdfs:label ?label }
            OPTIONAL { ?class rdfs:comment ?comment }
        }
        """
        
        results = self.ontology.query(query)
        
        for row in results:
            class_uri = str(row[0])
            label = str(row[1]) if row[1] else class_uri.split('#')[-1]
            comment = str(row[2]) if row[2] else ""
            
            session.run("""
                MATCH (o:Ontology {uri: $ontology_uri})
                CREATE (c:Class {
                    uri: $class_uri,
                    label: $label,
                    comment: $comment
                })
                CREATE (o)-[:CONTAINS]->(c)
            """, ontology_uri=ontology_uri, class_uri=class_uri, label=label, comment=comment)
    
    def _sync_properties(self, session, ontology_uri: str):
        """Sync ontology properties to property graph."""
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?property ?label ?comment ?domain ?range
        WHERE {
            ?property a ?type .
            FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
            FILTER(STRSTARTS(STR(?property), ?ontology))
            OPTIONAL { ?property rdfs:label ?label }
            OPTIONAL { ?property rdfs:comment ?comment }
            OPTIONAL { ?property rdfs:domain ?domain }
            OPTIONAL { ?property rdfs:range ?range }
        }
        """
        
        results = self.ontology.query(query)
        
        for row in results:
            prop_uri = str(row[0])
            label = str(row[1]) if row[1] else prop_uri.split('#')[-1]
            comment = str(row[2]) if row[2] else ""
            domain = str(row[3]) if row[3] else None
            range_val = str(row[4]) if row[4] else None
            
            session.run("""
                MATCH (o:Ontology {uri: $ontology_uri})
                CREATE (p:Property {
                    uri: $prop_uri,
                    label: $label,
                    comment: $comment,
                    domain: $domain,
                    range: $range
                })
                CREATE (o)-[:CONTAINS]->(p)
            """, ontology_uri=ontology_uri, prop_uri=prop_uri, label=label, 
                 comment=comment, domain=domain, range=range_val)
    
    def _sync_relationships(self, session, ontology_uri: str):
        """Sync ontology relationships to property graph."""
        # Sync subclass relationships
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?subclass ?superclass
        WHERE {
            ?subclass rdfs:subClassOf ?superclass .
            FILTER(STRSTARTS(STR(?subclass), ?ontology))
        }
        """
        
        results = self.ontology.query(query)
        
        for row in results:
            subclass = str(row[0])
            superclass = str(row[1])
            
            session.run("""
                MATCH (sub:Class {uri: $subclass})
                MATCH (super:Class {uri: $superclass})
                CREATE (sub)-[:SUBCLASS_OF]->(super)
            """, subclass=subclass, superclass=superclass)
    
    def fast_dependency_analysis(self, component_uri: str) -> List[Dict[str, Any]]:
        """Perform fast dependency analysis using property graph.
        
        Args:
            component_uri: URI of the component to analyze
            
        Returns:
            List of dependencies with metadata
        """
        if not self.driver:
            logger.warning("Neo4j not available, falling back to RDF query")
            return self._dependency_analysis_rdf(component_uri)
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (component:Component {uri: $uri})
                    -[:DEPENDS_ON*]->(dependency:Dependency)
                    RETURN dependency.uri as uri,
                           dependency.label as label,
                           dependency.type as type,
                           length(path()) as depth
                    ORDER BY depth
                """, uri=component_uri)
                
                return [dict(record) for record in result]
                
        except Exception as e:
            logger.error(f"Failed to perform dependency analysis: {e}")
            return self._dependency_analysis_rdf(component_uri)
    
    def _dependency_analysis_rdf(self, component_uri: str) -> List[Dict[str, Any]]:
        """Fallback dependency analysis using RDF/SPARQL."""
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?dependency ?label ?type
        WHERE {
            ?component rdfs:seeAlso ?dependency .
            OPTIONAL { ?dependency rdfs:label ?label }
            OPTIONAL { ?dependency a ?type }
        }
        """
        
        results = self.ontology.query(query)
        return [
            {
                'uri': str(row[0]),
                'label': str(row[1]) if row[1] else str(row[0]),
                'type': str(row[2]) if row[2] else 'Unknown'
            }
            for row in results
        ]
    
    def validation_rule_propagation(self, rule_uri: str) -> List[Dict[str, Any]]:
        """Track validation rule propagation using property graph.
        
        Args:
            rule_uri: URI of the validation rule
            
        Returns:
            List of affected ontologies and components
        """
        if not self.driver:
            return self._validation_propagation_rdf(rule_uri)
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (rule:ValidationRule {uri: $uri})
                    -[:VALIDATES]->(ontology:Ontology)
                    -[:AFFECTS]->(component:Component)
                    RETURN ontology.uri as ontology_uri,
                           ontology.label as ontology_label,
                           component.uri as component_uri,
                           component.label as component_label
                """, uri=rule_uri)
                
                return [dict(record) for record in result]
                
        except Exception as e:
            logger.error(f"Failed to track validation propagation: {e}")
            return self._validation_propagation_rdf(rule_uri)
    
    def _validation_propagation_rdf(self, rule_uri: str) -> List[Dict[str, Any]]:
        """Fallback validation propagation using RDF/SPARQL."""
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?ontology ?component
        WHERE {
            ?rule rdfs:seeAlso ?ontology .
            ?ontology rdfs:seeAlso ?component .
        }
        """
        
        results = self.ontology.query(query)
        return [
            {
                'ontology_uri': str(row[0]),
                'component_uri': str(row[1])
            }
            for row in results
        ]
    
    def namespace_conflict_detection(self) -> List[Dict[str, Any]]:
        """Detect namespace conflicts using property graph.
        
        Returns:
            List of detected conflicts
        """
        if not self.driver:
            return self._namespace_conflicts_rdf()
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (ns1:Namespace)-[:DEFINES]->(concept:Concept)<-[:DEFINES]-(ns2:Namespace)
                    WHERE ns1.uri <> ns2.uri
                    RETURN ns1.uri as namespace1,
                           ns2.uri as namespace2,
                           concept.uri as concept_uri,
                           concept.label as concept_label
                """)
                
                return [dict(record) for record in result]
                
        except Exception as e:
            logger.error(f"Failed to detect namespace conflicts: {e}")
            return self._namespace_conflicts_rdf()
    
    def _namespace_conflicts_rdf(self) -> List[Dict[str, Any]]:
        """Fallback namespace conflict detection using RDF/SPARQL."""
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?ns1 ?ns2 ?concept
        WHERE {
            ?ns1 rdfs:seeAlso ?concept .
            ?ns2 rdfs:seeAlso ?concept .
            FILTER(?ns1 != ?ns2)
        }
        """
        
        results = self.ontology.query(query)
        return [
            {
                'namespace1': str(row[0]),
                'namespace2': str(row[1]),
                'concept_uri': str(row[2])
            }
            for row in results
        ]
    
    def conversation_pattern_analysis(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze conversation patterns using property graph.
        
        Args:
            conversation_id: ID of the conversation to analyze
            
        Returns:
            Analysis results including patterns and participants
        """
        if not self.driver:
            return self._conversation_analysis_rdf(conversation_id)
        
        try:
            with self.driver.session() as session:
                # Get conversation flow
                flow_result = session.run("""
                    MATCH (conv:Conversation {id: $id})
                    -[:HAS_PARTICIPANT]->(participant:Person)
                    -[:MAKES]->(comment:Comment)
                    -[:REFERENCES]->(backlog:BacklogItem)
                    RETURN participant.name as participant,
                           comment.content as content,
                           backlog.label as backlog_item
                    ORDER BY comment.timestamp
                """, id=conversation_id)
                
                # Get decision points
                decision_result = session.run("""
                    MATCH (conv:Conversation {id: $id})
                    -[:LEADS_TO]->(decision:Decision)
                    RETURN decision.description as decision,
                           decision.timestamp as timestamp
                """, id=conversation_id)
                
                return {
                    'flow': [dict(record) for record in flow_result],
                    'decisions': [dict(record) for record in decision_result]
                }
                
        except Exception as e:
            logger.error(f"Failed to analyze conversation patterns: {e}")
            return self._conversation_analysis_rdf(conversation_id)
    
    def _conversation_analysis_rdf(self, conversation_id: str) -> Dict[str, Any]:
        """Fallback conversation analysis using RDF/SPARQL."""
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?participant ?content ?backlog_item
        WHERE {
            ?conversation rdfs:seeAlso ?participant .
            ?participant rdfs:seeAlso ?content .
            ?content rdfs:seeAlso ?backlog_item .
        }
        """
        
        results = self.ontology.query(query)
        return {
            'flow': [
                {
                    'participant': str(row[0]),
                    'content': str(row[1]),
                    'backlog_item': str(row[2])
                }
                for row in results
            ],
            'decisions': []
        }
    
    def _extract_ontology_name(self, ontology_uri: str) -> str:
        """Extract ontology name from URI."""
        return ontology_uri.split('/')[-1].split('#')[0]
    
    def close(self):
        """Close the property graph connection."""
        if self.driver:
            self.driver.close()


class HybridOntologyManager:
    """
    Hybrid ontology manager that combines RDF/OWL and property graph approaches.
    
    This class provides a unified interface for ontology operations, automatically
    choosing the most appropriate backend based on the operation type.
    """
    
    def __init__(self, property_graph_integration: PropertyGraphIntegration):
        """Initialize the hybrid ontology manager.
        
        Args:
            property_graph_integration: Property graph integration instance
        """
        self.pg_integration = property_graph_integration
        self.ontology = property_graph_integration.ontology
    
    def get_dependencies(self, component_uri: str) -> List[Dict[str, Any]]:
        """Get component dependencies using the most appropriate backend.
        
        Args:
            component_uri: URI of the component
            
        Returns:
            List of dependencies
        """
        # Use property graph for performance-critical dependency analysis
        return self.pg_integration.fast_dependency_analysis(component_uri)
    
    def validate_ontology(self, ontology_uri: str) -> Dict[str, Any]:
        """Validate ontology using RDF/OWL reasoning.
        
        Args:
            ontology_uri: URI of the ontology to validate
            
        Returns:
            Validation results
        """
        # Use RDF/OWL for formal validation
        return self.pg_integration.validation_module.validate_ontology(ontology_uri)
    
    def track_validation_propagation(self, rule_uri: str) -> List[Dict[str, Any]]:
        """Track validation rule propagation using property graph.
        
        Args:
            rule_uri: URI of the validation rule
            
        Returns:
            List of affected components
        """
        # Use property graph for relationship traversal
        return self.pg_integration.validation_rule_propagation(rule_uri)
    
    def detect_namespace_conflicts(self) -> List[Dict[str, Any]]:
        """Detect namespace conflicts using property graph.
        
        Returns:
            List of detected conflicts
        """
        # Use property graph for pattern matching
        return self.pg_integration.namespace_conflict_detection()
    
    def analyze_conversation_patterns(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze conversation patterns using property graph.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Analysis results
        """
        # Use property graph for temporal pattern analysis
        return self.pg_integration.conversation_pattern_analysis(conversation_id)


# Example usage
def main():
    """Example usage of the property graph integration."""
    
    # Initialize integration
    pg_integration = PropertyGraphIntegration()
    hybrid_manager = HybridOntologyManager(pg_integration)
    
    # Sync ontology to property graph
    ontology_uri = "http://example.org/ontology#"
    success = pg_integration.sync_ontology_to_property_graph(ontology_uri)
    
    if success:
        print("Ontology synced to property graph successfully")
        
        # Example: Fast dependency analysis
        dependencies = hybrid_manager.get_dependencies("http://example.org/component#ValidationModule")
        print(f"Found {len(dependencies)} dependencies")
        
        # Example: Validation propagation tracking
        affected = hybrid_manager.track_validation_propagation("http://example.org/rule#SHACLConstraint")
        print(f"Validation rule affects {len(affected)} components")
        
        # Example: Namespace conflict detection
        conflicts = hybrid_manager.detect_namespace_conflicts()
        print(f"Found {len(conflicts)} namespace conflicts")
        
        # Example: Conversation pattern analysis
        analysis = hybrid_manager.analyze_conversation_patterns("conv_123")
        print(f"Conversation has {len(analysis['flow'])} interactions and {len(analysis['decisions'])} decisions")
    
    # Clean up
    pg_integration.close()


if __name__ == "__main__":
    main() 