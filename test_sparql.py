import oracledb
import os
import logging
from ontology_framework.load_to_oracle import (
    connect_to_oracle, 
    setup_semantic_network
)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_rdf_prerequisites(conn):
    """Check Oracle prerequisites for RDF/OWL with unlimited tablespace support."""
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
            WHERE granted_role IN ('CONNECT', 'RESOURCE', 'UNLIMITED TABLESPACE')
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
            WHERE privilege IN ('CREATE VIEW', 'UNLIMITED TABLESPACE')
        """)
        privileges = [p[0] for p in cursor.fetchall()]
        logging.info(f"User has privileges: {privileges}")
        
        if 'CREATE VIEW' not in privileges:
            logging.error("User does not have CREATE VIEW privilege")
            return False
            
        # Check if we have UNLIMITED TABLESPACE privilege
        if 'UNLIMITED TABLESPACE' not in privileges and 'UNLIMITED TABLESPACE' not in roles:
            # Check specific tablespace quota
            cursor.execute("""
                SELECT bytes 
                FROM user_ts_quotas 
                WHERE tablespace_name = 'SYSAUX'
            """)
            quota = cursor.fetchone()
            if not quota:
                logging.error("No quota on SYSAUX tablespace and no UNLIMITED TABLESPACE privilege")
                return False
            else:
                logging.info(f"Quota on SYSAUX: {quota[0]}")
        else:
            logging.info("User has UNLIMITED TABLESPACE privilege")
            
        # Check if RDF network exists
        try:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM MDSYS.RDF_PARAMETER_TABLE
            """)
            if cursor.fetchone()[0] > 0:
                logging.info("RDF network exists")
            else:
                logging.error("RDF network does not exist")
                return False
        except oracledb.DatabaseError as e:
            error, = e.args
            if error.code == 942:  # ORA-00942: table or view does not exist
                logging.error("RDF tables do not exist")
                return False
            raise
            
        return True
        
    except oracledb.DatabaseError as e:
        error, = e.args
        logging.error(f"Oracle error {error.code}: {error.message}")
        raise
    finally:
        cursor.close()

def enable_rdf_support(conn):
    """Enable RDF support in the database."""
    cursor = conn.cursor()
    try:
        # First enable Java
        cursor.execute("""
            BEGIN
                DBMS_CLOUD_ADMIN.ENABLE_FEATURE('JAVAVM');
                COMMIT;
            END;
        """)
        logging.info("Java feature enabled")
        
        # Wait a moment for Java to be enabled
        cursor.execute("SELECT 1 FROM DUAL")
        
        # Create RDF network
        cursor.execute("""
            BEGIN
                SEM_APIS.CREATE_SEM_NETWORK('ONTOLOGY_FRAMEWORK');
                COMMIT;
            END;
        """)
        logging.info("RDF network created")
        
        return True
    except oracledb.DatabaseError as e:
        error, = e.args
        if error.code == 55321:  # Network already exists
            logging.info("RDF network already exists")
            return True
        logging.error(f"Error enabling RDF: {error.message}")
        return False
    finally:
        cursor.close()

def test_sparql_crud():
    """Test SPARQL CRUD operations with the meta ontology."""
    try:
        # Connect using existing connection function
        connection = connect_to_oracle()
        print("Connected successfully!")
        
        with connection.cursor() as cursor:
            # Verify prerequisites are met
            if not check_rdf_prerequisites(connection):
                print("Enabling RDF support...")
                if not enable_rdf_support(connection):
                    raise Exception("Failed to enable RDF support")
                
                print("Setting up semantic network...")
                setup_semantic_network(connection)
                
                if not check_rdf_prerequisites(connection):
                    raise Exception("Prerequisites still not met after setup")
            
            print("\nTesting SPARQL queries:")
            
            # Test 1: Count all triples in the model
            print("\n1. Counting total triples:")
            try:
                cursor.execute("""
                    SELECT COUNT(1) 
                    FROM TABLE(SEM_MATCH(
                        'SELECT ?s ?p ?o WHERE { ?s ?p ?o }',
                        SEM_MODELS('META'),
                        null, null, null))
                """)
                count = cursor.fetchone()[0]
                print(f"Total triples in META model: {count}")
            except Exception as e:
                print(f"Error counting triples: {str(e)}")

            # Test 2: List all classes with their labels
            print("\n2. Listing all classes with labels:")
            try:
                cursor.execute("""
                    SELECT DISTINCT t.sub, t.label 
                    FROM TABLE(SEM_MATCH(
                        'SELECT ?class ?label 
                         WHERE { 
                             ?class rdf:type owl:Class . 
                             ?class rdfs:label ?label 
                         }',
                        SEM_MODELS('META'),
                        SEM_RULEBASES('RDFS'),
                        SEM_ALIASES(
                            SEM_ALIAS('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
                            SEM_ALIAS('rdfs', 'http://www.w3.org/2000/01/rdf-schema#'),
                            SEM_ALIAS('owl', 'http://www.w3.org/2002/07/owl#')
                        ),
                        null)) t
                """)
                results = cursor.fetchall()
                for row in results:
                    print(f"Class: {row[0]}")
                    print(f"Label: {row[1]}\n")
            except Exception as e:
                print(f"Error listing classes: {str(e)}")

            # Test 3: Find all properties of SecurityConcept
            print("\n3. Properties of SecurityConcept:")
            try:
                cursor.execute("""
                    SELECT DISTINCT t.prop, t.label 
                    FROM TABLE(SEM_MATCH(
                        'SELECT ?prop ?label 
                         WHERE { 
                             ?prop rdfs:domain meta:SecurityConcept .
                             ?prop rdfs:label ?label 
                         }',
                        SEM_MODELS('META'),
                        SEM_RULEBASES('RDFS'),
                        SEM_ALIASES(
                            SEM_ALIAS('rdfs', 'http://www.w3.org/2000/01/rdf-schema#'),
                            SEM_ALIAS('meta', 'http://ontologies.louspringer.com/meta#')
                        ),
                        null)) t
                """)
                results = cursor.fetchall()
                for row in results:
                    print(f"Property: {row[0]}")
                    print(f"Label: {row[1]}\n")
            except Exception as e:
                print(f"Error listing SecurityConcept properties: {str(e)}")

        connection.close()
        print("\nConnection closed.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_sparql_crud() 