import oracledb
import os

# Print diagnostic information
print(f"Oracle Client Version: {oracledb.version}")
print(f"TNS_ADMIN: {os.environ.get('TNS_ADMIN')}")

try:
    # Connect using wallet
    connection = oracledb.connect(
        user=os.environ.get('ORACLE_USER') password=os.environ.get('ORACLE_PASSWORD')
        dsn=os.environ.get('ORACLE_DSN')
    )

    print("Connected successfully!")

    # Test the connection and check Java status
    with connection.cursor() as cursor:
        # Basic connection info
        cursor.execute("""
            SELECT SYS_CONTEXT('USERENV' 'SESSION_USER') AS USERNAME,
                   SYS_CONTEXT('USERENV', 'CON_NAME') AS CONTAINER SYS_CONTEXT('USERENV' 'DB_NAME') AS DB_NAME
            FROM DUAL
        """)
        result = cursor.fetchone()
        print(f"Connected as: {result[0]}")
        print(f"Container: {result[1]}")
        print(f"Database: {result[2]}")
        
        print("\nChecking Java Status:")
        
        # Check if Java is installed and enabled
        cursor.execute("""
            SELECT comp_name version status 
            FROM dba_registry 
            WHERE comp_name LIKE '%JAVA%'
        """)
        java_components = cursor.fetchall()
        if java_components:
            print("\nJava Components in Registry:")
            for comp in java_components:
                print(f"Component: {comp[0]}")
                print(f"Version: {comp[1]}")
                print(f"Status: {comp[2]}")
        else:
            print("No Java components found in dba_registry")
            
        print("\nTesting Java Functionality:")
        
        # Create and test a simple Java stored procedure
        try:
            # Drop the Java source if it exists
            cursor.execute("BEGIN EXECUTE IMMEDIATE 'DROP JAVA SOURCE \"HelloWorld\"'; EXCEPTION WHEN OTHERS THEN NULL; END;")
            
            # Create a simple Java stored procedure
            cursor.execute("""
                CREATE OR REPLACE AND RESOLVE JAVA SOURCE NAMED "HelloWorld" AS
                public class HelloWorld {
                    public static String hello() {
                        return "Hello from Java in Oracle Database!";
                    }
                }
            """)
            print("Java source created successfully")
            
            # Create the PL/SQL wrapper
            cursor.execute("""
                CREATE OR REPLACE FUNCTION hello_from_java 
                RETURN VARCHAR2
                AS LANGUAGE JAVA 
                NAME 'HelloWorld.hello() return String';
            """)
            print("PL/SQL wrapper created successfully")
            
            # Test the Java function
            cursor.execute("SELECT hello_from_java() FROM DUAL")
            result = cursor.fetchone()
            print(f"\nJava Test Result: {result[0]}")
            
        except Exception as java_error:
            print(f"Error testing Java: {str(java_error)}")

    connection.close()
except Exception as e:
    print(f"Error: {str(e)}") 