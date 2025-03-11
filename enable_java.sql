-- Check Java components
SELECT comp_name, status, version FROM dba_registry WHERE comp_name LIKE '%JAVA%';

-- Enable Java
ALTER SESSION SET JAVA_JIT_ENABLED = TRUE;

-- Check Java settings
SELECT property_name, property_value 
FROM database_properties 
WHERE property_name LIKE '%JAVA%';

-- Check Java permissions
SELECT * FROM user_java_policy;

-- Try to load Java
CREATE OR REPLACE AND RESOLVE JAVA SOURCE NAMED "HelloWorld" AS
public class HelloWorld {
    public static String hello() {
        return "Hello, World!";
    }
}
/

-- Create a function wrapper
CREATE OR REPLACE FUNCTION hello_world 
RETURN VARCHAR2
AS LANGUAGE JAVA 
NAME 'HelloWorld.hello() return String';
/

-- Test the function
SELECT hello_world() FROM dual;

exit; 