"""Guidance loader functionality for the ontology framework.

This module provides functionality for loading and parsing guidance files that
define rules and requirements for ontology development.
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
        
    def get_test_requirements(self) -> Dict[str, List[str]]:
        """Get test requirements from guidance.
        
        Returns:
            Dictionary mapping test types to lists of requirements
        """
        requirements = {}
        
        # Get test protocol requirements
        test_protocols = self.graph.subjects(RDF.type, GUIDANCE.TestProtocol)
        for protocol in test_protocols:
            protocol_reqs = []
            for phase in self.graph.objects(protocol, GUIDANCE.hasTestPhase):
                for test_case in self.graph.objects(phase, VALIDATION.hasTestCase):
                    protocol_reqs.append(str(test_case))
            requirements["protocol"] = protocol_reqs
            
        # Get coverage requirements
        coverage_reqs = []
        for coverage in self.graph.subjects(RDF.type, GUIDANCE.TestCoverage):
            threshold = self.graph.value(coverage, GUIDANCE.coverageThreshold)
            if threshold:
                coverage_reqs.append(f"Coverage threshold: {float(threshold)}")
        requirements["coverage"] = coverage_reqs
        
        return requirements
        
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