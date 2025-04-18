from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib.plugins.sparql import prepareQuery
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class GuidanceLoader:
    """Utility class for loading and querying the guidance ontology."""
    
    def __init__(self, guidance_path: Path):
        """Initialize the guidance loader with the path to guidance.ttl."""
        self.guidance_path = guidance_path
        self.graph = Graph()
        self._load_guidance()
        
        # Define namespaces
        self.NS = {
            "meta": URIRef("./meta#"),
            "metameta": URIRef("./metameta#"),
            "problem": URIRef("./problem#"),
            "solution": URIRef("./solution#"),
            "conversation": URIRef("./conversation#"),
            "guidance": URIRef("./guidance#"),
            "rdf": RDF,
            "rdfs": RDFS,
            "owl": OWL,
            "xsd": XSD
        }
        
        # Bind namespaces to the graph
        for prefix, uri in self.NS.items():
            self.graph.bind(prefix, uri)
            logger.debug(f"Bound prefix {prefix} to {uri}")
    
    def _load_guidance(self):
        """Load the guidance ontology from the specified path."""
        try:
            self.graph.parse(str(self.guidance_path), format="turtle")
            logger.info(f"Loaded guidance ontology from {self.guidance_path}")
            # Bind namespaces
            self.graph.bind('guidance', URIRef('./guidance#'))
            self.graph.bind('rdf', RDF)
            self.graph.bind('rdfs', RDFS)
            self.graph.bind('owl', OWL)
            self.graph.bind('xsd', XSD)
        except Exception as e:
            logger.error(f"Failed to load guidance ontology: {e}")
            raise
    
    def get_section(self, section_name: str) -> List[Dict[str, Any]]:
        """Retrieve all triples for a specific section."""
        query = prepareQuery("""
            SELECT ?subject ?predicate ?object
            WHERE {
                ?subject ?predicate ?object .
                FILTER (STRSTARTS(STR(?subject), "./guidance#") &&
                        CONTAINS(STR(?subject), ?section_name))
            }
        """)
        results = []
        for row in self.graph.query(query, initBindings={'section_name': Literal(section_name)}):
            if isinstance(row, tuple) and len(row) >= 3:
                results.append({
                    "subject": str(row[0]),
                    "predicate": str(row[1]),
                    "object": str(row[2])
                })
        return results
    
    def get_requirements(self, requirement_type: str) -> List[Dict[str, str]]:
        """Retrieve requirements of a specific type."""
        query = prepareQuery("""
            SELECT ?subject ?label ?comment
            WHERE {
                ?subject a ?type .
                ?subject rdfs:label ?label .
                ?subject rdfs:comment ?comment .
                FILTER (STRSTARTS(STR(?subject), "./guidance#"))
            }
        """)
        results = []
        for row in self.graph.query(query, initBindings={'type': URIRef(f"./guidance#{requirement_type}")}):
            if isinstance(row, tuple) and len(row) >= 3:
                results.append({
                    "subject": str(row[0]),
                    "label": str(row[1]),
                    "comment": str(row[2])
                })
        return results
    
    def get_shapes(self) -> List[Dict[str, Any]]:
        """Retrieve SHACL shapes from the guidance ontology."""
        query = prepareQuery("""
            SELECT ?shape ?targetClass ?path ?minCount ?maxCount ?datatype ?allowedValues
            WHERE {
                ?shape a sh:NodeShape .
                ?shape sh:targetClass ?targetClass .
                ?shape sh:property ?property .
                ?property sh:path ?path .
                OPTIONAL { ?property sh:minCount ?minCount }
                OPTIONAL { ?property sh:maxCount ?maxCount }
                OPTIONAL { ?property sh:datatype ?datatype }
                OPTIONAL { 
                    ?property sh:in ?allowedValues .
                    ?allowedValues rdf:rest*/rdf:first ?value .
                }
            }
        """)
        shapes = []
        seen_shapes = set()
        for row in self.graph.query(query):
            if isinstance(row, tuple) and len(row) >= 6:
                shape_uri = str(row[0])
                if shape_uri not in seen_shapes:
                    shape = {
                        "shape": shape_uri,
                        "targetClass": str(row[1]),
                        "path": str(row[2])
                    }
                    if row[3] is not None:
                        shape["minCount"] = int(row[3])
                    if row[4] is not None:
                        shape["maxCount"] = int(row[4])
                    if row[5] is not None:
                        shape["datatype"] = str(row[5])
                    
                    # Get allowed values
                    values_query = prepareQuery("""
                        SELECT ?value
                        WHERE {
                            ?property sh:in ?list .
                            ?list rdf:rest*/rdf:first ?value .
                            FILTER(?property = ?target_property)
                        }
                    """)
                    values = []
                    for value_row in self.graph.query(values_query, initBindings={'target_property': row[2]}):
                        values.append(str(value_row[0]))
                    if values:
                        shape["allowedValues"] = values
                    
                    shapes.append(shape)
                    seen_shapes.add(shape_uri)
        return shapes
    
    def get_test_requirements(self) -> Dict[str, Any]:
        """Retrieve all test-related requirements."""
        return {
            "protocols": self.get_requirements("TestProtocol"),
            "phases": self.get_requirements("TestPhase"),
            "coverage": self.get_requirements("TestCoverage"),
            "shapes": self.get_shapes()
        }
    
    def validate_against_shape(self, instance: dict, shape_name: str) -> dict:
        """Validate an instance against its SHACL shape."""
        shape = next(s for s in self.get_shapes() if s["shape"].endswith(shape_name))
        violations = []
        
        # Check required properties
        if "minCount" in shape:
            query = prepareQuery("""
                SELECT (COUNT(?value) as ?count)
                WHERE {
                    ?subject ?path ?value .
                    FILTER (?subject = ?instance)
                }
            """)
            count = next(self.graph.query(query, initBindings={
                'instance': URIRef(instance["subject"]),
                'path': URIRef(shape["path"])
            }))[0]
            if count < shape["minCount"]:
                violations.append(f"Minimum count of {shape['minCount']} not met")

        # Check maximum count
        if "maxCount" in shape:
            if count > shape["maxCount"]:
                violations.append(f"Maximum count of {shape['maxCount']} exceeded")

        # Check datatype
        if "datatype" in shape:
            query = prepareQuery("""
                SELECT ?value
                WHERE {
                    ?subject ?path ?value .
                    FILTER (?subject = ?instance)
                }
            """)
            for value in self.graph.query(query, initBindings={
                'instance': URIRef(instance["subject"]),
                'path': URIRef(shape["path"])
            }):
                if not isinstance(value[0], Literal) or str(value[0].datatype) != shape["datatype"]:
                    violations.append(f"Value {value[0]} does not match datatype {shape['datatype']}")

        # Check allowed values
        if "allowedValues" in shape:
            query = prepareQuery("""
                SELECT ?value
                WHERE {
                    ?subject ?path ?value .
                    FILTER (?subject = ?instance)
                }
            """)
            for value in self.graph.query(query, initBindings={
                'instance': URIRef(instance["subject"]),
                'path': URIRef(shape["path"])
            }):
                if str(value[0]) not in shape["allowedValues"]:
                    violations.append(f"Value {value[0]} not in allowed values {shape['allowedValues']}")

        return {
            "isValid": len(violations) == 0,
            "violations": violations
        } 