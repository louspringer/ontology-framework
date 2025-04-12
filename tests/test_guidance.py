import unittest
import logging
from pathlib import Path

from pyshacl import validate
from rdflib import OWL, RDF, RDFS, Graph, Literal, Namespace, URIRef

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_guidance.log')
    ]
)
logger = logging.getLogger(__name__)

class TestGuidanceOntology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("Setting up test environment")
        # Set up paths
        cls.base_path = Path(__file__).parent.parent
        cls.test_file = cls.base_path / "tests" / "guidance_test.ttl"
        cls.guidance_file = cls.base_path / "guidance.ttl"
        cls.modules_path = cls.base_path / "guidance" / "modules"

        # Load all ontologies
        cls.g = Graph()
        try:
            logger.info(f"Loading test file: {cls.test_file}")
            cls.g.parse(cls.test_file, format="turtle")
            logger.info(f"Loading guidance file: {cls.guidance_file}")
            cls.g.parse(cls.guidance_file, format="turtle")

            # Load all modules
            for module in [
                "core.ttl",
                "model.ttl",
                "security.ttl",
                "validation.ttl",
                "collaboration.ttl",
            ]:
                module_path = cls.modules_path / module
                logger.info(f"Loading module: {module_path}")
                cls.g.parse(module_path, format="turtle")
        except Exception as e:
            logger.error(f"Error loading ontologies: {str(e)}")
            raise

        # Define namespaces
        cls.GUIDANCE = Namespace("guidance#")
        cls.TEST = Namespace("guidance_test#")
        cls.CORE = Namespace(str(cls.modules_path / "core#"))

    def test_module_registry_completeness(self):
        """Test that all modules are properly registered"""
        logger.info("Testing module registry completeness")
        query = """
        SELECT (COUNT(?module) as ?count) WHERE {
            ?registry rdf:type guidance:ModuleRegistry ;
                     guidance:registeredModule ?module .
        }
        """
        try:
            logger.debug(f"Executing module registry query: {query}")
            results = list(self.g.query(query))
            if not results:
                logger.error("No results from module registry query")
                self.fail("No results from module registry query")
            result = results[0]
            if not isinstance(result[0], Literal):
                logger.error(f"Count result is not a Literal: {result[0]}")
                self.fail("Count result is not a Literal")
            count = int(result[0])
            logger.info(f"Found {count} registered modules")
            self.assertEqual(count, 5, f"Should have exactly 5 registered modules, found {count}")
        except Exception as e:
            logger.error(f"Error in module registry test: {str(e)}")
            raise

    def test_module_imports(self):
        """Test that each module has proper imports"""
        logger.info("Testing module imports")
        query = """
        SELECT ?module WHERE {
            ?module rdf:type owl:Ontology .
            FILTER NOT EXISTS { ?module owl:imports ?import }
        }
        """
        try:
            logger.debug(f"Executing module imports query: {query}")
            results = list(self.g.query(query))
            if results:
                logger.error("Found modules without imports:")
                for row in results:
                    logger.error(f"- {row[0]}")
                self.fail(f"Found {len(results)} modules without imports")
            logger.info("All modules have proper imports")
        except Exception as e:
            logger.error(f"Error in module imports test: {str(e)}")
            raise

    def test_legacy_support(self):
        """Test legacy support mappings"""
        logger.info("Testing legacy support mappings")
        query = """
        SELECT (COUNT(?mapping) as ?count) WHERE {
            ?support rdf:type guidance:LegacySupport ;
                    guidance:hasLegacyMapping ?mapping .
        }
        """
        try:
            logger.debug(f"Executing legacy support query: {query}")
            results = list(self.g.query(query))
            if not results:
                logger.error("No results from legacy support query")
                self.fail("No results from legacy support query")
            result = results[0]
            if not isinstance(result[0], Literal):
                logger.error(f"Count result is not a Literal: {result[0]}")
                self.fail("Count result is not a Literal")
            count = int(result[0])
            logger.info(f"Found {count} legacy mappings")
            self.assertEqual(count, 5, f"Should have legacy mappings for all modules, found {count}")
        except Exception as e:
            logger.error(f"Error in legacy support test: {str(e)}")
            raise

    def test_version_consistency(self):
        """Test version information consistency"""
        logger.info("Testing version information consistency")
        query = """
        SELECT ?module WHERE {
            ?module rdf:type owl:Ontology .
            FILTER NOT EXISTS { ?module owl:versionInfo ?version }
        }
        """
        try:
            logger.debug(f"Executing version consistency query: {query}")
            results = list(self.g.query(query))
            if results:
                logger.error("Found modules without version info:")
                for row in results:
                    logger.error(f"- {row[0]}")
                self.fail(f"Found {len(results)} modules without version info")
            logger.info("All modules have version information")
        except Exception as e:
            logger.error(f"Error in version consistency test: {str(e)}")
            raise

    def test_shacl_constraints(self):
        """Test SHACL constraints"""
        logger.info("Testing SHACL constraints")
        try:
            # Load test shapes
            shapes_graph = Graph()
            logger.info(f"Loading SHACL shapes from {self.test_file}")
            shapes_graph.parse(self.test_file, format="turtle")

            # Validate against SHACL shapes
            logger.info("Running SHACL validation")
            conforms, results_graph, results_text = validate(
                self.g,
                shacl_graph=shapes_graph,
                inference="rdfs",
                abort_on_first=True,
            )

            if not conforms:
                logger.error(f"SHACL validation failed:\n{results_text}")
                self.fail(f"SHACL validation failed:\n{results_text}")
            logger.info("SHACL validation passed")
        except Exception as e:
            logger.error(f"Error in SHACL constraints test: {str(e)}")
            raise

    def test_module_class_definitions(self):
        """Test that each module defines its required classes"""
        logger.info("Testing module class definitions")
        required_classes = {
            "core": ["Interpretation", "Action", "DomainAnalogy", "BestPractice"],
            "model": ["ModelFirstPrinciple", "ModelQualityPrecedence"],
            "security": ["SecurityPattern", "AuthenticationPattern"],
            "validation": ["ValidationPattern", "TestCase"],
            "collaboration": ["PRManagementPattern", "PRTemplate"],
        }

        try:
            # Debug: Log all classes and their labels
            logger.debug("All Classes and Labels:")
            for s, p, o in self.g.triples((None, RDF.type, OWL.Class)):
                label = self.g.value(s, RDFS.label)
                logger.debug(f"Class: {s} Label: {label}")

                # Special debug for BestPractice class
                if isinstance(label, Literal) and str(label) == "BestPractice":
                    logger.debug(f"Found BestPractice class at {s}")
                    for p2, o2 in self.g.predicate_objects(s):
                        logger.debug(f"  {p2} -> {o2}")

            for module, classes in required_classes.items():
                logger.info(f"Checking required classes for {module} module")
                for class_name in classes:
                    query = f"""
                    SELECT ?class ?label WHERE {{
                        ?class rdf:type owl:Class ;
                               rdfs:label ?label .
                        FILTER(str(?label) = "{class_name}")
                    }}
                    """
                    results = list(self.g.query(query))
                    if not results:
                        logger.error(f"Missing class {class_name} in {module} module")
                        logger.debug("Current classes with similar labels:")
                        similar_query = f"""
                        SELECT ?class ?label WHERE {{
                            ?class rdf:type owl:Class ;
                                   rdfs:label ?label .
                            FILTER(contains(str(?label), "{class_name}"))
                        }}
                        """
                        similar_results = list(self.g.query(similar_query))
                        for row in similar_results:
                            class_uri = row[0] if isinstance(row[0], (URIRef, Literal)) else str(row[0])
                            label = row[1] if isinstance(row[1], Literal) else str(row[1])
                            logger.debug(f"Found similar: {class_uri} with label {label}")

                        # Special debug for BestPractice
                        if class_name == "BestPractice":
                            bp_uri = self.CORE["BestPractice"]
                            logger.debug(f"Looking for BestPractice at {bp_uri}")
                            for p, o in self.g.predicate_objects(bp_uri):
                                logger.debug(f"  {p} -> {o}")

                        self.fail(f"Missing class {class_name} in {module} module")
                    logger.info(f"Found required class {class_name} in {module} module")
        except Exception as e:
            logger.error(f"Error in module class definitions test: {str(e)}")
            raise

    def test_modeling_rules_completeness(self):
        """Test that modeling rules have all required properties"""
        logger.info("Testing modeling rules completeness")
        query = """
        SELECT ?rule ?label ?pitfall ?motivation ?example ?severity ?governs WHERE {
            ?rule rdf:type meta:ModelingDisciplineRule .
            OPTIONAL { ?rule rdfs:label ?label }
            OPTIONAL { ?rule meta:addressesPitfall ?pitfall }
            OPTIONAL { ?rule meta:motivates ?motivation }
            OPTIONAL { ?rule meta:example ?example }
            OPTIONAL { ?rule meta:severity ?severity }
            OPTIONAL { ?rule meta:governs ?governs }
        }
        """
        try:
            logger.debug(f"Executing modeling rules query: {query}")
            results = list(self.g.query(query))
            for row in results:
                rule, label, pitfall, motivation, example, severity, governs = row
                if label is None:
                    logger.error(f"Rule {rule} missing label")
                    self.fail(f"Rule {rule} missing label")
                if pitfall is None:
                    logger.error(f"Rule {rule} missing pitfall")
                    self.fail(f"Rule {rule} missing pitfall")
                if motivation is None:
                    logger.error(f"Rule {rule} missing motivation")
                    self.fail(f"Rule {rule} missing motivation")
                if example is None:
                    logger.error(f"Rule {rule} missing example")
                    self.fail(f"Rule {rule} missing example")
                if severity is None:
                    logger.error(f"Rule {rule} missing severity")
                    self.fail(f"Rule {rule} missing severity")
                if governs is None:
                    logger.error(f"Rule {rule} missing governed aspect")
                    self.fail(f"Rule {rule} missing governed aspect")
            logger.info("All modeling rules have required properties")
        except Exception as e:
            logger.error(f"Error in modeling rules completeness test: {str(e)}")
            raise

    def test_validation_patterns_completeness(self):
        """Test that all validation patterns have complete metadata"""
        logger.info("Testing validation patterns completeness")
        query = """
        SELECT ?pattern WHERE {
            ?pattern rdf:type guidance:ValidationPattern
            FILTER NOT EXISTS {
                ?pattern rdfs:label ?label ;
                         rdfs:comment ?comment ;
                         guidance:targetClass ?target
            }
        }
        """
        try:
            logger.debug(f"Executing validation patterns query: {query}")
            results = list(self.g.query(query))
            if results:
                logger.error("Found validation patterns with incomplete metadata:")
                for row in results:
                    logger.error(f"- {row[0]}")
                self.fail(f"Found {len(results)} validation patterns with incomplete metadata")
            logger.info("All validation patterns have complete metadata")
        except Exception as e:
            logger.error(f"Error in validation patterns completeness test: {str(e)}")
            raise

    def test_test_requirements_completeness(self):
        """Test that test requirements have all required properties"""
        logger.info("Testing test requirements completeness")
        query = """
        SELECT ?req ?label ?validation ?test ?severity WHERE {
            ?req rdf:type meta:Requirement .
            OPTIONAL { ?req rdfs:label ?label }
            OPTIONAL { ?req meta:hasValidation ?validation }
            OPTIONAL { ?req meta:hasTest ?test }
            OPTIONAL { ?req meta:severity ?severity }
        }
        """
        try:
            logger.debug(f"Executing test requirements query: {query}")
            results = list(self.g.query(query))
            for row in results:
                req, label, validation, test, severity = row
                if label is None:
                    logger.error(f"Requirement {req} missing label")
                    self.fail(f"Requirement {req} missing label")
                if validation is None:
                    logger.error(f"Requirement {req} missing validation")
                    self.fail(f"Requirement {req} missing validation")
                if test is None:
                    logger.error(f"Requirement {req} missing test")
                    self.fail(f"Requirement {req} missing test")
                if severity is None:
                    logger.error(f"Requirement {req} missing severity")
                    self.fail(f"Requirement {req} missing severity")
            logger.info("All test requirements have required properties")
        except Exception as e:
            logger.error(f"Error in test requirements completeness test: {str(e)}")
            raise

    def test_test_coverage(self):
        """Test that all requirements, aspects, and components have test coverage"""
        logger.info("Running test coverage check")
        query = """
        PREFIX validation: <guidance/modules/validation#>
        SELECT ?entity ?type WHERE {
            {
                ?entity rdf:type guidance:Requirement .
                BIND("Requirement" AS ?type)
            } UNION {
                ?entity rdf:type guidance:FrameworkAspect .
                BIND("Aspect" AS ?type)
            } UNION {
                ?entity rdf:type guidance:Component .
                BIND("Component" AS ?type)
            }
            FILTER NOT EXISTS {
                ?test rdf:type validation:TestCase ;
                      validation:validates ?entity
            }
        }
        """
        try:
            logger.debug(f"Executing query: {query}")
            results = list(self.g.query(query))
            if results:
                logger.error("Found entities without test coverage:")
                for row in results:
                    entity, type_ = row
                    logger.error(f"- {type_}: {entity}")
                self.fail(f"Found {len(results)} entities without test coverage")
            logger.info("All entities have test coverage")
        except Exception as e:
            logger.error(f"Error executing test coverage query: {str(e)}")
            raise

    def test_integration_process_steps(self):
        """Test that integration processes have properly ordered steps"""
        logger.info("Testing integration process steps")
        query = """
        SELECT ?process ?step ?order ?description WHERE {
            ?process rdf:type guidance:IntegrationProcess ;
                    guidance:hasIntegrationStep ?step .
            ?step guidance:stepOrder ?order ;
                  guidance:stepDescription ?description .
        }
        ORDER BY ?process ?order
        """
        try:
            logger.debug(f"Executing integration process steps query: {query}")
            results = list(self.g.query(query))
            current_process = None
            current_order = 0
            for row in results:
                process, step, order, description = row
                if process != current_process:
                    current_process = process
                    current_order = 0
                expected_order = current_order + 1
                if int(order) != expected_order:
                    logger.error(f"Step {step} in process {process} has incorrect order: {order}, expected {expected_order}")
                    self.fail(f"Step {step} in process {process} has incorrect order")
                if description is None:
                    logger.error(f"Step {step} in process {process} missing description")
                    self.fail(f"Step {step} in process {process} missing description")
                current_order = int(order)
            logger.info("All integration processes have properly ordered steps")
        except Exception as e:
            logger.error(f"Error in integration process steps test: {str(e)}")
            raise

    def test_property_validation(self):
        """Test that all properties have proper domain and range definitions"""
        logger.info("Testing property validation")
        query = """
        SELECT ?property ?domain ?range WHERE {
            ?property rdf:type owl:ObjectProperty .
            OPTIONAL { ?property rdfs:domain ?domain }
            OPTIONAL { ?property rdfs:range ?range }
        }
        """
        try:
            logger.debug(f"Executing property validation query: {query}")
            results = list(self.g.query(query))
            for row in results:
                property, domain, range = row
                if domain is None:
                    logger.error(f"Property {property} missing domain definition")
                    self.fail(f"Property {property} missing domain definition")
                if range is None:
                    logger.error(f"Property {property} missing range definition")
                    self.fail(f"Property {property} missing range definition")
            logger.info("All properties have proper domain and range definitions")
        except Exception as e:
            logger.error(f"Error in property validation test: {str(e)}")
            raise

    def test_class_hierarchy(self):
        """Test that class hierarchies are properly defined"""
        logger.info("Testing class hierarchy")
        query = """
        SELECT ?class ?superclass WHERE {
            ?class rdfs:subClassOf ?superclass .
            FILTER (?class != ?superclass)
        }
        """
        try:
            logger.debug(f"Executing class hierarchy query: {query}")
            results = list(self.g.query(query))
            for row in results:
                class_, superclass = row
                if not isinstance(superclass, URIRef):
                    logger.error(f"Class {class_} has invalid superclass {superclass}")
                    self.fail(f"Class {class_} has invalid superclass {superclass}")
            logger.info("All class hierarchies are properly defined")
        except Exception as e:
            logger.error(f"Error in class hierarchy test: {str(e)}")
            raise

    def test_import_consistency(self):
        """Test that all imports are valid and accessible"""
        logger.info("Testing import consistency")
        query = """
        SELECT ?module ?import WHERE {
            ?module rdf:type owl:Ontology ;
                   owl:imports ?import .
        }
        """
        try:
            logger.debug(f"Executing import consistency query: {query}")
            results = list(self.g.query(query))
            for row in results:
                module, import_ = row
                if not isinstance(import_, URIRef):
                    logger.error(f"Module {module} has invalid import {import_}")
                    self.fail(f"Module {module} has invalid import {import_}")
            logger.info("All imports are valid and accessible")
        except Exception as e:
            logger.error(f"Error in import consistency test: {str(e)}")
            raise

    def test_version_compatibility(self):
        """Test that module versions are compatible"""
        logger.info("Testing version compatibility")
        query = """
        SELECT ?module ?version WHERE {
            ?module rdf:type owl:Ontology ;
                   owl:versionInfo ?version .
        }
        """
        try:
            logger.debug(f"Executing version compatibility query: {query}")
            results = list(self.g.query(query))
            versions = {}
            for row in results:
                module, version = row
                versions[str(module)] = str(version)
            
            # Check that all modules have the same major version
            major_versions = set(v.split('.')[0] for v in versions.values())
            if len(major_versions) > 1:
                logger.error(f"Modules have incompatible major versions: {major_versions}")
                self.fail(f"Modules have incompatible major versions: {major_versions}")
            
            logger.info("All module versions are compatible")
        except Exception as e:
            logger.error(f"Error in version compatibility test: {str(e)}")
            raise


if __name__ == "__main__":
    unittest.main()
