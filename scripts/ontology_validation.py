#!/usr/bin/env python3
"""
Ontology Validation Script

This script validates ontologies against a set of rules and tracks the validation results
as metadata in the ontology itself. The validation results are stored both in memory
as Python objects and in the ontology as RDF triples.

The validation metadata follows the structure defined in guidance/modules/ontology_tracking.ttl,
which defines classes and properties for tracking validation status, results, and errors.

Key concepts:
- ValidationResult: Represents a single validation check result
- ValidationReport: Aggregates results for an entire ontology
- OntologyValidator: Performs validation and updates the ontology with results

The metadata is stored in the ontology using the following pattern:
- Each validation result is an instance of tracking:ValidationResult
- Results are linked to the ontology via tracking:hasValidationResult
- The validation status is tracked via tracking:TestingStatus
"""

from datetime import datetime
import os
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
import requests
import logging
from pathlib import Path

# Define namespaces for validation metadata
TRACKING = Namespace("http://example.org/tracking#")
VAL = Namespace("http://example.org/validation#")

class ValidationResult:
    """
    Represents a single validation check result.
    This class maps to tracking:ValidationResult in the ontology.
    """
    def __init__(self, rule, status, message, severity):
        self.rule = rule
        self.status = status
        self.message = message
        self.severity = severity

    def to_dict(self):
        return {
            "rule": self.rule,
            "status": self.status,
            "message": self.message,
            "severity": self.severity
        }

    def to_rdf(self, graph, subject):
        """Convert this result to RDF triples in the given graph."""
        graph.add((subject, RDF.type, TRACKING.ValidationResult))
        graph.add((subject, TRACKING.validationRule, Literal(self.rule)))
        graph.add((subject, TRACKING.ruleResult, Literal(self.status)))
        graph.add((subject, TRACKING.errorMessage, Literal(self.message)))
        graph.add((subject, TRACKING.priority, Literal(self._get_priority())))

    def _get_priority(self):
        """Map severity to priority level."""
        if self.severity >= 2:
            return "HIGH"
        elif self.severity == 1:
            return "MEDIUM"
        return "LOW"

class ValidationReport:
    """
    Aggregates validation results for an ontology.
    This class maps to tracking:TestingStatus in the ontology.
    """
    def __init__(self, results, error_count, timestamp, ontology_path):
        self.results = results
        self.error_count = error_count
        self.timestamp = timestamp
        self.ontology_path = ontology_path

    def to_dict(self):
        return {
            "results": [r.to_dict() for r in self.results],
            "error_count": self.error_count,
            "timestamp": self.timestamp,
            "ontology_path": self.ontology_path
        }

    def to_rdf(self, graph, subject):
        """Convert this report to RDF triples in the given graph."""
        graph.add((subject, RDF.type, TRACKING.TestingStatus))
        graph.add((subject, TRACKING.lastTested, Literal(self.timestamp, datatype=XSD.dateTime)))
        graph.add((subject, TRACKING.testResult, Literal("PASS" if self.error_count == 0 else "FAIL")))
        graph.add((subject, TRACKING.errorCount, Literal(self.error_count, datatype=XSD.integer)))

        # Add validation results
        for i, result in enumerate(self.results):
            result_uri = URIRef(f"{subject}_result_{i}")
            result.to_rdf(graph, result_uri)
            graph.add((subject, TRACKING.hasValidationResult, result_uri))

class OntologyValidator:
    """
    Validates ontologies and tracks results in both memory and RDF.
    """
    def __init__(self, graphdb_endpoint):
        self.graphdb_endpoint = graphdb_endpoint
        self.logger = logging.getLogger(__name__)

    def _validate_shacl_shapes(self, g):
        """Validate SHACL shapes in the ontology."""
        results = []
        shapes = list(g.subjects(RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")))
        if not shapes:
            results.append(ValidationResult(
                rule="shacl_shapes",
                status="error",
                message="No SHACL shapes found in ontology",
                severity=2
            ))
        return results

    def _validate_class_labels(self, g):
        """Validate that all classes have labels."""
        results = []
        for cls in g.subjects(RDF.type, OWL.Class):
            if not any(g.triples((cls, RDFS.label, None))):
                results.append(ValidationResult(
                    rule="class_labels",
                    status="error",
                    message=f"Class {cls} is missing a label",
                    severity=2
                ))
        return results

    def _validate_comments(self, g):
        """Validate that all classes and properties have comments."""
        results = []
        for subject in g.subjects(RDF.type, OWL.Class):
            if not any(g.triples((subject, RDFS.comment, None))):
                results.append(ValidationResult(
                    rule="class_comments",
                    status="error",
                    message=f"Class {subject} is missing a comment",
                    severity=1
                ))
        return results

    def _validate_property_domains(self, g):
        """Validate that properties have defined domains."""
        results = []
        for prop in g.subjects(RDF.type, OWL.ObjectProperty):
            if not any(g.triples((prop, RDFS.domain, None))):
                results.append(ValidationResult(
                    rule="property_domains",
                    status="error",
                    message=f"Property {prop} is missing a domain",
                    severity=2
                ))
        return results

    def _validate_property_ranges(self, g):
        """Validate that properties have defined ranges."""
        results = []
        for prop in g.subjects(RDF.type, OWL.ObjectProperty):
            if not any(g.triples((prop, RDFS.range, None))):
                results.append(ValidationResult(
                    rule="property_ranges",
                    status="error",
                    message=f"Property {prop} is missing a range",
                    severity=2
                ))
        return results

    def _validate_version_info(self, g):
        """Validate that the ontology has version information."""
        results = []
        ontologies = list(g.subjects(RDF.type, OWL.Ontology))
        for ont in ontologies:
            if not any(g.triples((ont, OWL.versionInfo, None))):
                results.append(ValidationResult(
                    rule="version_info",
                    status="error",
                    message=f"Ontology {ont} is missing version information",
                    severity=1
                ))
        return results

    def _validate_example_instances(self, g):
        """Validate that classes have example instances."""
        results = []
        for cls in g.subjects(RDF.type, OWL.Class):
            if not any(g.subjects(RDF.type, cls)):
                results.append(ValidationResult(
                    rule="example_instances",
                    status="warning",
                    message=f"Class {cls} has no example instances",
                    severity=0
                ))
        return results

    def validate_ontology(self, ontology_path):
        """
        Validate an ontology file and return a validation report.
        Also updates the ontology with validation metadata.
        """
        g = Graph()
        try:
            g.parse(ontology_path, format='turtle')
        except Exception as e:
            self.logger.error(f"Failed to load ontology {ontology_path}: {e}")
            return ValidationReport(
                results=[ValidationResult(
                    rule="ontology_load",
                    status="error",
                    message=f"Failed to load ontology: {str(e)}",
                    severity=2
                )],
                error_count=1,
                timestamp=datetime.now().isoformat(),
                ontology_path=ontology_path
            )

        results = []
        
        # Run validation rules
        results.extend(self._validate_shacl_shapes(g))
        results.extend(self._validate_class_labels(g))
        results.extend(self._validate_comments(g))
        results.extend(self._validate_property_domains(g))
        results.extend(self._validate_property_ranges(g))
        results.extend(self._validate_version_info(g))
        results.extend(self._validate_example_instances(g))

        # Count errors
        error_count = sum(1 for r in results if r.status == "error")

        # Create report
        report = ValidationReport(
            results=results,
            error_count=error_count,
            timestamp=datetime.now().isoformat(),
            ontology_path=ontology_path
        )

        # Update validation status in GraphDB and ontology
        self._update_validation_status(ontology_path, report)
        self._update_ontology_metadata(g, report)

        return report

    def _update_ontology_metadata(self, graph, report):
        """
        Update the ontology with validation metadata.
        """
        # Create URIs for validation metadata
        status_uri = URIRef(f"urn:validation:status:{datetime.now().isoformat()}")
        
        # Add validation metadata to the graph
        report.to_rdf(graph, status_uri)
        
        # Link to the ontology
        ontologies = list(graph.subjects(RDF.type, OWL.Ontology))
        for ont in ontologies:
            graph.add((ont, TRACKING.hasTestingStatus, status_uri))

    def _update_validation_status(self, ontology_path, report):
        """
        Update the validation status in GraphDB.
        """
        try:
            # Convert report to SPARQL update
            update_query = self._report_to_sparql(ontology_path, report)
            
            # Send update to GraphDB
            response = requests.post(
                f"{self.graphdb_endpoint}/statements",
                headers={"Content-Type": "application/sparql-update"},
                data=update_query
            )
            response.raise_for_status()
            
        except Exception as e:
            self.logger.error(f"Failed to update validation status: {e}")

    def _report_to_sparql(self, ontology_path, report):
        """
        Convert a validation report to a SPARQL update query.
        """
        # Create unique URI for validation result
        validation_uri = f"urn:validation:{datetime.now().isoformat()}"
        
        query = f"""
        PREFIX val: <http://example.org/validation#>
        PREFIX tracking: <http://example.org/tracking#>
        INSERT DATA {{
            <{validation_uri}> a tracking:ValidationResult ;
                tracking:ontologyPath "{ontology_path}" ;
                tracking:timestamp "{report.timestamp}" ;
                tracking:errorCount {report.error_count} .
        }}
        """
        return query

def main():
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Initialize validator
    validator = OntologyValidator("http://localhost:7200/repositories/test-ontology-framework")

    # Scan for ontologies
    ontology_dir = Path("guidance/modules")
    for ontology_file in ontology_dir.glob("*.ttl"):
        logger.info(f"Validating {ontology_file}")
        report = validator.validate_ontology(str(ontology_file))
        print(f"Validation results for {ontology_file}:")
        print(f"Error count: {report.error_count}")
        for result in report.results:
            print(f"{result.status.upper()}: {result.message}")

if __name__ == "__main__":
    main() 