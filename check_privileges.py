import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_privileges():
    """Check RDF-related privileges."""
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
        
        # Check user privileges
        cursor.execute("""
            SELECT privilege
            FROM session_privs
            WHERE privilege LIKE '%RDF%'
               OR privilege LIKE '%SEM%'
               OR privilege LIKE '%MDSYS%'
            ORDER BY privilege
        """)
        
        print("Current user RDF-related privileges:")
        for row in cursor:
            print(f"- {row[0]}")
            
        # Check granted roles
        cursor.execute("""
            SELECT granted_role
            FROM user_role_privs
            ORDER BY granted_role
        """)
        
        print("\nGranted roles:")
        for row in cursor:
            print(f"- {row[0]}")
            
        # Check system privileges
        cursor.execute("""
            SELECT privilege
            FROM user_sys_privs
            ORDER BY privilege
        """)
        
        print("\nSystem privileges:")
        for row in cursor:
            print(f"- {row[0]}")
            
        # Check if RDF network exists
        cursor.execute("""
            SELECT table_name
            FROM all_tables
            WHERE owner = 'MDSYS'
              AND table_name LIKE 'RDF%'
            ORDER BY table_name
        """)
        
        print("\nMDSYS RDF tables:")
        for row in cursor:
            print(f"- {row[0]}")
        
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
    check_privileges() 