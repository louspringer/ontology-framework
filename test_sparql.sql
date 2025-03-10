-- Test SPARQL query capability
SET SERVEROUTPUT ON;

-- Create the semantic network if it doesn't exist
BEGIN
  SEM_APIS.CREATE_SEM_NETWORK('ONTOLOGY_FRAMEWORK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -55321 THEN  -- Network already exists
      RAISE;
    END IF;
END;
/

-- Verify privileges
SELECT * FROM SESSION_PRIVS 
WHERE PRIVILEGE IN ('CREATE TABLE', 'CREATE PROCEDURE', 'CREATE TYPE');

-- Create a simple RDF model for testing if it doesn't exist
BEGIN
  -- Drop the model if it exists
  BEGIN
    SEM_APIS.DROP_SEM_MODEL('TEST_MODEL', 'DATA_TABLE=TEST_MODEL_RDF_DATA');
  EXCEPTION
    WHEN OTHERS THEN NULL;
  END;
  
  -- Create the table first
  EXECUTE IMMEDIATE 'CREATE TABLE TEST_MODEL_RDF_DATA (
    id NUMBER GENERATED ALWAYS AS IDENTITY,
    triple SDO_RDF_TRIPLE_S
  )';
  
  -- Create a new model
  SEM_APIS.CREATE_SEM_MODEL(
    model_name => 'TEST_MODEL',
    table_name => 'TEST_MODEL_RDF_DATA',
    column_name => 'TRIPLE'
  );
END;
/

-- Insert a test triple
INSERT INTO TEST_MODEL_RDF_DATA(TRIPLE) VALUES (
  SDO_RDF_TRIPLE_S('TEST_MODEL',
    'http://example.org/subject',
    'http://example.org/predicate',
    'Test literal')
);
COMMIT;

-- Run a direct query
SELECT t.TRIPLE.GET_SUBJECT() as SUBJECT,
       t.TRIPLE.GET_PROPERTY() as PREDICATE,
       t.TRIPLE.GET_OBJECT() as OBJECT
FROM TEST_MODEL_RDF_DATA t;

-- Try SPARQL query
SELECT subject, object 
FROM TABLE(SEM_MATCH(
    'SELECT ?subject ?object 
     WHERE { ?subject <http://example.org/predicate> ?object }',
    SEM_MODELS('TEST_MODEL'),
    null, null, null));

-- Try another SPARQL query to list all triples
SELECT subject, predicate, object 
FROM TABLE(SEM_MATCH(
    'SELECT ?subject ?predicate ?object 
     WHERE { ?subject ?predicate ?object }',
    SEM_MODELS('TEST_MODEL'),
    null, null, null));

-- Clean up
BEGIN
  SEM_APIS.DROP_SEM_MODEL('TEST_MODEL', 'DATA_TABLE=TEST_MODEL_RDF_DATA');
  EXECUTE IMMEDIATE 'DROP TABLE TEST_MODEL_RDF_DATA PURGE';
END;
/

exit; 