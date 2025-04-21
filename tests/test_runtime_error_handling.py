import unittest
import logging
import traceback
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD
from rdflib.plugins.sparql import prepareQuery
from datetime import datetime, timedelta
import re

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('runtime_error_handling_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define namespaces
ns1 = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/#")

class TestRuntimeErrorHandling(unittest.TestCase):
    """Test cases for runtime error handling model."""
    
    def setUp(self):
        """Set up test environment."""
        logger.info("Setting up test environment")
        try:
            # Load runtime error handling ontology
            self.model_path = Path("guidance/modules/runtime_error_handling.ttl")
            self.graph = Graph()
            self.graph.parse(str(self.model_path), format="turtle")
            
            # Bind namespace
            self.graph.bind('ns1', ns1)
            self.graph.bind('sh', SH)
            
            # Define test queries
            self.error_types_query = prepareQuery("""
                SELECT ?type ?label ?comment
                WHERE {
                    ?type a ns1:ErrorType ;
                          rdfs:label ?label ;
                          rdfs:comment ?comment .
                }
            """, initNs={"ns1": ns1})
            
            self.error_steps_query = prepareQuery("""
                SELECT ?step ?order ?action
                WHERE {
                    ?step a ns1:ErrorHandlingStep ;
                          ns1:hasStepOrder ?order ;
                          ns1:hasStepAction ?action .
                }
                ORDER BY ?order
            """, initNs={"ns1": ns1})
            
            self.test_error_steps_query = prepareQuery("""
                SELECT ?step ?order ?action
                WHERE {
                    ?step a ns1:ErrorHandlingStep ;
                          ns1:hasStepOrder ?order ;
                          ns1:hasStepAction ?action .
                    FILTER (STRSTARTS(STR(?step), "http://example.org/guidance#TestError"))
                }
                ORDER BY ?order
            """, initNs={"ns1": ns1})
            
            logger.info("Test environment setup complete")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_types(self):
        """Test that all required error types are defined."""
        logger.info("Testing error types")
        try:
            results = list(self.graph.query(self.error_types_query))
            
            # Verify we have all required error types
            required_types = {
                "Validation Error": "Errors in data validation",
                "I/O Error": "Errors in input/output operations",
                "Runtime Error": "General runtime errors",
                "API Error": "Errors in API operations",
                "Test Failure": "Errors in test execution"
            }
            
            found_types = {str(row[1]): str(row[2]) for row in results}
            
            for type_name, comment in required_types.items():
                self.assertIn(type_name, found_types, f"Missing error type: {type_name}")
                self.assertEqual(found_types[type_name], comment, 
                               f"Comment mismatch for {type_name}")
            
            logger.info("Error types test passed")
        except Exception as e:
            logger.error(f"Error types test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_steps(self):
        """Test that all required error handling steps are defined."""
        logger.info("Testing error handling steps")
        try:
            results = list(self.graph.query(self.error_steps_query))
            
            # Verify we have all required steps
            required_steps = {
                1: "Error Identification",
                2: "Error Analysis",
                3: "Error Recovery",
                4: "Error Prevention"
            }
            
            found_steps = {int(row[1]): str(row[0]).split("#")[-1] for row in results}
            
            for order, step_name in required_steps.items():
                self.assertIn(order, found_steps, f"Missing step order: {order}")
                self.assertEqual(found_steps[order], step_name, 
                               f"Step name mismatch for order {order}")
            
            logger.info("Error handling steps test passed")
        except Exception as e:
            logger.error(f"Error handling steps test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_test_error_handling_steps(self):
        """Test that all required test error handling steps are defined."""
        logger.info("Testing test error handling steps")
        try:
            results = list(self.graph.query(self.test_error_steps_query))
            
            # Verify we have all required test steps
            required_steps = {
                1: "TestErrorIdentification",
                2: "TestErrorAnalysis",
                3: "TestErrorRecovery",
                4: "TestErrorPrevention"
            }
            
            found_steps = {int(row[1]): str(row[0]).split("#")[-1] for row in results}
            
            for order, step_name in required_steps.items():
                self.assertIn(order, found_steps, f"Missing test step order: {order}")
                self.assertEqual(found_steps[order], step_name, 
                               f"Test step name mismatch for order {order}")
            
            logger.info("Test error handling steps test passed")
        except Exception as e:
            logger.error(f"Test error handling steps test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_process(self):
        """Test that error handling process is properly defined."""
        logger.info("Testing error handling process")
        try:
            # Query for standard error handling
            query = prepareQuery("""
                SELECT ?process ?step
                WHERE {
                    ns1:standardErrorHandling a ns1:ErrorHandlingProcess ;
                                            ns1:hasProcessStep ?step .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            self.assertEqual(len(results), 4, "Standard error handling should have 4 steps")
            
            # Verify SHACL validation
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorHandlingProcess ;
                           sh:property [
                               sh:path ns1:hasProcessStep ;
                               sh:minCount 4
                           ] .
                }
            """, initNs={"ns1": ns1, "sh": SH})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "SHACL validation for error handling process is missing")
            
            logger.info("Error handling process test passed")
        except Exception as e:
            logger.error(f"Error handling process test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_test_error_handling_process(self):
        """Test that test error handling process is properly defined."""
        logger.info("Testing test error handling process")
        try:
            # Query for standard test error handling
            query = prepareQuery("""
                SELECT ?process ?step
                WHERE {
                    ns1:standardTestErrorHandling a ns1:TestErrorHandlingProcess ;
                                                ns1:hasProcessStep ?step .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            self.assertEqual(len(results), 4, "Standard test error handling should have 4 steps")
            
            # Verify SHACL validation
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:TestErrorHandlingProcess ;
                           sh:property [
                               sh:path ns1:hasProcessStep ;
                               sh:minCount 4
                           ] .
                }
            """, initNs={"ns1": ns1, "sh": SH})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "SHACL validation for test error handling process is missing")
            
            logger.info("Test error handling process test passed")
        except Exception as e:
            logger.error(f"Test error handling process test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_type_hierarchy(self):
        """Test that error types follow proper hierarchy and inheritance."""
        logger.info("Testing error type hierarchy")
        try:
            query = prepareQuery("""
                SELECT ?type ?supertype
                WHERE {
                    ?type rdfs:subClassOf ?supertype .
                    ?type a ns1:ErrorType .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            self.assertTrue(len(results) > 0, "No error type hierarchies found")
            
            # Verify TestFailure is properly subclassed
            query = prepareQuery("""
                ASK {
                    ns1:TestFailure rdfs:subClassOf ns1:RuntimeError .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "TestFailure should be a subclass of RuntimeError")
            
            logger.info("Error type hierarchy test passed")
        except Exception as e:
            logger.error(f"Error type hierarchy test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_property_validation(self):
        """Test that error properties have proper validation rules."""
        logger.info("Testing error property validation")
        try:
            # Verify error severity property
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorType ;
                           sh:property [
                               sh:path ns1:hasErrorSeverity ;
                               sh:datatype xsd:string ;
                               sh:minCount 1 ;
                               sh:maxCount 1 ;
                               sh:in ("CRITICAL" "ERROR" "WARNING" "INFO")
                           ] .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing severity property validation")
            
            # Verify error code property
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorType ;
                           sh:property [
                               sh:path ns1:hasErrorCode ;
                               sh:datatype xsd:string ;
                               sh:pattern "^[A-Z0-9_]+$" ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing error code property validation")
            
            logger.info("Error property validation test passed")
        except Exception as e:
            logger.error(f"Error property validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_metrics(self):
        """Test that error handling includes proper metrics tracking."""
        logger.info("Testing error handling metrics")
        try:
            query = prepareQuery("""
                SELECT ?metric ?type
                WHERE {
                    ?metric a ns1:ErrorMetric ;
                            rdf:type ?type .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_metrics = {
                "ErrorCount": "Count of errors by type",
                "ResolutionTime": "Time to resolve errors",
                "RecurrenceRate": "Rate of recurring errors",
                "PreventionEffectiveness": "Effectiveness of prevention measures"
            }
            
            found_metrics = {str(row[0]).split("#")[-1]: str(row[1]) for row in results}
            
            for metric, description in required_metrics.items():
                self.assertIn(metric, found_metrics, f"Missing required metric: {metric}")
            
            logger.info("Error handling metrics test passed")
        except Exception as e:
            logger.error(f"Error handling metrics test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_documentation_requirements(self):
        """Test that error handling includes proper documentation requirements."""
        logger.info("Testing error documentation requirements")
        try:
            query = prepareQuery("""
                SELECT ?doc ?type
                WHERE {
                    ?doc a ns1:ErrorDocumentation ;
                         rdf:type ?type .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_docs = {
                "ErrorReport": "Detailed error report",
                "ResolutionGuide": "Step-by-step resolution guide",
                "PreventionGuide": "Error prevention guidelines",
                "MetricsReport": "Error handling metrics report"
            }
            
            found_docs = {str(row[0]).split("#")[-1]: str(row[1]) for row in results}
            
            for doc, description in required_docs.items():
                self.assertIn(doc, found_docs, f"Missing required documentation: {doc}")
            
            logger.info("Error documentation requirements test passed")
        except Exception as e:
            logger.error(f"Error documentation requirements test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_security(self):
        """Test that error handling includes proper security measures."""
        logger.info("Testing error handling security")
        try:
            # Verify sensitive data handling
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorType ;
                           sh:property [
                               sh:path ns1:hasSensitiveData ;
                               sh:datatype xsd:boolean ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing sensitive data handling validation")
            
            # Verify error logging security
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorLog ;
                           sh:property [
                               sh:path ns1:hasLogSecurityLevel ;
                               sh:datatype xsd:string ;
                               sh:in ("PUBLIC" "PRIVATE" "CONFIDENTIAL")
                           ] .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing error logging security validation")
            
            logger.info("Error handling security test passed")
        except Exception as e:
            logger.error(f"Error handling security test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_integration(self):
        """Test that error handling integrates with other system components."""
        logger.info("Testing error handling integration")
        try:
            # Verify monitoring integration
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorType ;
                           sh:property [
                               sh:path ns1:hasMonitoringIntegration ;
                               sh:datatype xsd:boolean ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing monitoring integration validation")
            
            # Verify alerting integration
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorType ;
                           sh:property [
                               sh:path ns1:hasAlertingIntegration ;
                               sh:datatype xsd:boolean ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing alerting integration validation")
            
            logger.info("Error handling integration test passed")
        except Exception as e:
            logger.error(f"Error handling integration test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_recovery_strategy(self):
        """Test that error recovery strategies are properly defined."""
        logger.info("Testing error recovery strategies")
        try:
            # Verify recovery strategy for each error type
            query = prepareQuery("""
                SELECT ?type ?strategy ?fallback
                WHERE {
                    ?type a ns1:ErrorType ;
                          ns1:hasRecoveryStrategy ?strategy .
                    ?strategy ns1:hasFallbackMechanism ?fallback ;
                             ns1:hasStateRestoration ?restoration .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            self.assertTrue(len(results) > 0, "No recovery strategies found")
            
            # Verify state restoration procedures
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:RecoveryStrategy ;
                           sh:property [
                               sh:path ns1:hasStateRestoration ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing state restoration validation")
            
            logger.info("Error recovery strategy test passed")
        except Exception as e:
            logger.error(f"Error recovery strategy test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_prevention_measures(self):
        """Test that error prevention measures are properly defined."""
        logger.info("Testing error prevention measures")
        try:
            # Verify prevention measures for each error type
            query = prepareQuery("""
                SELECT ?type ?measure ?monitoring ?alerting
                WHERE {
                    ?type a ns1:ErrorType ;
                          ns1:hasPreventionMeasure ?measure .
                    ?measure ns1:hasMonitoring ?monitoring ;
                            ns1:hasAlerting ?alerting .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            self.assertTrue(len(results) > 0, "No prevention measures found")
            
            # Verify monitoring and alerting integration
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:PreventionMeasure ;
                           sh:property [
                               sh:path ns1:hasMonitoring ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] ;
                           sh:property [
                               sh:path ns1:hasAlerting ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing prevention measure validation")
            
            logger.info("Error prevention measures test passed")
        except Exception as e:
            logger.error(f"Error prevention measures test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_performance(self):
        """Test that error handling maintains acceptable performance."""
        logger.info("Testing error handling performance")
        try:
            # Verify performance metrics
            query = prepareQuery("""
                SELECT ?metric ?threshold
                WHERE {
                    ?metric a ns1:PerformanceMetric ;
                            ns1:hasThreshold ?threshold .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_metrics = {
                "LoggingLatency": "Maximum acceptable logging latency",
                "RecoveryTime": "Maximum acceptable recovery time",
                "ResourceUsage": "Maximum acceptable resource usage"
            }
            
            found_metrics = {str(row[0]).split("#")[-1]: str(row[1]) for row in results}
            
            for metric, description in required_metrics.items():
                self.assertIn(metric, found_metrics, f"Missing performance metric: {metric}")
            
            # Verify resource cleanup
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorHandlingStep ;
                           sh:property [
                               sh:path ns1:hasResourceCleanup ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing resource cleanup validation")
            
            logger.info("Error handling performance test passed")
        except Exception as e:
            logger.error(f"Error handling performance test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_compliance(self):
        """Test that error handling follows compliance requirements."""
        logger.info("Testing error handling compliance")
        try:
            # Verify industry standards compliance
            query = prepareQuery("""
                SELECT ?standard ?requirement
                WHERE {
                    ?standard a ns1:IndustryStandard ;
                             ns1:hasRequirement ?requirement .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_standards = {
                "ISO27001": "Information security management",
                "SOC2": "Security, availability, processing integrity",
                "GDPR": "Data protection and privacy"
            }
            
            found_standards = {str(row[0]).split("#")[-1]: str(row[1]) for row in results}
            
            for standard, description in required_standards.items():
                self.assertIn(standard, found_standards, f"Missing compliance standard: {standard}")
            
            # Verify audit trail
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorHandlingProcess ;
                           sh:property [
                               sh:path ns1:hasAuditTrail ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1, "sh": SH})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing audit trail validation")
            
            logger.info("Error handling compliance test passed")
        except Exception as e:
            logger.error(f"Error handling compliance test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_risks(self):
        """Test that error handling risks are properly defined and managed."""
        logger.info("Testing error handling risks")
        try:
            # Verify risk definitions
            query = prepareQuery("""
                SELECT ?risk ?level ?strategy
                WHERE {
                    ?risk a ns1:ErrorHandlingRisk ;
                          ns1:hasRiskLevel ?level ;
                          ns1:hasMitigationStrategy ?strategy .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_risks = {
                "DataLossRisk": "HIGH",
                "CascadingFailureRisk": "CRITICAL",
                "PerformanceImpactRisk": "MEDIUM",
                "SecurityBreachRisk": "CRITICAL"
            }
            
            found_risks = {str(row[0]).split("#")[-1]: str(row[1]) for row in results}
            
            for risk, level in required_risks.items():
                self.assertIn(risk, found_risks, f"Missing required risk: {risk}")
                self.assertEqual(found_risks[risk], level, 
                               f"Risk level mismatch for {risk}")
            
            logger.info("Error handling risks test passed")
        except Exception as e:
            logger.error(f"Error handling risks test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_assumptions(self):
        """Test that error handling assumptions are properly defined and validated."""
        logger.info("Testing error handling assumptions")
        try:
            # Verify assumption definitions
            query = prepareQuery("""
                SELECT ?assumption ?validation
                WHERE {
                    ?assumption a ns1:ErrorHandlingAssumption ;
                               ns1:hasValidationRequirement ?validation .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_assumptions = {
                "ErrorTypeExclusivity": "ErrorTypeValidation",
                "RecoveryAvailability": "RecoveryStrategyValidation",
                "MonitoringOperational": "MonitoringSystemValidation"
            }
            
            found_assumptions = {str(row[0]).split("#")[-1]: str(row[1]).split("#")[-1] 
                               for row in results}
            
            for assumption, validation in required_assumptions.items():
                self.assertIn(assumption, found_assumptions, 
                            f"Missing required assumption: {assumption}")
                self.assertEqual(found_assumptions[assumption], validation,
                               f"Validation mismatch for {assumption}")
            
            logger.info("Error handling assumptions test passed")
        except Exception as e:
            logger.error(f"Error handling assumptions test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_constraints(self):
        """Test that error handling constraints are properly defined and enforced."""
        logger.info("Testing error handling constraints")
        try:
            # Verify constraint definitions
            query = prepareQuery("""
                SELECT ?constraint ?type ?value
                WHERE {
                    ?constraint a ns1:ErrorHandlingConstraint ;
                               ns1:hasConstraintType ?type ;
                               ns1:hasConstraintValue ?value .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_constraints = {
                "ResourceConstraint": ["MAX_CPU_USAGE=80%", "MAX_MEMORY_USAGE=90%"],
                "TimeConstraint": ["MAX_RECOVERY_TIME=5m", "MAX_DETECTION_TIME=1m"],
                "StatePreservationConstraint": ["PRESERVE_TRANSACTION_STATE=true", 
                                             "PRESERVE_USER_SESSION=true"]
            }
            
            found_constraints = {}
            for row in results:
                constraint = str(row[0]).split("#")[-1]
                if constraint not in found_constraints:
                    found_constraints[constraint] = []
                found_constraints[constraint].append(str(row[2]))
            
            for constraint, values in required_constraints.items():
                self.assertIn(constraint, found_constraints, 
                            f"Missing required constraint: {constraint}")
                for value in values:
                    self.assertIn(value, found_constraints[constraint],
                                f"Missing constraint value {value} for {constraint}")
            
            logger.info("Error handling constraints test passed")
        except Exception as e:
            logger.error(f"Error handling constraints test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_validation(self):
        """Test that error handling validation rules are properly defined."""
        logger.info("Testing error handling validation")
        try:
            # Verify validation rules
            query = prepareQuery("""
                SELECT ?validation ?rule
                WHERE {
                    ?validation a ns1:ErrorHandlingValidation ;
                               ns1:hasValidationRule ?rule .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_validations = {
                "RiskValidation": ["RiskAssessmentRule", "RiskMitigationRule"],
                "AssumptionValidation": ["AssumptionVerificationRule", 
                                       "AssumptionTestingRule"],
                "ConstraintValidation": ["ConstraintMonitoringRule", 
                                       "ConstraintEnforcementRule"]
            }
            
            found_validations = {}
            for row in results:
                validation = str(row[0]).split("#")[-1]
                if validation not in found_validations:
                    found_validations[validation] = []
                found_validations[validation].append(str(row[1]).split("#")[-1])
            
            for validation, rules in required_validations.items():
                self.assertIn(validation, found_validations, 
                            f"Missing required validation: {validation}")
                for rule in rules:
                    self.assertIn(rule, found_validations[validation],
                                f"Missing validation rule {rule} for {validation}")
            
            logger.info("Error handling validation test passed")
        except Exception as e:
            logger.error(f"Error handling validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling_traceability(self):
        """Test that error handling has proper traceability between test cases, requirements, and implementations."""
        logger.info("Testing error handling traceability")
        try:
            # Verify test case definitions
            query = prepareQuery("""
                SELECT ?testCase ?implementation ?requirement
                WHERE {
                    ?testCase a ns1:ErrorHandlingTestCase ;
                             ns1:hasTestImplementation ?implementation ;
                             ns1:validatesRequirement ?requirement .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_test_cases = {
                "ErrorTypeTestCase": {
                    "implementation": "ErrorTypeTestImplementation",
                    "requirement": "ErrorTypeRequirement"
                },
                "ErrorStepTestCase": {
                    "implementation": "ErrorStepTestImplementation",
                    "requirement": "ErrorStepRequirement"
                },
                "RiskManagementTestCase": {
                    "implementation": "RiskManagementTestImplementation",
                    "requirement": "RiskManagementRequirement"
                }
            }
            
            found_test_cases = {}
            for row in results:
                test_case = str(row[0]).split("#")[-1]
                implementation = str(row[1]).split("#")[-1]
                requirement = str(row[2]).split("#")[-1]
                found_test_cases[test_case] = {
                    "implementation": implementation,
                    "requirement": requirement
                }
            
            for test_case, details in required_test_cases.items():
                self.assertIn(test_case, found_test_cases, 
                            f"Missing required test case: {test_case}")
                self.assertEqual(found_test_cases[test_case]["implementation"], 
                               details["implementation"],
                               f"Implementation mismatch for {test_case}")
                self.assertEqual(found_test_cases[test_case]["requirement"],
                               details["requirement"],
                               f"Requirement mismatch for {test_case}")
            
            # Verify test implementations
            query = prepareQuery("""
                SELECT ?implementation ?testCase ?file ?method
                WHERE {
                    ?implementation a ns1:ErrorHandlingImplementation ;
                                   ns1:implementsTestCase ?testCase ;
                                   ns1:hasTestFile ?file ;
                                   ns1:hasTestMethod ?method .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_implementations = {
                "ErrorTypeTestImplementation": {
                    "testCase": "ErrorTypeTestCase",
                    "file": "tests/test_runtime_error_handling.py",
                    "method": "test_error_types"
                },
                "ErrorStepTestImplementation": {
                    "testCase": "ErrorStepTestCase",
                    "file": "tests/test_runtime_error_handling.py",
                    "method": "test_error_handling_steps"
                },
                "RiskManagementTestImplementation": {
                    "testCase": "RiskManagementTestCase",
                    "file": "tests/test_runtime_error_handling.py",
                    "method": "test_error_handling_risks"
                }
            }
            
            found_implementations = {}
            for row in results:
                implementation = str(row[0]).split("#")[-1]
                test_case = str(row[1]).split("#")[-1]
                file = str(row[2])
                method = str(row[3])
                found_implementations[implementation] = {
                    "testCase": test_case,
                    "file": file,
                    "method": method
                }
            
            for implementation, details in required_implementations.items():
                self.assertIn(implementation, found_implementations,
                            f"Missing required implementation: {implementation}")
                self.assertEqual(found_implementations[implementation]["testCase"],
                               details["testCase"],
                               f"Test case mismatch for {implementation}")
                self.assertEqual(found_implementations[implementation]["file"],
                               details["file"],
                               f"Test file mismatch for {implementation}")
                self.assertEqual(found_implementations[implementation]["method"],
                               details["method"],
                               f"Test method mismatch for {implementation}")
            
            logger.info("Error handling traceability test passed")
        except Exception as e:
            logger.error(f"Error handling traceability test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_classification_accuracy(self):
        """Test error classification accuracy using confusion matrix."""
        logger.info("Testing error classification accuracy")
        try:
            # Verify confusion matrix exists for each error type
            query = prepareQuery("""
                SELECT ?errorType ?matrix ?tp ?fp ?fn ?tn
                WHERE {
                    ?errorType a ns1:ErrorType .
                    ?matrix a ns1:ErrorClassificationMatrix ;
                            ns1:hasErrorType ?errorType ;
                            ns1:truePositives ?tp ;
                            ns1:falsePositives ?fp ;
                            ns1:falseNegatives ?fn ;
                            ns1:trueNegatives ?tn .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            self.assertTrue(len(results) > 0, "No confusion matrices found")
            
            # Verify classification metrics
            query = prepareQuery("""
                SELECT ?errorType ?metric ?value
                WHERE {
                    ?errorType a ns1:ErrorType .
                    ?matrix ns1:hasErrorType ?errorType .
                    ?metric a ns1:ClassificationMetric ;
                            ns1:hasMetricValue ?value .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            required_metrics = {
                "Precision": 0.90,  # Minimum required precision
                "Recall": 0.90,     # Minimum required recall
                "F1Score": 0.90,    # Minimum required F1 score
                "Accuracy": 0.90    # Minimum required accuracy
            }
            
            found_metrics = {}
            for row in results:
                metric_type = str(row[1]).split("#")[-1]
                value = float(row[2])
                found_metrics[metric_type] = value
            
            for metric, min_value in required_metrics.items():
                self.assertIn(metric, found_metrics, f"Missing required metric: {metric}")
                self.assertGreaterEqual(found_metrics[metric], min_value,
                                      f"{metric} below minimum threshold")
            
            # Verify SHACL validation rules
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorClassificationMatrix ;
                           sh:property [
                               sh:path ?path ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                    VALUES ?path { 
                        ns1:truePositives 
                        ns1:falsePositives 
                        ns1:falseNegatives 
                        ns1:trueNegatives 
                    }
                }
            """, initNs={"ns1": ns1, "sh": SH})
            
            self.assertTrue(self.graph.query(query).askAnswer,
                          "Missing SHACL validation rules for confusion matrix")
            
            logger.info("Error classification accuracy test passed")
        except Exception as e:
            logger.error(f"Error classification accuracy test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_enhanced_confusion_matrix_validation(self):
        """Test enhanced validation rules for confusion matrices."""
        logger.info("Testing enhanced confusion matrix validation")
        try:
            # Verify basic matrix validation
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorClassificationMatrix ;
                           sh:property [
                               sh:path ns1:truePositives ;
                               sh:datatype xsd:integer ;
                               sh:minCount 1 ;
                               sh:maxCount 1 ;
                               sh:minInclusive 0
                           ] ;
                           sh:property [
                               sh:path ns1:falsePositives ;
                               sh:datatype xsd:integer ;
                               sh:minCount 1 ;
                               sh:maxCount 1 ;
                               sh:minInclusive 0
                           ] .
                }
            """, initNs={"ns1": ns1, "sh": SH})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing basic matrix validation rules")
            
            # Verify cross-validation
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorClassificationMatrix ;
                           sh:sparql [
                               sh:select ?select ;
                               sh:message ?message
                           ] .
                }
            """, initNs={"ns1": ns1, "sh": SH})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing cross-validation rules")
            
            # Verify temporal validation
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorClassificationMatrix ;
                           sh:property [
                               sh:path ns1:lastUpdated ;
                               sh:datatype xsd:dateTime ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1, "sh": SH})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing temporal validation rules")
            
            # Verify version control
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ErrorClassificationMatrix ;
                           sh:property [
                               sh:path ns1:version ;
                               sh:datatype xsd:string ;
                               sh:pattern "^\\d+\\.\\d+\\.\\d+$" ;
                               sh:minCount 1 ;
                               sh:maxCount 1
                           ] .
                }
            """, initNs={"ns1": ns1, "sh": SH})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing version control rules")
            
            # Verify confidence interval validation
            query = prepareQuery("""
                ASK {
                    ?shape a sh:NodeShape ;
                           sh:targetClass ns1:ClassificationMetric ;
                           sh:property [
                               sh:path ns1:hasConfidenceInterval ;
                               sh:datatype xsd:decimal ;
                               sh:minCount 1 ;
                               sh:maxCount 1 ;
                               sh:minInclusive 0.0 ;
                               sh:maxInclusive 1.0
                           ] .
                }
            """, initNs={"ns1": ns1, "sh": SH})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Missing confidence interval validation rules")
            
            # Verify example matrix
            query = prepareQuery("""
                ASK {
                    ns1:EnhancedValidationErrorMatrix a ns1:ErrorClassificationMatrix ;
                                                     ns1:truePositives ?tp ;
                                                     ns1:falsePositives ?fp ;
                                                     ns1:falseNegatives ?fn ;
                                                     ns1:trueNegatives ?tn ;
                                                     ns1:lastUpdated ?timestamp ;
                                                     ns1:version ?version .
                    FILTER (
                        ?tp >= 0 && ?fp >= 0 && ?fn >= 0 && ?tn >= 0 &&
                        ?tp + ?fp + ?fn + ?tn > 0 &&
                        ?timestamp <= NOW() &&
                        REGEX(?version, "^\\d+\\.\\d+\\.\\d+$")
                    )
                }
            """, initNs={"ns1": ns1})
            
            self.assertTrue(self.graph.query(query).askAnswer, 
                          "Example matrix does not satisfy validation rules")
            
            logger.info("Enhanced confusion matrix validation test passed")
        except Exception as e:
            logger.error(f"Enhanced confusion matrix validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_confusion_matrix_cross_validation(self):
        """Test cross-validation of confusion matrix values and metrics."""
        logger.info("Testing confusion matrix cross-validation")
        try:
            # Verify matrix value consistency
            query = prepareQuery("""
                SELECT ?matrix ?tp ?fp ?fn ?tn ?precision ?recall ?f1
                WHERE {
                    ?matrix a ns1:ErrorClassificationMatrix ;
                            ns1:truePositives ?tp ;
                            ns1:falsePositives ?fp ;
                            ns1:falseNegatives ?fn ;
                            ns1:trueNegatives ?tn .
                    ?matrix ns1:hasPrecision ?precision ;
                            ns1:hasRecall ?recall ;
                            ns1:hasF1Score ?f1 .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            for row in results:
                tp, fp, fn, tn, precision, recall, f1 = row[1:]
                
                # Verify matrix values are non-negative
                self.assertGreaterEqual(tp, 0, "True positives must be non-negative")
                self.assertGreaterEqual(fp, 0, "False positives must be non-negative")
                self.assertGreaterEqual(fn, 0, "False negatives must be non-negative")
                self.assertGreaterEqual(tn, 0, "True negatives must be non-negative")
                
                # Verify total count is positive
                total = tp + fp + fn + tn
                self.assertGreater(total, 0, "Matrix must have at least one entry")
                
                # Verify metric calculations
                expected_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                expected_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                expected_f1 = 2 * (expected_precision * expected_recall) / (expected_precision + expected_recall) if (expected_precision + expected_recall) > 0 else 0
                
                self.assertAlmostEqual(float(precision), expected_precision, places=3,
                                     msg="Precision calculation mismatch")
                self.assertAlmostEqual(float(recall), expected_recall, places=3,
                                     msg="Recall calculation mismatch")
                self.assertAlmostEqual(float(f1), expected_f1, places=3,
                                     msg="F1 score calculation mismatch")
            
            logger.info("Confusion matrix cross-validation test passed")
        except Exception as e:
            logger.error(f"Confusion matrix cross-validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_confusion_matrix_temporal_validation(self):
        """Test temporal validation of confusion matrices."""
        logger.info("Testing confusion matrix temporal validation")
        try:
            # Verify matrix update timestamps
            query = prepareQuery("""
                SELECT ?matrix ?lastUpdated
                WHERE {
                    ?matrix a ns1:ErrorClassificationMatrix ;
                            ns1:lastUpdated ?lastUpdated .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            for row in results:
                last_updated = row[1]
                # Verify timestamp is not in the future
                self.assertLessEqual(last_updated, datetime.now(),
                                   "Matrix update timestamp must not be in the future")
                
                # Verify timestamp is not too old (e.g., within last 30 days)
                max_age = timedelta(days=30)
                self.assertGreaterEqual(datetime.now() - last_updated, max_age,
                                      "Matrix should be updated within last 30 days")
            
            logger.info("Confusion matrix temporal validation test passed")
        except Exception as e:
            logger.error(f"Confusion matrix temporal validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_confusion_matrix_version_control(self):
        """Test version control of confusion matrices."""
        logger.info("Testing confusion matrix version control")
        try:
            # Verify version numbers
            query = prepareQuery("""
                SELECT ?matrix ?version
                WHERE {
                    ?matrix a ns1:ErrorClassificationMatrix ;
                            ns1:version ?version .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            for row in results:
                version = str(row[1])
                # Verify semantic versioning format
                self.assertTrue(re.match(r'^\d+\.\d+\.\d+$', version),
                              "Version must follow semantic versioning format")
                
                # Verify version components are non-negative integers
                major, minor, patch = map(int, version.split('.'))
                self.assertGreaterEqual(major, 0, "Major version must be non-negative")
                self.assertGreaterEqual(minor, 0, "Minor version must be non-negative")
                self.assertGreaterEqual(patch, 0, "Patch version must be non-negative")
            
            logger.info("Confusion matrix version control test passed")
        except Exception as e:
            logger.error(f"Confusion matrix version control test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_confusion_matrix_confidence_intervals(self):
        """Test confidence intervals of confusion matrix metrics."""
        logger.info("Testing confusion matrix confidence intervals")
        try:
            # Verify confidence intervals
            query = prepareQuery("""
                SELECT ?metric ?value ?ci
                WHERE {
                    ?metric a ns1:ClassificationMetric ;
                            ns1:hasMetricValue ?value ;
                            ns1:hasConfidenceInterval ?ci .
                }
            """, initNs={"ns1": ns1})
            
            results = list(self.graph.query(query))
            for row in results:
                value, ci = float(row[1]), float(row[2])
                
                # Verify confidence interval is valid
                self.assertGreaterEqual(ci, 0, "Confidence interval must be non-negative")
                self.assertLessEqual(ci, 1, "Confidence interval must be <= 1")
                
                # Verify confidence interval bounds
                lower_bound = value - ci
                upper_bound = value + ci
                self.assertGreaterEqual(lower_bound, 0,
                                      "Lower bound must be non-negative")
                self.assertLessEqual(upper_bound, 1,
                                   "Upper bound must be <= 1")
            
            logger.info("Confusion matrix confidence intervals test passed")
        except Exception as e:
            logger.error(f"Confusion matrix confidence intervals test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_validation_rules_compliance(self):
        """Test validation rules compliance."""
        logger.info("Testing validation rules compliance...")
        
        # Query to check validation rules
        query = """
        PREFIX : <http://example.org/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?rule ?type ?severity
        WHERE {
            ?rule rdf:type :ValidationRule ;
                  :hasRuleType ?type ;
                  :hasSeverity ?severity .
        }
        """
        
        results = list(self.graph.query(query))
        validation_rules = {str(result[0]): (str(result[1]), str(result[2])) for result in results}
        
        required_rules = {
            "SensitiveDataValidation": ("SECURITY", "HIGH"),
            "MonitoringIntegrationValidation": ("OPERATIONAL", "MEDIUM"),
            "ResourceUsageValidation": ("PERFORMANCE", "HIGH")
        }
        
        for rule, (expected_type, expected_severity) in required_rules.items():
            self.assertTrue(
                any(rule in str(key) for key in validation_rules.keys()),
                f"Missing validation rule: {rule}"
            )
            actual_rule = next(key for key in validation_rules.keys() if rule in str(key))
            actual_type, actual_severity = validation_rules[actual_rule]
            self.assertEqual(
                expected_type, actual_type,
                f"Incorrect type for {rule}: expected {expected_type}, got {actual_type}"
            )
            self.assertEqual(
                expected_severity, actual_severity,
                f"Incorrect severity for {rule}: expected {expected_severity}, got {actual_severity}"
            )
        
        logger.info("Validation rules compliance test passed successfully")

    def test_compliance_standards_validation(self):
        """Test compliance standards validation."""
        logger.info("Testing compliance standards validation...")
        
        # Query to check compliance standards
        query = """
        PREFIX : <http://example.org/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?standard ?requirement ?status
        WHERE {
            ?standard rdf:type :ComplianceStandard ;
                     :hasRequirement ?requirement ;
                     :hasComplianceStatus ?status .
        }
        """
        
        results = list(self.graph.query(query))
        standards = {str(result[0]): (str(result[1]), str(result[2])) for result in results}
        
        required_standards = ["ISO27001", "SOC2", "GDPR"]
        
        for standard in required_standards:
            self.assertTrue(
                any(standard in str(key) for key in standards.keys()),
                f"Missing compliance standard: {standard}"
            )
            actual_standard = next(key for key in standards.keys() if standard in str(key))
            _, status = standards[actual_standard]
            self.assertEqual(
                "COMPLIANT", status,
                f"Non-compliant status for {standard}: expected COMPLIANT, got {status}"
            )
        
        # Verify SHACL validation rules
        validation_query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        ASK {
            ?shape a sh:NodeShape ;
                   sh:targetClass :ComplianceStandard .
        }
        """
        
        self.assertTrue(
            self.graph.query(validation_query).askAnswer,
            "Missing SHACL validation rules for compliance standards"
        )
        
        logger.info("Compliance standards validation test passed successfully")

    def tearDown(self):
        """Clean up test environment."""
        logger.info("Cleaning up test environment")
        try:
            # Clean up any test artifacts
            if Path('runtime_error_handling_tests.log').exists():
                Path('runtime_error_handling_tests.log').unlink()
            logger.info("Test environment cleanup complete")
        except Exception as e:
            logger.error(f"Failed to clean up test environment: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

if __name__ == '__main__':
    unittest.main() 