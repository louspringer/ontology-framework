# Namespace Usage Pattern Analysis
Generated: 2025-04-17T18:45:57.531595

## Usage Statistics

### Python Files

#### Namespace Declaration
- boldo_content_enricher.py: http://example.org/boldo#
- boldo_content_enricher.py: http://example.org/boldo/structure#
- boldo_structural_scraper.py: http://example.org/boldo#
- conformance_tracking.py: http://example.org/guidance#
- ontology_framework/conformance_tracking.py: http://example.org/test#
- ontology_framework/conformance_tracking.py: http://example.org/violations#
- ontology_framework/jena_client.py: http://example.org/guidance#
- ontology_framework/manage_models.py: http://example.org/guidance#
- ontology_framework/manage_models.py: http://example.org/meta#
- ontology_framework/manage_models.py: http://example.org/model#
- ontology_framework/meta.py: http://example.org/guidance/modules/patch#
- ontology_framework/patch_management.py: http://example.org/patch#
- ontology_framework/sparql_client.py: http://example.org/guidance#
- ontology_framework/spore_integration.py: http://example.org/guidance#
- ontology_framework/spore_integration.py: http://example.org/spore#
- ontology_framework/spore_integration.py: http://example.org/test#
- ontology_framework/spore_validation.py: http://example.org/guidance#
- patch_management.py: http://example.org/guidance#
- scripts/add_missing_metadata.py: http://example.org/guidance#
- scripts/add_missing_metadata.py: http://example.org/tracking#
- scripts/add_missing_metadata.py: http://example.org/validation#
- scripts/load_ontology_tracking.py: http://example.org/ontology_tracking#
- scripts/ontology_validation.py: http://example.org/tracking#
- scripts/ontology_validation.py: http://example.org/validation#
- scripts/validate_graphdb.py: http://example.org/guidance#
- scripts/validate_graphdb.py: http://example.org/tracking#
- scripts/validate_graphdb.py: http://example.org/validation#
- spore_integration.py: http://example.org/guidance#
- tests/conftest.py: http://example.org/test#
- tests/test_checkin_manager.py: http://example.org/error#
- tests/test_checkin_manager.py: http://example.org/test#
- tests/test_conformance_tracking.py: http://example.org/test#
- tests/test_deployment.py: http://example.org/guidance#
- tests/test_error_handling.py: http://example.org/test#
- tests/test_guidance_conformance.py: http://example.org/guidance#
- tests/test_guidance_conformance.py: http://example.org/test#
- tests/test_manage_models.py: http://example.org/test#
- tests/test_patch_manager.py: http://example.org/patch#
- tests/test_runtime_error_handling.py: http://example.org/guidance#
- tests/test_sparql_client.py: http://example.org/guidance#
- tests/test_spore_integration.py: http://example.org/guidance#
- tests/test_spore_integration.py: http://example.org/test#

#### Test Data
- ontology_framework/conformance_tracking.py: example.org/test
- ontology_framework/spore_integration.py: example.org/test
- test_checkin.py: example.org/test
- test_rdf_setup.py: example.org/test
- tests/conftest.py: example.org/test
- tests/test_checkin_manager.py: example.org/test
- tests/test_conformance_tracking.py: example.org/test
- tests/test_error_handling.py: example.org/test
- tests/test_find_example_org.py: example.org/test
- tests/test_graphdb_patch_manager.py: example.org/test
- tests/test_guidance_conformance.py: example.org/test
- tests/test_manage_models.py: example.org/test
- tests/test_patch_management.py: example.org/test
- tests/test_patch_manager.py: example.org/test
- tests/test_sparql_operations.py: example.org/test
- tests/test_spore_integration.py: example.org/test

#### Prefix Definition
- tests/test_graphdb_patch_manager.py: http://example.org/patch#
- tests/test_guidance_conformance.py: http://example.org/guidance#
- tests/test_guidance_conformance.py: http://example.org/test#
- tests/test_manage_models.py: http://example.org/test#
- tests/test_patch_management.py: http://example.org/patch#
- tests/test_spore_integration.py: http://example.org/test#

### Ontology Files

#### Prefix Definition
- guidance/modules/deployment.ttl: http://example.org/guidance#
- guidance/modules/deployment_test.ttl: http://example.org/guidance#
- guidance/modules/sparql_operations.ttl: http://example.org/guidance#
- guidance/modules/spore_management.ttl: http://example.org/guidance#
- guidance/modules/test_error_plan.ttl: http://example.org/guidance#
- guidance/modules/testing.ttl: http://example.org/guidance#

#### Test Data
- tests/test_data/test_ontology.ttl: example.org/test

### Documentation Files

## Migration Strategies

### Ontology Files
- 1. Update prefix declarations to use new namespace
- 2. Update all entity IRIs
- 3. Update imports if present
- 4. Validate ontology after migration
- 5. Update any dependent ontologies

### Python Files
- 1. Update Namespace declarations
- 2. Update test data URIs
- 3. Update configuration references
- 4. Run test suite to verify changes
- 5. Update any import statements

## Recommendations
1. Start migration with files having fewest dependencies
2. Implement automated validation for each category
3. Create backup of each file before migration
4. Update CI/CD pipeline to validate new namespace usage
5. Document all changes in migration log