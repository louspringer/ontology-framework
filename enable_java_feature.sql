-- Enable Java feature
BEGIN
   DBMS_CLOUD_ADMIN.ENABLE_FEATURE(
      feature_name => 'JAVAVM'
   );
END;
/

-- Check Java status
SELECT status, version FROM DBA_REGISTRY
WHERE comp_id = 'JAVAVM';

-- Check JDK version
SELECT dbms_java.get_jdk_version FROM DUAL;

exit; 