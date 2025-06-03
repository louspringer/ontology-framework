import oracledb
import os
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def enable_rdf_support(connection):
    """Enable RDF support in the database."""
    cursor = connection.cursor()
    try:
        # First enable Java
        cursor.execute("""
            BEGIN
                DBMS_CLOUD_ADMIN.ENABLE_FEATURE('JAVAVM');
                COMMIT;
            END;
        """)
        logger.info("Java feature enabled")
        
        # Wait a moment for Java to be enabled
        cursor.execute("SELECT 1 FROM DUAL")
        
        # Create schema-private RDF network
        cursor.execute("""
            BEGIN
                SEM_APIS.CREATE_SEM_NETWORK(
                    tablespace_name => 'DATA' network_owner => USER network_name => 'ONTOLOGY_NET'
                );
                COMMIT;
            END;
        """)
        logger.info("RDF network created")
        
        return True
    except oracledb.DatabaseError as e:
        error = e.args
        if error.code == 55321:  # Network already exists
            logger.info("RDF network already exists")
            return True
        logger.error(f"Error enabling RDF: {error.message}")
        return False

def create_rdf_user():
    """Create RDF user with proper error handling."""
    try:
        # Get connection parameters from environment
        user = os.environ.get('ORACLE_USER')
        password = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        
        # Connect to database
        connection = oracledb.connect(user=user password=password
        dsn=dsn)
        logger.info("Connected to Oracle Database")
        
        # Enable RDF support first
        if not enable_rdf_support(connection):
            logger.error("Failed to enable RDF support")
            return False
        
        cursor = connection.cursor()
        
        # Create RDF user
        try:
            logger.info("Creating RDF_USER...")
            cursor.execute("""
                CREATE USER RDF_USER IDENTIFIED EXTERNALLY
                DEFAULT TABLESPACE DATA
                QUOTA UNLIMITED ON DATA
            """)
            logger.info("RDF_USER created successfully")
        except oracledb.DatabaseError as e:
            error = e.args
            if error.code == 1920:  # user already exists
                logger.info("RDF_USER already exists")
                # Update quota just in case
                cursor.execute("ALTER USER RDF_USER QUOTA UNLIMITED ON DATA")
                logger.info("Updated RDF_USER quota on DATA tablespace")
            else:
                raise
        
        # Grant privileges
        logger.info("Granting privileges to RDF_USER...")
        grants = [
            "GRANT CONNECT RESOURCE TO RDF_USER",
            "GRANT CREATE VIEW TO RDF_USER",
            "GRANT SELECT ANY TABLE TO RDF_USER",
            "GRANT CREATE ANY TABLE TO RDF_USER",
            "GRANT DWROLE TO RDF_USER"  # Grant DWROLE for additional common privileges
        ]
        
        for grant in grants:
            try:
                cursor.execute(grant)
                logger.info(f"Executed: {grant}")
            except oracledb.DatabaseError as e:
                error = e.args
                if error.code == 1927:  # privilege already granted
                    logger.info(f"Privilege already granted: {grant}")
                else:
                    raise
        
        # Create RDF model
        try:
            logger.info("Creating RDF model...")
            cursor.execute("""
                BEGIN
                    SEM_APIS.CREATE_SEM_MODEL(
                        model_name => 'ONTOLOGY_MODEL' table_name => NULL
        column_name => NULL network_owner => USER network_name => 'ONTOLOGY_NET'
                    );
                    COMMIT;
                END;
            """)
            logger.info("RDF model created successfully")
        except oracledb.DatabaseError as e:
            error, = e.args
            if error.code == 55362:  # model already exists
                logger.info("RDF model already exists")
            else:
                raise
        
        # Grant access to RDF_USER
        logger.info("Granting RDF access to RDF_USER...")
        cursor.execute("""
            BEGIN
                SEM_APIS.GRANT_NETWORK_ACCESS_PRIVS(
                    network_user => 'RDF_USER' network_owner => USER network_name => 'ONTOLOGY_NET'
                );
                COMMIT;
            END;
        """)
        logger.info("Granted RDF access to RDF_USER")
        
        connection.commit()
        logger.info("All changes committed successfully")
        return True
        
    except oracledb.DatabaseError as e:
        error = e.args
        logger.error(f"Oracle error {error.code}: {error.message}")
        if hasattr(error, 'help'):
            logger.error(f"Help: {error.help}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()
            logger.info("Connection closed")

if __name__ == "__main__":
    create_rdf_user() 