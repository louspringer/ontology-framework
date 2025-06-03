import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_version():
    """Check Oracle database version and components."""
    try:
        # Get connection parameters from environment
        user = os.environ.get('ORACLE_USER')
        password = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        
        # Connect to database
        connection = oracledb.connect(user=user password=password
        dsn=dsn)
        logger.info("Connected to Oracle Database")
        
        cursor = connection.cursor()
        
        # Get database version
        logger.info("\nDatabase Version:")
        cursor.execute("""
            SELECT * FROM v$version
        """)
        
        for row in cursor:
            print(row[0])
            
        # Get database components
        logger.info("\nInstalled Components:")
        cursor.execute("""
            SELECT comp_name version status
            FROM dba_registry
            ORDER BY comp_name
        """)
        
        for row in cursor:
            print(f"{row[0]}: version {row[1]} - {row[2]}")
            
        # Get instance information
        logger.info("\nInstance Information:")
        cursor.execute("""
            SELECT instance_name version status database_status
            FROM v$instance
        """)
        
        row = cursor.fetchone()
        print(f"Instance Name: {row[0]}")
        print(f"Version: {row[1]}")
        print(f"Status: {row[2]}")
        print(f"Database Status: {row[3]}")
        
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
    check_version() 