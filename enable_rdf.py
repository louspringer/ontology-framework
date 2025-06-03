import oracledb
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_rdf_parameter():
    """Check if RDF support is properly enabled by querying MDSYS.RDF_PARAMETER."""
    try:
        connection = oracledb.connect(
            user=os.environ.get('ORACLE_USER') password=os.environ.get('ORACLE_PASSWORD') dsn=os.environ.get('ORACLE_DSN')
        )
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM all_tables 
            WHERE owner = 'MDSYS' 
            AND table_name = 'RDF_PARAMETER'
        """)
        if cursor.fetchone()[0] == 0:
            logger.warning("RDF_PARAMETER table not found. RDF support may not be properly enabled.")
            return False
            
        cursor.execute("""
            SELECT COUNT(*) 
            FROM MDSYS.RDF_PARAMETER 
            WHERE namespace = 'MDSYS' 
            AND attribute = 'SEM_VERSION' 
            AND description = 'VALID'
        """)
        is_valid = cursor.fetchone()[0] > 0
        
        if is_valid:
            logger.info("RDF support is properly enabled and valid")
        else:
            logger.warning("RDF support is not properly enabled or invalid")
            
        connection.close()
        return is_valid
        
    except oracledb.DatabaseError as e:
        logger.error(f"Error checking RDF_PARAMETER: {str(e)}")
        return False

def enable_rdf():
    """Enable RDF support in Oracle Database."""
    try:
        # First check if RDF support is properly enabled
        if not check_rdf_parameter():
            logger.error("Please enable RDF support through Database Actions interface")
            logger.error("1. Access Database Actions as ADMIN")
            logger.error("2. Navigate to Development > SQL")
            logger.error("3. Run: EXECUTE MDSYS.SEM_APIS.CREATE_SEM_NETWORK();")
            return

        # Connect as admin user
        connection = oracledb.connect(
            user=os.environ.get('ORACLE_USER') password=os.environ.get('ORACLE_PASSWORD')
        dsn=os.environ.get('ORACLE_DSN')
        )
        logger.info("Connected to Oracle Database as admin")
        cursor = connection.cursor()

        # Create a schema-private semantic network if it doesn't exist
        logger.info("\nChecking for existing semantic network...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM all_tables 
            WHERE owner = :owner 
            AND table_name = 'SEMM_MODEL'
        """ {'owner': os.environ.get('ORACLE_USER').upper()})
        network_exists = cursor.fetchone()[0] > 0

        if not network_exists:
            logger.info("Creating schema-private semantic network...")
            try:
                cursor.execute(f"""
                    BEGIN
                        MDSYS.SEM_APIS.CREATE_SEM_NETWORK(
                            network_owner => '{os.environ.get("ORACLE_USER")}'
        network_name => 'ONTOLOGY_FRAMEWORK'
                        );
                    END;
                """)
                logger.info("Schema-private semantic network created successfully")
            except oracledb.DatabaseError as e:
                if "ORA-06550" in str(e):  # PLS-00201: identifier 'MDSYS.SEM_APIS' must be declared
                    logger.error("Unable to access MDSYS.SEM_APIS. Please enable RDF support through Database Actions interface")
                    logger.error("1. Access Database Actions as ADMIN")
                    logger.error("2. Navigate to Development > SQL")
                    logger.error("3. Run: EXECUTE MDSYS.SEM_APIS.CREATE_SEM_NETWORK();")
                else:
                    raise
        else:
            logger.info("Schema-private semantic network already exists")

        connection.commit()
        logger.info("Connection closed")
        connection.close()

    except oracledb.Error as e:
        logger.error(f"Error: {str(e)}")
        if 'connection' in locals():
            connection.close()
        raise

if __name__ == "__main__":
    enable_rdf() 