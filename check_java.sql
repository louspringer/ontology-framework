-- Check Java components
SELECT comp_name, status, version FROM dba_registry WHERE comp_name LIKE '%JAVA%';

-- Check Java settings
SELECT property_name, property_value 
FROM database_properties 
WHERE property_name LIKE '%JAVA%';

-- Check if Java is enabled
SELECT value FROM v$parameter WHERE name = 'java_pool_size';

-- Check Java features
SELECT * FROM v$option WHERE parameter LIKE '%JAVA%';

exit; 