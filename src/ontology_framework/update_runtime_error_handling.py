from ontology_framework.ontology_manager import OntologyManager
from ontology_framework.error_handler import ErrorHandler
from ontology_framework.ontology_types import ErrorType, ErrorSeverity, ErrorStep
from rdflib import URIRef, Literal
from rdflib.namespace import XSD, RDFS, RDF
from datetime import datetime
import os
import logging

def update_runtime_error_handling() -> None:
    """Update the runtime error handling ontology with missing components."""
    manager = OntologyManager("guidance/modules/runtime_error_handling.ttl")
    
    # Add provenance information
    manager.add_provenance(
        "ErrorHandlerUpdate",
        "Update to error handling ontology with new types and validation rules",
        datetime.now().isoformat(),
        os.path.basename(__file__),
        "https://github.com/louspringer/ontology-framework/blob/main/src/ontology_framework/update_runtime_error_handling.py"
    )
    
    # Add new error types
    new_error_types = [
        ("ConfigurationError", "Configuration Error", "Error occurring during configuration loading or validation"),
        ("AuthenticationError", "Authentication Error", "Error during authentication process"),
        ("AuthorizationError", "Authorization Error", "Error during authorization process"),
        ("NetworkError", "Network Error", "Error during network operations"),
        ("DatabaseError", "Database Error", "Error during database operations"),
        ("FileSystemError", "File System Error", "Error during file system operations"),
        ("MemoryError", "Memory Error", "Error related to memory management"),
        ("CPUError", "CPU Error", "Error related to CPU operations"),
        ("DiskError", "Disk Error", "Error related to disk operations"),
        ("SecurityError", "Security Error", "Error related to security operations"),
        ("ComplianceError", "Compliance Error", "Error related to compliance requirements")
    ]
    
    for error_type, label, comment in new_error_types:
        manager.add_error_type(error_type, label, comment)
    
    # Add new validation rules
    new_validation_rules = [
        ("SecurityValidation", "Security Validation", "Validates security requirements"),
        ("PerformanceValidation", "Performance Validation", "Validates performance requirements"),
        ("ReliabilityValidation", "Reliability Validation", "Validates reliability requirements"),
        ("AvailabilityValidation", "Availability Validation", "Validates availability requirements"),
        ("ScalabilityValidation", "Scalability Validation", "Validates scalability requirements"),
        ("MaintainabilityValidation", "Maintainability Validation", "Validates maintainability requirements")
    ]
    
    for rule, label, comment in new_validation_rules:
        manager.add_validation_rule(rule, label, comment)
    
    # Add new handling steps
    new_handling_steps = [
        ("ErrorMonitoring", "Error Monitoring", "Step to monitor error occurrences", 5),
        ("ErrorReporting", "Error Reporting", "Step to report errors", 6),
        ("ErrorDocumentation", "Error Documentation", "Step to document errors", 7),
        ("ErrorReview", "Error Review", "Step to review error handling", 8),
        ("ErrorClosure", "Error Closure", "Step to close error handling", 9)
    ]
    
    for step, label, comment, order in new_handling_steps:
        manager.add_handling_step(step, label, comment, order)
    
    # Add new SHACL shapes
    error_shape_properties = [
        {
            "path": URIRef("http://example.org/error#severity"),
            "minCount": 1,
            "maxCount": 1,
            "datatype": XSD.string,
            "message": "Each error must have exactly one severity level"
        },
        {
            "path": URIRef("http://example.org/error#step"),
            "minCount": 1,
            "maxCount": 1,
            "class": URIRef("http://example.org/error#HandlingStep"),
            "message": "Each error must have exactly one handling step"
        },
        {
            "path": URIRef("http://example.org/error#risk_level"),
            "minCount": 1,
            "maxCount": 1,
            "class": URIRef("http://example.org/error#RiskLevel"),
            "message": "Each error must have exactly one risk level"
        }
    ]
    
    manager.add_shacl_shape(
        "ErrorShape",
        URIRef("http://example.org/error#Error"),
        error_shape_properties
    )
    
    # Add performance metrics
    performance_metrics = [
        ("ResponseTime", "Response Time", "Time taken to respond to errors", 100, "milliseconds"),
        ("Throughput", "Throughput", "Number of errors handled per second", 1000, "count/second"),
        ("Latency", "Latency", "Time taken to process errors", 200, "milliseconds"),
        ("Bandwidth", "Bandwidth", "Data transfer rate during error handling", 1000, "bytes/second"),
        ("CPUUsage", "CPU Usage", "CPU usage during error handling", 80, "percent"),
        ("MemoryUsage", "Memory Usage", "Memory usage during error handling", 80, "percent"),
        ("DiskUsage", "Disk Usage", "Disk usage during error handling", 80, "percent"),
        ("NetworkUsage", "Network Usage", "Network usage during error handling", 80, "percent"),
        ("ErrorRate", "Error Rate", "Rate of error occurrence", 100, "errors/hour"),
        ("Availability", "Availability", "System availability during errors", 99.9, "percent")
    ]
    
    for metric, label, comment, threshold, unit in performance_metrics:
        manager.add_performance_metric(metric, label, comment, threshold, unit)
    
    # Save the updated ontology
    manager.save()
    
    # Validate the ontology
    if manager.validate():
        print("Ontology updated and validated successfully")
    else:
        print("Ontology updated but validation failed")

if __name__ == "__main__":
    update_runtime_error_handling() 