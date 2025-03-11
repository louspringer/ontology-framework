-- Test wallet-based connection
SET ECHO ON
SET FEEDBACK ON

-- Connect using wallet
CONNECT /@tfm_high

-- Verify connection
SELECT SYS_CONTEXT('USERENV', 'SESSION_USER') AS USERNAME,
       SYS_CONTEXT('USERENV', 'CON_NAME') AS CONTAINER,
       SYS_CONTEXT('USERENV', 'DB_NAME') AS DB_NAME
FROM DUAL;

exit; 