import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_rdf_features():
    """Check available RDF features in the database."""
    try:
        # Get connection parameters from environment
        user = os.environ.get('ORACLE_USER')
        password = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        
        # Connect to database
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        logger.info("Connected to Oracle Database")
        
        cursor = connection.cursor()
        
        # Check for RDF-related objects
        logger.info("\nChecking for RDF-related objects...")
        cursor.execute("""
            SELECT owner, object_name, object_type 
            FROM all_objects 
            WHERE object_name LIKE '%RDF%' OR object_name LIKE '%SEM%'
            ORDER BY owner, object_type, object_name
        """)
        
        for row in cursor:
            print(f"{row[0]}.{row[1]} ({row[2]})")
            
        # Check database options
        logger.info("\nChecking database options...")
        cursor.execute("""
            SELECT parameter, value 
            FROM v$option 
            WHERE parameter LIKE '%RDF%' OR parameter LIKE '%SEM%'
            ORDER BY parameter
        """)
        
        for row in cursor:
            print(f"{row[0]} = {row[1]}")
            
        # Check database features
        logger.info("\nChecking database features...")
        cursor.execute("""
            SELECT comp_name, version, status 
            FROM dba_registry 
            WHERE comp_name LIKE '%RDF%' OR comp_name LIKE '%SEM%'
            ORDER BY comp_name
        """)
        
        for row in cursor:
            print(f"{row[0]} version {row[1]} - {row[2]}")
            
        # Check user privileges
        logger.info("\nChecking current user privileges...")
        cursor.execute("""
            SELECT privilege 
            FROM session_privs 
            WHERE privilege LIKE '%RDF%' OR privilege LIKE '%SEM%'
            ORDER BY privilege
        """)
        
        for row in cursor:
            print(f"Has privilege: {row[0]}")
            
    except oracledb.DatabaseError as e:
        error, = e.args
        logger.error(f"Oracle error {error.code}: {error.message}")
        if hasattr(error, 'help'):
            logger.error(f"Help: {error.help}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()
            logger.info("Connection closed")

if __name__ == "__main__":
    check_rdf_features() 