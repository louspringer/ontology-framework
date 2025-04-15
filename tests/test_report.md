# Ontology Framework Test Report
Generated: 2025-04-15T09:25:03.083873
Runtime: 17.82 seconds

## Summary
- Tests Run: 116
- Failures: 39
- Errors: 7
- Skipped: 0

## Details

### Failures

#### tests.test_conformance_tracking.TestConformanceTracker.test_resolve_violation
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_conformance_tracking.py", line 95, in test_resolve_violation
    self.assertTrue((violation, META.resolvedAt, None) not in self.tracker.graph)
AssertionError: False is not true

```

#### tests.test_sparql_patterns.TestSPARQLPatterns.test_property_cardinality
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_sparql_patterns.py", line 105, in test_property_cardinality
    self.assertEqual(len(violations), 0, f"Found {len(violations)} cardinality violations")
AssertionError: 3 != 0 : Found 3 cardinality violations

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_compliance_standards_validation
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 1328, in test_compliance_standards_validation
    self.assertTrue(
AssertionError: False is not true : Missing compliance standard: ISO27001

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_enhanced_confusion_matrix_validation
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 1009, in test_enhanced_confusion_matrix_validation
    self.assertTrue(self.graph.query(query).askAnswer,
AssertionError: False is not true : Missing basic matrix validation rules

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_classification_accuracy
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 923, in test_error_classification_accuracy
    self.assertTrue(len(results) > 0, "No confusion matrices found")
AssertionError: False is not true : No confusion matrices found

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_documentation_requirements
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 365, in test_error_documentation_requirements
    self.assertIn(doc, found_docs, f"Missing required documentation: {doc}")
AssertionError: 'ErrorReport' not found in {} : Missing required documentation: ErrorReport

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_assumptions
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 698, in test_error_handling_assumptions
    self.assertIn(assumption, found_assumptions,
AssertionError: 'ErrorTypeExclusivity' not found in {} : Missing required assumption: ErrorTypeExclusivity

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_compliance
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 615, in test_error_handling_compliance
    self.assertIn(standard, found_standards, f"Missing compliance standard: {standard}")
AssertionError: 'ISO27001' not found in {} : Missing compliance standard: ISO27001

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_constraints
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 739, in test_error_handling_constraints
    self.assertIn(constraint, found_constraints,
AssertionError: 'ResourceConstraint' not found in {} : Missing required constraint: ResourceConstraint

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_integration
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 434, in test_error_handling_integration
    self.assertTrue(self.graph.query(query).askAnswer,
AssertionError: False is not true : Missing monitoring integration validation

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_metrics
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 334, in test_error_handling_metrics
    self.assertIn(metric, found_metrics, f"Missing required metric: {metric}")
AssertionError: 'ErrorCount' not found in {} : Missing required metric: ErrorCount

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_performance
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 568, in test_error_handling_performance
    self.assertIn(metric, found_metrics, f"Missing performance metric: {metric}")
AssertionError: 'LoggingLatency' not found in {} : Missing performance metric: LoggingLatency

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_process
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 174, in test_error_handling_process
    self.assertEqual(len(results), 4, "Standard error handling should have 4 steps")
AssertionError: 0 != 4 : Standard error handling should have 4 steps

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_risks
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 664, in test_error_handling_risks
    self.assertIn(risk, found_risks, f"Missing required risk: {risk}")
AssertionError: 'DataLossRisk' not found in {} : Missing required risk: DataLossRisk

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_security
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 391, in test_error_handling_security
    self.assertTrue(self.graph.query(query).askAnswer,
AssertionError: False is not true : Missing sensitive data handling validation

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_steps
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 123, in test_error_handling_steps
    self.assertIn(order, found_steps, f"Missing step order: {order}")
AssertionError: 1 not found in {} : Missing step order: 1

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_traceability
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 834, in test_error_handling_traceability
    self.assertIn(test_case, found_test_cases,
AssertionError: 'ErrorTypeTestCase' not found in {} : Missing required test case: ErrorTypeTestCase

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_handling_validation
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 781, in test_error_handling_validation
    self.assertIn(validation, found_validations,
AssertionError: 'RiskValidation' not found in {} : Missing required validation: RiskValidation

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_prevention_measures
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 516, in test_error_prevention_measures
    self.assertTrue(len(results) > 0, "No prevention measures found")
AssertionError: False is not true : No prevention measures found

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_property_validation
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 284, in test_error_property_validation
    self.assertTrue(self.graph.query(query).askAnswer,
AssertionError: False is not true : Missing severity property validation

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_recovery_strategy
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 476, in test_error_recovery_strategy
    self.assertTrue(len(results) > 0, "No recovery strategies found")
AssertionError: False is not true : No recovery strategies found

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_type_hierarchy
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 247, in test_error_type_hierarchy
    self.assertTrue(len(results) > 0, "No error type hierarchies found")
AssertionError: False is not true : No error type hierarchies found

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_error_types
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 96, in test_error_types
    self.assertIn(type_name, found_types, f"Missing error type: {type_name}")
AssertionError: 'Validation Error' not found in {} : Missing error type: Validation Error

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_test_error_handling_process
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 211, in test_test_error_handling_process
    self.assertEqual(len(results), 4, "Standard test error handling should have 4 steps")
AssertionError: 0 != 4 : Standard test error handling should have 4 steps

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_test_error_handling_steps
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 150, in test_test_error_handling_steps
    self.assertIn(order, found_steps, f"Missing test step order: {order}")
AssertionError: 1 not found in {} : Missing test step order: 1

```

#### tests.test_runtime_error_handling.TestRuntimeErrorHandling.test_validation_rules_compliance
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_runtime_error_handling.py", line 1287, in test_validation_rules_compliance
    self.assertTrue(
AssertionError: False is not true : Missing validation rule: SensitiveDataValidation

```

#### tests.test_guidance.TestGuidanceOntology.test_module_registry_completeness
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_guidance.py", line 78, in test_module_registry_completeness
    self.assertEqual(count, 5, f"Should have exactly 5 registered modules, found {count}")
AssertionError: 8 != 5 : Should have exactly 5 registered modules, found 8

```

#### tests.test_guidance.TestGuidanceOntology.test_shacl_constraints
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_guidance.py", line 173, in test_shacl_constraints
    self.fail(f"SHACL validation failed:\n{results_text}")
AssertionError: SHACL validation failed:
Validation Report
Conforms: False
Results (3):
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: [ sh:datatype xsd:string ; sh:message Literal("All modules must have version information") ; sh:minCount Literal("1", datatype=xsd:integer) ; sh:path owl:versionInfo ]
	Focus Node: sparql:SparqlServiceModule
	Result Path: owl:versionInfo
	Message: All modules must have version information
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: [ sh:datatype xsd:string ; sh:message Literal("All modules must have version information") ; sh:minCount Literal("1", datatype=xsd:integer) ; sh:path owl:versionInfo ]
	Focus Node: env:EnvironmentModule
	Result Path: owl:versionInfo
	Message: All modules must have version information
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: [ sh:datatype xsd:string ; sh:message Literal("All modules must have version information") ; sh:minCount Literal("1", datatype=xsd:integer) ; sh:path owl:versionInfo ]
	Focus Node: deploy:DeploymentValidationModule
	Result Path: owl:versionInfo
	Message: All modules must have version information


```

#### tests.test_sparql_client.TestSparqlClient.test_create_dataset
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_sparql_client.py", line 70, in setUp
    self.assertTrue(self.client.create_dataset(self.test_dataset))
AssertionError: False is not true

```

#### tests.test_sparql_client.TestSparqlClient.test_delete_dataset
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_sparql_client.py", line 70, in setUp
    self.assertTrue(self.client.create_dataset(self.test_dataset))
AssertionError: False is not true

```

#### tests.test_sparql_client.TestSparqlClient.test_execute_query
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_sparql_client.py", line 70, in setUp
    self.assertTrue(self.client.create_dataset(self.test_dataset))
AssertionError: False is not true

```

#### tests.test_sparql_client.TestSparqlClient.test_load_ontology
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_sparql_client.py", line 70, in setUp
    self.assertTrue(self.client.create_dataset(self.test_dataset))
AssertionError: False is not true

```

#### tests.test_sparql_client.TestSparqlClient.test_validate_ontology
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_sparql_client.py", line 70, in setUp
    self.assertTrue(self.client.create_dataset(self.test_dataset))
AssertionError: False is not true

```

#### tests.test_patch_management.TestPatchManagement.test_patch_application
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_patch_management.py", line 114, in test_patch_application
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_patch_management.TestPatchManagement.test_patch_dependencies
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_patch_management.py", line 150, in test_patch_dependencies
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_patch_management.TestPatchManagement.test_patch_rollback
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_patch_management.py", line 132, in test_patch_rollback
    self.assertTrue(result)
AssertionError: False is not true

```

#### tests.test_patch_management.TestPatchManagement.test_patch_validation
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_patch_management.py", line 186, in test_patch_validation
    with self.assertRaises(ValueError):
AssertionError: ValueError not raised

```

#### tests.test_spore_integration.TestSporeIntegration.test_concurrent_integration
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_spore_integration.py", line 141, in test_concurrent_integration
    with self.assertRaises(ConcurrentModificationError):
AssertionError: ConcurrentModificationError not raised

```

#### tests.test_spore_integration.TestSporeIntegration.test_model_compatibility_check
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_spore_integration.py", line 104, in test_model_compatibility_check
    self.assertTrue(result)
AssertionError: False is not true

```

### Errors

#### tests.test_conformance_tracking.TestConformanceTracker.test_error_handling
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/src/ontology_framework/conformance_tracking.py", line 372, in export_violations
    raise ValueError("Output path cannot be None")
ValueError: Output path cannot be None

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_conformance_tracking.py", line 258, in test_error_handling
    self.tracker.export_violations(None)
  File "/Users/lou/Documents/ontology-framework/src/ontology_framework/conformance_tracking.py", line 385, in export_violations
    self.logger.error(f"Failed to export violations: {str(e)}",
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/logging/__init__.py", line 1506, in error
    self._log(ERROR, msg, args, **kwargs)
TypeError: Logger._log() got an unexpected keyword argument 'context'

```

#### tests.test_error_handling.TestErrorHandling.test_error_handling_structure
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_error_handling.py", line 37, in setUp
    self.error_handling_query = prepareQuery("""
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/processor.py", line 32, in prepareQuery
    ret = translateQuery(parseQuery(queryString), base, initNs)
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

#### tests.test_error_handling.TestErrorHandling.test_error_trap_validation
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_error_handling.py", line 37, in setUp
    self.error_handling_query = prepareQuery("""
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/processor.py", line 32, in prepareQuery
    ret = translateQuery(parseQuery(queryString), base, initNs)
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

#### tests.test_error_handling.TestErrorHandling.test_fix_cycle_completeness
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_error_handling.py", line 37, in setUp
    self.error_handling_query = prepareQuery("""
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/processor.py", line 32, in prepareQuery
    ret = translateQuery(parseQuery(queryString), base, initNs)
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

#### tests.test_manage_models.TestModelManager.test_shacl_validation
```
Traceback (most recent call last):
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/unittest/mock.py", line 1379, in patched
    return func(*newargs, **newkeywargs)
  File "/Users/lou/Documents/ontology-framework/tests/test_manage_models.py", line 519, in test_shacl_validation
    result = self.manager.validate_model("test_model")
  File "/Users/lou/Documents/ontology-framework/src/ontology_framework/manage_models.py", line 555, in validate_model
    self.validate_model_projection(model_path)
  File "/Users/lou/Documents/ontology-framework/src/ontology_framework/manage_models.py", line 460, in validate_model_projection
    model_graph.parse(model_path, format="turtle")
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1507, in parse
    source = create_input_source(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 735, in create_input_source
    ) = _create_input_source_from_location(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/parser.py", line 795, in _create_input_source_from_location
    file = open(filename, "rb")
IsADirectoryError: [Errno 21] Is a directory: '/Users/lou/Documents/test_model'

```

#### tests.test_spore_integration.TestSporeIntegration.test_error_handling
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_spore_integration.py", line 198, in test_error_handling
    self.integrator.apply_patch(self.test_spore, None, self.target_model)
TypeError: SporeIntegrator.apply_patch() missing 1 required positional argument: 'version'

```

#### tests.test_spore_integration.TestSporeIntegration.test_patch_application
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_spore_integration.py", line 121, in test_patch_application
    result = self.integrator.apply_patch(self.test_spore, patch, self.target_model)
TypeError: SporeIntegrator.apply_patch() missing 1 required positional argument: 'version'

```
