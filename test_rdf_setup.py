import oracledb
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_rdf_setup():
    """Test RDF network setup."""
    try:
        # Get connection parameters from environment
        user = os.environ.get('ORACLE_USER')
        password = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        
        # Connect to database
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        logger.info("Connected to Oracle Database")
        
        cursor = connection.cursor()
        
        # Check RDF network
        cursor.execute("""
            SELECT network_name, owner, tablespace_name
            FROM admin.ontology_net#rdf_parameter
            WHERE network_name = 'ONTOLOGY_NET'
        """)
        result = cursor.fetchone()
        if result:
            logger.info(f"Found RDF network: {result}")
        else:
            logger.error("RDF network not found")
            return False
        
        # Check RDF model
        cursor.execute("""
            SELECT model_name, owner, network_name
            FROM admin.ontology_net#sem_model$
            WHERE model_name = 'ONTOLOGY_MODEL'
        """)
        result = cursor.fetchone()
        if result:
            logger.info(f"Found RDF model: {result}")
        else:
            logger.error("RDF model not found")
            return False
        
        # Try to insert a test triple
        logger.info("Inserting test triple...")
        cursor.execute("""
            INSERT INTO admin.ontology_net#rdft_ontology_model(triple) VALUES (
                SDO_RDF_TRIPLE_S(
                    'ONTOLOGY_MODEL',
                    '<http://example.org/test>',
                    '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
                    '<http://example.org/TestClass>',
                    network_owner => 'ADMIN',
                    network_name => 'ONTOLOGY_NET'
                )
            )
        """)
        logger.info("Test triple inserted successfully")
        
        # Query the test triple
        logger.info("Querying test triple...")
        cursor.execute("""
            SELECT s.value_name, p.value_name, o.value_name
            FROM TABLE(SEM_MATCH(
                'SELECT ?s ?p ?o WHERE { ?s ?p ?o }',
                SEM_MODELS('ONTOLOGY_MODEL'),
                null,
                null,
                null,
                null,
                'NETWORK_OWNER=''ADMIN'' NETWORK_NAME=''ONTOLOGY_NET'''
            )) t,
            admin.ontology_net#rdf_value$ s,
            admin.ontology_net#rdf_value$ p,
            admin.ontology_net#rdf_value$ o
            WHERE t.s_id = s.value_id
            AND t.p_id = p.value_id
            AND t.o_id = o.value_id
        """)
        for row in cursor:
            logger.info(f"Found triple: {row}")
        
        connection.commit()
        logger.info("All operations completed successfully")
        return True
        
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
    test_rdf_setup() 