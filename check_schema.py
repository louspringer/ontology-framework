import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_schema():
    """Check RDF network schema name."""
    try:
        # Get connection parameters from environment
        user = os.environ.get('ORACLE_USER')
        password = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        
        # Connect to database
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        logger.info("Connected to Oracle Database")
        
        cursor = connection.cursor()
        
        # Check for RDF-related schemas
        cursor.execute("""
            SELECT DISTINCT owner 
            FROM all_tables 
            WHERE table_name LIKE '%RDF%'
            ORDER BY owner
        """)
        
        print("Schemas with RDF tables:")
        for row in cursor:
            print(row[0])
            
        # Check for SEM_APIS package
        cursor.execute("""
            SELECT owner, object_name, object_type
            FROM all_objects
            WHERE object_name LIKE 'SEM_APIS'
            ORDER BY owner
        """)
        
        print("\nSchemas with SEM_APIS package:")
        for row in cursor:
            print(f"{row[0]}.{row[1]} ({row[2]})")
        
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
    check_schema() 