# Ontology Framework Test Report
Generated: 2025-04-21T03:31:49.770389
Runtime: 4.89 seconds

## Summary
- Tests Run: 120
- Failures: 41
- Errors: 29
- Skipped: 2

## Details

### Failures

#### tests.test_deployment_modeler.TestDeploymentModeler.test_load_core_ontologies_error
```
Traceback (most recent call last):
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1379, in patched
    return func(*newargs, **newkeywargs)
  File "/Users/lou/ontology-framework/tests/test_deployment_modeler.py", line 107, in test_load_core_ontologies_error
    self.assertIn("Failed to load core ontologies", log.output[0])
AssertionError: 'Failed to load core ontologies' not found in 'ERROR:ontology_framework.error_handler:Invalid error severity: HIGH'

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

#### tests.test_error_handler_root.TestErrorHandler.test_clear_errors
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 116, in test_clear_errors
    self.assertTrue(self.error_handler.has_errors())
AssertionError: False is not true

```

#### tests.test_error_handler_root.TestErrorHandler.test_error_types
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 98, in test_error_types
    self.assertIn(ErrorType.VALIDATION, error_types)
AssertionError: <ErrorType.VALIDATION: 'validation'> not found in {<ErrorType.VALIDATION: 'validation'>: 'validation', <ErrorType.RUNTIME: 'runtime'>: 'runtime', <ErrorType.CONFIGURATION: 'configuration'>: 'configuration', <ErrorType.NETWORK: 'network'>: 'network', <ErrorType.DATABASE: 'database'>: 'database', <ErrorType.FILE_SYSTEM: 'file_system'>: 'file_system', <ErrorType.MEMORY: 'memory'>: 'memory', <ErrorType.CPU: 'cpu'>: 'cpu', <ErrorType.DISK: 'disk'>: 'disk', <ErrorType.API: 'api'>: 'api', <ErrorType.AUTHENTICATION: 'authentication'>: 'authentication', <ErrorType.AUTHORIZATION: 'authorization'>: 'authorization', <ErrorType.COMPLIANCE: 'compliance'>: 'compliance', <ErrorType.SECURITY: 'security'>: 'security', <ErrorType.PERFORMANCE: 'performance'>: 'performance', <ErrorType.SCALABILITY: 'scalability'>: 'scalability', <ErrorType.AVAILABILITY: 'availability'>: 'availability', <ErrorType.RELIABILITY: 'reliability'>: 'reliability', <ErrorType.MAINTAINABILITY: 'maintainability'>: 'maintainability', <ErrorType.DATA_LOSS: 'data_loss'>: 'data_loss', <ErrorType.IO: 'io'>: 'io', <ErrorType.TEST: 'test'>: 'test'}

```

#### tests.test_error_handler_root.TestErrorHandler.test_get_errors_by_severity
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 52, in test_get_errors_by_severity
    self.assertEqual(len(high_severity_errors), 1)
AssertionError: 0 != 1

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

#### tests.test_guidance.TestGuidanceOntology.test_version_compatibility
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance.py", line 515, in test_version_compatibility
    self.fail(f"Modules have incompatible major versions: {major_versions}")
AssertionError: Modules have incompatible major versions: {'1', '0'}

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_integration_step_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 195, in test_integration_step_validation
    with self.assertRaises(ConformanceError):
AssertionError: ConformanceError not raised

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_namespace_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 160, in test_namespace_validation
    with self.assertRaises(ConformanceError):
AssertionError: ConformanceError not raised

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_ordered_step_execution
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 252, in test_ordered_step_execution
    with self.assertRaises(ConformanceError):
AssertionError: ConformanceError not raised

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_prefix_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 135, in test_prefix_validation
    with self.assertRaises(ConformanceError):
AssertionError: ConformanceError not raised

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_step_target_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 312, in test_step_target_validation
    with self.assertRaises(ConformanceError):
AssertionError: ConformanceError not raised

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_step_type_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 282, in test_step_type_validation
    with self.assertRaises(ConformanceError):
AssertionError: ConformanceError not raised

```

#### tests.test_deployment.TestDeployment.test_dataset_existence
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_deployment.py", line 222, in test_dataset_existence
    self.assertEqual(response.status_code, 200, "Dataset not found")
AssertionError: 404 != 200 : Dataset not found

```

#### tests.test_deployment.TestDeployment.test_dataset_exists
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_deployment.py", line 98, in test_dataset_exists
    self.assertEqual(
AssertionError: '404' != '200'
- 404
+ 200
 : Dataset check failed

```

### Errors

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
AttributeError: <ontology_framework.manage_models.ModelManager object at 0x12133ebc0> does not have the attribute 'check_model_quality'

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

#### tests.test_error_handler_root.TestErrorHandler.test_add_error
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 26, in test_add_error
    ErrorStep.IDENTIFICATION,
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/enum.py", line 437, in __getattr__
    raise AttributeError(name) from None
AttributeError: IDENTIFICATION. Did you mean: 'NOTIFICATION'?

```

#### tests.test_error_handler_root.TestErrorHandler.test_error_steps
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 91, in test_error_steps
    self.assertEqual(self.error_handler.get_current_step(), ErrorStep.IDENTIFICATION)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/enum.py", line 437, in __getattr__
    raise AttributeError(name) from None
AttributeError: IDENTIFICATION. Did you mean: 'NOTIFICATION'?

```

#### tests.test_error_handler_root.TestErrorHandler.test_validate_compliance
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 83, in test_validate_compliance
    "compliance_level": ComplianceLevel.FULL
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/enum.py", line 437, in __getattr__
    raise AttributeError(name) from None
AttributeError: FULL

```

#### tests.test_error_handler_root.TestErrorHandler.test_validate_matrix
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 59, in test_validate_matrix
    self.assertTrue(self.error_handler.validate(ValidationRule.MATRIX, valid_data))
AttributeError: type object 'ValidationRule' has no attribute 'MATRIX'

```

#### tests.test_error_handler_root.TestErrorHandler.test_validate_risk_assessment
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 66, in test_validate_risk_assessment
    self.assertTrue(self.error_handler.validate(ValidationRule.RISK_ASSESSMENT, valid_data))
AttributeError: type object 'ValidationRule' has no attribute 'RISK_ASSESSMENT'

```

#### tests.test_error_handler_root.TestErrorHandler.test_validate_sensitive_data
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 76, in test_validate_sensitive_data
    self.assertTrue(self.error_handler.validate(ValidationRule.SENSITIVE_DATA, valid_data))
AttributeError: type object 'ValidationRule' has no attribute 'SENSITIVE_DATA'

```

#### tests.test_error_handler_root.TestErrorHandler.test_validation_rules
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_error_handler_root.py", line 105, in test_validation_rules
    self.assertIn(ValidationRule.MATRIX, rules)
AttributeError: type object 'ValidationRule' has no attribute 'MATRIX'

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
  File "/Users/lou/ontology-framework/tests/test_sparql_client.py", line 38, in setUpClass
    cls.client = SparqlClient(
TypeError: SparqlClient.__init__() got an unexpected keyword argument 'auth'

```

#### tests.test_guidance_conformance.TestGuidanceConformance.test_conformance_level_validation
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_guidance_conformance.py", line 111, in test_conformance_level_validation
    self.integrator.set_conformance_level("INVALID")
  File "/Users/lou/ontology-framework/src/ontology_framework/spore_integration.py", line 70, in set_conformance_level
    raise ValueError(f"Invalid conformance level: {level}. Must be one of {valid_levels}")
ValueError: Invalid conformance level: INVALID. Must be one of {'MODERATE', 'STRICT', 'RELAXED'}

```

#### tests.test_session_update.TestSessionUpdate.test_session_update_rdflib_terms
```
Traceback (most recent call last):
  File "/Users/lou/ontology-framework/tests/test_session_update.py", line 28, in test_session_update_rdflib_terms
    update_session_ttl(ontology_info, model_name, session_file=self.test_session_file)
TypeError: update_session_ttl() got an unexpected keyword argument 'session_file'

```

## Test Run - 2025-04-21T03:33:29.173343

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-04-21T03:33:29.201117


## Test Session Summary - 2025-04-21T03:33:50.439915

- Total tests: 327
- Passed: 127
- Failed: 200
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T03:34:32.718170

- Total tests: 5
- Passed: 5
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T03:36:06.792512

- Total tests: 7
- Passed: 0
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T03:36:45.847180

- Total tests: 7
- Passed: 3
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T03:40:54.242585

- Total tests: 7
- Passed: 3
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T03:41:59.222560

- Total tests: 7
- Passed: 3
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T03:43:48.758389

- Total tests: 7
- Passed: 3
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T07:15:36.965299

- Total tests: 7
- Passed: 0
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T07:17:17.019365

- Total tests: 7
- Passed: 3
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-04-21T07:38:29.324736

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-04-21T07:38:29.355542


## Test Session Summary - 2025-04-21T07:39:09.052323

- Total tests: 341
- Passed: 128
- Failed: 213
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:33.182347

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:33.182577

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:33.186054

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:33.189133

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:34.924040

- Total tests: 0
- Passed: -4
- Failed: 4
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:56.736167

- Total tests: 7
- Passed: 5
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:56.736167

- Total tests: 7
- Passed: 5
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:56.739183

- Total tests: 7
- Passed: 5
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:57.148600

- Total tests: 7
- Passed: 6
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:13:58.430779

- Total tests: 7
- Passed: 0
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:15:07.229788

- Total tests: 7
- Passed: 6
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:15:07.268535

- Total tests: 7
- Passed: 5
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:15:07.280954

- Total tests: 7
- Passed: 5
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:15:07.282265

- Total tests: 7
- Passed: 5
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T08:15:08.569844

- Total tests: 7
- Passed: 0
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T10:21:35.730331

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T10:22:36.731485

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T12:30:54.327705

- Total tests: 0
- Passed: 0
- Failed: 0
- Exit status: 4

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-21T12:34:39.584176

- Total tests: 15
- Passed: 8
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests

