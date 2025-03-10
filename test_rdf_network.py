import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rdf_network():
    """Test RDF functionality using network tables directly."""
    try:
        # Connect to the database
        connection = oracledb.connect(
            user=os.environ.get('ORACLE_USER'),
            password=os.environ.get('ORACLE_PASSWORD'),
            dsn=os.environ.get('ORACLE_DSN')
        )
        logger.info("Connected to Oracle Database")
        
        cursor = connection.cursor()
        
        # Check RDF network parameters
        logger.info("\nChecking RDF network parameters...")
        cursor.execute("""
            SELECT param_name, param_value, param_desc 
            FROM MDSYS.RDF_PARAMETER$ 
            WHERE param_name LIKE 'NETWORK%'
        """)
        
        for row in cursor:
            print(f"{row[0]} = {row[1]}")
            print(f"Description: {row[2]}\n")
            
        # Create RDF model if it doesn't exist
        logger.info("\nCreating RDF model if it doesn't exist...")
        try:
            cursor.execute("""
                BEGIN
                    MDSYS.SEM_APIS.DROP_SEM_MODEL('ONTOLOGY_MODEL');
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE != -55301 THEN
                            RAISE;
                        END IF;
                END;
            """)
            
            cursor.execute("""
                BEGIN
                    MDSYS.SEM_APIS.CREATE_SEM_MODEL(
                        model_name => 'ONTOLOGY_MODEL',
                        table_name => 'ONTOLOGY_TRIPLES',
                        column_name => 'TRIPLE'
                    );
                END;
            """)
            connection.commit()
            logger.info("RDF model created successfully")
        except oracledb.DatabaseError as e:
            error_obj, = e.args
            logger.error(f"Error creating RDF model: {error_obj.message}")
            if "ORA-55301" not in error_obj.message:  # If error is not "model already exists"
                raise
            
        # Get model details
        logger.info("\nChecking RDF model details...")
        cursor.execute("""
            SELECT model_id, model_name, owner, table_name, column_name
            FROM MDSYS.SEM_MODEL$
            WHERE model_name = 'ONTOLOGY_MODEL'
        """)
        model_details = cursor.fetchone()
        if model_details:
            logger.info(f"Model ID: {model_details[0]}")
            logger.info(f"Model Name: {model_details[1]}")
            logger.info(f"Owner: {model_details[2]}")
            logger.info(f"Table Name: {model_details[3]}")
            logger.info(f"Column Name: {model_details[4]}")
            
            # Check table structure
            logger.info(f"\nChecking structure of {model_details[3]}...")
            cursor.execute(f"""
                SELECT column_name, data_type, data_length, nullable 
                FROM all_tab_columns 
                WHERE table_name = '{model_details[3]}' 
                AND owner = '{model_details[2]}'
                ORDER BY column_id
            """)
            columns = cursor.fetchall()
            
            if not columns:
                logger.error("No columns found for the RDF triple table")
                return
                
            logger.info("\nTable Structure:")
            for col in columns:
                logger.info(f"Column: {col[0]}, Type: {col[1]}, Length: {col[2]}, Nullable: {col[3]}")
            
            # Insert test triples
            logger.info("\nInserting test triples...")
            cursor.execute(f"""
                INSERT INTO {model_details[2]}.{model_details[3]} ({model_details[4]})
                VALUES (SDO_RDF_TRIPLE_S('ONTOLOGY_MODEL',
                    'http://example.org/person1',
                    'http://example.org/name',
                    'John Doe'))
            """)
            
            cursor.execute(f"""
                INSERT INTO {model_details[2]}.{model_details[3]} ({model_details[4]})
                VALUES (SDO_RDF_TRIPLE_S('ONTOLOGY_MODEL',
                    'http://example.org/person1',
                    'http://example.org/age',
                    '"30"^^<http://www.w3.org/2001/XMLSchema#integer>'))
            """)
            
            connection.commit()
            logger.info("Test triples inserted successfully")
            
            # Query the triples
            logger.info("\nQuerying all triples...")
            cursor.execute(f"""
                SELECT t.triple.GET_SUBJECT() subject,
                       t.triple.GET_PREDICATE() predicate,
                       t.triple.GET_OBJECT() object
                FROM {model_details[2]}.{model_details[3]} t
            """)
            
            for row in cursor:
                logger.info(f"Subject: {row[0]}")
                logger.info(f"Predicate: {row[1]}")
                logger.info(f"Object: {row[2]}\n")
                
        else:
            logger.error("RDF model not found after creation")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
        
    finally:
        if 'connection' in locals():
            connection.close()
            logger.info("Connection closed")

if __name__ == "__main__":
    test_rdf_network() 