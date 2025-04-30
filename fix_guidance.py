#!/usr/bin/env python3
from rdflib import Graph, Namespace, RDF, RDFS, OWL, SH, Literal, URIRef
from rdflib.namespace import XSD
import logging
from pyshacl import validate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_guidance_ontology():
    # Load the guidance ontology
    g = Graph()
    g.parse('guidance.ttl', format='turtle')
    
    # Define namespaces
    G = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
    
    # Add missing labels and comments
    g.add((G.SPORERule, RDFS.label, Literal("SPORE Rule", lang="en")))
    g.add((G.SPORERule, RDFS.comment, Literal("Validation rule for SPORE compliance", lang="en")))
    
    g.add((G.SemanticRule, RDFS.label, Literal("Semantic Rule", lang="en")))
    g.add((G.SemanticRule, RDFS.comment, Literal("Validation rule for semantic consistency", lang="en")))
    
    g.add((G.SyntaxRule, RDFS.label, Literal("Syntax Rule", lang="en")))
    g.add((G.SyntaxRule, RDFS.comment, Literal("Validation rule for syntax compliance", lang="en")))
    
    g.add((G.ConsistencyRule, RDFS.label, Literal("Consistency Rule", lang="en")))
    g.add((G.ConsistencyRule, RDFS.comment, Literal("Validation rule for consistency checks", lang="en")))
    
    g.add((G.ValidationRule, RDFS.label, Literal("Validation Rule", lang="en")))
    g.add((G.ValidationRule, RDFS.comment, Literal("Base class for all validation rules", lang="en")))
    
    # Add missing property definitions
    g.add((G.hasMessage, RDFS.range, XSD.string))
    g.add((G.hasMessage, RDFS.label, Literal("has message", lang="en")))
    g.add((G.hasMessage, RDFS.comment, Literal("Specifies the validation message", lang="en")))
    
    g.add((G.hasPriority, RDFS.range, XSD.string))
    g.add((G.hasPriority, RDFS.label, Literal("has priority", lang="en")))
    g.add((G.hasPriority, RDFS.comment, Literal("Specifies the validation priority", lang="en")))
    
    g.add((G.hasTarget, RDFS.range, XSD.anyURI))
    g.add((G.hasTarget, RDFS.label, Literal("has target", lang="en")))
    g.add((G.hasTarget, RDFS.comment, Literal("Specifies the validation target URI", lang="en")))
    
    g.add((G.hasValidator, RDFS.range, XSD.string))
    g.add((G.hasValidator, RDFS.label, Literal("has validator", lang="en")))
    g.add((G.hasValidator, RDFS.comment, Literal("Specifies the validation function", lang="en")))
    
    # Fix ClassHierarchyCheck instance
    # First remove any existing hasTarget triples
    for s, p, o in g.triples((G.ClassHierarchyCheck, G.hasTarget, None)):
        g.remove((s, p, o))
    
    g.add((G.ClassHierarchyCheck, G.hasConformanceLevel, G.StrictConformance))
    g.add((G.ClassHierarchyCheck, G.hasValidationTarget, G.ClassHierarchy))
    g.add((G.ClassHierarchyCheck, G.hasTarget, Literal("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#ClassHierarchy", datatype=XSD.anyURI)))
    
    # Add SHACL shapes for validation
    validation_rule_shape = G.ValidationRuleShape
    g.add((validation_rule_shape, SH.targetClass, G.ValidationRule))
    
    # Add property shapes
    message_shape = G.MessageShape
    g.add((message_shape, SH.path, G.hasMessage))
    g.add((message_shape, SH.datatype, XSD.string))
    g.add((message_shape, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((message_shape, SH.maxCount, Literal(1, datatype=XSD.integer)))
    
    priority_shape = G.PriorityShape
    g.add((priority_shape, SH.path, G.hasPriority))
    g.add((priority_shape, SH.datatype, XSD.string))
    g.add((priority_shape, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((priority_shape, SH.maxCount, Literal(1, datatype=XSD.integer)))
    
    target_shape = G.TargetShape
    g.add((target_shape, SH.path, G.hasTarget))
    g.add((target_shape, SH.datatype, XSD.anyURI))
    g.add((target_shape, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((target_shape, SH.maxCount, Literal(1, datatype=XSD.integer)))
    
    validator_shape = G.ValidatorShape
    g.add((validator_shape, SH.path, G.hasValidator))
    g.add((validator_shape, SH.datatype, XSD.string))
    g.add((validator_shape, SH.minCount, Literal(1, datatype=XSD.integer)))
    g.add((validator_shape, SH.maxCount, Literal(1, datatype=XSD.integer)))
    
    # Add shapes to validation rule shape
    g.add((validation_rule_shape, SH.property, message_shape))
    g.add((validation_rule_shape, SH.property, priority_shape))
    g.add((validation_rule_shape, SH.property, target_shape))
    g.add((validation_rule_shape, SH.property, validator_shape))
    
    # Save the fixed ontology
    g.serialize('guidance_fixed.ttl', format='turtle')

if __name__ == "__main__":
    fix_guidance_ontology() 