from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from pyshacl import validate

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
SH = Namespace("http://www.w3.org/ns/shacl#")

def update_ontology():
    # Load the guidance ontology
    g = Graph()
    g.parse("guidance.ttl", format="turtle")
    
    # Create a new graph for SHACL shapes
    shapes_graph = Graph()
    
    # ValidationRule shape
    validation_rule_shape = GUIDANCE.ValidationRuleShape
    shapes_graph.add((validation_rule_shape, RDF.type, SH.NodeShape))
    shapes_graph.add((validation_rule_shape, SH.targetClass, GUIDANCE.ValidationRule))
    
    # Message property shape
    message_property = BNode()
    shapes_graph.add((validation_rule_shape, SH.property, message_property))
    shapes_graph.add((message_property, SH.path, GUIDANCE.hasMessage))
    shapes_graph.add((message_property, SH.datatype, XSD.string))
    shapes_graph.add((message_property, SH.minCount, Literal(1)))
    shapes_graph.add((message_property, SH.maxCount, Literal(1)))
    shapes_graph.add((message_property, SH.message, Literal("Validation rule must have a message")))
    
    # Target property shape
    target_property = BNode()
    shapes_graph.add((validation_rule_shape, SH.property, target_property))
    shapes_graph.add((target_property, SH.path, GUIDANCE.hasTarget))
    shapes_graph.add((target_property, SH.class_, GUIDANCE.ValidationTarget))
    shapes_graph.add((target_property, SH.minCount, Literal(1)))
    shapes_graph.add((target_property, SH.maxCount, Literal(1)))
    shapes_graph.add((target_property, SH.message, Literal("Validation rule must have a target")))
    
    # Priority property shape
    priority_property = BNode()
    priority_list = BNode()
    shapes_graph.add((validation_rule_shape, SH.property, priority_property))
    shapes_graph.add((priority_property, SH.path, GUIDANCE.hasPriority))
    shapes_graph.add((priority_property, SH.datatype, XSD.string))
    shapes_graph.add((priority_property, SH.minCount, Literal(1)))
    shapes_graph.add((priority_property, SH.maxCount, Literal(1)))
    shapes_graph.add((priority_property, SH.message, Literal("Priority must be HIGH, MEDIUM, or LOW")))
    
    # Create the list of allowed values
    shapes_graph.add((priority_property, SH.in_, priority_list))
    shapes_graph.add((priority_list, RDF.first, Literal("HIGH")))
    list_node1 = BNode()
    shapes_graph.add((priority_list, RDF.rest, list_node1))
    shapes_graph.add((list_node1, RDF.first, Literal("MEDIUM")))
    list_node2 = BNode()
    shapes_graph.add((list_node1, RDF.rest, list_node2))
    shapes_graph.add((list_node2, RDF.first, Literal("LOW")))
    shapes_graph.add((list_node2, RDF.rest, RDF.nil))
    
    # Validator property shape
    validator_property = BNode()
    shapes_graph.add((validation_rule_shape, SH.property, validator_property))
    shapes_graph.add((validator_property, SH.path, GUIDANCE.hasValidator))
    shapes_graph.add((validator_property, SH.datatype, XSD.string))
    shapes_graph.add((validator_property, SH.minCount, Literal(1)))
    shapes_graph.add((validator_property, SH.maxCount, Literal(1)))
    shapes_graph.add((validator_property, SH.message, Literal("Validation rule must have a validator")))
    
    # Rule type property shape
    rule_type_property = BNode()
    shapes_graph.add((validation_rule_shape, SH.property, rule_type_property))
    shapes_graph.add((rule_type_property, SH.path, GUIDANCE.hasRuleType))
    shapes_graph.add((rule_type_property, SH.class_, GUIDANCE.ValidationRuleType))
    shapes_graph.add((rule_type_property, SH.minCount, Literal(1)))
    shapes_graph.add((rule_type_property, SH.maxCount, Literal(1)))
    shapes_graph.add((rule_type_property, SH.message, Literal("Validation rule must have a rule type")))
    
    # ValidationTarget shape
    validation_target_shape = GUIDANCE.ValidationTargetShape
    shapes_graph.add((validation_target_shape, RDF.type, SH.NodeShape))
    shapes_graph.add((validation_target_shape, SH.targetClass, GUIDANCE.ValidationTarget))
    
    # Label property shape
    label_property = BNode()
    shapes_graph.add((validation_target_shape, SH.property, label_property))
    shapes_graph.add((label_property, SH.path, RDFS.label))
    shapes_graph.add((label_property, SH.minCount, Literal(1)))
    shapes_graph.add((label_property, SH.maxCount, Literal(1)))
    shapes_graph.add((label_property, SH.message, Literal("Validation target must have a label")))
    
    # Comment property shape
    comment_property = BNode()
    shapes_graph.add((validation_target_shape, SH.property, comment_property))
    shapes_graph.add((comment_property, SH.path, RDFS.comment))
    shapes_graph.add((comment_property, SH.minCount, Literal(1)))
    shapes_graph.add((comment_property, SH.maxCount, Literal(1)))
    shapes_graph.add((comment_property, SH.message, Literal("Validation target must have a comment")))
    
    # Update ValidationTargets
    validation_targets = [
        (GUIDANCE.SyntaxValidation, "Syntax Validation", "Target for syntax validation"),
        (GUIDANCE.SPOREValidation, "SPORE Validation", "Target for SPORE validation"),
        (GUIDANCE.SecurityValidation, "Security Validation", "Target for security validation"),
        (GUIDANCE.SemanticValidation, "Semantic Validation", "Target for semantic validation"),
        (GUIDANCE.InstallationValidation, "Installation Validation", "Target for installation validation"),
        (GUIDANCE.ConsistencyValidation, "Consistency Validation", "Target for consistency validation")
    ]
    
    # Remove existing labels and comments
    for target, _, _ in validation_targets:
        g.remove((target, RDFS.label, None))
        g.remove((target, RDFS.comment, None))
    
    # Add labels and comments
    for target, label, comment in validation_targets:
        g.add((target, RDFS.label, Literal(label)))
        g.add((target, RDFS.comment, Literal(comment)))
    
    # Update InstallationRule
    installation_rule = GUIDANCE.InstallationRule
    
    # Remove existing properties
    g.remove((installation_rule, GUIDANCE.hasMessage, None))
    g.remove((installation_rule, GUIDANCE.hasTarget, None))
    g.remove((installation_rule, GUIDANCE.hasPriority, None))
    g.remove((installation_rule, GUIDANCE.hasValidator, None))
    g.remove((installation_rule, GUIDANCE.hasRuleType, None))
    
    # Add required properties
    g.add((installation_rule, GUIDANCE.hasMessage, Literal("Installation command validation")))
    g.add((installation_rule, GUIDANCE.hasTarget, GUIDANCE.InstallationValidation))
    g.add((installation_rule, GUIDANCE.hasPriority, Literal("HIGH")))
    g.add((installation_rule, GUIDANCE.hasValidator, Literal("validate_installation.py")))
    g.add((installation_rule, GUIDANCE.hasRuleType, GUIDANCE.SHACL))
    
    # Validate the data graph against the shapes graph
    conforms, results_graph, results_text = validate(
        g,
        shacl_graph=shapes_graph,
        ont_graph=None,
        inference='rdfs',
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=False,
        debug=False,
        js=False
    )
    
    if not conforms:
        print("Validation failed:")
        print(results_text)
        return
    
    # Merge the shapes graph into the data graph
    g += shapes_graph
    
    # Save the updated ontology
    g.serialize("guidance.ttl", format="turtle")
    print("Ontology has been updated with consistent SHACL constraints and data.")

if __name__ == "__main__":
    update_ontology() 