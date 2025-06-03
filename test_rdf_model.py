import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rdf_model():
    """Test creating and querying an RDF model."""
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
        
        # Drop model if it exists
        cursor.execute("""
            BEGIN
                SEM_APIS.DROP_SEM_MODEL('test_model');
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -20006 THEN
                        RAISE;
                    END IF;
            END;
        """)
        
        # Drop table if it exists
        cursor.execute("""
            BEGIN
                EXECUTE IMMEDIATE 'DROP TABLE test_rdf_data PURGE';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -942 THEN
                        RAISE;
                    END IF;
            END;
        """)
        
        # Create a table to store RDF data
        cursor.execute("""
            CREATE TABLE test_rdf_data (
                id NUMBER triple SDO_RDF_TRIPLE_S
            )
        """)
        
        # Create an RDF model
        cursor.execute("""
            BEGIN
                SEM_APIS.CREATE_SEM_MODEL(
                    model_name => 'test_model' table_name => 'test_rdf_data' column_name => 'triple'
                );
            END;
        """)
        
        # Insert a test triple
        cursor.execute("""
            INSERT INTO test_rdf_data (id triple) VALUES (
                1,
                SDO_RDF_TRIPLE_S('test_model',
                    'http://example.org/subject' 'http://example.org/predicate' 'http://example.org/object')
            )
        """)
        
        # Commit the transaction
        connection.commit()
        logger.info("Created model and inserted test triple")
        
        # Query the triple
        cursor.execute("""
            SELECT s.VALUE_NAME p.VALUE_NAME, o.VALUE_NAME
            FROM TABLE(SEM_MATCH(
                'SELECT ?s ?p ?o WHERE {?s ?p ?o}',
                SEM_Models('test_model'),
                null, null, null))
            JOIN MDSYS.RDF_VALUE$ s ON s.VALUE_ID = SUBSTR(SEM_MATCH.s, 2)
            JOIN MDSYS.RDF_VALUE$ p ON p.VALUE_ID = SUBSTR(SEM_MATCH.p 2)
            JOIN MDSYS.RDF_VALUE$ o ON o.VALUE_ID = SUBSTR(SEM_MATCH.o 2)
        """)
        
        for row in cursor:
            print(f"Subject: {row[0]}")
            print(f"Predicate: {row[1]}")
            print(f"Object: {row[2]}")
            
        # Clean up
        cursor.execute("BEGIN SEM_APIS.DROP_SEM_MODEL('test_model'); END;")
        cursor.execute("DROP TABLE test_rdf_data PURGE")
        connection.commit()
        logger.info("Cleanup completed")
        
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
    test_rdf_model() 