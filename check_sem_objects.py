import os
import oracledb
import logging

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    # Log connection attempt
    logging.info("Attempting to connect with credentials:")
    logging.info(f"User: {os.environ.get('ORACLE_USER')}")
    logging.info(f"DSN: {os.environ.get('ORACLE_DSN')}")
    
    # Establish connection
    connection = oracledb.connect(
        user=os.environ['ORACLE_USER'],
        password=os.environ['ORACLE_PASSWORD'],
        dsn=os.environ['ORACLE_DSN']
    )
    logging.info(f"Successfully connected to Oracle Database {connection.version}")
    
    # Create cursor
    cursor = connection.cursor()
    
    # First check SEM_APIS specifically
    sem_apis_query = """
    SELECT owner, object_name, object_type, status 
    FROM all_objects 
    WHERE object_name = 'SEM_APIS'
    """
    logging.info(f"Executing query:\n{sem_apis_query}")
    cursor.execute(sem_apis_query)
    sem_apis_result = cursor.fetchall()
    logging.info(f"SEM_APIS check result: {sem_apis_result}")
    
    # Check user privileges
    privs_query = """
    SELECT * FROM session_privs 
    WHERE privilege LIKE '%SEM%' 
    OR privilege IN ('CREATE ANY TABLE', 'DROP ANY TABLE')
    """
    logging.info(f"Executing query:\n{privs_query}")
    cursor.execute(privs_query)
    privs_result = cursor.fetchall()
    logging.info("Current user privileges:")
    for priv in privs_result:
        logging.info(f"  - {priv[0]}")
        
    # Check execute privileges on SEM_APIS
    execute_privs_query = """
    SELECT table_name, privilege 
    FROM all_tab_privs 
    WHERE table_name LIKE '%SEM%'
    AND grantee = USER
    """
    logging.info(f"Checking execute privileges:\n{execute_privs_query}")
    cursor.execute(execute_privs_query)
    execute_privs = cursor.fetchall()
    logging.info("Execute privileges on SEM objects:")
    for priv in execute_privs:
        logging.info(f"  - {priv[0]}: {priv[1]}")
        
    # Check if we can see the actual package
    package_query = """
    SELECT text
    FROM all_source 
    WHERE name = 'SEM_APIS' 
    AND owner = 'MDSYS'
    AND rownum = 1
    """
    logging.info(f"Checking package source:\n{package_query}")
    cursor.execute(package_query)
    package_source = cursor.fetchone()
    if package_source:
        logging.info("Found package source")
    else:
        logging.info("No access to package source")
    
    # Query to check SEM* objects
    sem_objects_query = """
    SELECT object_name, object_type, status 
    FROM all_objects 
    WHERE owner = 'MDSYS' 
    AND object_name LIKE '%SEM%'
    ORDER BY object_type, object_name
    """
    logging.info(f"Executing query:\n{sem_objects_query}")
    cursor.execute(sem_objects_query)
    
    # Fetch and print results
    print("\nSEM* Objects in MDSYS:")
    print("=" * 80)
    print(f"{'OBJECT_NAME':<40} {'OBJECT_TYPE':<20} {'STATUS':<10}")
    print("-" * 80)
    
    for row in cursor:
        print(f"{row[0]:<40} {row[1]:<20} {row[2]:<10}")
    
    # Try to execute a simple SEM_APIS call
    test_query = """
    BEGIN
        -- Enable RDF functionality
        execute immediate 'ALTER SESSION SET CURRENT_SCHEMA = MDSYS';
        
        -- Now try to create semantic network
        sys.dbms_output.put_line('Testing SEM_APIS access...');
        sem_apis.create_sem_network(
            tablespace_name => 'rdf_tblspace',
            options => NULL
        );
        sys.dbms_output.put_line('Semantic network created');
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLCODE != -55321 THEN  -- Network already exists
                RAISE;
            END IF;
    END;
    """
    logging.info(f"Testing SEM_APIS access with:\n{test_query}")
    try:
        cursor.execute(test_query)
        logging.info("SEM_APIS test successful")
    except Exception as e:
        logging.error(f"SEM_APIS test failed: {str(e)}")
        logging.error(f"Oracle Error Code: {e.args[0].code if hasattr(e.args[0], 'code') else 'N/A'}")
        logging.error(f"Oracle Error Message: {e.args[0].message if hasattr(e.args[0], 'message') else str(e)}")
    
    # Try to create a test model
    logging.info("Attempting to create a test model...")
    test_model_query = """
    BEGIN
        -- Try to create a test model
        sys.dbms_output.put_line('Creating test model...');
        sem_apis.create_sem_model(
            model_name => 'TEST_MODEL',
            table_name => 'TEST_MODEL_TABLE',
            column_name => 'TRIPLE'
        );
        sys.dbms_output.put_line('Test model created successfully');
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLCODE != -29882 THEN  -- Model already exists
                RAISE;
            END IF;
            sys.dbms_output.put_line('Test model already exists');
    END;
    """
    logging.info(test_model_query)
    cursor.execute(test_model_query)
    logging.info("Model creation test successful")
    
    # Close cursor and connection
    cursor.close()
    connection.close()
    logging.info("Database connection closed successfully")

except oracledb.Error as error:
    logging.error(f"Oracle Error Code: {error.args[0].code if hasattr(error.args[0], 'code') else 'N/A'}")
    logging.error(f"Oracle Error Message: {error.args[0].message if hasattr(error.args[0], 'message') else str(error)}")
except Exception as error:
    logging.error(f"Error: {error}")
    logging.error(f"Error type: {type(error)}")
    if hasattr(error, '__dict__'):
        logging.error(f"Error attributes: {error.__dict__}") 