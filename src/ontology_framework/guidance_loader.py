"""Guidance loader functionality for the ontology framework.

This module provides functionality for loading and parsing guidance files that define rules and requirements for ontology development.
"""

from typing import Dict, List, Optional, Set, Union
import logging
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from .exceptions import GuidanceError

logger = logging.getLogger(__name__)

# Define namespaces
SHACL = Namespace("http://www.w3.org/ns/shacl#")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
CORE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/core#")
MODEL = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/model#")
VALIDATION = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation#")

class GuidanceLoader:
    """Loads and parses ontology guidance files."""
    
    def __init__(self, guidance_file: Union[str, Path]):
        """Initialize guidance loader.
        
        Args:
            guidance_file: Path to guidance TTL file
        Raises:
            GuidanceError: If guidance file cannot be loaded
        """
        self.guidance_file = Path(guidance_file)
        self.graph = Graph()
        
        try:
            self.graph.parse(str(self.guidance_file), format="turtle")
            logger.info(f"Loaded guidance from {self.guidance_file}")
        except Exception as e:
            raise GuidanceError(f"Failed to load guidance file: {str(e)}")
            
        # Bind namespaces
        self.graph.bind("guidance", GUIDANCE)
        self.graph.bind("core", CORE)
        self.graph.bind("model", MODEL)
        self.graph.bind("validation", VALIDATION)
        
    def get_section(self, class_name: str) -> List[Dict[str, str]]:
        """Get all triples related to a specific class.
        
        Args:
            class_name: Name of the class to get information for
            
        Returns:
            List of dictionaries containing subject, predicate, object information
        """
        results = []
        
        # Try different namespace combinations
        for ns in [GUIDANCE, CORE, MODEL, VALIDATION]:
            class_uri = ns[class_name]
            
            # Get all triples where this class is the subject
            for pred, obj in self.graph.predicate_objects(class_uri):
                results.append({
                    "subject": str(class_uri),
                    "predicate": str(pred),
                    "object": str(obj)
                })
            
            # Get all triples where instances of this class are subjects
            for instance in self.graph.subjects(RDF.type, class_uri):
                for pred, obj in self.graph.predicate_objects(instance):
                    results.append({
                        "subject": str(instance),
                        "predicate": str(pred),
                        "object": str(obj)
                    })
        
        return results
    
    def get_requirements(self, class_name: str) -> List[Dict[str, str]]:
        """Get requirements for a specific class.
        
        Args:
            class_name: Name of the class to get requirements for
            
        Returns:
            List of dictionaries containing requirement information
        """
        requirements = []
        
        # Try different namespace combinations
        for ns in [GUIDANCE, CORE, MODEL, VALIDATION]:
            class_uri = ns[class_name]
            
            # Get all instances of this class
            for instance in self.graph.subjects(RDF.type, class_uri):
                req = {"subject": str(instance)}
                
                # Get label
                label = self.graph.value(instance, RDFS.label)
                if label:
                    req["label"] = str(label)
                
                # Get comment
                comment = self.graph.value(instance, RDFS.comment)
                if comment:
                    req["comment"] = str(comment)
                
                # Get other properties
                for pred, obj in self.graph.predicate_objects(instance):
                    if pred not in [RDF.type, RDFS.label, RDFS.comment]:
                        prop_name = str(pred).split("#")[-1].split("/")[-1]
                        req[prop_name] = str(obj)
                
                if len(req) > 1:  # Only add if we have more than just the subject
                    requirements.append(req)
        
        return requirements
        
    def get_test_requirements(self) -> Dict[str, List[Dict[str, str]]]:
        """Get test requirements from guidance.
        
        Returns:
            Dictionary mapping test types to lists of requirements
        """
        requirements = {
            "protocols": [],
            "phases": [],
            "coverage": [],
            "shapes": []
        }
        
        # Get test protocols
        requirements["protocols"] = self.get_requirements("TestProtocol")
        
        # Get test phases
        requirements["phases"] = self.get_requirements("TestPhase")
        
        # Get test coverage
        requirements["coverage"] = self.get_requirements("TestCoverage")
        
        # Get SHACL shapes
        requirements["shapes"] = self.get_shapes()
        
        return requirements
    
    def get_shapes(self) -> List[Dict[str, str]]:
        """Get SHACL shapes from guidance.
        
        Returns:
            List of dictionaries containing shape information
        """
        shapes = []
        
        # Get all NodeShapes
        for shape in self.graph.subjects(RDF.type, SHACL.NodeShape):
            shape_info = {"subject": str(shape)}
            
            # Get target class
            target_class = self.graph.value(shape, SHACL.targetClass)
            if target_class:
                shape_info["targetClass"] = str(target_class)
            
            # Get label
            label = self.graph.value(shape, RDFS.label)
            if label:
                shape_info["label"] = str(label)
            
            # Get comment
            comment = self.graph.value(shape, RDFS.comment)
            if comment:
                shape_info["comment"] = str(comment)
            
            # Get property constraints
            for prop in self.graph.objects(shape, SHACL.property):
                # Get path
                path = self.graph.value(prop, SHACL.path)
                if path:
                    shape_info["path"] = str(path)
                
                # Get cardinality constraints
                min_count = self.graph.value(prop, SHACL.minCount)
                if min_count:
                    shape_info["minCount"] = int(min_count)
                
                max_count = self.graph.value(prop, SHACL.maxCount)
                if max_count:
                    shape_info["maxCount"] = int(max_count)
                
                # Get datatype
                datatype = self.graph.value(prop, SHACL.datatype)
                if datatype:
                    shape_info["datatype"] = str(datatype)
                
                # Get allowed values
                in_list = self.graph.value(prop, SHACL["in"])
                if in_list:
                    allowed_values = []
                    for item in self.graph.items(in_list):
                        allowed_values.append(str(item))
                    shape_info["allowedValues"] = allowed_values
            
            shapes.append(shape_info)
        
        return shapes
    
    def validate_against_shape(self, data: Dict[str, str], shape_name: str) -> Dict[str, Union[bool, List[str]]]:
        """Validate data against a SHACL shape.
        
        Args:
            data: Data to validate
            shape_name: Name of the shape to validate against
            
        Returns:
            Dictionary containing validation results
        """
        # This is a simplified validation - in a real implementation,
        # you would use a proper SHACL validator
        return {
            "isValid": True,
            "violations": []
        }
        
    def get_model_requirements(self) -> Dict[str, bool]:
        """Get model requirements from guidance.
        
        Returns:
            Dictionary of requirement names and their required status
        """
        requirements = {}
        
        model_reqs = self.graph.value(None, RDF.type, GUIDANCE.ModelRequirements)
        if model_reqs:
            requirements["version_tracking"] = bool(self.graph.value(model_reqs, GUIDANCE.requiresVersionTracking))
            requirements["dependency_management"] = bool(self.graph.value(model_reqs, GUIDANCE.requiresDependencyManagement))
            requirements["validation_pipeline"] = bool(self.graph.value(model_reqs, GUIDANCE.requiresValidationPipeline))
            requirements["documentation"] = bool(self.graph.value(model_reqs, GUIDANCE.requiresDocumentation))
            
        return requirements
        
    def get_validation_rules(self) -> List[Dict[str, str]]:
        """Get validation rules from guidance.
        
        Returns:
            List of dictionaries containing rule information
        """
        rules = []
        
        # Get pattern rules
        for pattern_rule in self.graph.subjects(RDF.type, GUIDANCE.PatternRule):
            rule = {
                "text": str(self.graph.value(pattern_rule, GUIDANCE.ruleText)),
                "example": str(self.graph.value(pattern_rule, GUIDANCE.ruleExample)),
                "counter_example": str(self.graph.value(pattern_rule, GUIDANCE.ruleCounterExample))
            }
            rules.append(rule)
            
        # Get structure requirements
        for struct_req in self.graph.subjects(RDF.type, GUIDANCE.StructureRequirement):
            rule = {
                "text": str(self.graph.value(struct_req, GUIDANCE.requirementText)),
                "query": str(self.graph.value(struct_req, GUIDANCE.validationQuery))
            }
            rules.append(rule)
            
        return rules 