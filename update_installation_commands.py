import logging
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib.namespace import SH

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update.log'),
        logging.StreamHandler()
    ]
)

def log_graph_contents(graph, name):
    """Log the contents of a graph for debugging."""
    logging.info(f"\nContents of {name} graph:")
    for s, p, o in graph:
        logging.debug(f"Subject: {s}")
        logging.debug(f"Predicate: {p}")
        logging.debug(f"Object: {o}")
        logging.debug("---")

def main():
    try:
        logging.info("Starting installation commands update process")
        
        # Create a new graph
        g = Graph()
        logging.info("Created new RDF graph")

        # Define namespaces
        GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
        INSTALL = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/installation#")
        logging.info("Defined namespaces")

        # Load existing guidance ontology
        logging.info("Loading existing guidance ontology")
        g.parse("guidance.ttl", format="turtle")
        log_graph_contents(g, "initial")

        # Update validation rules with required properties
        logging.info("Updating validation rules with required properties")
        
        # Update ConsistencyRule
        consistency_rule = GUIDANCE.ConsistencyRule
        g.add((consistency_rule, GUIDANCE.hasRuleType, GUIDANCE.SHACL))
        g.add((consistency_rule, GUIDANCE.hasPriority, Literal("HIGH")))
        g.add((consistency_rule, GUIDANCE.hasTarget, GUIDANCE.ConsistencyValidation))
        g.add((consistency_rule, GUIDANCE.hasValidator, Literal("validate_consistency")))
        g.add((consistency_rule, GUIDANCE.hasMessage, Literal("Consistency validation failed")))

        # Update SPORERule
        spore_rule = GUIDANCE.SPORERule
        g.add((spore_rule, GUIDANCE.hasRuleType, GUIDANCE.STRUCTURAL))
        g.add((spore_rule, GUIDANCE.hasPriority, Literal("HIGH")))
        g.add((spore_rule, GUIDANCE.hasTarget, GUIDANCE.SPOREValidation))
        g.add((spore_rule, GUIDANCE.hasValidator, Literal("validate_spore")))
        g.add((spore_rule, GUIDANCE.hasMessage, Literal("SPORE validation failed")))

        # Update SemanticRule
        semantic_rule = GUIDANCE.SemanticRule
        g.add((semantic_rule, GUIDANCE.hasRuleType, GUIDANCE.SEMANTIC))
        g.add((semantic_rule, GUIDANCE.hasPriority, Literal("HIGH")))
        g.add((semantic_rule, GUIDANCE.hasTarget, GUIDANCE.SemanticValidation))
        g.add((semantic_rule, GUIDANCE.hasValidator, Literal("validate_semantic")))
        g.add((semantic_rule, GUIDANCE.hasMessage, Literal("Semantic validation failed")))

        # Update SyntaxRule
        syntax_rule = GUIDANCE.SyntaxRule
        g.add((syntax_rule, GUIDANCE.hasRuleType, GUIDANCE.SYNTAX))
        g.add((syntax_rule, GUIDANCE.hasPriority, Literal("HIGH")))
        g.add((syntax_rule, GUIDANCE.hasTarget, GUIDANCE.SyntaxValidation))
        g.add((syntax_rule, GUIDANCE.hasValidator, Literal("validate_syntax")))
        g.add((syntax_rule, GUIDANCE.hasMessage, Literal("Syntax validation failed")))

        # Add installation commands class and properties
        logging.info("Adding installation commands class and properties")
        g.add((INSTALL.InstallationCommand, RDF.type, OWL.Class))
        g.add((INSTALL.InstallationCommand, RDFS.label, Literal("Installation Command", lang="en")))
        g.add((INSTALL.InstallationCommand, RDFS.comment, Literal("Commands for installing dependencies and tools", lang="en")))

        # Add installation rule class with all required properties
        logging.info("Adding installation rule class with properties")
        g.add((INSTALL.InstallationRule, RDF.type, OWL.Class))
        g.add((INSTALL.InstallationRule, RDFS.label, Literal("Installation Rule", lang="en")))
        g.add((INSTALL.InstallationRule, RDFS.comment, Literal("Rules for installation validation", lang="en")))
        g.add((INSTALL.InstallationRule, GUIDANCE.hasMessage, Literal("Installation command validation", lang="en")))
        g.add((INSTALL.InstallationRule, GUIDANCE.hasRuleType, GUIDANCE.ValidationRuleType))
        g.add((INSTALL.InstallationRule, GUIDANCE.hasPriority, Literal("HIGH")))
        g.add((INSTALL.InstallationRule, GUIDANCE.hasValidator, Literal("installation_validator.py")))
        g.add((INSTALL.InstallationRule, GUIDANCE.hasTarget, INSTALL.InstallationValidation))

        # Add installation validation target
        logging.info("Adding installation validation target")
        g.add((INSTALL.InstallationValidation, RDF.type, GUIDANCE.ValidationTarget))
        g.add((INSTALL.InstallationValidation, RDFS.label, Literal("Installation Validation", lang="en")))
        g.add((INSTALL.InstallationValidation, RDFS.comment, Literal("Target for installation validation", lang="en")))

        # Add conda installation command
        logging.info("Adding conda installation command")
        conda_cmd = INSTALL.CondaInstallCommand
        g.add((conda_cmd, RDF.type, INSTALL.InstallationCommand))
        g.add((conda_cmd, RDFS.label, Literal("Conda Installation Command", lang="en")))
        g.add((conda_cmd, RDFS.comment, Literal("Command to install Conda package manager", lang="en")))
        g.add((conda_cmd, INSTALL.hasCommand, Literal("curl -L -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda3-latest-Linux-x86_64.sh -b")))

        # Add graphviz installation command
        logging.info("Adding graphviz installation command")
        graphviz_cmd = INSTALL.GraphvizInstallCommand
        g.add((graphviz_cmd, RDF.type, INSTALL.InstallationCommand))
        g.add((graphviz_cmd, RDFS.label, Literal("Graphviz Installation Command", lang="en")))
        g.add((graphviz_cmd, RDFS.comment, Literal("Command to install Graphviz development tools", lang="en")))
        g.add((graphviz_cmd, INSTALL.hasCommand, Literal("sudo apt-get update && sudo apt-get install -y graphviz graphviz-dev")))

        # Log final graph contents
        log_graph_contents(g, "final")

        # Save the updated ontology
        logging.info("Saving updated ontology to guidance_updated.ttl")
        g.serialize(destination="guidance_updated.ttl", format="turtle")
        logging.info("Update process completed successfully")

    except Exception as e:
        logging.error(f"Error during update process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()