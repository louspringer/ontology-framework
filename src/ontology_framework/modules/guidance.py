"""Module for managing the guidance ontology."""

from rdflib import Graph, URIRef, Literal, BNode, Namespace, XSD, RDF, RDFS, OWL, SH
from rdflib.namespace import RDF, RDFS, OWL, XSD
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, cast, Sequence, TypedDict, TypeGuard
from rdflib.query import ResultRow, Result
from .ontology import Ontology
from .constants import CONFORMANCE_LEVELS

# Define SHACL terms
SH_CLASS = URIRef("http://www.w3.org/ns/shacl#class")
SH_IN = URIRef("http://www.w3.org/ns/shacl#in")

class GuidanceOntology(Ontology):
    """Class for managing the guidance ontology."""
    
    def __init__(self, guidance_file: Optional[str] = None) -> None:
        """Initialize the guidance ontology.
        
        Args:
            guidance_file: Optional path to an existing guidance.ttl file
        """
        base_uri = "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#"
        super().__init__(base_uri)
        self.base = Namespace(base_uri)
        self.graph.bind("guidance", self.base)
        
        # Define properties
        self.hasStep = self.base['hasStep']
        self.hasName = self.base['hasName']
        self.hasDescription = self.base['hasDescription']
        self.isComplete = self.base['isComplete']
        self.hasStringRepresentation = self.base['hasStringRepresentation']
        self.hasValidationRules = self.base['hasValidationRules']
        self.hasMinimumRequirements = self.base['hasMinimumRequirements']
        self.hasComplianceMetrics = self.base['hasComplianceMetrics']
        self.hasIntegrationStep = self.base['hasIntegrationStep']
        self.stepOrder = self.base['stepOrder']
        self.stepDescription = self.base['stepDescription']
        self.conformanceLevel = self.base['conformanceLevel']
        self.hasTestPhase = self.base['hasTestPhase']
        self.requiresNamespaceValidation = self.base['requiresNamespaceValidation']
        self.requiresPrefixValidation = self.base['requiresPrefixValidation']
        
        # Define all ontology terms
        # Core Classes
        self.ConformanceLevel = self.base.ConformanceLevel
        self.IntegrationProcess = self.base.IntegrationProcess
        self.IntegrationStep = self.base.IntegrationStep
        self.ModelConformance = self.base.ModelConformance
        self.TestProtocol = self.base.TestProtocol
        self.TestPhase = self.base.TestPhase
        self.TestCoverage = self.base.TestCoverage
        self.TODO = self.base.TODO
        self.SHACLValidation = self.base.SHACLValidation
        self.ValidationPattern = self.base.ValidationPattern
        self.IntegrationRequirement = self.base.IntegrationRequirement
        
        # Define SHACL shapes
        self.ConformanceLevelShape = self.base.ConformanceLevelShape
        self.IntegrationProcessShape = self.base.IntegrationProcessShape
        self.IntegrationStepShape = self.base.IntegrationStepShape
        self.ModelConformanceShape = self.base.ModelConformanceShape
        self.TestProtocolShape = self.base.TestProtocolShape
        
        if guidance_file:
            self.load(guidance_file)
        else:
            self._initialize_guidance_ontology()
            
    def _initialize_guidance_ontology(self) -> None:
        """Initialize the guidance ontology with required classes and properties."""
        # Add ontology metadata
        self.graph.add((self.base.uri, RDF.type, OWL.Ontology))
        self.graph.add((self.base.uri, RDFS.label, Literal("Guidance Ontology", lang="en")))
        self.graph.add((self.base.uri, RDFS.comment, Literal("Core guidance ontology for the ontology framework", lang="en")))
        self.graph.add((self.base.uri, OWL.versionInfo, Literal("0.1.0")))
        
        # Add core classes
        classes = [
            (self.ConformanceLevel, "Conformance Level", "A level of conformance for validation"),
            (self.IntegrationProcess, "Integration Process", "Process for integrating model changes"),
            (self.IntegrationStep, "Integration Step", "A step in the integration process"),
            (self.ModelConformance, "Model Conformance", "Rules for ensuring model consistency"),
            (self.TestProtocol, "Test Protocol", "A protocol for testing ontology components"),
            (self.TestPhase, "Test Phase", "A phase in the testing process"),
            (self.TestCoverage, "Test Coverage", "Coverage metrics for testing"),
            (self.TODO, "Future Improvements", "Items for future development and enhancement"),
            (self.SHACLValidation, "SHACL Validation", "Rules and patterns for SHACL validation"),
            (self.ValidationPattern, "Validation Pattern", "Pattern for implementing validation rules"),
            (self.IntegrationRequirement, "Integration Requirement", "Requirements for integrating validation components")
        ]
        
        for class_uri, label, comment in classes:
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(label, lang="en")))
            self.graph.add((class_uri, RDFS.comment, Literal(comment, lang="en")))
            
        # Add properties
        properties = [
            (self.hasStringRepresentation, "has string representation", "The string representation of a conformance level", self.ConformanceLevel, XSD.string),
            (self.hasValidationRules, "has validation rules", "The validation rules for this conformance level", self.ConformanceLevel, XSD.string),
            (self.hasMinimumRequirements, "has minimum requirements", "The minimum requirements for this conformance level", self.ConformanceLevel, XSD.string),
            (self.hasComplianceMetrics, "has compliance metrics", "The compliance metrics for this conformance level", self.ConformanceLevel, XSD.string),
            (self.hasIntegrationStep, "has integration step", "Links a process to its steps", self.IntegrationProcess, self.IntegrationStep),
            (self.stepOrder, "step order", "The order of the integration step", self.IntegrationStep, XSD.string),
            (self.stepDescription, "step description", "Description of the integration step", self.IntegrationStep, XSD.string),
            (self.conformanceLevel, "conformance level", "The level of conformance required", self.ModelConformance, XSD.string),
            (self.hasTestPhase, "has test phase", "Links a test protocol to its phases", self.TestProtocol, self.TestPhase),
            (self.requiresNamespaceValidation, "requires namespace validation", "Whether namespace validation is required", self.TestProtocol, XSD.boolean),
            (self.requiresPrefixValidation, "requires prefix validation", "Whether prefix validation is required", self.TestProtocol, XSD.boolean)
        ]
        
        for prop_uri, label, comment, domain, range_uri in properties:
            if isinstance(range_uri, (URIRef, BNode)):
                self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
            else:
                self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop_uri, RDFS.label, Literal(label, lang="en")))
            self.graph.add((prop_uri, RDFS.comment, Literal(comment, lang="en")))
            self.graph.add((prop_uri, RDFS.domain, domain))
            self.graph.add((prop_uri, RDFS.range, range_uri))
            
        # Add SHACL shapes
        shapes = [
            (self.ConformanceLevelShape, self.ConformanceLevel, [
                (self.hasStringRepresentation, XSD.string, 1, 1),
                (self.hasValidationRules, XSD.string, 1, 1),
                (self.hasMinimumRequirements, XSD.string, 1, 1),
                (self.hasComplianceMetrics, XSD.string, 1, 1)
            ]),
            (self.IntegrationProcessShape, self.IntegrationProcess, [
                (self.hasIntegrationStep, self.IntegrationStep, 1, None),
                (self.stepOrder, XSD.string, 1, 1),
                (self.stepDescription, XSD.string, 1, 1)
            ]),
            (self.IntegrationStepShape, self.IntegrationStep, [
                (self.stepOrder, XSD.string, 1, 1),
                (self.stepDescription, XSD.string, 1, 1)
            ]),
            (self.ModelConformanceShape, self.ModelConformance, [
                (self.conformanceLevel, XSD.string, 1, 1)
            ]),
            (self.TestProtocolShape, self.TestProtocol, [
                (self.hasTestPhase, self.TestPhase, 1, 5),
                (self.requiresPrefixValidation, XSD.boolean, 1, 1),
                (self.requiresNamespaceValidation, XSD.boolean, 1, 1)
            ])
        ]
        
        for shape_uri, target_class, properties in shapes:
            self.graph.add((shape_uri, RDF.type, SH.NodeShape))
            self.graph.add((shape_uri, SH.targetClass, target_class))
            self.graph.add((shape_uri, RDFS.label, Literal(f"{target_class.split('#')[-1]} Shape", lang="en")))
            self.graph.add((shape_uri, RDFS.comment, Literal(f"SHACL shape for validating {target_class.split('#')[-1].lower()}s", lang="en")))
            
            for prop_uri, datatype, min_count, max_count in properties:
                blank = BNode()
                self.graph.add((shape_uri, SH.property, blank))
                self.graph.add((blank, SH.path, prop_uri))
                self.graph.add((blank, SH.minCount, Literal(min_count)))
                if max_count is not None:
                    self.graph.add((blank, SH.maxCount, Literal(max_count)))
                if isinstance(datatype, (URIRef, BNode)):
                    self.graph.add((blank, SH['class'], datatype))
                else:
                    self.graph.add((blank, SH.datatype, datatype))
                    
        # Add individuals
        individuals = [
            (self.base.STRICT, self.ConformanceLevel, "Strict Conformance", "Strict validation rules requiring full compliance", {
                self.hasStringRepresentation: "STRICT",
                self.hasValidationRules: "All validation rules must pass",
                self.hasMinimumRequirements: "All required properties must be present",
                self.hasComplianceMetrics: "100% compliance required"
            }),
            (self.base.MODERATE, self.ConformanceLevel, "Moderate Conformance", "Moderate validation rules allowing some flexibility", {
                self.hasStringRepresentation: "MODERATE",
                self.hasValidationRules: "Most validation rules must pass",
                self.hasMinimumRequirements: "Core properties must be present",
                self.hasComplianceMetrics: "80% compliance required"
            }),
            (self.base.RELAXED, self.ConformanceLevel, "Relaxed Conformance", "Relaxed validation rules with significant flexibility", {
                self.hasStringRepresentation: "RELAXED",
                self.hasValidationRules: "Basic validation rules must pass",
                self.hasMinimumRequirements: "Essential properties must be present",
                self.hasComplianceMetrics: "60% compliance required"
            }),
            (self.base.Phase1, self.TestPhase, "Phase 1", "The first phase of testing", {}),
            (self.base.SampleTestProtocol, self.TestProtocol, "Sample Test Protocol", "A sample test protocol for unit testing", {
                self.conformanceLevel: "STRICT",
                self.requiresNamespaceValidation: True,
                self.requiresPrefixValidation: True
            }),
            (self.base.StandardCoverage, self.TestCoverage, "Standard Coverage", "Standard test coverage requirements", {}),
            (self.base.IntegrationStep1, self.IntegrationStep, "Step 1", "First integration step", {
                self.stepDescription: "First integration step",
                self.stepOrder: "1"
            })
        ]
        
        for ind_uri, type_uri, label, comment, properties in individuals:
            self.graph.add((ind_uri, RDF.type, type_uri))
            self.graph.add((ind_uri, RDFS.label, Literal(label, lang="en")))
            self.graph.add((ind_uri, RDFS.comment, Literal(comment, lang="en")))
            for prop_uri, value in properties.items():
                if isinstance(value, bool):
                    self.graph.add((ind_uri, prop_uri, Literal(value)))
                else:
                    self.graph.add((ind_uri, prop_uri, Literal(value)))
        
    def emit(self, output_path: Union[str, Path] = "guidance.ttl") -> None:
        """Emit the guidance ontology to a Turtle file.
        
        Args:
            output_path: Path where to save the guidance.ttl file
        """
        self.save(output_path)
        
    def get_conformance_levels(self) -> List[Dict[str, str]]:
        """Get all conformance levels and their properties.
        
        Returns:
            List of dictionaries containing conformance level details
        """
        query = """
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?level ?string_rep ?rules ?requirements ?metrics ?label ?comment
        WHERE {
            ?level rdf:type :ConformanceLevel ;
                   :hasStringRepresentation ?string_rep ;
                   :hasValidationRules ?rules ;
                   :hasMinimumRequirements ?requirements ;
                   :hasComplianceMetrics ?metrics ;
                   rdfs:label ?label ;
                   rdfs:comment ?comment .
        }
        """
        results = []
        for row in self.query(query):
            if isinstance(row, ResultRow):
                results.append({
                    'uri': str(row[0]),
                    'string_rep': str(row[1]),
                    'rules': str(row[2]),
                    'requirements': str(row[3]),
                    'metrics': str(row[4]),
                    'label': str(row[5]),
                    'comment': str(row[6])
                })
        return results
    
    def get_validation_rules(self) -> List[Dict[str, str]]:
        """Get all validation rules from the guidance ontology.
        
        Returns:
            List of dictionaries containing validation rule details
        """
        query = """
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        SELECT ?pattern ?label ?description ?priority
        WHERE {
            ?rule rdf:type :ValidationRule ;
                  :hasPattern ?pattern ;
                  rdfs:label ?label ;
                  rdfs:comment ?description ;
                  :hasPriority ?priority .
        }
        """
        results = []
        for row in self.query(query):
            if isinstance(row, ResultRow):
                results.append({
                    'pattern': str(row[0]),
                    'label': str(row[1]),
                    'description': str(row[2]),
                    'priority': str(row[3])
                })
        return results

if __name__ == "__main__":
    # Generate guidance.ttl in the project root
    project_root = Path(__file__).parent.parent.parent
    output_path = project_root / "guidance.ttl"
    guidance = GuidanceOntology()
    guidance.emit(output_path) 