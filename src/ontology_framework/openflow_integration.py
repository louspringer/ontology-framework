"""
OpenFlow-Playground integration with the ontology framework.

This module provides vocabulary alignment between reverse engineering and code generation
domains using the ontology framework's validation and transformation capabilities.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import rdflib
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Import ontology framework components
from .ontology_validator import OntologyValidator
from .sparql_operations import SPARQLOperations
from .validation_handler import ValidationHandler

logger = logging.getLogger(__name__)

class OpenFlowIntegration:
    """
    Integration layer between OpenFlow-Playground and the ontology framework.
    
    This class handles vocabulary alignment between reverse engineering (list-based)
    and code generation (dict-based) representations using ontological validation
    and transformation rules.
    """
    
    def __init__(self, ontology_path: Optional[str] = None):
        """
        Initialize the OpenFlow integration.
        
        Args:
            ontology_path: Path to the OpenFlow-Playground ontology files
        """
        self.ontology_path = ontology_path or Path(__file__).parent.parent.parent / "models"
        self.graph = Graph()
        self._load_ontologies()
        self.validator = OntologyValidator()
        self.sparql = SPARQLOperations(self.graph)
        self.validation_handler = ValidationHandler()
        
    def _load_ontologies(self) -> None:
        """Load all relevant ontology files."""
        try:
            # Load core guidance ontology
            guidance_path = self.ontology_path.parent / "guidance.ttl"
            if guidance_path.exists():
                self.graph.parse(str(guidance_path), format="turtle")
                logger.info("Loaded guidance ontology")
            
            # Load OpenFlow-Playground ontology
            op_path = self.ontology_path / "openflow_playground.ttl"
            if op_path.exists():
                self.graph.parse(str(op_path), format="turtle")
                logger.info("Loaded OpenFlow-Playground ontology")
            
            # Load transformation rules
            transform_path = self.ontology_path / "openflow_transformations.ttl"
            if transform_path.exists():
                self.graph.parse(str(transform_path), format="turtle")
                logger.info("Loaded transformation rules ontology")
                
        except Exception as e:
            logger.error(f"Failed to load ontologies: {e}")
            raise
    
    def validate_vocabulary_alignment(self, reverse_engineering_data: Any, 
                                    code_generation_data: Any) -> Dict[str, Any]:
        """
        Validate vocabulary alignment between reverse engineering and code generation.
        
        Args:
            reverse_engineering_data: Data from reverse engineering domain
            code_generation_data: Data from code generation domain
            
        Returns:
            Validation results and recommendations
        """
        try:
            # Analyze the data structures
            re_analysis = self._analyze_data_structure(reverse_engineering_data, "reverse_engineering")
            cg_analysis = self._analyze_data_structure(code_generation_data, "code_generation")
            
            # Check for vocabulary mismatches
            mismatches = self._identify_vocabulary_mismatches(re_analysis, cg_analysis)
            
            # Generate transformation recommendations
            transformations = self._recommend_transformations(mismatches)
            
            return {
                "valid": len(mismatches) == 0,
                "reverse_engineering_analysis": re_analysis,
                "code_generation_analysis": cg_analysis,
                "vocabulary_mismatches": mismatches,
                "recommended_transformations": transformations,
                "validation_timestamp": str(rdflib.URIRef("http://www.w3.org/2001/XMLSchema#dateTime"))
            }
            
        except Exception as e:
            logger.error(f"Vocabulary alignment validation failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "validation_timestamp": str(rdflib.URIRef("http://www.w3.org/2001/XMLSchema#dateTime"))
            }
    
    def _analyze_data_structure(self, data: Any, domain: str) -> Dict[str, Any]:
        """
        Analyze the structure of data from a specific domain.
        
        Args:
            data: The data to analyze
            domain: The domain name (reverse_engineering or code_generation)
            
        Returns:
            Analysis results
        """
        analysis = {
            "domain": domain,
            "data_type": type(data).__name__,
            "structure": self._get_structure_info(data),
            "components": self._extract_components(data),
            "methods": self._extract_methods(data),
            "vocabulary": self._extract_vocabulary(data)
        }
        
        return analysis
    
    def _get_structure_info(self, data: Any) -> Dict[str, Any]:
        """Get information about the data structure."""
        if isinstance(data, dict):
            return {
                "type": "dictionary",
                "keys": list(data.keys()),
                "depth": self._calculate_depth(data),
                "size": len(data)
            }
        elif isinstance(data, list):
            return {
                "type": "list",
                "length": len(data),
                "item_types": list(set(type(item).__name__ for item in data)),
                "depth": self._calculate_depth(data)
            }
        else:
            return {
                "type": type(data).__name__,
                "depth": 0,
                "size": 1
            }
    
    def _calculate_depth(self, data: Any, current_depth: int = 0) -> int:
        """Calculate the maximum depth of nested data structures."""
        if isinstance(data, (dict, list)) and data:
            if isinstance(data, dict):
                return max(self._calculate_depth(v, current_depth + 1) for v in data.values())
            else:  # list
                return max(self._calculate_depth(item, current_depth + 1) for item in data)
        return current_depth
    
    def _extract_components(self, data: Any) -> List[Dict[str, Any]]:
        """Extract component information from the data."""
        components = []
        
        if isinstance(data, dict):
            # Dictionary format - components are values
            for key, value in data.items():
                if isinstance(value, dict) and self._is_component(value):
                    components.append({
                        "name": key,
                        "type": value.get("type", "unknown"),
                        "description": value.get("description", ""),
                        "properties": list(value.keys())
                    })
        elif isinstance(data, list):
            # List format - components are list items
            for item in data:
                if isinstance(item, dict) and self._is_component(item):
                    components.append({
                        "name": item.get("name", "unnamed"),
                        "type": item.get("type", "unknown"),
                        "description": item.get("description", ""),
                        "properties": list(item.keys())
                    })
        
        return components
    
    def _is_component(self, item: Any) -> bool:
        """Check if an item represents a component."""
        if not isinstance(item, dict):
            return False
        
        # Check for component indicators
        component_indicators = ["name", "type", "description", "methods", "properties"]
        return any(indicator in item for indicator in component_indicators)
    
    def _extract_methods(self, data: Any) -> List[Dict[str, Any]]:
        """Extract method information from the data."""
        methods = []
        
        if isinstance(data, dict):
            # Look for methods in components
            for value in data.values():
                if isinstance(value, dict):
                    methods.extend(self._extract_methods_from_component(value))
        elif isinstance(data, list):
            # Look for methods in list items
            for item in data:
                if isinstance(item, dict):
                    methods.extend(self._extract_methods_from_component(item))
        
        return methods
    
    def _extract_methods_from_component(self, component: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract methods from a single component."""
        methods = []
        
        # Check if component has methods
        if "methods" in component:
            method_list = component["methods"]
            if isinstance(method_list, list):
                for method in method_list:
                    if isinstance(method, dict):
                        methods.append({
                            "name": method.get("name", "unnamed"),
                            "type": method.get("type", "unknown"),
                            "return_type": method.get("return_type", "unknown"),
                            "parameters": method.get("parameters", [])
                        })
        
        return methods
    
    def _extract_vocabulary(self, data: Any) -> Dict[str, Any]:
        """Extract vocabulary information from the data."""
        vocabulary = {
            "terms": set(),
            "data_types": set(),
            "structures": set()
        }
        
        def _extract_from_item(item: Any):
            if isinstance(item, dict):
                vocabulary["terms"].update(item.keys())
                vocabulary["structures"].add("dictionary")
                for value in item.values():
                    _extract_from_item(value)
            elif isinstance(item, list):
                vocabulary["structures"].add("list")
                for subitem in item:
                    _extract_from_item(subitem)
            else:
                vocabulary["data_types"].add(type(item).__name__)
        
        _extract_from_item(data)
        
        # Convert sets to lists for JSON serialization
        return {
            "terms": list(vocabulary["terms"]),
            "data_types": list(vocabulary["data_types"]),
            "structures": list(vocabulary["structures"])
        }
    
    def _identify_vocabulary_mismatches(self, re_analysis: Dict[str, Any], 
                                      cg_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify vocabulary mismatches between domains."""
        mismatches = []
        
        # Check structure mismatches
        re_structure = re_analysis["structure"]["type"]
        cg_structure = cg_analysis["structure"]["type"]
        
        if re_structure != cg_structure:
            mismatches.append({
                "type": "structure_mismatch",
                "reverse_engineering": re_structure,
                "code_generation": cg_structure,
                "description": f"Reverse engineering uses {re_structure}, code generation expects {cg_structure}",
                "severity": "HIGH"
            })
        
        # Check vocabulary term mismatches
        re_terms = set(re_analysis["vocabulary"]["terms"])
        cg_terms = set(cg_analysis["vocabulary"]["terms"])
        
        missing_in_cg = re_terms - cg_terms
        missing_in_re = cg_terms - re_terms
        
        if missing_in_cg:
            mismatches.append({
                "type": "missing_vocabulary",
                "domain": "code_generation",
                "missing_terms": list(missing_in_cg),
                "description": f"Code generation domain missing terms: {missing_in_cg}",
                "severity": "MEDIUM"
            })
        
        if missing_in_re:
            mismatches.append({
                "type": "missing_vocabulary",
                "domain": "reverse_engineering",
                "missing_terms": list(missing_in_re),
                "description": f"Reverse engineering domain missing terms: {missing_in_re}",
                "severity": "MEDIUM"
            })
        
        return mismatches
    
    def _recommend_transformations(self, mismatches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recommend transformations to resolve vocabulary mismatches."""
        transformations = []
        
        for mismatch in mismatches:
            if mismatch["type"] == "structure_mismatch":
                if (mismatch["reverse_engineering"] == "list" and 
                    mismatch["code_generation"] == "dictionary"):
                    transformations.append({
                        "type": "list_to_dict",
                        "description": "Transform list-based components to dictionary format",
                        "transformation_rule": "OpenFlowComponentTransformation",
                        "implementation": "Use transform_list_to_dict function",
                        "priority": "HIGH"
                    })
                elif (mismatch["reverse_engineering"] == "dictionary" and 
                      mismatch["code_generation"] == "list"):
                    transformations.append({
                        "type": "dict_to_list",
                        "description": "Transform dictionary-based components to list format",
                        "transformation_rule": "OpenFlowMethodTransformation",
                        "implementation": "Use transform_dict_to_list function",
                        "priority": "HIGH"
                    })
        
        return transformations
    
    def apply_transformation(self, data: Any, transformation_type: str) -> Any:
        """
        Apply a transformation to resolve vocabulary mismatches.
        
        Args:
            data: The data to transform
            transformation_type: Type of transformation to apply
            
        Returns:
            Transformed data
        """
        if transformation_type == "list_to_dict":
            return self._transform_list_to_dict(data)
        elif transformation_type == "dict_to_list":
            return self._transform_dict_to_list(data)
        else:
            raise ValueError(f"Unknown transformation type: {transformation_type}")
    
    def _transform_list_to_dict(self, component_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform list of components to dictionary keyed by name."""
        if not isinstance(component_list, list):
            raise ValueError("Input must be a list")
        
        result = {}
        for component in component_list:
            if isinstance(component, dict) and 'name' in component:
                result[component['name']] = component
            else:
                raise ValueError("Each component must be a dict with 'name' field")
        
        return result
    
    def _transform_dict_to_list(self, component_dict: Dict[str, Any]) -> List[Any]:
        """Transform dictionary of components to list."""
        if not isinstance(component_dict, dict):
            raise ValueError("Input must be a dictionary")
        
        return list(component_dict.values())
    
    def get_ontology_summary(self) -> Dict[str, Any]:
        """Get a summary of the loaded ontology."""
        try:
            # Count classes, properties, and instances
            classes = list(self.graph.subjects(RDF.type, OWL.Class))
            object_properties = list(self.graph.subjects(RDF.type, OWL.ObjectProperty))
            data_properties = list(self.graph.subjects(RDF.type, OWL.DatatypeProperty))
            instances = list(self.graph.subjects(RDF.type, OWL.NamedIndividual))
            
            return {
                "classes": len(classes),
                "object_properties": len(object_properties),
                "data_properties": len(data_properties),
                "instances": len(instances),
                "total_statements": len(self.graph),
                "namespaces": list(self.graph.namespaces())
            }
        except Exception as e:
            logger.error(f"Failed to get ontology summary: {e}")
            return {"error": str(e)}
