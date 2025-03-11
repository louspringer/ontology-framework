import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_structure():
    """Check RDF parameter table structure."""
    try:
        # Get connection parameters from environment
        user = os.environ.get('ORACLE_USER')
        password = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        
        # Connect to database
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        logger.info("Connected to Oracle Database")
        
        cursor = connection.cursor()
        
        # Check table columns
        logger.info("\nChecking RDF parameter table columns...")
        cursor.execute("""
            SELECT column_name, data_type, data_length, nullable
            FROM all_tab_columns
            WHERE table_name = 'RDF_PARAMETER'
              AND owner = 'ADMIN'
              AND table_name LIKE 'ONTOLOGY_NET#%'
            ORDER BY column_id
        """)
        
        print("RDF Parameter Table Structure:")
        for row in cursor:
            print(f"Column: {row[0]}")
            print(f"  Type: {row[1]}({row[2]})")
            print(f"  Nullable: {row[3]}")
            print()
            
        # Check table contents
        logger.info("\nChecking RDF parameter table contents...")
        cursor.execute("""
            SELECT *
            FROM admin.ontology_net#rdf_parameter
        """)
        
        columns = [d[0] for d in cursor.description]
        print("\nColumns:", columns)
        
        print("\nData:")
        for row in cursor:
            for i, value in enumerate(row):
                print(f"{columns[i]}: {value}")
            print()
        
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
    check_table_structure() 