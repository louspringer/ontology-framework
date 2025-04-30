from rdflib import Graph, Namespace, RDF, RDFS, OWL, SH, Literal, XSD, BNode, URIRef
from pathlib import Path

def fix_guidance_ontology():
    # Load the guidance ontology
    g = Graph()
    g.parse('guidance.ttl', format='turtle')
    
    # Define and bind all required namespaces
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    META = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/meta#")
    CORE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/core#")
    
    g.bind("guidance", GUIDANCE)
    g.bind("meta", META)
    g.bind("core", CORE)
    
    # Declare the ontology itself
    g.add((GUIDANCE[""], RDF.type, OWL.Ontology))
    
    # Add module imports
    modules = [
        "core",
        "model", 
        "security",
        "validation",
        "collaboration"
    ]
    
    for module in modules:
        module_uri = URIRef(f"https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/{module}#")
        g.add((GUIDANCE[""], OWL.imports, module_uri))
    
    # Add Interpretation class to core module
    g.add((CORE.Interpretation, RDF.type, OWL.Class))
    g.add((CORE.Interpretation, RDFS.label, Literal("Interpretation", lang="en")))
    g.add((CORE.Interpretation, RDFS.comment, Literal("Class for representing interpretations of ontology elements", lang="en")))
    g.add((CORE.Interpretation, OWL.versionInfo, Literal("1.0.0")))
    
    # Add module registry
    registry = BNode()
    g.add((registry, RDF.type, GUIDANCE.ModuleRegistry))
    g.add((GUIDANCE[""], GUIDANCE.hasRegistry, registry))
    
    for module in modules:
        module_uri = URIRef(f"https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/{module}#")
        g.add((registry, GUIDANCE.registeredModule, module_uri))
    
    # Add legacy support mappings
    legacy_support = BNode()
    g.add((legacy_support, RDF.type, GUIDANCE.LegacySupport))
    g.add((GUIDANCE[""], GUIDANCE.hasLegacySupport, legacy_support))
    
    for module in modules:
        mapping = BNode()
        module_uri = URIRef(f"https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/{module}#")
        g.add((legacy_support, GUIDANCE.hasLegacyMapping, mapping))
        g.add((mapping, GUIDANCE.sourceModule, module_uri))
        g.add((mapping, GUIDANCE.targetModule, module_uri))
        g.add((mapping, GUIDANCE.mappingType, Literal("direct")))
        g.add((mapping, RDFS.label, Literal(f"Legacy mapping for {module} module", lang="en")))
    
    # Add modeling rules
    modeling_rule = BNode()
    g.add((modeling_rule, RDF.type, META.ModelingDisciplineRule))
    g.add((modeling_rule, RDFS.label, Literal("Ontology Structure Rule", lang="en")))
    g.add((modeling_rule, META.addressesPitfall, Literal("Inconsistent ontology structure", lang="en")))
    g.add((modeling_rule, META.motivates, Literal("Ensure consistent ontology structure", lang="en")))
    g.add((modeling_rule, META.example, Literal("Example of proper ontology structure", lang="en")))
    g.add((modeling_rule, META.severity, Literal("HIGH")))
    g.add((modeling_rule, META.governs, GUIDANCE.ValidationRule))
    
    # Add test requirements
    test_req = BNode()
    g.add((test_req, RDF.type, META.Requirement))
    g.add((test_req, RDFS.label, Literal("Validation Test Requirement", lang="en")))
    g.add((test_req, META.hasValidation, GUIDANCE.ValidationRule))
    g.add((test_req, META.hasTest, GUIDANCE.TestProtocol))
    g.add((test_req, META.severity, Literal("HIGH")))
    
    # Save the fixed ontology
    g.serialize('guidance_fixed.ttl', format='turtle')

if __name__ == "__main__":
    fix_guidance_ontology() 