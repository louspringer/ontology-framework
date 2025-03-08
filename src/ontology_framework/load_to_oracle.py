import oracledb
import os
import logging
from rdflib import Graph, URIRef, BNode, Literal
from pathlib import Path
from urllib.parse import urlparse
from ontology_framework.prefix_map import default_prefix_map

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
            WHERE tablespace_name = 'SYSAUX'
        """)
        quota = cursor.fetchone()
        if quota:
            logging.info(f"Quota on SYSAUX: {quota[0]}")
        else:
            logging.error("No quota on SYSAUX tablespace")
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
    """Connect to Oracle database using thin mode."""
    try:
        # Get password from environment variable
        password = os.getenv('ORACLE_PASSWORD')
        if not password:
            raise ValueError("Please set the ORACLE_PASSWORD environment variable")
            
        # Set global configuration
        os.environ['TNS_ADMIN'] = '/Users/lou/Oracle/network/admin/Wallet_tfm'
        oracledb.defaults.config_dir = '/Users/lou/Oracle/network/admin/Wallet_tfm'
        
        # Simple connection like VS Code
        connection = oracledb.connect(
            user='ADMIN',
            password=password,
            dsn='tfm_medium'
        )
        
        logger.info("Successfully connected to Oracle database")
        return connection
        
    except Exception as e:
        logger.error(f"Error connecting to Oracle: {str(e)}")
        if isinstance(e, oracledb.DatabaseError):
            error, = e.args
            logger.error(f"Oracle Error Code: {error.code}")
            logger.error(f"Oracle Error Message: {error.message}")
        raise

def transform_uri(uri_str):
    """Transform URIs to use ontologies.louspringer.com domain consistently.
    
    Args:
        uri_str: The URI string to transform
        
    Returns:
        Transformed URI using ontologies.louspringer.com domain
    """
    if uri_str.startswith('file:///'):
        # Extract the last part of the path after ontology-framework/
        parts = uri_str.split('ontology-framework/')
        if len(parts) > 1:
            return f'http://ontologies.louspringer.com/{parts[1]}'
        return uri_str
    elif uri_str.startswith('./'):
        # Handle relative URIs
        return f'http://ontologies.louspringer.com/{uri_str[2:]}'
    elif uri_str.startswith('http://example.org/') or uri_str.startswith('http://louspringer.com/'):
        # Replace example.org or louspringer.com with ontologies.louspringer.com
        return uri_str.replace(
            uri_str.split('/')[2], 
            'ontologies.louspringer.com'
        )
    return uri_str

def check_and_request_quota(conn):
    """Check and request quota on SYSAUX tablespace."""
    cursor = conn.cursor()
    try:
        # Check current quota
        cursor.execute("""
            SELECT bytes 
            FROM user_ts_quotas 
            WHERE tablespace_name = 'SYSAUX'
        """)
        quota = cursor.fetchone()
        
        if not quota:
            logging.info("Requesting quota on SYSAUX tablespace...")
            try:
                cursor.execute("ALTER USER ADMIN QUOTA UNLIMITED ON SYSAUX")
                conn.commit()
                logging.info("Quota granted on SYSAUX tablespace")
                return True
            except oracledb.DatabaseError as e:
                error, = e.args
                logging.error(f"Failed to grant quota: {error.message}")
                return False
        else:
            logging.info(f"Current quota on SYSAUX: {quota[0]} bytes")
            return True
            
    except oracledb.DatabaseError as e:
        error, = e.args
        logging.error(f"Error checking quota: {error.message}")
        return False
    finally:
        cursor.close()

def setup_semantic_network(connection):
    """Set up schema-private semantic network."""
    try:
        cursor = connection.cursor()
        
        # Try to create schema-private semantic network
        try:
            cursor.execute("""
                BEGIN
                    SEM_APIS.CREATE_SEM_NETWORK(
                        'SYSAUX',
                        network_owner => 'ADMIN',
                        network_name => 'ONTOLOGY_FRAMEWORK'
                    );
                END;
            """)
            connection.commit()
            logging.info("Created schema-private semantic network ONTOLOGY_FRAMEWORK")
        except oracledb.DatabaseError as e:
            error, = e.args
            if error.code == 55321:  # ORA-55321: network already exists
                logging.info("Schema-private semantic network ONTOLOGY_FRAMEWORK already exists.")
            else:
                raise
            
    except oracledb.DatabaseError as e:
        error, = e.args
        logging.error(f"Oracle error {error.code}: {error.message}")
        raise
    finally:
        cursor.close()

def load_ontology_to_oracle(connection, ttl_file_path):
    """Load an ontology from a TTL file into Oracle RDF store.
    
    Args:
        connection: Oracle database connection
        ttl_file_path: Path to the TTL file to load
    """
    # Create a new graph and bind our prefixes
    g = Graph()
    default_prefix_map.bind_to_graph(g)
    
    # Parse the TTL file
    g.parse(ttl_file_path, format="turtle")
    
    cursor = connection.cursor()
    
    try:
        # Create temporary table for bulk loading
        cursor.execute("""
            CREATE GLOBAL TEMPORARY TABLE TEMP_ONTOLOGY (
                triple SDO_RDF_TRIPLE_S
            ) ON COMMIT PRESERVE ROWS
        """)
        
        # Convert triples to Oracle RDF format and insert
        for s, p, o in g:
            # Transform URIs to use louspringer.com domain
            subject = transform_uri(s.n3())
            predicate = transform_uri(p.n3())
            obj = transform_uri(o.n3())
            
            # Insert the triple with 'META' as the model name
            cursor.execute("""
                INSERT INTO TEMP_ONTOLOGY (triple) VALUES (
                    SDO_RDF_TRIPLE_S('META', :1, :2, :3)
                )
            """, [subject, predicate, obj])
        
        # Bulk load into RDF model
        cursor.execute("""
            BEGIN
                SEM_APIS.BULK_LOAD_FROM_STAGING_TABLE(
                    model_name => 'META',
                    table_name => 'TEMP_ONTOLOGY',
                    column_name => 'TRIPLE',
                    tablespace => 'SYSAUX'
                );
            END;
        """)
        
        # Clean up temporary table
        cursor.execute("TRUNCATE TABLE TEMP_ONTOLOGY")
        cursor.execute("DROP TABLE TEMP_ONTOLOGY")
        
        # Commit the transaction
        connection.commit()
        
        logging.info(f"Successfully loaded {len(g)} triples into Oracle RDF store")
        
    except oracledb.DatabaseError as e:
        error, = e.args
        logging.error(f"Oracle error {error.code}: {error.message}")
        raise
    finally:
        cursor.close()

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
        
        # Load meta.ttl
        logger.info("Loading meta.ttl...")
        load_ontology_to_oracle(connection, "meta.ttl")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    main() 