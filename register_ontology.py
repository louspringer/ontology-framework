import oracledb
import os
import logging
import re
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("http://ontologies.louspringer.com/guidance#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
DEPLOYMENT = Namespace("./oracle_deployment#")

def get_absolute_uri(relative_path):
    """Convert a relative path to an absolute file:// URI"""
    abs_path = os.path.abspath(relative_path)
    return f"file://{os.path.dirname(abs_path)}"

def sanitize_name(name, max_length=25):
    """
    Sanitize a name to conform to Oracle naming conventions:
    - Uppercase
    - Start with letter
    - Only letters, numbers, and underscores
    - Max length (default 25 for model names)
    """
    # Convert to uppercase and replace non-alphanumeric with underscore
    name = re.sub(r'[^a-zA-Z0-9]', '_', name.upper())
    # Ensure starts with letter
    if not name[0].isalpha():
        name = 'O_' + name
    # Truncate to max length
    return name[:max_length]

def load_ontology(file_path):
    """Load an ontology file and return its graph"""
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

def get_ontology_info(graph):
    """Extract ontology information from the graph"""
    # Try to find the ontology declaration
    for s, p, o in graph.triples((None, RDF.type, OWL.Ontology)):
        ontology_uri = str(s)
        # Get label
        label = None
        for _, _, l in graph.triples((s, RDFS.label, None)):
            label = str(l)
            break
        # Get version
        version = None
        for _, _, v in graph.triples((s, OWL.versionInfo, None)):
            version = str(v)
            break
        return {
            'uri': ontology_uri,
            'label': label or Path(ontology_uri).stem,
            'version': version or '1.0.0'
        }
    
    # If no explicit ontology declaration found, infer from file and prefixes
    prefixes = dict(graph.namespaces())
    # Look for domain-specific prefix
    domain_prefix = None
    for prefix, uri in prefixes.items():
        if 'louspringer.com' in str(uri):
            domain_prefix = prefix
            break
    
    if domain_prefix:
        uri = str(prefixes[domain_prefix])
        # Extract name from URI
        name = uri.split('/')[-1].replace('#', '')
        return {
            'uri': uri,
            'label': name,
            'version': '1.0.0'
        }
    
    # Fallback to file name
    file_name = Path(graph.identifier).stem if graph.identifier else "unknown"
    return {
        'uri': f"http://ontologies.louspringer.com/{file_name}#",
        'label': file_name.replace('transformed_', ''),
        'version': '1.0.0'
    }

def register_ontology(ontology_path):
    """Register an ontology with Oracle RDF"""
    try:
        # Load and validate ontology
        logger.info(f"Loading ontology from {ontology_path}")
        graph = load_ontology(ontology_path)
        ontology_info = get_ontology_info(graph)
        
        if not ontology_info:
            raise ValueError("No ontology declaration found in the file")
            
        # Generate Oracle-compatible model name
        model_name = sanitize_name(ontology_info['label'])
        
        logger.info(f"Registering ontology:")
        logger.info(f"  URI: {ontology_info['uri']}")
        logger.info(f"  Label: {ontology_info['label']}")
        logger.info(f"  Version: {ontology_info['version']}")
        logger.info(f"  Model Name: {model_name}")
        
        # Connect to Oracle
        connection = oracledb.connect(
            user=os.environ.get('ORACLE_USER'),
            password=os.environ.get('ORACLE_PASSWORD'),
            dsn=os.environ.get('ORACLE_DSN')
        )
        logger.info("Connected to Oracle Database")
        
        cursor = connection.cursor()
        
        # Get current schema for network owner
        cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
        current_schema = cursor.fetchone()[0]
        
        # Drop existing model if it exists
        try:
            cursor.execute("""
                BEGIN
                    SEM_APIS.DROP_SEM_MODEL(
                        model_name => :model_name,
                        network_owner => :network_owner,
                        network_name => 'ONTOLOGY_FRAMEWORK'
                    );
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE != -55301 THEN
                            RAISE;
                        END IF;
                END;
            """, {'model_name': model_name, 'network_owner': current_schema})
            
            # Create RDF model in schema-private network
            cursor.execute("""
                BEGIN
                    SEM_APIS.CREATE_SEM_MODEL(
                        model_name => :model_name,
                        table_name => NULL,
                        column_name => NULL,
                        network_owner => :network_owner,
                        network_name => 'ONTOLOGY_FRAMEWORK'
                    );
                END;
            """, {
                'model_name': model_name,
                'network_owner': current_schema
            })
            
            connection.commit()
            logger.info(f"Created RDF model {model_name}")
            
            # Update session.ttl with registration info
            update_session_ttl(ontology_info, model_name)
            
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            logger.error(f"Database error: {error_obj.message}")
            if hasattr(error_obj, 'help'):
                logger.error(f"Help: {error_obj.help}")
            raise
            
        finally:
            if 'connection' in locals():
                connection.close()
                logger.info("Connection closed")
                
    except Exception as e:
        logger.error(f"Error registering ontology: {str(e)}")
        raise

def update_session_ttl(ontology_info, model_name, session_file=Path('session.ttl')):
    """Update session.ttl with registration information"""
    session_ttl = session_file
    if not session_ttl.exists():
        # Create session.ttl if it doesn't exist
        with open(session_ttl, 'w') as f:
            f.write("""@prefix : <file:///Users/lou/Documents/ontology-framework/session#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix guidance: <./guidance#> .
@prefix deployment: <./oracle_deployment#> .

:SessionOntology rdf:type owl:Ontology ;
    rdfs:label "Session Ontology" ;
    rdfs:comment "Tracks current work and next steps" ;
    owl:versionInfo "1.0.0" .

:RegisteredOntology rdf:type owl:Class ;
    rdfs:label "Registered Ontology" ;
    rdfs:comment "An ontology registered with Oracle RDF" ;
    rdfs:subClassOf deployment:DeployedModel .

:hasModelName rdf:type owl:DatatypeProperty ;
    rdfs:domain :RegisteredOntology ;
    rdfs:range xsd:string .

:hasVersion rdf:type owl:DatatypeProperty ;
    rdfs:domain :RegisteredOntology ;
    rdfs:range xsd:string .
""")
    
    # Load existing session graph
    session_graph = Graph()
    if session_ttl.exists():
        session_graph.parse(session_ttl, format="turtle")
    
    # Add registration info using proper RDFLib terms with absolute URIs
    base_uri = get_absolute_uri(session_ttl)
    SESSION = Namespace(f"{base_uri}/session#")
    registration_node = URIRef(f"{SESSION}{model_name}")
    session_graph.add((registration_node, RDF.type, SESSION.RegisteredOntology))
    session_graph.add((registration_node, SESSION.hasModelName, Literal(model_name)))
    session_graph.add((registration_node, SESSION.hasVersion, Literal(ontology_info['version'])))
    session_graph.add((registration_node, RDFS.label, Literal(ontology_info['label'])))
    
    # Save updated session.ttl
    session_graph.serialize(session_ttl, format="turtle")
    logger.info(f"Updated {session_ttl} with registration info")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python register_ontology.py <ontology_file>")
        sys.exit(1)
    register_ontology(sys.argv[1]) 