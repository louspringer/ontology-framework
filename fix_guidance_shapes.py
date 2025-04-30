from rdflib import Graph, Namespace, RDF, RDFS, OWL, SH, Literal, URIRef
from rdflib.namespace import XSD

def fix_guidance_shapes():
    # Load the ontology
    g = Graph()
    g.parse("guidance.ttl", format="turtle")
    
    # Define namespaces
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    SH = Namespace("http://www.w3.org/ns/shacl#")
    
    # Ensure ModuleRegistry is properly typed
    g.add((GUIDANCE.ModuleRegistry, RDF.type, RDFS.Class))
    g.add((GUIDANCE.ModuleRegistry, RDF.type, OWL.Class))
    
    # Ensure LegacySupport is properly typed
    g.add((GUIDANCE.LegacySupport, RDF.type, RDFS.Class))
    g.add((GUIDANCE.LegacySupport, RDF.type, OWL.Class))
    
    # Add SHACL shape for ModuleRegistry
    registry_shape = GUIDANCE.ModuleRegistryShape
    g.add((registry_shape, RDF.type, SH.NodeShape))
    g.add((registry_shape, SH.targetClass, GUIDANCE.ModuleRegistry))
    g.add((registry_shape, RDFS.label, Literal("Module Registry Shape", lang="en")))
    g.add((registry_shape, RDFS.comment, Literal("Validates module registry structure", lang="en")))
    
    # Add property shape for registeredModule
    prop_shape = GUIDANCE.RegisteredModuleShape
    g.add((registry_shape, SH.property, prop_shape))
    g.add((prop_shape, SH.path, GUIDANCE.registeredModule))
    g.add((prop_shape, SH.minCount, Literal(5)))
    g.add((prop_shape, SH.message, Literal("Module registry must contain all 5 core modules")))
    
    # Add SHACL shape for LegacySupport
    legacy_shape = GUIDANCE.LegacySupportShape
    g.add((legacy_shape, RDF.type, SH.NodeShape))
    g.add((legacy_shape, SH.targetClass, GUIDANCE.LegacySupport))
    g.add((legacy_shape, RDFS.label, Literal("Legacy Support Shape", lang="en")))
    g.add((legacy_shape, RDFS.comment, Literal("Validates legacy support mappings", lang="en")))
    
    # Add property shape for hasLegacyMapping
    mapping_shape = GUIDANCE.LegacyMappingShape
    g.add((legacy_shape, SH.property, mapping_shape))
    g.add((mapping_shape, SH.path, GUIDANCE.hasLegacyMapping))
    g.add((mapping_shape, SH.minCount, Literal(5)))
    g.add((mapping_shape, SH.message, Literal("Legacy support must map all core modules")))
    
    # Save the fixed ontology
    g.serialize("guidance_fixed.ttl", format="turtle")

if __name__ == "__main__":
    fix_guidance_shapes() 