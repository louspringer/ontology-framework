# Example.org Usage Inventory
Generated: 2025-04-17T17:45:38.508445

## README.md
Line 35: spore_uri = "http://example.org/spores/example-spore"

## artifact-representation-rule.ttl
Line 1: @prefix meta: <http:/example.org/meta#> .

## audio_deployment_ontology.ttl
Line 1: @prefix : <http:/example.org/audioOntology#> .

## boldo_content_enricher.py
Line 18: EX = Namespace("http://example.org/boldo#")
Line 19: STRUCT = Namespace("http://example.org/boldo/structure#")

## boldo_structural_scraper.py
Line 36: EX = Namespace("http://example.org/boldo#")

## boldo_structure.ttl
Line 1: @prefix ex: <http:/example.org/boldo#> .

## boldo_structure_enriched.ttl
Line 1: @prefix ex: <http:/example.org/boldo#> .

## bow-tie-transformation.ttl
Line 1: @prefix bt: <http:/example.org/bow-tie-pattern#> .
Line 2: @prefix ex: <http:/example.org/bow-tie-examples#> .
Line 140: owl:versionIRI <http:/example.org/bow-tie-examples#JPEGCompression-1.0.0> ;
Line 141: owl:priorVersion <http:/example.org/bow-tie-examples#JPEGCompression-0.9.0> ;
Line 142: owl:backwardCompatibleWith <http:/example.org/bow-tie-examples#JPEGCompression-0.9.0> ;
Line 163: owl:versionIRI <http:/example.org/bow-tie-examples#NeuralNetworkPruning-1.0.0> ;
Line 164: owl:priorVersion <http:/example.org/bow-tie-examples#NeuralNetworkPruning-0.9.0> ;
Line 165: owl:backwardCompatibleWith <http:/example.org/bow-tie-examples#NeuralNetworkPruning-0.9.0> ;
Line 186: owl:versionIRI <http:/example.org/bow-tie-examples#TextSummarization-1.0.0> ;
Line 187: owl:priorVersion <http:/example.org/bow-tie-examples#TextSummarization-0.9.0> ;
Line 188: owl:backwardCompatibleWith <http:/example.org/bow-tie-examples#TextSummarization-0.9.0> ;

## cognitive_automata.ttl
Line 10: @prefix cog: <http:/example.org/cognitive-automata#> .

## conformance_tracking.py
Line 10: META = Namespace("http://example.org/guidance#")
Line 27: violation = URIRef(f"http://example.org/violations/{label.lower().replace(' ', '-')}")

## creative_analogies.ttl
Line 1: @prefix : <http:/example.org/creative_analogies#> .

## docs/namespace_recovery_plan.md
Line 24: | ANAL-001 | Inventory all files using example.org | HIGH | IN_PROGRESS | Ontology Team | 16 | Complete list of all files using example.org with line numbers and context | 2 team members, 2 days | None | R1 |

## documentation_scraping.ttl
Line 1: @prefix ns1: <http:/example.org/documentation#> .

## finite_automaton_infinite_world.ttl
Line 1: @prefix ex: <http:/example.org/speculation#> .

## guidance/modules/deployment.ttl
Line 4: @prefix ns1: <http://example.org/guidance#> .

## guidance/modules/deployment_test.ttl
Line 4: @prefix ns1: <http://example.org/guidance#> .

## guidance/modules/deployment_validation.ttl
Line 183: <http://example.org/resource> a <http://example.org/Class> .
Line 203: <http://example.org/resource> ?p ?o .
Line 223: <http://example.org/resource> ?p ?o .
Line 242: DELETE { <http://example.org/resource> ?p ?o }
Line 243: INSERT { <http://example.org/resource> ?p ?newValue }
Line 245: <http://example.org/resource> ?p ?o .

## guidance/modules/runtime_error_handling.ttl
Line 275: <http://example.org/error-handling#OntologyFramework#ModuleShape> a sh:NodeShape ;
Line 278: sh:path <http://example.org/error-handling#OntologyFramework#label>  .
Line 281: sh:path <http://example.org/error-handling#OntologyFramework#version>  .
Line 284: sh:path <http://example.org/error-handling#OntologyFramework#description> ;
Line 285: sh:targetClass <http://example.org/error-handling#OntologyFramework#Module> .

## guidance/modules/sparql_operations.ttl
Line 4: @prefix ns1: <http://example.org/guidance#> .

## guidance/modules/spore_management.ttl
Line 7: @prefix meta: <http://example.org/guidance#> .

## guidance/modules/test_error_plan.ttl
Line 4: @prefix ns1: <http://example.org/guidance#> .

## guidance/modules/testing.ttl
Line 6: @prefix ns1: <http://example.org/guidance#> .

## langgraph.ttl
Line 31: ###  http://example.org/langgraph#connectsNode
Line 44: ###  http://example.org/langgraph#hasType
Line 52: ###  http://example.org/langgraph#hasWeight
Line 64: ###  http://example.org/langgraph#Edge
Line 70: ###  http://example.org/langgraph#Node
Line 80: ###  http://example.org/langgraph#Edge1
Line 88: ###  http://example.org/langgraph#Edge2
Line 94: ###  http://example.org/langgraph#Edge3
Line 100: ###  http://example.org/langgraph#Node1
Line 105: ###  http://example.org/langgraph#Node2
Line 110: ###  http://example.org/langgraph#Node3
Line 115: ###  http://example.org/langgraph#Node4

## models/recovery_plan.md
Line 38: Status: Implemented example.org inventory script and tests, CLI tool delivered, validation pipeline in place.
Line 42: ### ANAL-001: Inventory all files using "example.org"

## models/recovery_plan.ttl
Line 26: rdfs:label "Has example.org usage" ;
Line 27: rdfs:comment "Indicates if example.org is being used" .
Line 55: recovery:hasStepDescription "Identify all files using example.org" .
Line 107: rdfs:comment "Add CI/CD validation for example.org usage" .
Line 124: recovery:hasProblemDescription "Incorrect usage of example.org in production code instead of relative paths, causing validation failures and potential security risks" .
Line 631: recovery:hasTaskDescription "Inventory all files using example.org" ;
Line 636: recovery:hasCompletionCriteria "Complete list of all files using example.org with line numbers and context" ;

## oci.ttl
Line 2: @prefix : <http:/example.org/ontology#> .
Line 3: @prefix dialog: <http:/example.org/dialog#> .
Line 180: owl:imports <http:/example.org/meta-core#> .

## ontology_analysis_plan.ttl
Line 78: rdfs:comment "Move all cognitive domain prefixes to use relative paths (./prefix#) instead of http://example.org/" .

## ontology_framework/conformance_tracking.py
Line 15: TEST = Namespace("http://example.org/test#")
Line 16: VIOLATIONS = Namespace("http://example.org/violations#")
Line 104: violation = URIRef(f"http://example.org/violations/{violation_id}")

## ontology_framework/error_handling.py
Line 40: error_uri = URIRef(f"http://example.org/errors/{self.value}")

## ontology_framework/graphdb_client.py
Line 146: context = context or "<http://example.org/default>"

## ontology_framework/jena_client.py
Line 27: self.ns1 = Namespace("http://example.org/guidance#")

## ontology_framework/manage_models.py
Line 30: GUIDANCE = Namespace("http://example.org/guidance#")
Line 31: META = Namespace("http://example.org/meta#")
Line 32: MODEL = Namespace("http://example.org/model#")

## ontology_framework/meta.py
Line 7: META = Namespace("http://example.org/guidance/modules/patch#")

## ontology_framework/namespace_recovery.py
Line 17: description="Identify all files using example.org and relative paths",

## ontology_framework/namespace_recovery/find_example_org.py
Line 2: """Script to find all files using example.org."""
Line 19: """Finds files using example.org in the codebase."""
Line 28: """Find example.org usage in a single file."""
Line 40: """Find example.org usage in RDF files."""
Line 46: if isinstance(s, URIRef) and 'example.org' in str(s):
Line 48: if isinstance(p, URIRef) and 'example.org' in str(p):
Line 50: if isinstance(o, URIRef) and 'example.org' in str(o):
Line 57: """Scan the directory for files using example.org."""
Line 73: logger.info(f"Found example.org usage in {file_path}")
Line 93: logger.info("Starting scan for example.org usage...")
Line 103: logger.info(f"Found {len(finder.results)} files using example.org")

## ontology_framework/namespace_recovery_test.py
Line 41: # Document the example.org finding
Line 44: "issue": "Using absolute URIs with example.org instead of relative URIs",

## ontology_framework/patch_management.py
Line 30: PATCH = Namespace("http://example.org/patch#")

## ontology_framework/prefix_map.py
Line 87: elif uri_str.startswith('http://example.org/') or uri_str.startswith('http://louspringer.com/'):
Line 88: # Replace example.org or louspringer.com with ontologies.louspringer.com

## ontology_framework/sparql_client.py
Line 22: NS1 = Namespace("http://example.org/guidance#")
Line 269: PREFIX meta: <http://example.org/guidance/meta#>

## ontology_framework/sparql_operations.py
Line 85: "meta": "http://example.org/guidance/meta#"

## ontology_framework/spore_integration.py
Line 18: META = Namespace("http://example.org/guidance#")
Line 19: GUIDANCE = Namespace("http://example.org/guidance#")
Line 20: TEST = Namespace("http://example.org/test#")
Line 21: SPORE = Namespace("http://example.org/spore#")

## ontology_framework/spore_validation.py
Line 10: META = Namespace("http://example.org/guidance#")
Line 142: spore_uri = "http://example.org/spores/example-spore"

## patch_management.py
Line 11: META = Namespace("http://example.org/guidance#")

## scripts/add_missing_metadata.py
Line 17: TRACK = Namespace("http://example.org/tracking#")
Line 18: VALID = Namespace("http://example.org/validation#")
Line 19: GUIDE = Namespace("http://example.org/guidance#")

## scripts/deploy.py
Line 45: PREFIX ns1: <http://example.org/guidance#>

## scripts/import_ontologies.py
Line 42: "meta": "http://example.org/meta#",
Line 43: "core": "http://example.org/core#",
Line 44: "model": "http://example.org/model#"

## scripts/inventory_example_org.py
Line 26: """Scan a single file for example.org usage."""
Line 38: """Scan all files in the directory for example.org usage."""
Line 44: """Generate a report of all example.org usage."""
Line 67: logging.info("Starting example.org usage inventory...")

## scripts/load_guidance_ontology.py
Line 49: owlim:base-URL "http://example.org/"

## scripts/load_ontology_tracking.py
Line 22: TRACKING = Namespace("http://example.org/ontology_tracking#")

## scripts/load_patch_ontology.py
Line 49: owlim:base-URL "http://example.org/"
Line 77: turtle_data = g.serialize(format="turtle", base="http://example.org/ontology/")

## scripts/ontology_validation.py
Line 32: TRACKING = Namespace("http://example.org/tracking#")
Line 33: VAL = Namespace("http://example.org/validation#")
Line 294: PREFIX val: <http://example.org/validation#>
Line 295: PREFIX tracking: <http://example.org/tracking#>

## scripts/validate_graphdb.py
Line 23: TRACKING = Namespace("http://example.org/tracking#")
Line 24: VALIDATION = Namespace("http://example.org/validation#")
Line 25: GUIDANCE = Namespace("http://example.org/guidance#")
Line 253: PREFIX tracking: <http://example.org/tracking#>

## session.ttl
Line 1: @prefix bt: <http:/example.org/bow-tie-pattern#> .
Line 2: @prefix ex: <http:/example.org/bow-tie-examples#> .

## spore-xna-governance.ttl
Line 1: @prefix meta: <http:/example.org/guidance#> .

## spore_integration.py
Line 11: META = Namespace("http://example.org/guidance#")

## sraper-requirements.ttl
Line 1: @prefix : <http:/example.org/boldo/requirements#> .
Line 2: @prefix ex: <http:/ontology-framework.example.org/requirements#> .
Line 3: @prefix guidance: <http:/ontology-framework.example.org/guidance#> .

## src/api/documentation_scraper.py
Line 198: result_uri = URIRef("http://example.org/documentation#ScrapingResult")
Line 201: self.graph.add((result_uri, URIRef("http://example.org/documentation#resultStatus"),
Line 203: self.graph.add((result_uri, URIRef("http://example.org/documentation#resultContent"),
Line 231: result_uri = URIRef("http://example.org/documentation#ScrapingResult")
Line 234: self.graph.add((result_uri, URIRef("http://example.org/documentation#resultStatus"),
Line 236: self.graph.add((result_uri, URIRef("http://example.org/documentation#resultContent"),
Line 347: doc = Namespace('http://example.org/documentation#')

## test_checkin.py
Line 41: target_ontology="http://example.org/ontology",
Line 46: subject="http://example.org/test",
Line 47: predicate="http://example.org/hasValue",

## test_rdf_direct.py
Line 46: VALUES (1, 'http://example.org/subject',
Line 47: 'http://example.org/predicate',
Line 48: 'http://example.org/object')

## test_rdf_model.py
Line 71: 'http://example.org/subject',
Line 72: 'http://example.org/predicate',
Line 73: 'http://example.org/object')

## test_rdf_network.py
Line 104: 'http://example.org/person1',
Line 105: 'http://example.org/name',
Line 112: 'http://example.org/person1',
Line 113: 'http://example.org/age',

## test_rdf_setup.py
Line 58: '<http://example.org/test>',
Line 60: '<http://example.org/TestClass>',

## test_rdflib.py
Line 14: rdflib.URIRef("http://example.org/subject"),
Line 15: rdflib.URIRef("http://example.org/predicate"),

## test_spore_validation.py
Line 8: self.test_spore = URIRef("http://example.org/spores/test-spore")
Line 22: shape = URIRef("http://example.org/shapes/test-shape")
Line 32: patch = URIRef("http://example.org/patches/test-patch")
Line 42: violation = URIRef("http://example.org/violations/test-violation")

## tests/conftest.py
Line 49: return Namespace("http://example.org/test#")

## tests/test_abematv.py
Line 62: cls.g.bind('security', Namespace('http://example.org/security#'))
Line 67: security = Namespace('http://example.org/security#')

## tests/test_checkin_manager.py
Line 40: TEST = Namespace("http://example.org/test#")
Line 41: ERROR = Namespace("http://example.org/error#")
Line 79: PREFIX process: <http://example.org/process#>

## tests/test_conformance_tracking.py
Line 25: TEST = Namespace("http://example.org/test#")

## tests/test_data/test_ontology.ttl
Line 5: @prefix test: <http:/example.org/test#> .
Line 6: @prefix error: <http:/example.org/error#> .

## tests/test_deployment.py
Line 23: NS1 = Namespace("http://example.org/guidance#")
Line 43: PREFIX ns1: <http://example.org/guidance#>
Line 60: PREFIX ns1: <http://example.org/guidance#>

## tests/test_error_handling.py
Line 29: TEST = Namespace("http://example.org/test#")

## tests/test_example_org_inventory.py
Line 7: """Test scanning a single file for example.org usage."""
Line 10: @prefix ex: <http://example.org/> .
Line 23: assert "example.org" in inventory.results[str(f.name)][0][1]  # Line content
Line 28: """Test scanning a directory for example.org usage."""
Line 32: 'test1.ttl': '@prefix ex: <http://example.org/> .',
Line 33: 'test2.py': 'import ontology_framework  # example.org reference',
Line 34: 'test3.md': '[Example](http://example.org/)',
Line 35: 'test4.txt': 'No example.org here'
Line 45: # Should find example.org in .ttl, .py, and .md files
Line 50: # Should not find example.org in .txt file
Line 57: 'test.ttl': [(1, '@prefix ex: <http://example.org/> .')]
Line 63: assert 'Line 1: @prefix ex: <http://example.org/> .' in report
Line 70: 'test.ttl': [(1, '@prefix ex: <http://example.org/> .')]
Line 78: assert 'Line 1: @prefix ex: <http://example.org/> .' in content

## tests/test_find_example_org.py
Line 2: """Test suite for example.org finder."""
Line 10: """Create test files with example.org usage."""
Line 11: # Create a Python file with example.org
Line 14: from example.org import something
Line 15: # Another example.org reference
Line 16: print("http://example.org/test")
Line 19: # Create a Turtle file with example.org
Line 21: ttl_file.write_text('''@prefix ex: <http://example.org/> .
Line 27: # Create a file without example.org
Line 34: """Test finding example.org in regular files."""
Line 41: assert "example.org" in matches[0][1]  # Line content
Line 43: assert "example.org" in matches[1][1]
Line 46: """Test finding example.org in RDF files."""
Line 52: assert "Subject: http://example.org/Test" in matches[0][1]
Line 55: """Test scanning directory for example.org usage."""

## tests/test_graphdb_client.py
Line 26: @prefix ex: <http://example.org/> .

## tests/test_graphdb_patch_manager.py
Line 12: @prefix : <http://example.org/test#> .
Line 16: @prefix patch: <http://example.org/patch#> .
Line 105: patch_uri = URIRef("http://example.org/test#TestPatch")

## tests/test_guidance_conformance.py
Line 23: GUIDANCE = Namespace("http://example.org/guidance#")
Line 24: META = Namespace("http://example.org/guidance#")
Line 25: TEST = Namespace("http://example.org/test#")
Line 40: self.test_spore = URIRef("http://example.org/spores/test-spore")
Line 41: self.target_model = URIRef("http://example.org/models/target-model")
Line 60: @prefix test: <http://example.org/test#> .
Line 61: @prefix guidance: <http://example.org/guidance#> .
Line 172: process = URIRef("http://example.org/processes/test-process")
Line 176: step1 = URIRef("http://example.org/steps/step1")
Line 177: step2 = URIRef("http://example.org/steps/step2")
Line 207: process = URIRef("http://example.org/processes/test-process")
Line 211: step1 = URIRef("http://example.org/steps/step1")
Line 212: step2 = URIRef("http://example.org/steps/step2")
Line 213: step3 = URIRef("http://example.org/steps/step3")
Line 264: process = URIRef("http://example.org/processes/test-process")
Line 268: step = URIRef("http://example.org/steps/invalid-step")
Line 294: process = URIRef("http://example.org/processes/test-process")
Line 298: step = URIRef("http://example.org/steps/validation-step")

## tests/test_guidance_loader.py
Line 17: @prefix : <http://example.org/guidance#> .

## tests/test_manage_models.py
Line 33: TEST = Namespace("http://example.org/test#")
Line 78: @prefix test: <http://example.org/test#> .
Line 198: <http://example.org/test#InvalidClass>
Line 319: model_graph.add((TEST.DependentClass, OWL.imports, URIRef("http://example.org/dependency1")))
Line 320: model_graph.add((TEST.DependentClass, OWL.imports, URIRef("http://example.org/dependency2")))
Line 333: self.assertIn("http://example.org/dependency1", deps)
Line 334: self.assertIn("http://example.org/dependency2", deps)
Line 344: complete_model.add((TEST.CompleteClass, OWL.imports, URIRef("http://example.org/dependency")))
Line 450: @prefix test: <http://example.org/test#> .

## tests/test_patch_management.py
Line 16: @prefix patch: <http://example.org/patch#> .
Line 105: patch_uri = URIRef("http://example.org/test#TestPatch")

## tests/test_patch_manager.py
Line 10: PATCH = Namespace("http://example.org/patch#")
Line 124: patch_manager.validate_patch(URIRef("http://example.org/nonexistent"))
Line 129: patch_uri = URIRef("http://example.org/test-patch")
Line 140: patch_uri = URIRef("http://example.org/conformance-patch")
Line 156: patch_uri = URIRef("http://example.org/integration-patch")
Line 172: patch_uri = URIRef("http://example.org/legacy-patch")
Line 188: patch_uri = URIRef("http://example.org/registry-patch")
Line 204: patch_uri = URIRef("http://example.org/shacl-patch")

## tests/test_runtime_error_handling.py
Line 23: ns1 = Namespace("http://example.org/guidance#")
Line 67: FILTER (STRSTARTS(STR(?step), "http://example.org/guidance#TestError"))
Line 1265: PREFIX : <http://example.org/ontology#>
Line 1310: PREFIX : <http://example.org/ontology#>

## tests/test_sparql_client.py
Line 24: NS1 = Namespace("http://example.org/guidance#")
Line 50: <http://example.org/Person>
Line 54: <http://example.org/PersonShape>
Line 56: sh:targetClass <http://example.org/Person> ;
Line 58: sh:path <http://example.org/name> ;
Line 288: <http://example.org/InvalidPerson>

## tests/test_sparql_operations.py
Line 38: {"s": {"type": "uri", "value": "http://example.org/test"}}
Line 79: assert result.data[0]["s"]["value"] == "http://example.org/test"
Line 99: "INSERT DATA { <http://example.org/test> <http://example.org/p> <http://example.org/o> }",

## tests/test_spore_integration.py
Line 23: META = Namespace("http://example.org/guidance#")
Line 24: TEST = Namespace("http://example.org/test#")
Line 39: self.test_spore = URIRef("http://example.org/spores/test-spore")
Line 40: self.target_model = URIRef("http://example.org/models/target-model")
Line 59: @prefix test: <http://example.org/test#> .
Line 116: patch = URIRef("http://example.org/patches/test-patch")
Line 141: spore1 = URIRef("http://example.org/spores/spore1")
Line 142: spore2 = URIRef("http://example.org/spores/spore2")
Line 143: patch1 = URIRef("http://example.org/patches/patch1")
Line 144: patch2 = URIRef("http://example.org/patches/patch2")
Line 193: dependency = URIRef("http://example.org/spores/dependency")

## tests/test_validation.py
Line 24: <http://example.org/ontology> a owl:Ontology .
Line 26: <http://example.org/Class1> a owl:Class ;
Line 38: <http://example.org/ontology> a owl:Ontology
Line 48: <http://example.org/Class1> a owl:Class .
Line 79: valid_uri = "http://example.org/ontology"
Line 92: no_scheme = "example.org/ontology"
Line 124: valid_context = "http://example.org/ontology"

## updated_audio_deployment_ontology.ttl
Line 1: @prefix : <http:/example.org/audioOntology#> .
Line 2: @prefix default1: <http:/example.org/audio#> .
