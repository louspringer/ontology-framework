from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib.plugins.sparql import prepareQuery
from typing import List, Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class GuidanceLoader:
    """Utility class for loading and querying the guidance ontology."""
    
    def __init__(self, guidance_path: Union[str, Path]):
        """Initialize the GuidanceLoader with a path to the guidance TTL file."""
        self.guidance_path = Path(guidance_path)
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
        """Load the guidance ontology from the TTL file."""
        try:
            self.graph.parse(self.guidance_path, format="turtle")
            logger.info(f"Loaded guidance ontology from {self.guidance_path}")
            
            # Bind common prefixes
            prefixes = {
                "meta": "./meta#",
                "metameta": "./metameta#",
                "problem": "./problem#",
                "solution": "./solution#",
                "conversation": "./conversation#",
                "guidance": "./guidance#",
                "rdf": str(RDF),
                "rdfs": str(RDFS),
                "owl": str(OWL),
                "xsd": str(XSD)
            }
            for prefix, uri in prefixes.items():
                self.graph.bind(prefix, uri)
                logger.debug(f"Bound prefix {prefix} to {uri}")
        except Exception as e:
            logger.error(f"Failed to load guidance ontology: {e}")
            raise
    
    def get_section(self, section_name: str) -> List[Dict[str, str]]:
        """Get all triples where the subject starts with the given section name."""
        query = f"""
        SELECT ?s ?p ?o
        WHERE {{
            ?s ?p ?o .
            FILTER(STRSTARTS(STR(?s), "./guidance#{section_name}"))
        }}
        """
        results = []
        for row in self.graph.query(query):
            s, p, o = row
            results.append({
                "subject": str(s),
                "predicate": str(p),
                "object": str(o.value) if isinstance(o, Literal) else str(o)
            })
        return results
    
    def get_requirements(self, requirement_type: str) -> List[Dict[str, str]]:
        """Get all requirements of a specific type."""
        query = f"""
        SELECT ?s ?label ?comment
        WHERE {{
            ?s rdf:type guidance:{requirement_type} .
            OPTIONAL {{ ?s rdfs:label ?label }}
            OPTIONAL {{ ?s rdfs:comment ?comment }}
        }}
        """
        results = []
        for row in self.graph.query(query):
            s, label, comment = row
            results.append({
                "uri": str(s),
                "label": str(label) if label else "",
                "comment": str(comment) if comment else ""
            })
        return results
    
    def get_shapes(self, shape_type: str) -> List[Dict[str, Union[str, int]]]:
        """Get all SHACL shapes for a specific type."""
        query = f"""
        SELECT ?shape ?targetClass ?property ?minCount ?maxCount ?datatype ?allowedValues
        WHERE {{
            ?shape a sh:NodeShape ;
                   sh:targetClass ?targetClass .
            ?shape sh:property ?property .
            OPTIONAL {{ ?property sh:minCount ?minCount }}
            OPTIONAL {{ ?property sh:maxCount ?maxCount }}
            OPTIONAL {{ ?property sh:datatype ?datatype }}
            OPTIONAL {{ ?property sh:in ?allowedValues }}
            FILTER(STRSTARTS(STR(?shape), "./guidance#{shape_type}"))
        }}
        """
        results = []
        for row in self.graph.query(query):
            shape, target_class, prop, min_count, max_count, datatype, allowed_values = row
            result = {
                "shape": str(shape),
                "targetClass": str(target_class),
                "property": str(prop),
                "minCount": int(min_count.value) if min_count else "",
                "maxCount": int(max_count.value) if max_count else "",
                "datatype": str(datatype) if datatype else ""
            }
            if allowed_values:
                result["allowedValues"] = [str(v) for v in allowed_values]
            results.append(result)
        return results
    
    def get_test_requirements(self) -> Dict[str, Any]:
        """Retrieve all test-related requirements."""
        return {
            "protocols": self.get_requirements("TestProtocol"),
            "phases": self.get_requirements("TestPhase"),
            "coverage": self.get_requirements("TestCoverage"),
            "shapes": self.get_shapes("Test")
        }
    
    def validate_against_shape(self, instance: Dict[str, str], shape_type: str) -> Dict[str, bool]:
        """Validate an instance against a SHACL shape."""
        # Create a temporary graph with the instance
        instance_graph = Graph()
        instance_uri = URIRef(instance.get("uri", "./temp#instance"))
        
        # Add the instance triples
        for pred, obj in instance.items():
            if pred != "uri":
                instance_graph.add((
                    instance_uri,
                    URIRef(f"./guidance#{pred}"),
                    Literal(obj)
                ))

        # Get the shape
        shapes = self.get_shapes(shape_type)
        if not shapes:
            return {"isValid": False, "errors": ["Shape not found"]}

        shape = shapes[0]
        
        # Validate required properties
        errors = []
        if shape.get("minCount"):
            for prop in shape.get("properties", []):
                count = len(list(instance_graph.triples((instance_uri, URIRef(prop), None))))
                if count < shape["minCount"]:
                    errors.append(f"Property {prop} has {count} values, minimum required is {shape['minCount']}")

        return {
            "isValid": len(errors) == 0,
            "errors": errors
        } 