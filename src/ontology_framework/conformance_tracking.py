import logging
import traceback
from pathlib import Path
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import Dict, Any, List, Optional
from ontology_framework.logging_config import framework_logger
from dataclasses import dataclass
import uuid
from .logging_config import OntologyFrameworkLogger
from .meta import META

# Define namespaces
TEST = Namespace("http://example.org/test#")
VIOLATIONS = Namespace("http://example.org/violations#")

@dataclass
class ViolationDetails:
    """Details of a conformance violation."""
    violation: URIRef
    label: str
    comment: str
    type: URIRef
    severity: URIRef
    timestamp: datetime
    resolution: Optional[str] = None
    resolvedAt: Optional[datetime] = None
    status: Optional[URIRef] = None

class ConformanceTracker:
    """Tracks conformance violations and their resolution."""
    
    def __init__(self):
        """Initialize the conformance tracker."""
        self.logger = OntologyFrameworkLogger.get_logger(__name__)
        self.graph = Graph()
        self._load_ontologies()
        # Bind namespaces
        self.graph.bind("meta", META)
        self.graph.bind("test", TEST)
        self.graph.bind("violations", VIOLATIONS)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.logger.info("Conformance tracker initialized successfully")

    def _load_ontologies(self):
        """Load required ontologies."""
        self.logger.debug("Loading ontologies")
        try:
            # Load guidance ontology
            guidance_path = Path("guidance/guidance.ttl")
            if guidance_path.exists():
                self.graph.parse(guidance_path, format="turtle")
                self.logger.info("Guidance ontology loaded successfully")
            else:
                self.logger.warning("Guidance ontology not found")
        except Exception as e:
            self.logger.error(f"Failed to load ontologies: {str(e)}", 
                            context={"error": str(e)},
                            traceback=traceback.format_exc())
            raise

    def record_violation(
            self,
            spore: URIRef,
            label: str,
            comment: str,
            violation_type: str,
            severity: str,
            timestamp: Optional[datetime] = None
        ) -> URIRef:
        """Record a conformance violation.

        Args:
            spore (URIRef): The spore that has the violation.
            label (str): Short label for the violation.
            comment (str): Detailed description of the violation.
            violation_type (str): Type of violation.
            severity (str): Severity level of the violation.
            timestamp (Optional[datetime]): When the violation occurred. Defaults to now.

        Returns:
            URIRef: The URI of the recorded violation.

        Raises:
            ValueError: If any required parameter is missing or invalid.
        """
        if not spore:
            raise ValueError("Spore URI is required")
        if not label:
            raise ValueError("Violation label is required")
        if not comment:
            raise ValueError("Violation comment is required")
        if not violation_type:
            raise ValueError("Violation type is required")
        if not severity:
            raise ValueError("Violation severity is required")

        try:
            violation_id = str(uuid.uuid4())
            violation = URIRef(f"http://example.org/violations/{violation_id}")

            self.graph.add((violation, RDF.type, META.ConformanceViolation))
            self.graph.add((violation, META.affects, spore))
            self.graph.add((violation, RDFS.label, Literal(label)))
            self.graph.add((violation, RDFS.comment, Literal(comment)))
            self.graph.add((violation, META.violationType, getattr(META, violation_type)))
            self.graph.add((violation, META.severity, getattr(META, severity)))
            self.graph.add((violation, META.timestamp, Literal((timestamp or datetime.now()).isoformat(), datatype=XSD.dateTime)))
            self.graph.add((violation, META.status, META.OPEN))

            self.logger.info(f"Recording violation for spore: {spore}")
            self.logger.info(f"Recorded violation: {label}")

            return violation

        except Exception as e:
            self.logger.error(f"Failed to record violation: {str(e)}")
            raise

    def resolve_violation(self, violation: URIRef, resolution: str) -> bool:
        """Resolve a conformance violation.

        Args:
            violation (URIRef): The violation to resolve.
            resolution (str): Description of how the violation was resolved.

        Returns:
            bool: True if the violation was resolved successfully.

        Raises:
            ValueError: If the violation URI is invalid or resolution is empty.
        """
        if not violation:
            raise ValueError("Violation URI is required")
        if not resolution:
            raise ValueError("Resolution message is required")

        try:
            if not (violation, RDF.type, META.ConformanceViolation) in self.graph:
                self.logger.error(f"Invalid violation URI: {violation}")
                raise ValueError(f"Invalid violation URI: {violation}")

            # Remove any existing resolution info
            self.graph.remove((violation, META.resolutionComment, None))
            self.graph.remove((violation, META.resolvedAt, None))
            self.graph.remove((violation, META.status, None))

            # Add new resolution info
            self.graph.add((violation, META.resolutionComment, Literal(resolution)))
            self.graph.add((violation, META.resolvedAt, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
            self.graph.add((violation, META.status, META.Resolved))

            self.logger.info(f"Resolved violation: {violation}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to resolve violation: {str(e)}")
            raise

    def get_violation(self, violation_uri: str) -> Optional[ViolationDetails]:
        """Get details of a specific violation.
        
        Args:
            violation_uri: The URI of the violation
            
        Returns:
            Optional[ViolationDetails]: The violation details if found
        """
        try:
            self.logger.info(f"Getting violation details: {violation_uri}")
            
            query = """
                SELECT ?label ?comment ?type ?severity ?timestamp ?resolution ?resolvedAt ?status
                WHERE {{
                    <{violation_uri}> a meta:ConformanceViolation ;
                        rdfs:label ?label ;
                        rdfs:comment ?comment ;
                        meta:violationType ?type ;
                        meta:severity ?severity ;
                        meta:timestamp ?timestamp .
                    OPTIONAL {{
                        <{violation_uri}> meta:resolutionComment ?resolution ;
                            meta:resolvedAt ?resolvedAt ;
                            meta:status ?status .
                    }}
                }}
            """.format(violation_uri=violation_uri)
            
            results = list(self.graph.query(query))
            if not results:
                return None
                
            row = results[0]
            return ViolationDetails(
                violation=URIRef(violation_uri),
                label=str(row.label),
                comment=str(row.comment),
                type=row.type,
                severity=row.severity,
                timestamp=datetime.fromisoformat(str(row.timestamp).rstrip('Z')),
                resolution=str(row.resolution) if row.resolution else None,
                resolvedAt=datetime.fromisoformat(str(row.resolvedAt).rstrip('Z')) if row.resolvedAt else None,
                status=row.status if row.status else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get violation details: {str(e)}")
            raise

    def get_violation_history(self, spore_uri: str) -> List[ViolationDetails]:
        """Get history of violations for a spore.
        
        Args:
            spore_uri: The URI of the spore
            
        Returns:
            List of ViolationDetails objects containing violation history
        """
        try:
            self.logger.info(f"Getting violation history for spore: {spore_uri}")
            
            query = """
                SELECT ?violation ?label ?comment ?type ?severity ?timestamp ?resolution ?resolvedAt ?status
                WHERE {{
                    ?violation a meta:ConformanceViolation ;
                        meta:affects <{spore_uri}> ;
                        rdfs:label ?label ;
                        rdfs:comment ?comment ;
                        meta:violationType ?type ;
                        meta:severity ?severity ;
                        meta:timestamp ?timestamp .
                    OPTIONAL {{
                        ?violation meta:resolutionComment ?resolution ;
                            meta:resolvedAt ?resolvedAt ;
                            meta:status ?status .
                    }}
                }}
                ORDER BY DESC(?timestamp)
            """.format(spore_uri=spore_uri)
            
            results = list(self.graph.query(query))
            return [
                ViolationDetails(
                    violation=row.violation,
                    label=str(row.label),
                    comment=str(row.comment),
                    type=row.type,
                    severity=row.severity,
                    timestamp=datetime.fromisoformat(str(row.timestamp).rstrip('Z')),
                    resolution=str(row.resolution) if row.resolution else None,
                    resolvedAt=datetime.fromisoformat(str(row.resolvedAt).rstrip('Z')) if row.resolvedAt else None,
                    status=row.status if row.status else None
                )
                for row in results
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get violation history: {str(e)}")
            raise

    def get_violation_statistics(self, spore_uri: str) -> Dict[str, int]:
        """Get statistics about violations for a spore.
        
        Args:
            spore_uri: The URI of the spore
            
        Returns:
            Dict containing violation statistics
        """
        try:
            self.logger.info(f"Getting violation statistics for spore: {spore_uri}")
            
            query = """
                SELECT 
                    (COUNT(?violation) as ?total)
                    (COUNT(?resolved) as ?resolved)
                    (COUNT(?unresolved) as ?unresolved)
                    (COUNT(?high) as ?high)
                    (COUNT(?medium) as ?medium)
                    (COUNT(?low) as ?low)
                WHERE {{
                    {{
                        SELECT ?violation
                        WHERE {{
                            ?violation a meta:ConformanceViolation ;
                                meta:affects <{spore_uri}> .
                        }}
                    }}
                    OPTIONAL {{
                        ?violation meta:status meta:Resolved
                        BIND(?violation as ?resolved)
                    }}
                    OPTIONAL {{
                        ?violation meta:status ?status
                        FILTER (?status != meta:Resolved)
                        BIND(?violation as ?unresolved)
                    }}
                    OPTIONAL {{
                        ?violation meta:severity meta:High
                        BIND(?violation as ?high)
                    }}
                    OPTIONAL {{
                        ?violation meta:severity meta:Medium
                        BIND(?violation as ?medium)
                    }}
                    OPTIONAL {{
                        ?violation meta:severity meta:Low
                        BIND(?violation as ?low)
                    }}
                }}
            """.format(spore_uri=spore_uri)
            
            results = list(self.graph.query(query))
            if not results:
                return {
                    "total": 0,
                    "resolved": 0,
                    "unresolved": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                }
                
            row = results[0]
            return {
                "total": int(row.total),
                "resolved": int(row.resolved),
                "unresolved": int(row.unresolved),
                "high": int(row.high),
                "medium": int(row.medium),
                "low": int(row.low)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get violation statistics: {str(e)}")
            raise

    def notify_violation(self, violation: URIRef) -> bool:
        """Notify about a violation.
        
        Args:
            violation: The URI of the violation to notify about
            
        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Get violation details from graph
            label = str(list(self.graph.objects(violation, RDFS.label))[0])
            comment = str(list(self.graph.objects(violation, RDFS.comment))[0])
            severity = str(list(self.graph.objects(violation, META.severity))[0])
            
            self.logger.info(f"Notifying about violation: {label}")
            self.logger.info(f"Severity: {severity}")
            self.logger.info(f"Details: {comment}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to notify about violation: {str(e)}")
            raise

    def export_violations(self, output_path: str) -> bool:
        """Export violation data to a file."""
        self.logger.info(f"Exporting violations to: {output_path}")
        try:
            if not output_path:
                raise ValueError("Output path cannot be None")
            
            # Create a new graph with only violation-related triples
            export_graph = Graph()
            for s, p, o in self.graph.triples((None, RDF.type, META.ConformanceViolation)):
                export_graph += self.graph.triples((s, None, None))
                
            # Serialize to file
            export_graph.serialize(destination=output_path, format="turtle")
            
            self.logger.info(f"Violations exported successfully to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export violations: {str(e)}", 
                            context={"output_path": output_path, "error": str(e)},
                            traceback=traceback.format_exc())
            raise 