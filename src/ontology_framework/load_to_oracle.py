import oracledb
import os
import logging
from rdflib import Graph, URIRef, BNode, Literal
from pathlib import Path
from urllib.parse import urlparse
from ontology_framework.prefix_map import default_prefix_map
import time
import re
from datetime import datetime
from typing import Optional
import rdflib

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_prerequisites(conn):
    """Check Oracle prerequisites for RDF/OWL."""
    logging.info("Checking Oracle prerequisites...")
    cursor = conn.cursor()
    
    try:
        # Check Oracle version
        cursor.execute("SELECT version FROM v$instance")
        version = cursor.fetchone()[0]
        logging.info(f"Oracle version: {version}")
        
        # Check Spatial component
        cursor.execute("""
            SELECT comp_name, version, status
            FROM dba_registry
            WHERE comp_name LIKE 'Spatial%'
        """)
        spatial = cursor.fetchone()
        if spatial:
            logging.info(f"Spatial component: {spatial[0]}, version {spatial[1]}, status {spatial[2]}")
        else:
            logging.error("Spatial component not found")
            return False
            
        # Check Partitioning option
        cursor.execute("""
            SELECT value 
            FROM v$option 
            WHERE parameter = 'Partitioning'
        """)
        partitioning = cursor.fetchone()
        if partitioning and partitioning[0] == 'TRUE':
            logging.info("Partitioning option is enabled")
        else:
            logging.error("Partitioning option is not enabled - required for RDF support")
            return False
            
        # Check user roles
        cursor.execute("""
            SELECT granted_role
            FROM user_role_privs
            WHERE granted_role IN ('CONNECT', 'RESOURCE')
        """)
        roles = [r[0] for r in cursor.fetchall()]
        logging.info(f"User has roles: {roles}")
        
        if not ('CONNECT' in roles and 'RESOURCE' in roles):
            logging.error("User does not have required CONNECT and RESOURCE roles")
            return False
        
        # Check CREATE VIEW privilege
        cursor.execute("""
            SELECT privilege 
            FROM user_sys_privs 
            WHERE privilege = 'CREATE VIEW'
        """)
        has_create_view = cursor.fetchone() is not None
        logging.info(f"User has CREATE VIEW privilege: {has_create_view}")
        
        if not has_create_view:
            logging.error("User does not have CREATE VIEW privilege")
            return False
        
        # Check available tablespaces
        cursor.execute("""
            SELECT tablespace_name, status, contents
            FROM dba_tablespaces
            ORDER BY tablespace_name
        """)
        tablespaces = cursor.fetchall()
        logging.info("Available tablespaces:")
        for ts in tablespaces:
            logging.info(f"  {ts[0]}: status={ts[1]}, contents={ts[2]}")
        
        # Check tablespace quota
        cursor.execute("""
            SELECT bytes 
            FROM user_ts_quotas 
            WHERE tablespace_name = 'DATA'
        """)
        quota = cursor.fetchone()
        if quota:
            logging.info(f"Quota on DATA: {quota[0]}")
        else:
            logging.error("No quota on DATA tablespace")
            return False
            
        # Check if USER_SEM_NETWORKS view exists
        try:
            cursor.execute("SELECT COUNT(*) FROM USER_SEM_NETWORKS")
            logging.info("USER_SEM_NETWORKS view exists")
        except oracledb.DatabaseError as e:
            error, = e.args
            if error.code == 942:  # ORA-00942: table or view does not exist
                logging.error("USER_SEM_NETWORKS view does not exist - RDF support may not be enabled")
                return False
            raise
            
        return True
        
    except oracledb.DatabaseError as e:
        error, = e.args
        logging.error(f"Oracle error {error.code}: {error.message}")
        raise
    finally:
        cursor.close()

def connect_to_oracle():
    """Connect to Oracle database using environment variables."""
    wallet_location = os.getenv('WALLET_LOCATION')
    if not wallet_location:
        raise ValueError("WALLET_LOCATION environment variable not set")
    
    user = os.getenv('ORACLE_USER')
    if not user:
        raise ValueError("ORACLE_USER environment variable not set")
    
    password = os.getenv('ORACLE_PASSWORD')
    if not password:
        raise ValueError("ORACLE_PASSWORD environment variable not set")
    
    dsn = os.getenv('ORACLE_DSN')
    if not dsn:
        raise ValueError("ORACLE_DSN environment variable not set")

    os.environ['TNS_ADMIN'] = wallet_location
    connection = oracledb.connect(user=user, password=password, dsn=dsn)
    return connection

def check_and_request_quota(connection):
    """Check and request quota on the DATA tablespace."""
    cursor = connection.cursor()
    user = os.getenv('ORACLE_USER')
    try:
        cursor.execute(f"ALTER USER {user} QUOTA UNLIMITED ON DATA")
        connection.commit()
    except Exception as e:
        print(f"Warning: Could not set quota on DATA tablespace: {e}")
    finally:
        cursor.close()

def setup_semantic_network(connection):
    """Set up the semantic network."""
    cursor = connection.cursor()
    try:
        # Check if semantic network exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM USER_SEM_NETWORKS 
            WHERE NETWORK_NAME = 'ONTOLOGY_FRAMEWORK'
        """)
        exists = cursor.fetchone()[0] > 0

        if not exists:
            # Create schema-private semantic network
            cursor.execute("""
                BEGIN
                    MDSYS.SEM_APIS.CREATE_SEM_NETWORK(
                        tablespace_name => 'DATA',
                        network_owner => USER,
                        network_name => 'ONTOLOGY_FRAMEWORK'
                    );
                END;
            """)
            connection.commit()
            print("Created schema-private semantic network ONTOLOGY_FRAMEWORK")
        else:
            print("Schema-private semantic network ONTOLOGY_FRAMEWORK already exists")

    except Exception as e:
        print(f"Warning: Error checking/creating semantic network: {e}")
    finally:
        cursor.close()

def sanitize_model_name(model_name: str) -> str:
    """
    Sanitize the model name to conform to Oracle requirements.
    - Remove non-alphanumeric characters
    - Ensure it starts with a letter
    - Truncate to 25 characters (Oracle's limit for RDF model names)
    - Remove 'transformed_' prefix to save space
    """
    # Remove 'transformed_' prefix if present
    model_name = model_name.replace('transformed_', '')
    
    # Remove non-alphanumeric characters and replace with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', model_name)
    
    # Ensure it starts with a letter
    if not sanitized[0].isalpha():
        sanitized = 'M_' + sanitized
    
    # Truncate to 25 characters
    return sanitized[:25].upper()

def check_model_exists(connection, model_name: str) -> bool:
    """Check if a model already exists in the schema-private network."""
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ONTOLOGY_FRAMEWORK#SEM_MODEL$ 
            WHERE MODEL_NAME = :model_name
        """, {'model_name': model_name})
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Warning: Could not check if model exists: {e}")
        return False
    finally:
        cursor.close()

def drop_model(connection, model_name: str) -> None:
    """Drop an existing model from the schema-private network."""
    cursor = connection.cursor()
    try:
        cursor.execute("""
            BEGIN
                SEM_APIS.DROP_SEM_MODEL(
                    model_name => :model_name,
                    network_owner => USER,
                    network_name => 'ONTOLOGY_FRAMEWORK'
                );
            END;
        """, {'model_name': model_name})
        connection.commit()
        print(f"Dropped existing model {model_name}")
    except Exception as e:
        print(f"Warning: Could not drop model: {e}")
        connection.rollback()
    finally:
        cursor.close()

def escape_rdf_value(connection, value: str) -> str:
    """
    Use Oracle's built-in RDF value escaping function.
    """
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT SEM_APIS.ESCAPE_RDF_VALUE(:1) FROM DUAL", [value])
        result = cursor.fetchone()[0]
        return result if result is not None else value
    except Exception as e:
        print(f"Warning: Could not escape RDF value: {e}")
        return value
    finally:
        cursor.close()

def preprocess_literal(connection, value):
    """Preprocess literal values for Oracle RDF."""
    if isinstance(value, Literal):
        # Handle datatype URIs
        if value.datatype:
            datatype = str(value.datatype)
            val_str = str(value)
            
            # Handle datetime
            if datatype == "http://www.w3.org/2001/XMLSchema#dateTime":
                try:
                    # If no time component, add it
                    if 'T' not in val_str:
                        val_str = f"{val_str}T00:00:00"
                    
                    # Handle timezone
                    if not any(x in val_str for x in ['+', '-', 'Z']):
                        val_str = f"{val_str}+00:00"
                    
                    # Parse and format datetime
                    dt = datetime.fromisoformat(val_str.replace('Z', '+00:00'))
                    return dt.isoformat()
                except (ValueError, TypeError):
                    # Return a default datetime for invalid values
                    return "2024-01-01T00:00:00+00:00"
            
            # Handle integers
            elif datatype == "http://www.w3.org/2001/XMLSchema#integer":
                try:
                    # Extract first number from string (handles ranges and other formats)
                    num_match = re.search(r'-?\d+', val_str)
                    if num_match:
                        return str(int(num_match.group()))
                    return '0'
                except (ValueError, TypeError):
                    return '0'
            
            # Handle other datatypes
            elif datatype == "http://www.w3.org/2001/XMLSchema#string":
                return escape_rdf_value(connection, val_str)
            elif datatype == "http://www.w3.org/2001/XMLSchema#boolean":
                return str(bool(value)).lower()
            elif datatype == "http://www.w3.org/2001/XMLSchema#decimal":
                try:
                    return str(float(val_str))
                except (ValueError, TypeError):
                    return '0.0'
            elif datatype == "http://www.w3.org/2001/XMLSchema#anyURI":
                return val_str  # Preserve URIs exactly as is
    
    # For non-Literal values or no datatype
    return escape_rdf_value(connection, str(value))

def format_rdf_value(value: rdflib.term.Node) -> str:
    """Format an RDF value for Oracle.
    
    Args:
        value: RDFLib node to format
        
    Returns:
        Formatted string value
    """
    if isinstance(value, rdflib.URIRef):
        # URIs are wrapped in angle brackets
        return f"<{str(value)}>"
    elif isinstance(value, rdflib.Literal):
        if value.datatype:
            # Handle typed literals
            if value.datatype == rdflib.XSD.integer:
                # For integer ranges, take first number
                try:
                    num = str(value).split('-')[0]
                    return f'"{int(num)}"^^<{rdflib.XSD.integer}>'
                except (ValueError, IndexError):
                    return f'"0"^^<{rdflib.XSD.integer}>'
            elif value.datatype == rdflib.XSD.string:
                # Escape quotes and backslashes in string literals
                val_str = str(value)
                # Double escape backslashes first
                val_str = val_str.replace('\\', '\\\\')
                # Then escape quotes
                val_str = val_str.replace('"', '\\"')
                return f'"{val_str}"^^<{rdflib.XSD.string}>'
            else:
                # Other typed literals - preserve as is but escape quotes
                val_str = str(value).replace('"', '\\"')
                return f'"{val_str}"^^<{value.datatype}>'
        elif value.language:
            # Language tagged literals
            escaped = str(value).replace('"', '\\"')
            return f'"{escaped}"@{value.language}'
        else:
            # Plain literals
            escaped = str(value).replace('"', '\\"')
            return f'"{escaped}"'
    else:
        # BNodes are prefixed with _:
        return f"_:{value}"

def load_ontology_to_oracle(connection: oracledb.Connection, ttl_file: str, model_name: Optional[str] = None) -> None:
    """
    Load an ontology file into Oracle.
    
    Args:
        connection: Oracle database connection
        ttl_file: Path to the TTL file to load
        model_name: Optional model name (defaults to sanitized file name without extension)
    """
    if model_name is None:
        model_name = os.path.splitext(os.path.basename(ttl_file))[0]
    
    model_name = sanitize_model_name(model_name)
    print(f"Loading {ttl_file} into model {model_name}")
    
    # Check if model exists and drop it
    if check_model_exists(connection, model_name):
        print(f"Model {model_name} already exists, dropping it...")
        drop_model(connection, model_name)
    
    # Parse the TTL file
    g = Graph()
    g.parse(ttl_file, format="turtle")
    
    cursor = connection.cursor()
    try:
        # Create staging table with exact Oracle requirements
        staging_table = f"STAGE_{model_name}"
        cursor.execute(f"""
            CREATE TABLE {staging_table} (
                RDF$STC_sub VARCHAR2(4000) NOT NULL,
                RDF$STC_pred VARCHAR2(4000) NOT NULL,
                RDF$STC_obj VARCHAR2(4000) NOT NULL
            )
        """)
        
        # Insert triples into staging table
        insert_sql = f"""
            INSERT INTO {staging_table} (RDF$STC_sub, RDF$STC_pred, RDF$STC_obj)
            VALUES (:1, :2, :3)
        """
        
        # Process and insert triples
        batch = []
        for s, p, o in g:
            # Format each component in N-Triples format
            subj = format_rdf_value(s)
            pred = format_rdf_value(p)
            obj = format_rdf_value(o)
            
            if len(obj) <= 4000:  # Oracle's VARCHAR2 limit
                batch.append((subj, pred, obj))
        
        # Bulk insert using executemany
        cursor.executemany(insert_sql, batch)
        
        # Create the model with correct parameters for schema-private network
        cursor.execute(f"""
            BEGIN
                SEM_APIS.CREATE_SEM_MODEL(
                    model_name => '{model_name}',
                    table_name => NULL,
                    column_name => NULL,
                    network_owner => USER,
                    network_name => 'ONTOLOGY_FRAMEWORK'
                );
            END;
        """)
        
        # Get current schema for table_owner parameter
        cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
        current_schema = cursor.fetchone()[0]
        
        # Bulk load from staging table with correct parameters
        cursor.execute(f"""
            BEGIN
                SEM_APIS.BULK_LOAD_FROM_STAGING_TABLE(
                    model_name => '{model_name}',
                    table_owner => '{current_schema}',
                    table_name => '{staging_table}',
                    flags => 'PARALLEL=4 PARALLEL_CREATE_INDEX DEL_BATCH_DUPS=USE_INSERT'
                );
            END;
        """)
        
        # Commit the transaction
        connection.commit()
        print(f"Successfully loaded {len(batch)} triples into model {model_name}")
        
    except Exception as e:
        print(f"Error loading ontology {ttl_file}: {e}")
        connection.rollback()
        raise
    finally:
        # Clean up staging table
        try:
            cursor.execute(f"DROP TABLE {staging_table} PURGE")
            connection.commit()
        except Exception as e:
            print(f"Warning: Could not drop staging table: {e}")
        cursor.close()

def get_model_triples(connection: oracledb.Connection, model_name: str) -> set:
    """Get all triples from an Oracle RDF model.
    
    Args:
        connection: Oracle database connection
        model_name: Name of the model to query
        
    Returns:
        Set of (subject, predicate, object) tuples
    """
    cursor = connection.cursor()
    try:
        # Get current schema for network owner
        cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
        current_schema = cursor.fetchone()[0]
        
        # Query all triples using SEM_MATCH with schema-private network parameters
        cursor.execute("""
            SELECT s, p, o
            FROM TABLE(SEM_MATCH(
                'SELECT ?s ?p ?o WHERE { ?s ?p ?o }',
                SEM_MODELS(UPPER(:model_name)),
                NULL,
                NULL,
                NULL,
                :network_owner,
                'HINT0={ LEADING(?s) USE_NL(?s ?p) USE_NL(?p ?o) } ',
                NULL,
                NULL,
                :network_name
            ))
        """, {
            'model_name': model_name,
            'network_owner': current_schema,
            'network_name': 'ONTOLOGY_FRAMEWORK'
        })
        
        # Convert Oracle RDF terms to N-Triples format
        triples = set()
        for s, p, o in cursor:
            # Oracle returns RDF terms in N-Triples format
            triples.add((s, p, o))
        
        return triples
        
    finally:
        cursor.close()

def get_file_triples(ttl_file: str) -> set:
    """Get all triples from a TTL file.
    
    Args:
        ttl_file: Path to the TTL file
        
    Returns:
        Set of (subject, predicate, object) tuples in N-Triples format
    """
    g = Graph()
    g.parse(ttl_file, format="turtle")
    
    # Convert to N-Triples format for comparison
    triples = set()
    for s, p, o in g:
        subj = format_rdf_value(s)
        pred = format_rdf_value(p)
        obj = format_rdf_value(o)
        triples.add((subj, pred, obj))
    
    return triples

def validate_model(connection: oracledb.Connection, ttl_file: str, model_name: Optional[str] = None) -> bool:
    """Validate semantic equivalence between TTL file and Oracle model.
    
    Args:
        connection: Oracle database connection
        ttl_file: Path to the TTL file
        model_name: Optional model name (defaults to sanitized file name without extension)
        
    Returns:
        True if semantically equivalent, False otherwise
    """
    if model_name is None:
        model_name = os.path.splitext(os.path.basename(ttl_file))[0]
    model_name = sanitize_model_name(model_name)
    
    print(f"\nValidating semantic equivalence for {ttl_file} against model {model_name}...")
    
    # Get triples from both sources
    file_triples = get_file_triples(ttl_file)
    model_triples = get_model_triples(connection, model_name)
    
    # Compare triple sets
    missing_in_model = file_triples - model_triples
    extra_in_model = model_triples - file_triples
    
    if not missing_in_model and not extra_in_model:
        print("✓ Model is semantically equivalent to source file")
        print(f"  Total triples: {len(file_triples)}")
        return True
    
    if missing_in_model:
        print("✗ Triples in source file but missing from model:")
        for s, p, o in sorted(missing_in_model)[:5]:  # Show first 5 differences
            print(f"  {s} {p} {o} .")
        if len(missing_in_model) > 5:
            print(f"  ... and {len(missing_in_model) - 5} more")
    
    if extra_in_model:
        print("✗ Extra triples in model not in source file:")
        for s, p, o in sorted(extra_in_model)[:5]:  # Show first 5 differences
            print(f"  {s} {p} {o} .")
        if len(extra_in_model) > 5:
            print(f"  ... and {len(extra_in_model) - 5} more")
    
    return False

def validate_loaded_models(connection: oracledb.Connection, models_to_validate: list[str]) -> None:
    """Validate a list of loaded models against their source files.
    
    Args:
        connection: Oracle database connection
        models_to_validate: List of TTL file paths to validate
    """
    print("\nStarting semantic validation of loaded models...")
    
    success_count = 0
    failure_count = 0
    
    for ttl_file in models_to_validate:
        try:
            if validate_model(connection, ttl_file):
                success_count += 1
            else:
                failure_count += 1
        except Exception as e:
            print(f"Error validating {ttl_file}: {e}")
            failure_count += 1
    
    print(f"\nValidation complete: {success_count} passed, {failure_count} failed")

def main():
    """Main function to load ontologies into Oracle."""
    try:
        # Connect to Oracle
        connection = connect_to_oracle()
        
        # Check prerequisites
        logger.info("Checking prerequisites...")
        check_prerequisites(connection)
        
        # Set up semantic network
        setup_semantic_network(connection)
        
        # Track successfully loaded models for validation
        loaded_models = []
        
        # Load meta.ttl
        logger.info("Loading meta.ttl...")
        try:
            load_ontology_to_oracle(connection, "meta.ttl", "META")
            loaded_models.append("meta.ttl")
        except Exception as e:
            logger.error(f"Error loading meta.ttl: {e}")
        
        # Validate loaded models
        if loaded_models:
            validate_loaded_models(connection, loaded_models)
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    main() 