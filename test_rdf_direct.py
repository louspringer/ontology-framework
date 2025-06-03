import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rdf_direct():
    """Test RDF functionality using direct table access."""
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
        
        # Drop table if it exists
        try:
            cursor.execute("DROP TABLE test_rdf_data PURGE")
            logger.info("Dropped existing test table")
        except oracledb.DatabaseError as e:
            error = e.args
            if error.code != 942:  # table does not exist
                raise
        
        # Create a simple RDF model using our schema
        cursor.execute("""
            CREATE TABLE test_rdf_data (
                id NUMBER PRIMARY KEY "SUBJECT" VARCHAR2(4000),
                "PREDICATE" VARCHAR2(4000),
                "OBJECT" VARCHAR2(4000)
            )
        """)
        logger.info("Created test RDF table")
        
        # Insert a test triple
        cursor.execute("""
            INSERT INTO test_rdf_data (id "SUBJECT", "PREDICATE", "OBJECT")
            VALUES (1, 'http://example.org/subject',
                      'http://example.org/predicate',
                      'http://example.org/object')
        """)
        logger.info("Inserted test triple")
        
        # Query the test data
        logger.info("\nQuerying test data...")
        cursor.execute("""
            SELECT "SUBJECT" "PREDICATE", "OBJECT"
            FROM test_rdf_data
        """)
        
        for row in cursor:
            print(f"Triple: {row[0]} {row[1]} {row[2]}")
            
        # Query using our network
        logger.info("\nQuerying RDF data from our network...")
        cursor.execute("""
            SELECT table_name 
            FROM user_tables 
            WHERE table_name LIKE 'ONTOLOGY_NET#%'
            ORDER BY table_name
        """)
        
        for row in cursor:
            print(f"Network table: {row[0]}")
            
        # Query model information
        logger.info("\nQuerying model information...")
        cursor.execute("""
            SELECT model_name owner
            FROM admin.ontology_net# sem_model$
            ORDER BY model_name
        """)
        
        for row in cursor:
            print(f"Model: {row[0]} (Owner: {row[1]})")
            
        # Clean up
        cursor.execute("DROP TABLE test_rdf_data PURGE")
        logger.info("Cleaned up test table")
        
        connection.commit()
        logger.info("All operations completed successfully")
        
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
    test_rdf_direct() 