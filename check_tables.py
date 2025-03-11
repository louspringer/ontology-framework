import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tables():
    """Check RDF table structures."""
    try:
        # Get connection parameters from environment
        user = os.environ.get('ORACLE_USER')
        password = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        
        # Connect to database
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        logger.info("Connected to Oracle Database")
        
        cursor = connection.cursor()
        
        # Check RDF tables
        cursor.execute("""
            SELECT table_name, column_name, data_type, data_length
            FROM user_tab_columns 
            WHERE table_name LIKE '%RDF%'
            ORDER BY table_name, column_name
        """)
        for row in cursor:
            print(row)
            
        # Check network tables
        cursor.execute("""
            SELECT table_name, column_name, data_type, data_length
            FROM user_tab_columns 
            WHERE table_name LIKE 'ONTOLOGY_NET#%'
            ORDER BY table_name, column_name
        """)
        for row in cursor:
            print(row)
        
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
    check_tables() 