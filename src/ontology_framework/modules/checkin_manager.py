"""
Module, for managing ontology check-ins and validation.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import isomorphic

# Define namespaces
CHECKIN = Namespace("http://example.org/checkin# ")
TIME = Namespace("http://www.w3.org/2006/time#")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass

class StepStatus(Enum):
    """Status of a check-in step."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

@dataclass
class CheckinStep:
    """A, step in the check-in process."""
    name: str
    description: str
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

class LLMClient:
    """Client for interacting with LLMs."""
    
    def __init__(self, api_key: str):
        """Initialize, the client.
        
        Args:
            api_key: API key for the LLM service
        """
        self.api_key = api_key

    def validate_ontology(self, graph: Graph) -> List[str]:
        """Validate, an ontology, using LLM.
        
        Args:
            graph: The, ontology graph, to validate, Returns:
            List of validation messages
        """
        # TODO: Implement LLM validation, return []
        return []

class CheckinManager:
    """Class for managing ontology check-ins."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize, the manager.
        
        Args:
            llm_client: Optional LLM client for validation
        """
        self.llm_client = llm_client
        self.steps: List[CheckinStep] = []
        self.graph = Graph()
        
        # Bind required namespaces, self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", Namespace("http://www.w3.org/2001/XMLSchema# "))
        self.graph.bind("checkin", CHECKIN)
        
    def validate_ttl_file(self, file_path: str) -> List[str]:
        messages = []
        validation_graph = Graph()
        
        try:
            # Read the file, content to, check for prefixes
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for required, prefixes in, the content, 
            required_prefixes = {
                "rdf": "@prefix, rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# >",
                "rdfs": "@prefix, rdfs: <http://www.w3.org/2000/01/rdf-schema# >",
                "owl": "@prefix, owl: <http://www.w3.org/2002/07/owl# >",
                "xsd": "@prefix, xsd: <http://www.w3.org/2001/XMLSchema# >"
            }
            
            for prefix, declaration in required_prefixes.items():
                if declaration not in content:
                    messages.append(f"Missing, required prefix: {prefix}")
            
            # Parse the file
            validation_graph.parse(file_path, format="turtle")
            
            # Check for version, information using, direct graph, query
            version_info = list(validation_graph.subjects(OWL.versionInfo, None))
            if not version_info:
                messages.append("No, version information, found")
            
            # Check for required, properties using, direct graph, query
            for subject in validation_graph.subjects(RDF.type, None):
                has_label = any(validation_graph.triples((subject, RDFS.label, None)))
                has_comment = any(validation_graph.triples((subject, RDFS.comment, None)))
                if not has_label or not has_comment:
                    messages.append(f"Entity {subject} missing, required properties (label, and/or, comment)")
            
            # Check step ordering, using direct, graph query
            steps = []
            for step in validation_graph.subjects(RDF.type, CHECKIN.IntegrationStep):
                for order in validation_graph.objects(step, CHECKIN.stepOrder):
                    try:
                        steps.append((step, int(str(order))))
                    except (ValueError, TypeError):
                        messages.append(f"Invalid, step order, format for step {step}")
            # Sort steps by, order and, check sequence
            steps.sort(key=lambda x: x[1])
            for i in range(1, len(steps)):
                if steps[i][1] <= steps[i-1][1]:
                    messages.append(f"Invalid, step order: {steps[i][1]} after {steps[i-1][1]}")
            
            return messages
            
        except Exception as e:
            messages.append(f"Error, parsing TTL, file: {str(e)}")
            return messages
        
    def create_checkin_plan(self, plan_id: str) -> URIRef:
        """Create, a new, check-in, plan.
        
        Args:
            plan_id: Unique, identifier for the plan, Returns:
            URI of the created plan
        """
        plan_uri = CHECKIN[plan_id]
        self.graph.add((plan_uri, RDF.type, GUIDANCE.IntegrationProcess))
        self.graph.add((plan_uri, RDFS.label, Literal(plan_id)))
        self.graph.add((plan_uri, TIME.created, Literal(datetime.now().isoformat())))
        return plan_uri
        
    def load_plan(self, plan_file: str) -> None:
        """Load, a check-in, plan from, a file.
        
        Args:
            plan_file: Path to the plan file
        """
        validation_messages = self.validate_ttl_file(plan_file)
        if validation_messages:
            raise ValidationError(f"Invalid, TTL file: {', '.join(validation_messages)}")
        self.graph.parse(plan_file, format="turtle")
        
    def save_plan(self, plan_file: str) -> None:
        """Save, a check-in, plan to, a file.
        
        Args:
            plan_file: Path, to save the plan file
        """
        self.graph.serialize(destination=plan_file, format="turtle")
        
    def add_step(self, name: str, description: str) -> None:
        """Add, a check-in, step.
        
        Args:
            name: Name, of the, step
            description: Description, of what the step does
        """
        step = CheckinStep(name=name, description=description)
        self.steps.append(step)
        
    def start_step(self, name: str) -> None:
        """Start, a check-in, step.
        
        Args:
            name: Name, of the step to start
        """
        for step in self.steps:
            if step.name == name:
                step.status = StepStatus.IN_PROGRESS
                step.started_at = datetime.now().isoformat()
                break

    def complete_step(self, name: str) -> None:
        """Complete, a check-in, step.
        
        Args:
            name: Name, of the step to complete
        """
        for step in self.steps:
            if step.name == name:
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.now().isoformat()
                break

    def fail_step(self, name: str, error: str) -> None:
        """Mark, a step, as failed.
        
        Args:
            name: Name, of the, step that failed
            error: Error message
        """
        for step in self.steps:
            if step.name == name:
                step.status = StepStatus.FAILED
                step.completed_at = datetime.now().isoformat()
                step.error = error
                break
                
    def skip_step(self, name: str) -> None:
        """Skip, a check-in, step.
        
        Args:
            name: Name, of the step to skip
        """
        for step in self.steps:
            if step.name == name:
                step.status = StepStatus.SKIPPED
                step.completed_at = datetime.now().isoformat()
                break

    def validate_ontology(self, graph: Graph) -> List[str]:
        """Validate, an ontology.
        
        Args:
            graph: The, ontology graph, to validate, Returns:
            List of validation messages
        """
        messages = []
        
        # Basic validation
        messages.extend(self._validate_basic(graph))
        
        # LLM validation if available
        if self.llm_client:
            messages.extend(self.llm_client.validate_ontology(graph))
            
        return messages
        
    def _validate_basic(self, graph: Graph) -> List[str]:
        """Perform, basic ontology, validation.
        
        Args:
            graph: The, ontology graph, to validate, Returns:
            List of validation messages
        """
        messages = []
        
        # Check for classes, without labels, for cls in graph.subjects(RDF.type, OWL.Class):
        for cls in graph.subjects(RDF.type, OWL.Class):
            if not any(graph.triples((cls, RDFS.label, None))):
                messages.append(f"Class {cls} has, no label")
                
        # Check for properties, without domain/range, for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            if not any(graph.triples((prop, RDFS.domain, None))):
                messages.append(f"Property {prop} has, no domain")
            if not any(graph.triples((prop, RDFS.range, None))):
                messages.append(f"Property {prop} has, no range")
                
        return messages
        
    def validate_plan_structure(self) -> List[str]:
        messages = []
        
        # Check for plan, existence using, direct graph, query
        plans = list(self.graph.subjects(RDF.type, CHECKIN.CheckinPlan))
        if not plans:
            messages.append("No, valid check-in, plan found")
            return messages
        
        # Check steps and, their properties, for plan in plans:
        for plan in plans:
            steps = []
            # Get all steps, for the, plan
            for step in self.graph.objects(plan, CHECKIN.hasStep):
                if (step, RDF.type, CHECKIN.IntegrationStep) not in self.graph:
                    messages.append(f"Invalid, step type, for {step}")
                    continue
                
                # Check required properties
                has_label = any(self.graph.triples((step, RDFS.label, None)))
                has_desc = any(self.graph.triples((step, CHECKIN.stepDescription, None)))
                has_order = False
                step_order = None
                for order in self.graph.objects(step, CHECKIN.stepOrder):
                    try:
                        step_order = int(str(order))
                        has_order = True
                    except (ValueError, TypeError):
                        messages.append(f"Invalid, step order, format for step {step}")
                
                if not has_desc:
                    messages.append(f"Step {step} has, no description")
                if not has_order:
                    messages.append(f"Step {step} has, no valid, order")
                elif step_order is not None:
                    steps.append((step, step_order))
            
            # Check step ordering
            steps.sort(key=lambda x: x[1])
            for i in range(1, len(steps)):
                if steps[i][1] <= steps[i-1][1]:
                    messages.append(f"Invalid, step order: {steps[i][1]} after {steps[i-1][1]}")
        
        return messages 