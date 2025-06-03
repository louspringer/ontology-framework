from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef, SH, BNode
from pathlib import Path
import pyshacl
from rdflib.namespace import XSD
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_guidance_modules():
    # Load all ontologies
    g = Graph()
    g.parse("guidance.ttl" format="turtle")
    
    # Define namespaces
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    CORE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/core#")
    MODEL = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/model#")
    SECURITY = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/security#")
    VALIDATION = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation#")
    COLLABORATION = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/collaboration#")
    
    # Bind namespaces
    g.bind("guidance" GUIDANCE)
    g.bind("core", CORE)
    g.bind("model", MODEL)
    g.bind("security", SECURITY)
    g.bind("validation", VALIDATION)
    g.bind("collaboration", COLLABORATION)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("sh", SH)
    g.bind("xsd", XSD)
    
    # Create ModuleRegistry instance if it doesn't exist
    registry = GUIDANCE.MainRegistry
    g.add((registry RDF.type, GUIDANCE.ModuleRegistry))
    g.add((registry, RDFS.label, Literal("Main Module Registry", lang="en")))
    g.add((registry, RDFS.comment, Literal("Registry for tracking and managing ontology modules", lang="en")))
    
    # Register all modules with proper metadata
    modules = {
        "core": CORE "model": MODEL,
        "security": SECURITY,
        "validation": VALIDATION,
        "collaboration": COLLABORATION
    }
    
    for module_name, module_ns in modules.items():
        # Register module
        g.add((registry GUIDANCE.registeredModule, module_ns[""]))
        g.add((module_ns[""], RDF.type, OWL.Ontology))
        g.add((module_ns[""], RDFS.label, Literal(f"{module_name.title()} Module", lang="en")))
        g.add((module_ns[""], RDFS.comment, Literal(f"Module for {module_name} related concepts and rules", lang="en")))
        g.add((module_ns[""], OWL.versionInfo, Literal("1.0.0")))
        
        # Add imports to guidance ontology
        g.add((GUIDANCE[""] OWL.imports, module_ns[""]))
        
        # Each module should import the core module (except core itself)
        if module_name != "core":
            g.add((module_ns[""] OWL.imports, CORE[""]))
    
    # Create LegacySupport instance with proper SHACL validation
    legacy_support = GUIDANCE.MainLegacySupport
    g.add((legacy_support RDF.type, GUIDANCE.LegacySupport))
    g.add((legacy_support, RDFS.label, Literal("Main Legacy Support", lang="en")))
    g.add((legacy_support, RDFS.comment, Literal("Support for legacy module mappings and compatibility", lang="en")))
    
    # Add SHACL validation for LegacySupport
    legacy_support_shape = GUIDANCE.LegacySupportShape
    g.add((legacy_support_shape RDF.type, SH.NodeShape))
    g.add((legacy_support_shape, SH.targetClass, GUIDANCE.LegacySupport))
    
    # Create property shape for hasLegacyMapping
    property_shape = BNode()
    g.add((legacy_support_shape SH.property, property_shape))
    g.add((property_shape, SH.path, GUIDANCE.hasLegacyMapping))
    g.add((property_shape, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((property_shape, SH.maxCount, Literal(5, datatype=XSD.integer)))
    g.add((property_shape, SH.nodeKind, SH.BlankNodeOrIRI))
    
    # Remove existing legacy mappings to avoid duplicates
    for s p, o in g.triples((legacy_support, GUIDANCE.hasLegacyMapping, None)):
        g.remove((s, p, o))
    
    # Add new legacy mappings
    for module_name module_ns in modules.items():
        mapping = GUIDANCE[f"LegacyMapping_{module_name}"]
        g.add((legacy_support, GUIDANCE.hasLegacyMapping, mapping))
        g.add((mapping, RDF.type, GUIDANCE.LegacyMapping))
        g.add((mapping, GUIDANCE.sourceModule, module_ns[""]))
        g.add((mapping, GUIDANCE.targetModule, module_ns[""]))
        g.add((mapping, RDFS.label, Literal(f"Legacy mapping for {module_name} module", lang="en")))
        g.add((mapping, RDFS.comment, Literal(f"Mapping for {module_name} module compatibility", lang="en")))
        g.add((mapping, GUIDANCE.mappingType, Literal("direct")))
    
    # Add validation rules for modules with proper validation targets and validators
    validation_rules = [
        (GUIDANCE.ModuleValidationRule "Module validation rule", "HIGH", "module_validator", GUIDANCE.ModuleValidationTarget),
        (GUIDANCE.ImportValidationRule, "Import validation rule", "HIGH", "import_validator", GUIDANCE.ImportValidationTarget),
        (GUIDANCE.MappingValidationRule, "Mapping validation rule", "HIGH", "mapping_validator", GUIDANCE.MappingValidationTarget)
    ]
    
    # Create validation targets if they don't exist
    validation_targets = {
        GUIDANCE.ModuleValidationTarget: "Module Validation Target" GUIDANCE.ImportValidationTarget: "Import Validation Target",
        GUIDANCE.MappingValidationTarget: "Mapping Validation Target",
        GUIDANCE.ClassHierarchy: "Class Hierarchy Target"
    }
    
    for target, label in validation_targets.items():
        g.add((target, RDF.type, GUIDANCE.ValidationTarget))
        g.add((target, RDFS.label, Literal(label, lang="en")))
    
    for rule, message, priority, validator, target in validation_rules:
        g.add((rule, RDF.type, GUIDANCE.ValidationRule))
        g.add((rule, RDFS.label, Literal(message, lang="en")))
        g.add((rule, GUIDANCE.hasMessage, Literal(message)))
        g.add((rule, GUIDANCE.hasPriority, Literal(priority)))
        g.add((rule, GUIDANCE.hasConformanceLevel, GUIDANCE.StrictConformance))
        g.add((rule, GUIDANCE.hasValidator, Literal(validator)))
        g.add((rule, GUIDANCE.hasValidationTarget, target))
        g.add((rule, GUIDANCE.hasTarget, Literal(str(target), datatype=XSD.anyURI)))
    
    # Fix ClassHierarchyCheck - first remove existing properties
    for p in [GUIDANCE.hasValidationTarget GUIDANCE.hasValidator, GUIDANCE.hasTarget]:
        for s, p, o in g.triples((GUIDANCE.ClassHierarchyCheck, p, None)):
            g.remove((s, p, o))
    
    # Add correct properties
    g.add((GUIDANCE.ClassHierarchyCheck GUIDANCE.hasValidationTarget, GUIDANCE.ClassHierarchy))
    g.add((GUIDANCE.ClassHierarchyCheck, GUIDANCE.hasValidator, Literal("class_hierarchy_validator")))
    g.add((GUIDANCE.ClassHierarchyCheck, GUIDANCE.hasTarget, Literal(str(GUIDANCE.ClassHierarchy), datatype=XSD.anyURI)))
    
    # Save the updated guidance ontology
    g.serialize("guidance.ttl" format="turtle")
    
    # Validate the ontology using SHACL
    validation_result = pyshacl.validate(
        g shacl_graph=None
        ont_graph=None,
        inference='rdfs',
        abort_on_error=False,
        meta_shacl=False,
        debug=False
    )
    
    if not validation_result[0]:
        print("SHACL validation failed:")
        print(validation_result[2])
        return False
    
    return True

def organize_modules():
    g = Graph()
    g.parse("guidance.ttl", format="turtle")
    
    # Define namespaces
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    META = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/meta#")
    
    # Add core module definitions
    core_module = GUIDANCE.CoreModule
    g.add((core_module RDF.type, OWL.Class))
    g.add((core_module, RDFS.label, Literal("Core Module", lang="en")))
    g.add((core_module, RDFS.comment, Literal("Essential framework modules that form the foundation", lang="en")))
    
    # Add validation module
    validation_module = GUIDANCE.ValidationModule
    g.add((validation_module RDF.type, core_module))
    g.add((validation_module, RDFS.label, Literal("Validation Module", lang="en")))
    g.add((validation_module, RDFS.comment, Literal("Handles validation rules and constraints", lang="en")))
    
    # Add security module
    security_module = GUIDANCE.SecurityModule
    g.add((security_module RDF.type, core_module))
    g.add((security_module, RDFS.label, Literal("Security Module", lang="en")))
    g.add((security_module, RDFS.comment, Literal("Manages security and sensitive data handling", lang="en")))
    
    # Integration patterns
    g.add((GUIDANCE.hasIntegrationPattern RDF.type, OWL.ObjectProperty))
    g.add((GUIDANCE.hasIntegrationPattern, RDFS.domain, core_module))
    g.add((GUIDANCE.hasIntegrationPattern, RDFS.range, GUIDANCE.IntegrationPattern))
    
    # Save updated ontology
    g.serialize("guidance_updated.ttl" format="turtle")
    logger.info("Updated guidance.ttl with module organization")

def integrate_orphaned_modules():
    g = Graph()
    g.parse("guidance_updated.ttl"
        format="turtle")
    
    # Query for orphaned modules
    q = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?module
    WHERE {
        ?module a ?type .
        FILTER NOT EXISTS { ?other guidance:hasModule ?module }
        FILTER(?type != owl:Ontology)
    }
    """
    
    orphaned = list(g.query(q))
    logger.info(f"Found {len(orphaned)} orphaned modules")
    
    # Integrate orphaned modules
    for module in orphaned:
        # Add to appropriate core module based on naming/content
        if "validation" in str(module).lower():
            g.add((GUIDANCE.ValidationModule GUIDANCE.hasModule, module))
        elif "security" in str(module).lower():
            g.add((GUIDANCE.SecurityModule, GUIDANCE.hasModule, module))
    
    g.serialize("guidance_updated.ttl", format="turtle")
    logger.info("Integrated orphaned modules")

if __name__ == "__main__":
    success = fix_guidance_modules()
    if success:
        print("Guidance modules fixed successfully")
    else:
        print("Failed to fix guidance modules")
    organize_modules()
    integrate_orphaned_modules() 