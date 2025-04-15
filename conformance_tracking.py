import logging
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
META = Namespace("http://example.org/guidance#")

class ConformanceTracker:
    def __init__(self):
        self.graph = Graph()
        self.load_ontologies()
        
    def load_ontologies(self):
        """Load required ontologies for tracking"""
        self.graph.parse("spore-xna-governance.ttl", format="turtle")
        self.graph.parse("guidance/modules/validation.ttl", format="turtle")
        
    def record_violation(self, spore, label, comment, violation_type, severity):
        """Record a conformance violation"""
        if not all([spore, label, comment, violation_type, severity]):
            raise ValueError("All parameters are required")
            
        violation = URIRef(f"http://example.org/violations/{label.lower().replace(' ', '-')}")
        
        self.graph.add((violation, RDF.type, META.ConformanceViolation))
        self.graph.add((violation, RDFS.label, Literal(label)))
        self.graph.add((violation, RDFS.comment, Literal(comment)))
        self.graph.add((violation, META.violationType, META[violation_type]))
        self.graph.add((violation, META.severity, META[severity]))
        self.graph.add((violation, META.affects, spore))
        
        return violation
        
    def get_violation(self, violation):
        """Get violation details"""
        if not violation:
            raise ValueError("Violation URI is required")
            
        query = """
        SELECT ?label ?comment ?type ?severity ?spore
        WHERE {
            ?violation rdfs:label ?label .
            ?violation rdfs:comment ?comment .
            ?violation meta:violationType ?type .
            ?violation meta:severity ?severity .
            ?violation meta:affects ?spore .
        }
        """
        
        results = list(self.graph.query(query, initBindings={'violation': violation}))
        return results[0] if results else None
        
    def resolve_violation(self, violation, resolution):
        """Resolve a violation"""
        if not violation or not resolution:
            raise ValueError("Violation URI and resolution are required")
            
        self.graph.add((violation, META.resolution, Literal(resolution)))
        return True
        
    def get_violation_history(self, spore):
        """Get violation history for a spore"""
        if not spore:
            raise ValueError("Spore URI is required")
            
        query = """
        SELECT ?violation ?label ?comment ?type ?severity ?resolution
        WHERE {
            ?violation meta:affects ?spore .
            ?violation rdfs:label ?label .
            ?violation rdfs:comment ?comment .
            ?violation meta:violationType ?type .
            ?violation meta:severity ?severity .
            OPTIONAL { ?violation meta:resolution ?resolution }
        }
        """
        
        return list(self.graph.query(query, initBindings={'spore': spore}))
        
    def get_violation_statistics(self, spore):
        """Get violation statistics for a spore"""
        if not spore:
            raise ValueError("Spore URI is required")
            
        query = """
        SELECT ?severity (COUNT(?violation) as ?count)
        WHERE {
            ?violation meta:affects ?spore .
            ?violation meta:severity ?severity .
        }
        GROUP BY ?severity
        """
        
        results = list(self.graph.query(query, initBindings={'spore': spore}))
        stats = {"total": 0, "high": 0, "medium": 0, "low": 0}
        
        for row in results:
            severity = str(row.severity).split("#")[-1]
            count = int(str(row.count))  # Convert to string first
            stats["total"] += count
            stats[severity.lower()] = count
            
        return stats
        
    def notify_violation(self, violation):
        """Send notification for a violation"""
        if not violation:
            raise ValueError("Violation URI is required")
            
        # Implementation would send actual notification
        return True
        
    def export_violations(self, path):
        """Export violations to file"""
        if not path:
            raise ValueError("Export path is required")
            
        self.graph.serialize(destination=path, format="turtle")
        return True 