from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib.namespace import PROV, TIME
import datetime
import rdflib
from ontology_framework.tools.guidance_manager import GuidanceManager

def create_guidance_update():
    # Create a new graph
    g = Graph()
    
    # Define namespaces
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    PDCA = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/pdca#")
    WORKFLOW = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/workflow_setup_plan#")
    
    # Add namespace bindings
    g.bind("guidance", GUIDANCE)
    g.bind("pdca", PDCA)
    g.bind("workflow", WORKFLOW)
    g.bind("prov", PROV)
    g.bind("time", TIME)
    
    # Current PDCA Loop
    current_loop = GUIDANCE.CurrentPDCALoop
    g.add((current_loop, RDF.type, PDCA.PDCALoop))
    g.add((current_loop, RDFS.label, Literal("Current PDCA Loop")))
    g.add((current_loop, PDCA.hasStartTime, Literal(datetime.datetime.now().isoformat(), datatype=XSD.dateTime)))
    g.add((current_loop, PDCA.hasStatus, Literal("ACTIVE")))
    
    # Plan Phase
    plan_phase = GUIDANCE.PlanPhase
    g.add((plan_phase, RDF.type, PDCA.PlanPhase))
    g.add((current_loop, PDCA.hasPlanPhase, plan_phase))
    
    # Integration Steps
    steps = [
        ("Prefix Validation", "Validate prefix usage against prefix management rules", 1),
        ("Namespace Validation", "Validate namespace usage and relationships", 2),
        ("Model Conformance", "Check model against conformance rules", 3),
        ("Version Alignment", "Ensure version compatibility", 4)
    ]
    
    for label, description, order in steps:
        step = GUIDANCE[f"IntegrationStep{order}"]
        g.add((step, RDF.type, GUIDANCE.IntegrationStep))
        g.add((step, RDFS.label, Literal(label)))
        g.add((step, RDFS.comment, Literal(description)))
        g.add((step, GUIDANCE.stepOrder, Literal(str(order))))
        g.add((step, GUIDANCE.stepDescription, Literal(description)))
        g.add((plan_phase, PDCA.hasTask, step))
    
    # Test Protocol Requirements
    test_protocol = GUIDANCE.SampleTestProtocol
    g.add((test_protocol, RDF.type, GUIDANCE.TestProtocol))
    g.add((test_protocol, GUIDANCE.conformanceLevel, Literal("STRICT")))
    g.add((test_protocol, GUIDANCE.requiresPrefixValidation, Literal(True, datatype=XSD.boolean)))
    g.add((test_protocol, GUIDANCE.requiresNamespaceValidation, Literal(True, datatype=XSD.boolean)))
    
    # High Priority TODO Items
    todos = [
        ("Implement comprehensive error logging", "HIGH", "2024-04-18"),
        ("Add test coverage for all code updates", "HIGH", "2024-04-18")
    ]
    
    for description, priority, target_date in todos:
        todo = BNode()
        g.add((todo, RDF.type, GUIDANCE.TODO))
        g.add((todo, RDFS.comment, Literal(description)))
        g.add((todo, GUIDANCE.hasPriority, Literal(priority)))
        g.add((todo, GUIDANCE.hasTargetDate, Literal(target_date, datatype=XSD.date)))
        g.add((plan_phase, PDCA.hasTask, todo))
    
    # Validation Pipeline
    validation_pipeline = GUIDANCE.ValidationPipeline
    g.add((validation_pipeline, RDF.type, GUIDANCE.Process))
    g.add((validation_pipeline, RDFS.label, Literal("Validation Pipeline")))
    g.add((validation_pipeline, RDFS.comment, Literal("Automated validation pipeline for ontology development")))
    
    # Add pipeline steps
    pipeline_steps = [
        ("Prefix Validation", "Validate prefix usage and consistency"),
        ("Namespace Validation", "Validate namespace declarations and relationships"),
        ("Model Conformance", "Check model against conformance rules"),
        ("Version Compatibility", "Ensure version alignment"),
        ("Test Coverage", "Verify test coverage requirements")
    ]
    
    for label, description in pipeline_steps:
        step = BNode()
        g.add((step, RDF.type, GUIDANCE.ProcessStep))
        g.add((step, RDFS.label, Literal(label)))
        g.add((step, RDFS.comment, Literal(description)))
        g.add((validation_pipeline, GUIDANCE.hasStep, step))
    
    # Save the updated guidance
    g.serialize("guidance_updated.ttl", format="turtle")
    
    return g

def main():
    # Initialize guidance manager
    manager = GuidanceManager("guidance.ttl")
    
    # Start a transaction for our updates
    tx_id = manager.begin_transaction()
    
    try:
        # Add new validation rules
        manager.add_validation_rule(
            "NewRule1",
            "A new validation rule",
            "HIGH",
            ["pattern1", "pattern2"]
        )
        
        manager.add_validation_rule(
            "NewRule2",
            "Another validation rule",
            "MEDIUM",
            ["pattern3"]
        )
        
        # Add new validation patterns
        manager.add_validation_pattern(
            "NewPattern1",
            {"description": "A new validation pattern", "type": "Type1"}
        )
        
        manager.add_validation_pattern(
            "NewPattern2",
            {"description": "Another validation pattern", "type": "Type2"}
        )
        
        # Commit the transaction
        manager.commit_transaction(tx_id)
        print("Successfully updated guidance ontology")
        
    except Exception as e:
        # Rollback on error
        manager.rollback_transaction(tx_id)
        print(f"Error updating guidance ontology: {str(e)}")
        raise

if __name__ == "__main__":
    main() 