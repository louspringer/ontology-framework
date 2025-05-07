# Ontology Framework Test Report
Generated: 2025-04-29T17:08:56.114581
Runtime: 22.16 seconds

## Summary
- Tests Run: 219
- Failures: 50
- Errors: 77
- Skipped: 7

## Details

### Failures

#### tests.test_mcp_config.TestMCPValidator.test_validate_context
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_config.py", line 73, in test_validate_context
    self.assertTrue(self.validator.validate_context(valid_context))
AssertionError: False is not true

```

#### tests.test_validation.TestValidationHandler.test_risk_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 443, in test_risk_validation
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_validation.TestValidationHandler.test_security_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 453, in test_security_validation
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_validation.TestValidationHandler.test_semantic_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 472, in test_semantic_validation
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_sparql_patterns.TestSPARQLPatterns.test_pattern_application
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_sparql_patterns.py", line 176, in test_pattern_application
    self.assertGreater(len(applications), 0, "No pattern applications found")
AssertionError: 0 not greater than 0 : No pattern applications found

```

#### tests.test_sparql_patterns.TestSPARQLPatterns.test_pattern_recognition
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_sparql_patterns.py", line 74, in test_pattern_recognition
    self.assertGreater(len(patterns), 0, "No test patterns found")
AssertionError: 0 not greater than 0 : No test patterns found

```

#### tests.test_guidance_consistency.TestGuidanceConsistency.test_emit_reload_consistency
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_consistency.py", line 24, in test_emit_reload_consistency
    self.assertTrue(
AssertionError: False is not true : Emitted and reloaded graphs are not semantically equivalent

```

#### tests.test_guidance_consistency.TestGuidanceConsistency.test_guidance_structure
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_consistency.py", line 48, in test_guidance_structure
    self.assertTrue(
AssertionError: False is not true : Required class IntegrationStep not found in ontology

```

#### tests.test_guidance_consistency.TestGuidanceConsistency.test_round_trip_consistency
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_consistency.py", line 60, in test_round_trip_consistency
    self.assertTrue(
AssertionError: False is not true : Python-generated and Turtle ontologies are not semantically equivalent

```

#### tests.test_guidance_consistency.TestGuidanceConsistency.test_shacl_validation_patterns
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_consistency.py", line 69, in test_shacl_validation_patterns
    self.assertTrue(any(self.python_guidance.graph.triples((conformance_shape, RDF.type, SH.NodeShape))))
AssertionError: False is not true

```

#### tests.test_manage_models.TestModelManager.test_command_line_interface
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 394, in test_command_line_interface
    self.assertTrue(output_path.exists(), "Output file was not created")
AssertionError: False is not true : Output file was not created

```

#### tests.test_manage_models.TestModelManager.test_load_invalid_model
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 202, in test_load_invalid_model
    with self.assertRaises(ValueError):
AssertionError: ValueError not raised

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_compliance_standards_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 1328, in test_compliance_standards_validation
    self.assertTrue(
AssertionError: False is not true : Missing compliance standard: ISO27001

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_enhanced_confusion_matrix_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 1009, in test_enhanced_confusion_matrix_validation
    self.assertTrue(self.graph.query(query).askAnswer,
AssertionError: False is not true : Missing basic matrix validation rules

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_classification_accuracy
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 923, in test_error_classification_accuracy
    self.assertTrue(len(results) > 0, "No confusion matrices found")
AssertionError: False is not true : No confusion matrices found

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_documentation_requirements
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 365, in test_error_documentation_requirements
    self.assertIn(doc, found_docs, f"Missing required documentation: {doc}")
AssertionError: 'PreventionGuide' not found in {'ErrorReport': 'https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/#ErrorDocumentation', 'ResolutionGuide': 'https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/#ErrorDocumentation'} : Missing required documentation: PreventionGuide

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_assumptions
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 698, in test_error_handling_assumptions
    self.assertIn(assumption, found_assumptions,
AssertionError: 'ErrorTypeExclusivity' not found in {} : Missing required assumption: ErrorTypeExclusivity

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_compliance
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 615, in test_error_handling_compliance
    self.assertIn(standard, found_standards, f"Missing compliance standard: {standard}")
AssertionError: 'ISO27001' not found in {} : Missing compliance standard: ISO27001

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_constraints
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 739, in test_error_handling_constraints
    self.assertIn(constraint, found_constraints,
AssertionError: 'ResourceConstraint' not found in {} : Missing required constraint: ResourceConstraint

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_integration
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 434, in test_error_handling_integration
    self.assertTrue(self.graph.query(query).askAnswer,
AssertionError: False is not true : Missing monitoring integration validation

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_metrics
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 334, in test_error_handling_metrics
    self.assertIn(metric, found_metrics, f"Missing required metric: {metric}")
AssertionError: 'RecurrenceRate' not found in {'ErrorCount': 'https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/#ErrorMetric', 'ResolutionTime': 'https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/#ErrorMetric'} : Missing required metric: RecurrenceRate

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_performance
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 568, in test_error_handling_performance
    self.assertIn(metric, found_metrics, f"Missing performance metric: {metric}")
AssertionError: 'LoggingLatency' not found in {} : Missing performance metric: LoggingLatency

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_risks
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 664, in test_error_handling_risks
    self.assertIn(risk, found_risks, f"Missing required risk: {risk}")
AssertionError: 'DataLossRisk' not found in {} : Missing required risk: DataLossRisk

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_security
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 391, in test_error_handling_security
    self.assertTrue(self.graph.query(query).askAnswer,
AssertionError: False is not true : Missing sensitive data handling validation

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_steps
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 124, in test_error_handling_steps
    self.assertEqual(found_steps[order], step_name,
AssertionError: 'TestErrorIdentification' != 'Error Identification'
- TestErrorIdentification
? ----
+ Error Identification
?      +
 : Step name mismatch for order 1

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_traceability
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 834, in test_error_handling_traceability
    self.assertIn(test_case, found_test_cases,
AssertionError: 'ErrorTypeTestCase' not found in {} : Missing required test case: ErrorTypeTestCase

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 781, in test_error_handling_validation
    self.assertIn(validation, found_validations,
AssertionError: 'RiskValidation' not found in {} : Missing required validation: RiskValidation

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_prevention_measures
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 516, in test_error_prevention_measures
    self.assertTrue(len(results) > 0, "No prevention measures found")
AssertionError: False is not true : No prevention measures found

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_property_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 284, in test_error_property_validation
    self.assertTrue(self.graph.query(query).askAnswer,
AssertionError: False is not true : Missing severity property validation

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_recovery_strategy
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 476, in test_error_recovery_strategy
    self.assertTrue(len(results) > 0, "No recovery strategies found")
AssertionError: False is not true : No recovery strategies found

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_test_error_handling_steps
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 150, in test_test_error_handling_steps
    self.assertIn(order, found_steps, f"Missing test step order: {order}")
AssertionError: 1 not found in {} : Missing test step order: 1

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_validation_rules_compliance
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_runtime_error_handling.py", line 1287, in test_validation_rules_compliance
    self.assertTrue(
AssertionError: False is not true : Missing validation rule: SensitiveDataValidation

```

#### tests.test_error_handler_root.TestErrorHandler.test_metrics_management
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 315, in test_metrics_management
    self.assertTrue(self.error_handler.check_metrics_thresholds(metrics, thresholds))
AssertionError: False is not true

```

#### tests.test_guidance.TestGuidanceOntology.test_legacy_support
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance.py", line 126, in test_legacy_support
    self.assertEqual(count, 5, f"Should have legacy mappings for all modules, found {count}")
AssertionError: 0 != 5 : Should have legacy mappings for all modules, found 0

```

#### tests.test_guidance.TestGuidanceOntology.test_module_class_definitions
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance.py", line 237, in test_module_class_definitions
    self.fail(f"Missing class {class_name} in {module} module")
AssertionError: Missing class Interpretation in core module

```

#### tests.test_guidance.TestGuidanceOntology.test_module_imports
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance.py", line 99, in test_module_imports
    self.fail(f"Found {len(results)} modules without imports")
AssertionError: Found 1 modules without imports

```

#### tests.test_guidance.TestGuidanceOntology.test_module_registry_completeness
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance.py", line 78, in test_module_registry_completeness
    self.assertEqual(count, 5, f"Should have exactly 5 registered modules, found {count}")
AssertionError: 0 != 5 : Should have exactly 5 registered modules, found 0

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_namespace_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 194, in test_namespace_validation
    with self.assertRaises(ConformanceError):
AssertionError: ConformanceError not raised

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_prefix_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 169, in test_prefix_validation
    with self.assertRaises(ConformanceError):
AssertionError: ConformanceError not raised

```

#### tests.test_guidance_validation.TestGuidanceValidation.test_validate_guidance_ontology
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_validation.py", line 40, in test_validate_guidance_ontology
    self.assertEqual(len(results["errors"]), 0,
AssertionError: 9 != 0 : Found validation errors: ['Missing label for ValidationRule', 'Missing comment for ValidationRule', 'Missing range for property: hasMessage', 'Missing range for property: hasPriority', 'Missing range for property: hasValidator', 'Missing range for property: hasTarget', 'Missing required SHACL shape: ValidationPatternShape', 'Missing target class for shape: ValidationPatternShape', 'Missing properties for shape: ValidationPatternShape']

```

#### tests.test_spore_integration.TestSporeIntegration.test_concurrent_integration
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_spore_integration.py", line 121, in test_concurrent_integration
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_spore_integration.TestSporeIntegration.test_dependency_resolution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_spore_integration.py", line 150, in test_dependency_resolution
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_spore_integration.TestSporeIntegration.test_error_handling
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_spore_integration.py", line 169, in test_error_handling
    with self.assertRaises(ConcurrentModificationError):
AssertionError: ConcurrentModificationError not raised

```

#### tests.test_spore_integration.TestSporeIntegration.test_model_compatibility_check
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_spore_integration.py", line 80, in test_model_compatibility_check
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_spore_integration.TestSporeIntegration.test_patch_application
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_spore_integration.py", line 90, in test_patch_application
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_mcp_prompt.TestCheckPhase.test_failed_do_phase
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 148, in test_failed_do_phase
    self.phase.execute(self.context, failed_do)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 437, in execute
    g.add((check_phase, PDCA.hasStartTime, self.start_time.isoformat()))
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 581, in add
    assert isinstance(o, Node), "Object %s must be an rdflib term" % (o,)
AssertionError: Object 2025-04-29T17:08:55.079727 must be an rdflib term

```

#### tests.test_mcp_prompt.TestCheckPhase.test_successful_execution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 138, in test_successful_execution
    results = self.phase.execute(self.context, self.do_results)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 437, in execute
    g.add((check_phase, PDCA.hasStartTime, self.start_time.isoformat()))
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 581, in add
    assert isinstance(o, Node), "Object %s must be an rdflib term" % (o,)
AssertionError: Object 2025-04-29T17:08:55.081515 must be an rdflib term

```

#### tests.test_mcp_prompt.TestPlanPhase.test_invalid_context
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 86, in test_invalid_context
    self.phase.execute(invalid_context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 307, in execute
    g.add((plan_phase, PDCA.hasStartTime, self.start_time.isoformat()))
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 581, in add
    assert isinstance(o, Node), "Object %s must be an rdflib term" % (o,)
AssertionError: Object 2025-04-29T17:08:55.085146 must be an rdflib term

```

#### tests.test_mcp_prompt.TestPlanPhase.test_successful_execution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 72, in test_successful_execution
    results = self.phase.execute(self.context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 307, in execute
    g.add((plan_phase, PDCA.hasStartTime, self.start_time.isoformat()))
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 581, in add
    assert isinstance(o, Node), "Object %s must be an rdflib term" % (o,)
AssertionError: Object 2025-04-29T17:08:55.087806 must be an rdflib term

```

#### tests.test_mcp_prompt.TestPromptContext.test_invalid_target_file
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 57, in test_invalid_target_file
    self.assertIn("Target file does not exist", str(cm.exception))
AssertionError: 'Target file does not exist' not found in 'Ontology path does not exist: models/mcp_prompt.ttl'

```

### Errors

#### tests.test_guidance_queries.TestGuidanceQueries.test_get_conformance_levels
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_queries.py", line 16, in test_get_conformance_levels
    levels = self.guidance.get_conformance_levels()
AttributeError: 'GuidanceOntology' object has no attribute 'get_conformance_levels'

```

#### tests.test_guidance_queries.TestGuidanceQueries.test_get_integration_steps
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_queries.py", line 32, in test_get_integration_steps
    steps = self.guidance.get_integration_steps()
AttributeError: 'GuidanceOntology' object has no attribute 'get_integration_steps'

```

#### tests.test_guidance_queries.TestGuidanceQueries.test_get_shacl_shapes
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_queries.py", line 63, in test_get_shacl_shapes
    shapes = self.guidance.get_shacl_shapes()
AttributeError: 'GuidanceOntology' object has no attribute 'get_shacl_shapes'

```

#### tests.test_guidance_queries.TestGuidanceQueries.test_get_test_protocols
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_queries.py", line 42, in test_get_test_protocols
    protocols = self.guidance.get_test_protocols()
AttributeError: 'GuidanceOntology' object has no attribute 'get_test_protocols'

```

#### tests.test_guidance_queries.TestGuidanceQueries.test_get_validation_patterns
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_queries.py", line 53, in test_get_validation_patterns
    patterns = self.guidance.get_validation_patterns()
AttributeError: 'GuidanceOntology' object has no attribute 'get_validation_patterns'. Did you mean: 'ValidationPattern'?

```

#### tests.test_guidance_queries.TestGuidanceQueries.test_validate_conformance_level
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_queries.py", line 73, in test_validate_conformance_level
    self.assertTrue(self.guidance.validate_conformance_level("STRICT"))
AttributeError: 'GuidanceOntology' object has no attribute 'validate_conformance_level'

```

#### tests.test_mcp_config.TestMCPConfig.test_get_server_config
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_config.py", line 28, in test_get_server_config
    self.assertEqual(server_config["url"], "http://localhost:8080/sse")
KeyError: 'url'

```

#### tests.test_validation_handler.TestValidationHandler.test_load_validation_rules
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation_handler.py", line 37, in setUp
    self.handler.register_rule(
TypeError: ValidationHandler.register_rule() got an unexpected keyword argument 'pattern'

```

#### tests.test_validation_handler.TestValidationHandler.test_validate_graph
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation_handler.py", line 37, in setUp
    self.handler.register_rule(
TypeError: ValidationHandler.register_rule() got an unexpected keyword argument 'pattern'

```

#### tests.test_validation_handler.TestValidationHandler.test_validate_sensitive_data
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation_handler.py", line 37, in setUp
    self.handler.register_rule(
TypeError: ValidationHandler.register_rule() got an unexpected keyword argument 'pattern'

```

#### tests.test_validation_handler.TestValidationHandler.test_validate_syntax
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation_handler.py", line 37, in setUp
    self.handler.register_rule(
TypeError: ValidationHandler.register_rule() got an unexpected keyword argument 'pattern'

```

#### tests.test_validation.TestValidation.test_bfg9k_pattern_strict
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 292, in setUp
    self.handler = ValidationHandler(self.graph)
TypeError: ValidationHandler.__init__() takes 1 positional argument but 2 were given

```

#### tests.test_validation.TestValidation.test_individual_type_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 292, in setUp
    self.handler = ValidationHandler(self.graph)
TypeError: ValidationHandler.__init__() takes 1 positional argument but 2 were given

```

#### tests.test_validation.TestValidation.test_invalid_data
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 292, in setUp
    self.handler = ValidationHandler(self.graph)
TypeError: ValidationHandler.__init__() takes 1 positional argument but 2 were given

```

#### tests.test_validation.TestValidation.test_semantic_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 292, in setUp
    self.handler = ValidationHandler(self.graph)
TypeError: ValidationHandler.__init__() takes 1 positional argument but 2 were given

```

#### tests.test_validation.TestValidation.test_spore_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 292, in setUp
    self.handler = ValidationHandler(self.graph)
TypeError: ValidationHandler.__init__() takes 1 positional argument but 2 were given

```

#### tests.test_validation.TestValidation.test_syntax_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 292, in setUp
    self.handler = ValidationHandler(self.graph)
TypeError: ValidationHandler.__init__() takes 1 positional argument but 2 were given

```

#### tests.test_validation.TestValidation.test_validation_history
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 292, in setUp
    self.handler = ValidationHandler(self.graph)
TypeError: ValidationHandler.__init__() takes 1 positional argument but 2 were given

```

#### tests.test_validation.TestValidationHandler.test_individual_type_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 489, in test_individual_type_validation
    result = self.validator.validate(ValidationRule.INDIVIDUAL_TYPE, data)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/enum.py", line 437, in __getattr__
    raise AttributeError(name) from None
AttributeError: INDIVIDUAL_TYPE

```

#### tests.test_validation.TestValidationHandler.test_invalid_rule
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 504, in test_invalid_rule
    self.validator.validate('invalid_rule', data)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/error_handling/validation.py", line 103, in validate
    raise ValueError(f"Rule {rule} not found in validation rules")
ValueError: Rule invalid_rule not found in validation rules

```

#### tests.test_validation.TestValidationHandler.test_none_data
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_validation.py", line 498, in test_none_data
    result = self.validator.validate(ValidationRule.RISK, None)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/error_handling/validation.py", line 100, in validate
    raise TypeError("Data must be a dictionary")
TypeError: Data must be a dictionary

```

#### tests.test_deployment_modeler.TestDeploymentModeler.test_load_core_ontologies_error
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/src/ontology_framework/deployment_modeler.py", line 24, in __init__
    self._load_core_ontologies()
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1114, in __call__
    return self._mock_call(*args, **kwargs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1118, in _mock_call
    return self._execute_mock_call(*args, **kwargs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1173, in _execute_mock_call
    raise effect
Exception: Failed to load ontologies

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1379, in patched
    return func(*newargs, **newkeywargs)
  File "/Users/lou/ontology-framework/tests/test_deployment_modeler.py", line 105, in test_load_core_ontologies_error
    modeler = DeploymentModeler()  # This should not raise an exception
  File "/Users/lou/ontology-framework/src/ontology_framework/deployment_modeler.py", line 26, in __init__
    self.error_handler.add_error(
TypeError: ErrorHandler.add_error() takes 2 positional arguments but 4 were given

```

#### tests.test_deployment_modeler.TestDeploymentModeler.test_validate_deployment_failure
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/src/ontology_framework/deployment_modeler.py", line 98, in validate_deployment
    self.error_handler.add_error(
TypeError: ErrorHandler.add_error() takes 2 positional arguments but 4 were given

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_deployment_modeler.py", line 58, in test_validate_deployment_failure
    result = self.modeler.validate_deployment(invalid_config)
  File "/Users/lou/ontology-framework/src/ontology_framework/deployment_modeler.py", line 107, in validate_deployment
    self.error_handler.add_error(
TypeError: ErrorHandler.add_error() takes 2 positional arguments but 4 were given

```

#### tests.test_conformance_tracking.TestConformanceTracker.test_add_violation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_conformance_tracking.py", line 56, in setUp
    self.tracker.graph.add((self.test_spore, RDF.type, META.SemanticSpore))
AttributeError: 'ConformanceTracker' object has no attribute 'graph'

```

#### tests.test_conformance_tracking.TestConformanceTracker.test_clear_violations
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_conformance_tracking.py", line 56, in setUp
    self.tracker.graph.add((self.test_spore, RDF.type, META.SemanticSpore))
AttributeError: 'ConformanceTracker' object has no attribute 'graph'

```

#### tests.test_conformance_tracking.TestConformanceTracker.test_export_violations
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_conformance_tracking.py", line 56, in setUp
    self.tracker.graph.add((self.test_spore, RDF.type, META.SemanticSpore))
AttributeError: 'ConformanceTracker' object has no attribute 'graph'

```

#### tests.test_conformance_tracking.TestConformanceTracker.test_get_violations
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_conformance_tracking.py", line 56, in setUp
    self.tracker.graph.add((self.test_spore, RDF.type, META.SemanticSpore))
AttributeError: 'ConformanceTracker' object has no attribute 'graph'

```

#### tests.test_conformance_tracking.TestConformanceTracker.test_import_violations
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_conformance_tracking.py", line 56, in setUp
    self.tracker.graph.add((self.test_spore, RDF.type, META.SemanticSpore))
AttributeError: 'ConformanceTracker' object has no attribute 'graph'

```

#### tests.test_guidance_manager.TestGuidanceManager.test_add_validation_rule
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_manager.py", line 106, in test_add_validation_rule
    rule_uri = self.manager.add_validation_rule(
  File "/Users/lou/ontology-framework/src/ontology_framework/tools/guidance_manager.py", line 221, in add_validation_rule
    self.graph.update(update_query)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1684, in update
    return processor.update(update_object, initBindings, initNs, **kwargs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/processor.py", line 104, in update
    strOrQuery = translateUpdate(parseUpdate(strOrQuery), initNs=initNs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/parser.py", line 1564, in parseUpdate
    return UpdateUnit.parseString(q, parseAll=True)[0]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/pyparsing/util.py", line 417, in _inner
    return fn(self, *args, **kwargs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/pyparsing/core.py", line 1219, in parse_string
    raise exc.with_traceback(None)
pyparsing.exceptions.ParseException: Expected end of text, found 'INSERT'  (at char 242), (line:6, col:9)

```

#### tests.test_guidance_manager.TestGuidanceManager.test_save_and_reload
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_manager.py", line 141, in test_save_and_reload
    self.manager.add_validation_rule(
  File "/Users/lou/ontology-framework/src/ontology_framework/tools/guidance_manager.py", line 221, in add_validation_rule
    self.graph.update(update_query)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1684, in update
    return processor.update(update_object, initBindings, initNs, **kwargs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/processor.py", line 104, in update
    strOrQuery = translateUpdate(parseUpdate(strOrQuery), initNs=initNs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/parser.py", line 1564, in parseUpdate
    return UpdateUnit.parseString(q, parseAll=True)[0]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/pyparsing/util.py", line 417, in _inner
    return fn(self, *args, **kwargs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/pyparsing/core.py", line 1219, in parse_string
    raise exc.with_traceback(None)
pyparsing.exceptions.ParseException: Expected end of text, found 'INSERT'  (at char 242), (line:6, col:9)

```

#### tests.test_dependency_model.TestDependencyModelGenerator.test_analyze_ontology
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_dependency_model.py", line 85, in test_analyze_ontology
    self.generator.analyze_ontology()
  File "/Users/lou/ontology-framework/src/ontology_framework/dependency_model.py", line 128, in analyze_ontology
    self.nodes[prop].dependencies.add(self.nodes[domain_uri])
TypeError: unhashable type: 'DependencyNode'

```

#### tests.test_dependency_model.TestDependencyModelGenerator.test_generate_code_types
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_dependency_model.py", line 111, in test_generate_code_types
    self.generator.analyze_ontology()
  File "/Users/lou/ontology-framework/src/ontology_framework/dependency_model.py", line 128, in analyze_ontology
    self.nodes[prop].dependencies.add(self.nodes[domain_uri])
TypeError: unhashable type: 'DependencyNode'

```

#### tests.test_dependency_model.TestDependencyModelGenerator.test_save_dependency_model
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_dependency_model.py", line 143, in test_save_dependency_model
    self.generator.analyze_ontology()
  File "/Users/lou/ontology-framework/src/ontology_framework/dependency_model.py", line 128, in analyze_ontology
    self.nodes[prop].dependencies.add(self.nodes[domain_uri])
TypeError: unhashable type: 'DependencyNode'

```

#### tests.test_dependency_model.TestDependencyModelGenerator.test_visualize_dependencies
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_dependency_model.py", line 154, in test_visualize_dependencies
    self.generator.analyze_ontology()
  File "/Users/lou/ontology-framework/src/ontology_framework/dependency_model.py", line 128, in analyze_ontology
    self.nodes[prop].dependencies.add(self.nodes[domain_uri])
TypeError: unhashable type: 'DependencyNode'

```

#### tests.test_manage_models.TestModelManager.test_dependency_tracking
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 327, in test_dependency_tracking
    self.assertIn("dependent_model", self.manager.dependencies)
AttributeError: 'ModelManager' object has no attribute 'dependencies'

```

#### tests.test_manage_models.TestModelManager.test_integrate_models
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 254, in test_integrate_models
    self.manager.integrate_models("model1", ["model2"])
AttributeError: 'ModelManager' object has no attribute 'integrate_models'

```

#### tests.test_manage_models.TestModelManager.test_model_documentation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 505, in test_model_documentation
    self.manager.validate_documentation(test_model),
AttributeError: 'ModelManager' object has no attribute 'validate_documentation'

```

#### tests.test_manage_models.TestModelManager.test_model_first_principle
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 414, in test_model_first_principle
    with patch.object(self.manager, 'check_model_quality', return_value=False):
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1447, in __enter__
    original, local = self.get_original()
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1420, in get_original
    raise AttributeError(
AttributeError: <ontology_framework.manage_models.ModelManager object at 0x1116cfbe0> does not have the attribute 'check_model_quality'

```

#### tests.test_manage_models.TestModelManager.test_model_projection_alignment
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 462, in test_model_projection_alignment
    result = self.manager.validate_projection(test_model, test_projection)
AttributeError: 'ModelManager' object has no attribute 'validate_projection'. Did you mean: 'validate_version'?

```

#### tests.test_manage_models.TestModelManager.test_model_quality_precedence
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 437, in test_model_quality_precedence
    self.manager.validate_system_quality(str(self.test_model_path))
AttributeError: 'ModelManager' object has no attribute 'validate_system_quality'

```

#### tests.test_manage_models.TestModelManager.test_model_validation_pipeline
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 480, in test_model_validation_pipeline
    result = self.manager.validate_model_quality(model_name)
AttributeError: 'ModelManager' object has no attribute 'validate_model_quality'

```

#### tests.test_manage_models.TestModelManager.test_save_model
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 275, in test_save_model
    self.manager.save_model("test_model", str(output_path))
AttributeError: 'ModelManager' object has no attribute 'save_model'

```

#### tests.test_manage_models.TestModelManager.test_shacl_validation
```
Traceback (most recent call last):
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1376, in patched
    with self.decoration_helper(patched,
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/contextlib.py", line 135, in __enter__
    return next(self.gen)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1358, in decoration_helper
    arg = exit_stack.enter_context(patching)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/contextlib.py", line 492, in enter_context
    result = _cm_type.__enter__(cm)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1447, in __enter__
    original, local = self.get_original()
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1420, in get_original
    raise AttributeError(
AttributeError: <class 'ontology_framework.manage_models.ModelManager'> does not have the attribute 'check_shacl_constraints'

```

#### tests.test_manage_models.TestModelManager.test_validate_model
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 220, in test_validate_model
    self.manager._validate_model(model_graph)  # Should not raise an exception
AttributeError: 'ModelManager' object has no attribute '_validate_model'

```

#### tests.test_manage_models.TestModelManager.test_validation_pipeline
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 347, in test_validation_pipeline
    self.manager._run_validation_pipeline(complete_model)  # Should not raise warnings
AttributeError: 'ModelManager' object has no attribute '_run_validation_pipeline'

```

#### tests.test_manage_models.TestModelManager.test_version_tracking
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_manage_models.py", line 303, in test_version_tracking
    self.assertIn("versioned_model", self.manager.versions)
AttributeError: 'ModelManager' object has no attribute 'versions'

```

#### tests.test_python_validator.TestPythonValidator.test_validate_bad_naming
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_python_validator.py", line 14, in setUp
    self.validator = PythonValidator()
  File "/Users/lou/ontology-framework/src/ontology_framework/validation/python_validator.py", line 20, in __init__
    self.shapes_graph.parse(shapes_file, format="turtle")
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1518, in parse
    source = create_input_source(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 735, in create_input_source
    ) = _create_input_source_from_location(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 795, in _create_input_source_from_location
    file = open(filename, "rb")
FileNotFoundError: [Errno 2] No such file or directory: '/Users/lou/tests/test_data/python_shapes.ttl'

```

#### tests.test_python_validator.TestPythonValidator.test_validate_good_class
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_python_validator.py", line 14, in setUp
    self.validator = PythonValidator()
  File "/Users/lou/ontology-framework/src/ontology_framework/validation/python_validator.py", line 20, in __init__
    self.shapes_graph.parse(shapes_file, format="turtle")
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1518, in parse
    source = create_input_source(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 735, in create_input_source
    ) = _create_input_source_from_location(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 795, in _create_input_source_from_location
    file = open(filename, "rb")
FileNotFoundError: [Errno 2] No such file or directory: '/Users/lou/tests/test_data/python_shapes.ttl'

```

#### tests.test_python_validator.TestPythonValidator.test_validate_inheritance
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_python_validator.py", line 14, in setUp
    self.validator = PythonValidator()
  File "/Users/lou/ontology-framework/src/ontology_framework/validation/python_validator.py", line 20, in __init__
    self.shapes_graph.parse(shapes_file, format="turtle")
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1518, in parse
    source = create_input_source(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 735, in create_input_source
    ) = _create_input_source_from_location(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 795, in _create_input_source_from_location
    file = open(filename, "rb")
FileNotFoundError: [Errno 2] No such file or directory: '/Users/lou/tests/test_data/python_shapes.ttl'

```

#### tests.test_python_validator.TestPythonValidator.test_validate_missing_docstring
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_python_validator.py", line 14, in setUp
    self.validator = PythonValidator()
  File "/Users/lou/ontology-framework/src/ontology_framework/validation/python_validator.py", line 20, in __init__
    self.shapes_graph.parse(shapes_file, format="turtle")
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1518, in parse
    source = create_input_source(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 735, in create_input_source
    ) = _create_input_source_from_location(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 795, in _create_input_source_from_location
    file = open(filename, "rb")
FileNotFoundError: [Errno 2] No such file or directory: '/Users/lou/tests/test_data/python_shapes.ttl'

```

#### tests.test_python_validator.TestPythonValidator.test_validate_return_types
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_python_validator.py", line 14, in setUp
    self.validator = PythonValidator()
  File "/Users/lou/ontology-framework/src/ontology_framework/validation/python_validator.py", line 20, in __init__
    self.shapes_graph.parse(shapes_file, format="turtle")
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1518, in parse
    source = create_input_source(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 735, in create_input_source
    ) = _create_input_source_from_location(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 795, in _create_input_source_from_location
    file = open(filename, "rb")
FileNotFoundError: [Errno 2] No such file or directory: '/Users/lou/tests/test_data/python_shapes.ttl'

```

#### tests.test_error_handler_root.TestErrorHandler.test_error_summary
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 341, in test_error_summary
    self.assertEqual(summary["error_types"]["validation"], 1)
KeyError: 'validation'

```

#### tests.test_model_generator.TestModelGenerator.test_analyze_file
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_model_generator.py", line 18, in test_analyze_file
    with open(self.test_file, "w") as f:
FileNotFoundError: [Errno 2] No such file or directory: '/Users/lou/ontology-framework/tests/test_data/test_module.py'

```

#### tests.test_model_generator.TestModelGenerator.test_generate_model
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_model_generator.py", line 33, in test_generate_model
    model = self.generator.generate_model(self.test_file)
  File "/Users/lou/ontology-framework/src/ontology_framework/tools/model_generator.py", line 84, in generate_model
    info = self.analyze_file(file_path)
  File "/Users/lou/ontology-framework/src/ontology_framework/tools/model_generator.py", line 43, in analyze_file
    with open(file_path, 'r', encoding='utf-8') as f:
FileNotFoundError: [Errno 2] No such file or directory: '/Users/lou/ontology-framework/tests/test_data/test_module.py'

```

#### tests.test_model_generator.TestModelGenerator.test_save_models
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_model_generator.py", line 46, in test_save_models
    model = self.generator.generate_model(self.test_file)
  File "/Users/lou/ontology-framework/src/ontology_framework/tools/model_generator.py", line 84, in generate_model
    info = self.analyze_file(file_path)
  File "/Users/lou/ontology-framework/src/ontology_framework/tools/model_generator.py", line 43, in analyze_file
    with open(file_path, 'r', encoding='utf-8') as f:
FileNotFoundError: [Errno 2] No such file or directory: '/Users/lou/ontology-framework/tests/test_data/test_module.py'

```

#### tests.test_guidance.TestGuidanceOntology.test_modeling_rules_completeness
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance.py", line 259, in test_modeling_rules_completeness
    results = list(self.g.query(query))
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1632, in query
    return result(processor.query(query_object, initBindings, initNs, **kwargs))  # type: ignore[arg-type]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/processor.py", line 145, in query
    strOrQuery = translateQuery(parseQuery(strOrQuery), base, initNs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 933, in translateQuery
    q[1] = traverse(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 468, in traverse
    r = _traverse(tree, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 427, in _traverse
    e[k] = _traverse(val, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 427, in _traverse
    e[k] = _traverse(val, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in _traverse
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in <listcomp>
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 427, in _traverse
    e[k] = _traverse(val, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in _traverse
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in <listcomp>
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in _traverse
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in <listcomp>
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 429, in _traverse
    _e = visitPost(e)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 193, in translatePName
    return prologue.absolutize(p)  # type: ignore[return-value]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/sparql.py", line 468, in absolutize
    return self.resolvePName(iri.prefix, iri.localname)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/sparql.py", line 450, in resolvePName
    raise Exception("Unknown namespace prefix : %s" % prefix)
Exception: Unknown namespace prefix : meta

```

#### tests.test_guidance.TestGuidanceOntology.test_test_requirements_completeness
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance.py", line 330, in test_test_requirements_completeness
    results = list(self.g.query(query))
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1632, in query
    return result(processor.query(query_object, initBindings, initNs, **kwargs))  # type: ignore[arg-type]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/processor.py", line 145, in query
    strOrQuery = translateQuery(parseQuery(strOrQuery), base, initNs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 933, in translateQuery
    q[1] = traverse(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 468, in traverse
    r = _traverse(tree, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 427, in _traverse
    e[k] = _traverse(val, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 427, in _traverse
    e[k] = _traverse(val, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in _traverse
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in <listcomp>
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 427, in _traverse
    e[k] = _traverse(val, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in _traverse
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in <listcomp>
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in _traverse
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in <listcomp>
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 429, in _traverse
    _e = visitPost(e)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 193, in translatePName
    return prologue.absolutize(p)  # type: ignore[return-value]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/sparql.py", line 468, in absolutize
    return self.resolvePName(iri.prefix, iri.localname)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/sparql.py", line 450, in resolvePName
    raise Exception("Unknown namespace prefix : %s" % prefix)
Exception: Unknown namespace prefix : meta

```

#### setUpClass (tests.test_sparql_client.TestSparqlClient)
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_sparql_client.py", line 74, in _setup_fuseki
    subprocess.run(["docker", "info"], capture_output=True, check=True)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/subprocess.py", line 526, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['docker', 'info']' returned non-zero exit status 1.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_sparql_client.py", line 35, in setUpClass
    cls._setup_fuseki()
  File "/Users/lou/ontology-framework/tests/test_sparql_client.py", line 77, in _setup_fuseki
    raise RuntimeError("Docker is required for running tests")
RuntimeError: Docker is required for running tests

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_conformance_level_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 129, in test_conformance_level_validation
    self.integrator.set_conformance_level(GUIDANCE.STRICT)
  File "/Users/lou/ontology-framework/src/ontology_framework/spore_integration.py", line 92, in set_conformance_level
    raise ConformanceError(f"Invalid conformance level: {level}. Must be one of {set(CONFORMANCE_LEVELS.keys())}")
ontology_framework.exceptions.ConformanceError: Invalid conformance level: https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#STRICT. Must be one of {'STRICT', 'RELAXED', 'MODERATE'}

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_integration_step_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 229, in test_integration_step_validation
    result = self.integrator.validate_integration_steps(process)
  File "/Users/lou/ontology-framework/src/ontology_framework/spore_integration.py", line 618, in validate_integration_steps
    raise ConformanceError("No integration steps found in process")
ontology_framework.exceptions.ConformanceError: No integration steps found in process

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_ordered_step_execution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 286, in test_ordered_step_execution
    result = self.integrator.execute_integration_steps(process)
  File "/Users/lou/ontology-framework/src/ontology_framework/spore_integration.py", line 682, in execute_integration_steps
    raise ConformanceError(f"Step {step} has no target")
ontology_framework.exceptions.ConformanceError: Step http://example.org/steps/step1 has no target

```

#### tests.test_guidance_validation.TestGuidanceValidation.test_validate_conformance_levels
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_validation.py", line 21, in test_validate_conformance_levels
    results = self.validator.validate_conformance_levels()
AttributeError: 'OntologyValidator' object has no attribute 'validate_conformance_levels'

```

#### tests.test_guidance_validation.TestGuidanceValidation.test_validate_integration_process
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_validation.py", line 27, in test_validate_integration_process
    results = self.validator.validate_integration_process()
AttributeError: 'OntologyValidator' object has no attribute 'validate_integration_process'

```

#### tests.test_guidance_validation.TestGuidanceValidation.test_validate_test_protocol
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_validation.py", line 33, in test_validate_test_protocol
    results = self.validator.validate_test_protocol()
AttributeError: 'OntologyValidator' object has no attribute 'validate_test_protocol'

```

#### tests.test_session_update.TestSessionUpdate.test_session_update_rdflib_terms
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_session_update.py", line 28, in test_session_update_rdflib_terms
    update_session_ttl(ontology_info, model_name, session_file=self.test_session_file)
TypeError: update_session_ttl() got an unexpected keyword argument 'session_file'

```

#### tests.test_spore_integration.TestSporeIntegration.test_spore_validation_before_integration
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_spore_integration.py", line 69, in test_spore_validation_before_integration
    result = self.integrator.integrate_spore(self.test_spore, self.test_model)
  File "/Users/lou/ontology-framework/src/ontology_framework/spore_integration.py", line 406, in integrate_spore
    raise ValueError("Spore not compatible with target model")
ValueError: Spore not compatible with target model

```

#### tests.test_mcp_prompt.TestActPhase.test_failed_check_phase
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 157, in setUp
    self.phase = ActPhase()
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 507, in __init__
    super().__init__()
TypeError: PromptPhase.__init__() missing 1 required positional argument: 'name'

```

#### tests.test_mcp_prompt.TestActPhase.test_successful_execution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 157, in setUp
    self.phase = ActPhase()
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 507, in __init__
    super().__init__()
TypeError: PromptPhase.__init__() missing 1 required positional argument: 'name'

```

#### tests.test_mcp_prompt.TestAdjustPhase.test_no_adjustments_needed
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 364, in test_no_adjustments_needed
    results = self.phase.execute(context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 590, in execute
    self.validate(context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 179, in validate
    raise PromptError(
src.ontology_framework.modules.prompt_base.PromptError: Invalid context type: <class 'dict'>

```

#### tests.test_mcp_prompt.TestAdjustPhase.test_successful_execution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 348, in test_successful_execution
    results = self.phase.execute(self.context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 590, in execute
    self.validate(context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 179, in validate
    raise PromptError(
src.ontology_framework.modules.prompt_base.PromptError: Invalid context type: <class 'dict'>

```

#### tests.test_mcp_prompt.TestDiscoveryPhase.test_invalid_context
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 190, in setUp
    self.phase = DiscoveryPhase()
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 191, in __init__
    self.targeter = BFG9KTargeter()
TypeError: BFG9KTargeter.__init__() missing 1 required positional argument: 'hypercube_analyzer'

```

#### tests.test_mcp_prompt.TestDiscoveryPhase.test_successful_execution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 190, in setUp
    self.phase = DiscoveryPhase()
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 191, in __init__
    self.targeter = BFG9KTargeter()
TypeError: BFG9KTargeter.__init__() missing 1 required positional argument: 'hypercube_analyzer'

```

#### tests.test_mcp_prompt.TestDoPhase.test_error_handling
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 117, in test_error_handling
    results = self.phase.execute(error_context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 355, in execute
    self.validate(context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 179, in validate
    raise PromptError(
src.ontology_framework.modules.prompt_base.PromptError: Invalid context type: <class 'dict'>

```

#### tests.test_mcp_prompt.TestDoPhase.test_successful_execution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 107, in test_successful_execution
    results = self.phase.execute(self.context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 355, in execute
    self.validate(context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 179, in validate
    raise PromptError(
src.ontology_framework.modules.prompt_base.PromptError: Invalid context type: <class 'dict'>

```

#### tests.test_mcp_prompt.TestMCPPrompt.test_error_handling
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 324, in test_error_handling
    prompt = MCPPrompt(invalid_context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 650, in __init__
    ActPhase(),
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 507, in __init__
    super().__init__()
TypeError: PromptPhase.__init__() missing 1 required positional argument: 'name'

```

#### tests.test_mcp_prompt.TestMCPPrompt.test_successful_execution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 257, in test_successful_execution
    prompt = MCPPrompt(self.context)
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 650, in __init__
    ActPhase(),
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 507, in __init__
    super().__init__()
TypeError: PromptPhase.__init__() missing 1 required positional argument: 'name'

```

#### tests.test_mcp_prompt.TestPromptContext.test_valid_context
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_mcp_prompt.py", line 37, in test_valid_context
    context.validate()  # Should not raise
  File "/Users/lou/ontology-framework/src/ontology_framework/modules/mcp_prompt.py", line 96, in validate
    raise PromptError(
src.ontology_framework.modules.prompt_base.PromptError: Ontology path does not exist: models/mcp_prompt.ttl

```

## Test Session Summary - 2025-04-29T17:15:51.146219

- Total tests: 14
- Passed: 2
- Failed: 12
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T17:17:46.506841

- Total tests: 14
- Passed: 1
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T18:15:34.403408

- Total tests: 14
- Passed: 2
- Failed: 12
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T18:17:28.934895

- Total tests: 14
- Passed: 2
- Failed: 12
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T18:20:29.655728

- Total tests: 14
- Passed: 2
- Failed: 12
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T18:26:06.327796

- Total tests: 17
- Passed: 2
- Failed: 15
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T18:28:26.291489

- Total tests: 17
- Passed: 3
- Failed: 14
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T18:30:07.823994

- Total tests: 17
- Passed: 1
- Failed: 16
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T18:31:24.134566

- Total tests: 17
- Passed: 3
- Failed: 14
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T18:46:31.419129

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T19:23:43.466240

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T19:26:21.082186

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T19:27:27.494519

- Total tests: 17
- Passed: 1
- Failed: 16
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T19:34:43.660759

- Total tests: 17
- Passed: 1
- Failed: 16
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T19:36:27.934438

- Total tests: 17
- Passed: 1
- Failed: 16
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T19:39:32.263459

- Total tests: 17
- Passed: 5
- Failed: 12
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T19:41:30.341739

- Total tests: 17
- Passed: 5
- Failed: 12
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-29T19:44:00.629266

- Total tests: 17
- Passed: 5
- Failed: 12
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:32:08.136972

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:33:29.226932

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:36:07.955656

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:37:17.132570

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:39:39.333556

- Total tests: 17
- Passed: 0
- Failed: 17
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:40:27.809982

- Total tests: 17
- Passed: 0
- Failed: 17
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:41:16.033789

- Total tests: 17
- Passed: 0
- Failed: 17
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:42:58.221690

- Total tests: 17
- Passed: 0
- Failed: 17
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:44:46.195329

- Total tests: 17
- Passed: 0
- Failed: 17
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:47:24.332627

- Total tests: 17
- Passed: 10
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T07:51:34.659983

- Total tests: 17
- Passed: 11
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-04-30T08:12:48.643824

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-04-30T08:12:48.732632


## Test Session Summary - 2025-04-30T08:15:14.678807

- Total tests: 619
- Passed: 283
- Failed: 336
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-04-30T08:38:23.106990

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-04-30T08:38:23.170184


## Test Session Summary - 2025-04-30T08:40:29.781807

- Total tests: 619
- Passed: 281
- Failed: 338
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T08:55:46.728235

- Total tests: 4
- Passed: 0
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T08:58:16.273578

- Total tests: 4
- Passed: 1
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T08:59:02.658192

- Total tests: 4
- Passed: 1
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T09:15:10.171718

- Total tests: 15
- Passed: 9
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T09:15:57.416449

- Total tests: 15
- Passed: 9
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T09:17:20.195792

- Total tests: 15
- Passed: 9
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T09:22:49.878764

- Total tests: 15
- Passed: 12
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T09:23:48.600798

- Total tests: 15
- Passed: 12
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T09:25:40.328349

- Total tests: 15
- Passed: 10
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-04-30T09:54:45.349904

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-04-30T09:54:45.485509


## Test Session Summary - 2025-04-30T09:57:09.714205

- Total tests: 619
- Passed: 264
- Failed: 355
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-04-30T10:36:31.907445

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-04-30T10:36:31.995457


## Test Session Summary - 2025-04-30T10:38:43.309196

- Total tests: 619
- Passed: 266
- Failed: 353
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T10:40:14.885349

- Total tests: 27
- Passed: 7
- Failed: 20
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T10:50:12.833920

- Total tests: 5
- Passed: 0
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T10:54:19.823999

- Total tests: 11
- Passed: 4
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T10:57:48.970891

- Total tests: 12
- Passed: 9
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T10:59:07.420641

- Total tests: 12
- Passed: 10
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T10:59:49.758896

- Total tests: 12
- Passed: 10
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:00:38.432268

- Total tests: 12
- Passed: 11
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:01:59.485369

- Total tests: 12
- Passed: 12
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:05:59.437682

- Total tests: 12
- Passed: 12
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:09:22.205108

- Total tests: 12
- Passed: 12
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:11:59.108642

- Total tests: 56
- Passed: 55
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:15:29.387426

- Total tests: 4
- Passed: 0
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:16:51.189042

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:17:26.165457

- Total tests: 4
- Passed: 0
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:18:37.328857

- Total tests: 4
- Passed: 1
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T11:19:49.138551

- Total tests: 4
- Passed: 2
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T12:39:28.164196

- Total tests: 624
- Passed: 622
- Failed: 2
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T12:44:52.691052

- Total tests: 17
- Passed: 0
- Failed: 17
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T12:47:13.355558

- Total tests: 17
- Passed: 16
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T12:48:26.066164

- Total tests: 17
- Passed: 16
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T12:50:23.158680

- Total tests: 17
- Passed: 16
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T12:52:04.913620

- Total tests: 17
- Passed: 17
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:17:20.284965

- Total tests: 7
- Passed: 7
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:20:13.839407

- Total tests: 8
- Passed: 8
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:29:38.472289

- Total tests: 6
- Passed: 2
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:31:12.072277

- Total tests: 6
- Passed: 2
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:33:41.790097

- Total tests: 6
- Passed: 2
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:35:27.972188

- Total tests: 6
- Passed: 2
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:37:35.150820

- Total tests: 6
- Passed: 0
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:44:43.283091

- Total tests: 6
- Passed: 0
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:46:22.357905

- Total tests: 6
- Passed: 0
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:49:33.784852

- Total tests: 6
- Passed: 0
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T13:50:52.217268

- Total tests: 6
- Passed: 0
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:00:02.594109

- Total tests: 5
- Passed: 0
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:01:22.892410

- Total tests: 5
- Passed: 0
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:09:43.757216

- Total tests: 5
- Passed: 0
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:12:31.643923

- Total tests: 5
- Passed: 0
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:38:06.929116

- Total tests: 6
- Passed: 1
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:38:55.344566

- Total tests: 6
- Passed: 1
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:40:34.720728

- Total tests: 6
- Passed: 0
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:41:22.880346

- Total tests: 6
- Passed: 1
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:43:04.641352

- Total tests: 6
- Passed: 1
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:44:13.399137

- Total tests: 6
- Passed: 1
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:45:33.762434

- Total tests: 6
- Passed: 1
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:46:42.440119

- Total tests: 6
- Passed: 1
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:53:01.128346

- Total tests: 6
- Passed: 2
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-30T14:54:39.448527

- Total tests: 6
- Passed: 2
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T19:36:19.406969

- Total tests: 13
- Passed: 2
- Failed: 11
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T19:40:39.370273

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T19:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T19:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T19:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T19:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T19:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T20:06:16.086867

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T20:08:21.064205

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T20:28:05.579667

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T20:30:14.121683

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T20:31:33.743952

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T20:35:40.281523

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T20:38:41.699483

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T20:51:34.178852

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T21:33:51.516153

- Total tests: 532
- Passed: 510
- Failed: 22
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T21:35:10.947809

- Total tests: 592
- Passed: 580
- Failed: 12
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T21:41:22.604426

- Total tests: 605
- Passed: 597
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T21:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T21:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T21:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T21:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T21:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T22:06:16.086867

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T22:08:21.064205

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T22:28:05.579667

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T22:30:14.121683

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T22:31:33.743952

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T22:35:40.281523

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T22:38:41.699483

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T22:51:34.178852

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:33:51.516153

- Total tests: 532
- Passed: 510
- Failed: 22
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:35:10.947809

- Total tests: 592
- Passed: 580
- Failed: 12
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:41:22.604426

- Total tests: 605
- Passed: 597
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T00:06:16.086867

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T00:08:21.064205

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T00:28:05.579667

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T00:30:14.121683

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T00:31:33.743952

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T00:35:40.281523

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T00:38:41.699483

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T00:51:34.178852

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T01:33:51.516153

- Total tests: 532
- Passed: 510
- Failed: 22
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T01:35:10.947809

- Total tests: 592
- Passed: 580
- Failed: 12
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T01:41:22.604426

- Total tests: 605
- Passed: 597
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T01:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T01:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T01:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T01:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T01:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T02:06:16.086867

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T02:08:21.064205

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T02:28:05.579667

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T02:30:14.121683

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T02:31:33.743952

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T02:35:40.281523

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T02:38:41.699483

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T02:51:34.178852

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T03:33:51.516153

- Total tests: 532
- Passed: 510
- Failed: 22
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T03:35:10.947809

- Total tests: 592
- Passed: 580
- Failed: 12
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T03:41:22.604426

- Total tests: 605
- Passed: 597
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T03:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T03:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T03:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T03:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T03:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T04:06:16.086867

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T04:08:21.064205

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T04:28:05.579667

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T04:30:14.121683

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T04:31:33.743952

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T04:35:40.281523

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T04:38:41.699483

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T04:51:34.178852

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T05:33:51.516153

- Total tests: 532
- Passed: 510
- Failed: 22
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T05:35:10.947809

- Total tests: 592
- Passed: 580
- Failed: 12
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T05:41:22.604426

- Total tests: 605
- Passed: 597
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T05:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T05:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T05:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T05:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T05:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T06:06:16.086867

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T06:08:21.064205

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T06:28:05.579667

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T06:30:14.121683

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T06:31:33.743952

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T06:35:40.281523

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T06:38:41.699483

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T06:51:34.178852

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T07:33:51.516153

- Total tests: 532
- Passed: 510
- Failed: 22
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T07:35:10.947809

- Total tests: 592
- Passed: 580
- Failed: 12
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T07:41:22.604426

- Total tests: 605
- Passed: 597
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T07:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T07:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T07:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T07:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T07:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T08:06:16.086867

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T08:08:21.064205

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T08:28:05.579667

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T08:30:14.121683

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T08:31:33.743952

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T08:35:40.281523

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T08:38:41.699483

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T08:51:34.178852

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T09:33:51.516153

- Total tests: 532
- Passed: 510
- Failed: 22
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T09:35:10.947809

- Total tests: 592
- Passed: 580
- Failed: 12
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T09:41:22.604426

- Total tests: 605
- Passed: 597
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T09:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T09:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T09:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T09:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T09:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T10:06:16.086867

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T10:08:21.064205

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T10:28:05.579667

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T10:30:14.121683

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T10:31:33.743952

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T10:35:40.281523

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T10:38:41.699483

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T10:51:34.178852

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T11:33:51.516153

- Total tests: 532
- Passed: 510
- Failed: 22
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T11:35:10.947809

- Total tests: 592
- Passed: 580
- Failed: 12
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T11:41:22.604426

- Total tests: 605
- Passed: 597
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T11:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T11:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T11:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T11:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T11:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T12:06:16.086867

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T12:08:21.064205

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T12:28:05.579667

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T12:30:14.121683

- Total tests: 19
- Passed: 12
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T12:31:33.743952

- Total tests: 19
- Passed: 13
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T12:35:40.281523

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T12:38:41.699483

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T12:51:34.178852

- Total tests: 19
- Passed: 14
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T13:33:51.516153

- Total tests: 532
- Passed: 510
- Failed: 22
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T13:35:10.947809

- Total tests: 592
- Passed: 580
- Failed: 12
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T13:41:22.604426

- Total tests: 605
- Passed: 597
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T13:42:25.410643

- Total tests: 15
- Passed: 2
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T13:48:30.571564

- Total tests: 17
- Passed: 8
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T13:55:17.171783

- Total tests: 14
- Passed: 10
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T13:56:51.928848

- Total tests: 14
- Passed: 13
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-02T13:59:03.353330

- Total tests: 14
- Passed: 14
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T21:48:26.098518

- Total tests: 613
- Passed: 606
- Failed: 7
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:03:54.932651

- Total tests: 5
- Passed: 2
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-01T23:04:48.181808

- Total tests: 5
- Passed: 5
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-03T16:42:42.036731

- Total tests: 0
- Passed: 0
- Failed: 0
- Exit status: 4

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-03T16:42:53.959786

- Total tests: 3
- Passed: 3
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-03T16:43:02.139179

- Total tests: 13
- Passed: 0
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-03T16:43:12.773022

- Total tests: 5
- Passed: 0
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-04T16:10:01.383360

- Total tests: 658
- Passed: 656
- Failed: 2
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-04T16:10:33.526130

- Total tests: 0
- Passed: 0
- Failed: 0
- Exit status: 4

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-04T16:11:12.782786

- Total tests: 658
- Passed: 656
- Failed: 2
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-04T22:19:40.350888

- Total tests: 658
- Passed: 656
- Failed: 2
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-04T22:21:35.915334

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-04T22:21:47.167174

- Total tests: 658
- Passed: 656
- Failed: 2
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-05-04T23:37:50.286878

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-05-04T23:37:50.316429


## Test Session Summary - 2025-05-04T23:45:40.651130

- Total tests: 679
- Passed: 678
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-05-05T11:37:21.554935

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-05-05T11:37:21.579976


## Test Session Summary - 2025-05-05T11:40:38.625850

- Total tests: 679
- Passed: 254
- Failed: 425
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T15:25:36.257775

- Total tests: 13
- Passed: 0
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T15:27:41.361703

- Total tests: 16
- Passed: 3
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T15:29:03.734184

- Total tests: 16
- Passed: 3
- Failed: 13
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T15:29:58.202474

- Total tests: 16
- Passed: 7
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T16:07:22.525503

- Total tests: 16
- Passed: 8
- Failed: 8
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T16:08:05.141549

- Total tests: 16
- Passed: 10
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T16:09:23.999149

- Total tests: 16
- Passed: 16
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T10:20:19.346600

- Total tests: 681
- Passed: 680
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T10:33:41.708089

- Total tests: 681
- Passed: 680
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T10:34:24.241188

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T10:40:20.456507

- Total tests: 1
- Passed: 0
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T10:44:19.347645

- Total tests: 1
- Passed: 0
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T10:49:31.248060

- Total tests: 1
- Passed: 0
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T10:54:47.335896

- Total tests: 1
- Passed: 0
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T10:58:28.916078

- Total tests: 1
- Passed: 0
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-05-06T11:02:16.990379

- Total tests: 1
- Passed: 1
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-05-06T17:22:47.105555

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-05-06T17:22:47.131193

### shacl_pattern_validation
- Status: PASSED
- Details: All SHACL patterns validated successfully


## Test Session Summary - 2025-05-06T17:23:48.718528

- Total tests: 682
- Passed: 282
- Failed: 400
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-05-06T17:24:35.574941

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-05-06T17:24:35.601226

### shacl_pattern_validation
- Status: PASSED
- Details: All SHACL patterns validated successfully


## Test Session Summary - 2025-05-06T17:25:36.510415

- Total tests: 682
- Passed: 283
- Failed: 399
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-05-06T17:26:25.890897

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-05-06T17:26:25.917716

### shacl_pattern_validation
- Status: PASSED
- Details: All SHACL patterns validated successfully


## Test Session Summary - 2025-05-06T17:27:25.072075

- Total tests: 682
- Passed: 283
- Failed: 399
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-05-06T17:29:29.228401

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-05-06T17:29:29.255372

### shacl_pattern_validation
- Status: PASSED
- Details: All SHACL patterns validated successfully


## Test Session Summary - 2025-05-06T17:30:29.583790

- Total tests: 682
- Passed: 283
- Failed: 399
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests

