from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef
from pathlib import Path

def fix_guidance_core():
    # Load the ontology
    g = Graph()
    g.parse("guidance.ttl", format="turtle")
    
    # Define namespaces
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    CORE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/core#")
    
    # Bind namespaces
    g.bind("guidance", GUIDANCE)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    
    # Add core module classes
    core_classes = {
        "Interpretation": "Class for representing interpretations of ontology elements",
        "Action": "Class for representing actions that can be taken",
        "DomainAnalogy": "Class for representing domain analogies",
        "BestPractice": "Class for representing best practices"
    }
    
    for class_name, description in core_classes.items():
        class_uri = CORE[class_name]
        g.add((class_uri, RDF.type, OWL.Class))
        g.add((class_uri, RDFS.label, Literal(class_name, lang="en")))
        g.add((class_uri, RDFS.comment, Literal(description, lang="en")))
        g.add((class_uri, OWL.versionInfo, Literal("1.0.0")))
    
    # Ensure ModuleRegistry is properly typed and has instances
    g.add((GUIDANCE.ModuleRegistry, RDF.type, OWL.Class))
    g.add((GUIDANCE.ModuleRegistry, RDFS.label, Literal("Module Registry", lang="en")))
    g.add((GUIDANCE.ModuleRegistry, RDFS.comment, Literal("Registry for tracking ontology modules", lang="en")))
    
    # Create main registry instance
    main_registry = GUIDANCE.MainRegistry
    g.add((main_registry, RDF.type, GUIDANCE.ModuleRegistry))
    
    # Add module registrations
    modules = [
        "core",
        "model",
        "security",
        "validation",
        "collaboration"
    ]
    
    for module in modules:
        module_uri = URIRef(f"https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/{module}#")
        g.add((main_registry, GUIDANCE.registeredModule, module_uri))
    
    # Ensure LegacySupport is properly typed and has instances
    g.add((GUIDANCE.LegacySupport, RDF.type, OWL.Class))
    g.add((GUIDANCE.LegacySupport, RDFS.label, Literal("Legacy Support", lang="en")))
    g.add((GUIDANCE.LegacySupport, RDFS.comment, Literal("Support for legacy module mappings", lang="en")))
    
    # Create main legacy support instance
    legacy_support = GUIDANCE.MainLegacySupport
    g.add((legacy_support, RDF.type, GUIDANCE.LegacySupport))
    
    # Add legacy mappings
    for module in modules:
        module_uri = URIRef(f"https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/{module}#")
        mapping = URIRef(f"{GUIDANCE}LegacyMapping_{module}")
        
        g.add((legacy_support, GUIDANCE.hasLegacyMapping, mapping))
        g.add((mapping, RDF.type, GUIDANCE.LegacyMapping))
        g.add((mapping, GUIDANCE.sourceModule, module_uri))
        g.add((mapping, GUIDANCE.targetModule, module_uri))
        g.add((mapping, GUIDANCE.mappingType, Literal("direct")))
        g.add((mapping, RDFS.label, Literal(f"Legacy mapping for {module} module", lang="en")))
    
    # Save the fixed ontology
    g.serialize("guidance.ttl", format="turtle")
    
    # Create core module file
    core_g = Graph()
    core_g.bind("owl", OWL)
    core_g.bind("rdfs", RDFS)
    core_g.bind("core", CORE)
    
    # Add core module ontology declaration
    core_g.add((CORE[""], RDF.type, OWL.Ontology))
    core_g.add((CORE[""], OWL.versionInfo, Literal("1.0.0")))
    core_g.add((CORE[""], RDFS.label, Literal("Core Module", lang="en")))
    core_g.add((CORE[""], RDFS.comment, Literal("Core concepts for the guidance framework", lang="en")))
    
    # Add core classes to core module
    for class_name, description in core_classes.items():
        class_uri = CORE[class_name]
        core_g.add((class_uri, RDF.type, OWL.Class))
        core_g.add((class_uri, RDFS.label, Literal(class_name, lang="en")))
        core_g.add((class_uri, RDFS.comment, Literal(description, lang="en")))
        core_g.add((class_uri, OWL.versionInfo, Literal("1.0.0")))
    
    # Create modules directory if it doesn't exist
    Path("guidance/modules").mkdir(parents=True, exist_ok=True)
    
    # Save the core module
    core_g.serialize("guidance/modules/core.ttl", format="turtle")

if __name__ == "__main__":
    fix_guidance_core() 