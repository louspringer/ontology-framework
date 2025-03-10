-- Check Java status
SELECT comp_id, status, version FROM DBA_REGISTRY
WHERE comp_id = 'JAVAVM';

-- Check Java components
SELECT comp_name, status, version FROM dba_registry WHERE comp_name LIKE '%JAVA%';

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