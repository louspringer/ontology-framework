"""Tests for Oracle RDF store integration."""

import os
import unittest
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional
import oracledb
import pytest
from rdflib import Graph, URIRef, Literal, Namespace
from pyshacl import validate
from ontology_framework.prefix_map import default_prefix_map

class StorageType(Enum):
    """Storage type for RDF data."""

    LOCAL = 1
    ORACLE = 2

def get_oracle_connection() -> Optional[oracledb.Connection]:
    """Get Oracle database connection."""
    try:
        return oracledb.connect(
            user=os.environ["ORACLE_USER"],
            password=os.environ["ORACLE_PASSWORD"],
            dsn=os.environ["ORACLE_DSN"],
        )
    except Exception as e:
        print(f"Failed to connect to Oracle: {e}")
        return None


def verify_oracle_rdf_access(connection: oracledb.Connection) -> None:
    """Verify access to Oracle RDF packages and objects.

    Args:
        connection: Oracle database connection
    Raises:
        Exception: If required access is not available
    """
    cursor = connection.cursor()

    try:
        # Log Oracle version and environment
        print("\n=== Oracle Environment ===")
        cursor.execute("SELECT * FROM V$VERSION")
        for row in cursor:
            print(f"Version info: {row[0]}")

        cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
        current_schema = cursor.fetchone()[0]
        print(f"Current schema: {current_schema}")

        cursor.execute("SELECT SYS_CONTEXT('USERENV', 'SESSION_USER') FROM DUAL")
        session_user = cursor.fetchone()[0]
        print(f"Session user: {session_user}")

        # First verify SEM_APIS access
        print("\n=== Verifying SEM_APIS Access ===")
        cursor.execute(
            """
            SELECT owner, object_name, object_type, status 
            FROM all_objects 
            WHERE object_name = 'SEM_APIS'
            AND object_type = 'SYNONYM'
        """
        )
        sem_apis = cursor.fetchone()
        if not sem_apis:
            raise Exception("SEM_APIS synonym not found")
        print(
            f"Found SEM_APIS: {sem_apis[0]}.{sem_apis[1]} ({sem_apis[2]}) - Status: {sem_apis[3]}"
        )

        # Check if semantic network exists
        print("\nChecking for existing semantic network...")
        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM all_tables 
            WHERE owner = 'MDSYS' 
            AND table_name = 'SEM_MODEL$'
        """
        )
        if cursor.fetchone()[0] > 0:
            print("Semantic network tables exist")
        else:
            print("WARNING: Semantic network tables not found")
            print("Attempting to create semantic network...")
            try:
                cursor.execute(
                    """
                    BEGIN 
                        SEM_APIS.CREATE_SEM_NETWORK('SYSAUX');
                        DBMS_OUTPUT.PUT_LINE('Network created successfully');
                    END;
                """
                )
                print("Successfully created semantic network")
            except Exception as e:
                error_str = str(e)
                if "ORA-55321" in error_str:  # Network already exists
                    print("Network already exists - this is OK")
                else:
                    raise Exception(f"Failed to create semantic network: {e}")

        # Now check if we can create a test table
        print("\n=== Test Table Setup ===")
        print("Checking for existing test table...")
        drop_sql = """
            BEGIN 
                EXECUTE IMMEDIATE 'DROP TABLE TEST_RDF_ACCESS PURGE';
                DBMS_OUTPUT.PUT_LINE('Existing table dropped');
            EXCEPTION 
                WHEN OTHERS THEN
                    IF SQLCODE != -942 THEN  -- Table does not exist
                        DBMS_OUTPUT.PUT_LINE('Error dropping table: ' || SQLERRM);
                        RAISE;
                    ELSE 
                        DBMS_OUTPUT.PUT_LINE('No existing table found');
                    END IF;
            END;
        """
        print(f"Executing cleanup SQL:\n{drop_sql}")
        cursor.execute(drop_sql)
        print("Table cleanup completed")

        # Try to create a test table with RDF column
        print("\nAttempting to create test RDF table...")
        create_table_sql = """
            CREATE TABLE TEST_RDF_ACCESS (
                id NUMBER,
                triple SDO_RDF_TRIPLE_S
            )
        """
        print(f"Executing create SQL:\n{create_table_sql}")
        cursor.execute(create_table_sql)
        print("Successfully created RDF table")

        # Clean up
        print("\n=== Cleanup ===")
        print("Dropping test table...")
        drop_sql = "DROP TABLE TEST_RDF_ACCESS PURGE"
        print(f"Executing SQL: {drop_sql}")
        cursor.execute(drop_sql)
        print("Successfully dropped test table")

        try:
            cursor.execute("SELECT status FROM all_users WHERE username = 'MDSYS'")
            mdsys_status = cursor.fetchone()
            if mdsys_status:
                print(f"MDSYS schema status: {mdsys_status[0]}")
            else:
                print("MDSYS schema not found!")
        except Exception as e:
            print(f"Could not check MDSYS schema status: {e}")
            
    finally:
        cursor.close()


def setup_semantic_network(connection: oracledb.Connection) -> None:
    """Set up semantic network for testing.

    Args:
        connection: Oracle database connection
    """
    cursor = connection.cursor()

    # Check if network exists
    cursor.execute(
        """
        SELECT MODEL_NAME 
        FROM MDSYS.SEM_MODEL$
        WHERE ROWNUM = 1
    """
    )
    if not cursor.fetchone():
        print("Creating semantic network...")
        cursor.execute(
            """
            BEGIN 
                SEM_APIS.CREATE_SEM_NETWORK('SYSAUX');
            END;
        """
        )
        connection.commit()


def ensure_model_empty(connection: oracledb.Connection, model_name: str) -> None:
    """Ensure RDF model is empty before testing.

    Args:
        connection: Oracle database connection
        model_name: Name of the RDF model
    Raises:
        oracledb.DatabaseError: If model operations fail
    """
    cursor = connection.cursor()

    # Get current schema
    cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
    current_schema = cursor.fetchone()[0]
    print(f"Current schema: {current_schema}")

    # First check if model exists
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM MDSYS.SEM_MODEL$ 
        WHERE MODEL_NAME = :1
    """,
        [model_name],
    )
    model_exists = cursor.fetchone()[0] > 0
    
    if model_exists:
        print(f"Dropping existing model {model_name}")
        cursor.execute(
            """
            BEGIN 
                SEM_APIS.DROP_RDF_MODEL(:1);
            END;
        """,
            [model_name],
        )
        connection.commit()

    # Drop table if it exists
    cursor.execute(
        """
        BEGIN 
            EXECUTE IMMEDIATE 'DROP TABLE TEST_RDF_DATA PURGE';
        EXCEPTION 
            WHEN OTHERS THEN
                IF SQLCODE != -942 THEN  -- Table does not exist
                    RAISE;
                END IF;
        END;
    """
    )

    # Create model table
    print("Creating model table...")
    cursor.execute(
        """
        CREATE TABLE TEST_RDF_DATA (
            id NUMBER,
            triple SDO_RDF_TRIPLE_S
        )
    """
    )
    connection.commit()

    # Grant necessary privileges to MDSYS
    print("Granting privileges to MDSYS...")
    cursor.execute(
        """
        BEGIN 
            EXECUTE IMMEDIATE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TEST_RDF_DATA TO MDSYS';
            EXECUTE IMMEDIATE 'GRANT SELECT, INSERT ON TEST_RDF_DATA TO PUBLIC';
        END;
    """
    )
    connection.commit()

    # Create model
    print(f"Creating model {model_name}...")
    cursor.execute(
        """
        BEGIN 
            SEM_APIS.CREATE_RDF_MODEL(:1, 'TEST_RDF_DATA', 'triple');
        END;
    """,
        [model_name],
    )

    connection.commit()
    print(f"Created empty model {model_name} with table TEST_RDF_DATA")


def get_current_schema(connection):
    """Get the current schema name."""
    cursor = connection.cursor()
    cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
    schema = cursor.fetchone()[0]
    cursor.close()
    return schema


def register_namespaces(connection):
    """Register RDF namespaces with Oracle."""
    cursor = connection.cursor()

    # Define the namespaces
    namespaces = [
        ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
        ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
        ("owl", "http://www.w3.org/2002/07/owl#"),
        ("meta", "http://ontologies.louspringer.com/meta#"),
    ]

    # Register each namespace
    for prefix, uri in namespaces:
        cursor.execute(
            """
            BEGIN 
                MDSYS.SEM_APIS.CREATE_SEM_NAMESPACE(
                    namespace_in => :uri,
                    prefix_in => :prefix
                );
            EXCEPTION 
                WHEN OTHERS THEN
                    IF SQLCODE != -20182 THEN
                        RAISE;
                    END IF;
            END;
        """,
            uri=uri,
            prefix=prefix,
        )

    cursor.close()


def load_test_data(connection, model_name, test_data_path):
    """Load test data into the RDF model."""
    print("Loading test ontology...")
    cursor = connection.cursor()
    current_schema = get_current_schema(connection)
    print(f"Current schema: {current_schema}")

    # Parse the test data
    g = Graph()
    g.parse(test_data_path, format="turtle")

    # Drop staging table if it exists
    print("Creating staging table...")
    cursor.execute(
        """
        BEGIN 
            EXECUTE IMMEDIATE 'DROP TABLE RDF_STAGING PURGE';
        EXCEPTION 
            WHEN OTHERS THEN
                IF SQLCODE != -942 THEN
                    RAISE;
                END IF;
        END;
    """
    )

    # Create staging table
    cursor.execute(
        """
        CREATE TABLE RDF_STAGING (
            RDF$STC_sub VARCHAR2(4000),
            RDF$STC_pred VARCHAR2(4000),
            RDF$STC_obj VARCHAR2(4000)
        )
    """
    )

    # Grant privileges
    cursor.execute("""
        GRANT SELECT ON RDF_STAGING TO MDSYS
    """)

    print("Loading data into staging table...")
    # Insert data into staging table
    insert_sql = """
        INSERT INTO RDF_STAGING (RDF$STC_sub, RDF$STC_pred, RDF$STC_obj)
        VALUES (:1, :2, :3)
    """

    # Process and load triples
    for s, p, o in g:
        # Format subject
        subject = f"<{s}>" if isinstance(s, URIRef) else s

        # Format predicate
        predicate = f"<{p}>" if isinstance(p, URIRef) else p

        # Format object
        if isinstance(o, URIRef):
            object_val = f"<{o}>"
        elif isinstance(o, Literal):
            if o.language:
                # Handle language tags by appending them to the literal
                object_val = f'"{o}"@{o.language}'
            else:
                object_val = f'"{o}"'
        else:
            object_val = str(o)

        cursor.execute(insert_sql, [subject, predicate, object_val])

    connection.commit()

    print("Loading data into RDF model...")
    # Bulk load data from staging table
    cursor.execute(
        f"""
        BEGIN 
            SEM_APIS.BULK_LOAD_FROM_STAGING_TABLE(
                model_name => '{model_name}',
                table_owner => USER,
                table_name => 'RDF_STAGING',
                flags => NULL
            );
        END;
    """
    )

    # Drop staging table
    cursor.execute(
        """
        DROP TABLE RDF_STAGING PURGE
    """
    )

    cursor.close()


def execute_sparql(store: Any, query: str, store_type: StorageType) -> List[Any]:
    """Execute a SPARQL query against the RDF store."""
    if store_type == StorageType.LOCAL:
        results = store.query(query)
        return list(results)
    else:
        cursor = store.cursor()
        
        # Register namespaces if needed
        register_namespaces(store)
        
        if query.strip().upper().startswith('INSERT') or query.strip().upper().startswith('DELETE'):
            # Handle updates
            cursor.execute("""
                BEGIN 
                    MDSYS.SEM_APIS.UPDATE_MODEL(
                        models => SEM_MODELS('TEST_MODEL'),
                        sparql_update => :1,
                        options => 'USE_BIND_VAR=T'
                    );
                END;
            """, [query])
            store.commit()
            return []
        else:
            # Handle queries
            cursor.execute("""
                SELECT *
                FROM TABLE(MDSYS.SEM_MATCH(
                    :1,
                    SEM_MODELS('TEST_MODEL'),
                    null,
                    null,
                    null,
                    null,
                    'USE_BIND_VAR=T'
                ))
            """, [query])
            
            results = cursor.fetchall()
            cursor.close()
            return results


@pytest.fixture
def rdf_store(request):
    """Fixture for RDF store setup."""
    store_type = request.param
    if store_type == StorageType.LOCAL:
        g = Graph()
        default_prefix_map.bind_to_graph(g)
        print("Loading test ontology...")
        test_data = Path(__file__).parent / "test_data" / "test_ontology.ttl"
        print(f"Test data path: {test_data}")
        print(f"Test data exists: {test_data.exists()}")
        g.parse(test_data, format="turtle")
        return g
    else:
        connection = get_oracle_connection()
        if not connection:
            pytest.skip("Oracle connection not available")

        # Verify RDF access before proceeding
        try:
            verify_oracle_rdf_access(connection)
        except Exception as e:
            pytest.skip(f"Oracle RDF access not available: {e}")

        setup_semantic_network(connection)
        ensure_model_empty(connection, "TEST_MODEL")

        # Load test data
        print("Loading test ontology...")
        test_data = Path(__file__).parent / "test_data" / "test_ontology.ttl"
        load_test_data(connection, "TEST_MODEL", test_data)

        return connection


class TestOracleRDFStore:
    """Test Oracle RDF store functionality."""

    @pytest.mark.parametrize("rdf_store", [StorageType.ORACLE], indirect=True)
    def test_model_creation(self, rdf_store):
        """Test model creation (ModelCreationTest)."""
        cursor = rdf_store.cursor()
        cursor.execute(
            """
            SELECT model_name, owner, table_name 
            FROM MDSYS.SEM_MODEL$
            WHERE model_name = 'TEST_MODEL'
        """
        )
        result = cursor.fetchone()
        assert result is not None, "Model should exist"
        assert result[0] == "TEST_MODEL", "Model name should match"
        assert result[2] == "TEST_RDF_DATA", "Table name should match"

    @pytest.mark.parametrize("rdf_store", [StorageType.ORACLE], indirect=True)
    def test_triple_loading(self, rdf_store):
        """Test triple loading (TripleLoadingTest)."""
        cursor = rdf_store.cursor()
        cursor.execute(
            """
            SELECT *
            FROM TABLE(MDSYS.SEM_MATCH(
                'SELECT ?s ?p ?o WHERE {?s ?p ?o}',
                SEM_MODELS('TEST_MODEL'),
                null,
                null,
                null,
                null,
                'USE_BIND_VAR=T'
            ))
        """
        )
        results = cursor.fetchall()
        assert len(results) > 0, "No triples found in the model"
        cursor.close()

    @pytest.mark.parametrize("rdf_store", [StorageType.ORACLE], indirect=True)
    def test_oracle_rdf_setup(self, rdf_store):
        """Test Oracle RDF setup and access."""
        verify_oracle_rdf_access(rdf_store)
        assert True, "Oracle RDF access verified"


class TestOntologyQueries:
    """Test ontology queries."""

    @pytest.mark.parametrize(
        "rdf_store,store_type",
        [
            (StorageType.LOCAL, StorageType.LOCAL),
            (StorageType.ORACLE, StorageType.ORACLE),
        ],
        indirect=["rdf_store"],
    )
    def test_security_concepts(self, rdf_store, store_type):
        """Test listing security concepts."""
        query = """
            SELECT ?concept ?label WHERE {
                ?concept a meta:SecurityConcept ;
                        rdfs:label ?label .
            }
            ORDER BY ?label
        """
        results = execute_sparql(rdf_store, query, store_type)
        assert len(results) > 0, "Should find security concepts"

        meta_ns = str(default_prefix_map.get_namespace("meta"))
        if store_type == StorageType.LOCAL:
            assert all(
                str(r[0]).startswith(meta_ns) for r in results
            ), "All concepts should be in meta namespace"

    @pytest.mark.parametrize(
        "rdf_store,store_type",
        [
            (StorageType.LOCAL, StorageType.LOCAL),
            (StorageType.ORACLE, StorageType.ORACLE),
        ],
        indirect=["rdf_store"],
    )
    def test_rca_issues(self, rdf_store, store_type):
        """Test RCA issues and solutions."""
        query = """
            SELECT ?issue ?issueName ?solution ?solutionDesc WHERE {
                ?issue a meta:RCAIssue ;
                       rdfs:label ?issueName ;
                       meta:hasSolution ?solution .
                ?solution rdfs:comment ?solutionDesc .
            }
            ORDER BY ?issueName
        """
        results = execute_sparql(rdf_store, query, store_type)
        assert len(results) > 0, "Should find RCA issues"


class TestOracleCRUD:
    """Test CRUD operations in Oracle RDF store."""

    @pytest.mark.parametrize("rdf_store", [StorageType.ORACLE], indirect=True)
    def test_crud_operations(self, rdf_store):
        """Test CRUD operations in Oracle RDF store."""
        # Create
        create_query = """
            INSERT DATA {
                meta:TestSecurityConcept a meta:SecurityConcept ;
                    rdfs:label "Test Security Concept"@en ;
                    rdfs:comment "Test concept for CRUD operations" ;
                    owl:versionInfo "1.0.0" .
            }
        """
        execute_sparql(rdf_store, create_query, StorageType.ORACLE)

        # Read
        read_query = """
            SELECT ?label WHERE {
                meta:TestSecurityConcept rdfs:label ?label .
            }
        """
        results = execute_sparql(rdf_store, read_query, StorageType.ORACLE)
        assert len(results) == 1, "Should find created concept"
        assert str(results[0][0]) == "Test Security Concept", "Label should match"


@pytest.mark.parametrize(
    "rdf_store,store_type",
    [(StorageType.LOCAL, StorageType.LOCAL), (StorageType.ORACLE, StorageType.ORACLE)],
    indirect=["rdf_store"],
)
def test_component_dependencies(rdf_store, store_type):
    """Test component dependency relationships."""
    query = """
        SELECT ?component ?dependsOn ?implements WHERE {
            ?component a meta:Component ;
                      rdfs:label ?name .
            OPTIONAL { ?component meta:dependsOn ?dependsOn }
            OPTIONAL { ?component meta:implements ?implements }
        }
        ORDER BY ?component
    """
    results = execute_sparql(rdf_store, query, store_type)
    assert len(results) > 0, "Should find components"


@pytest.mark.parametrize("rdf_store", [StorageType.ORACLE], indirect=True)
def test_oracle_rdf_access(rdf_store):
    """Test Oracle RDF functionality."""
    verify_oracle_rdf_access(rdf_store)
    assert True, "Oracle RDF functionality verified"


class TestOracleRDFModel(unittest.TestCase):
    """Test Oracle RDF functionality using the test model."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        pass


if __name__ == '__main__':
    unittest.main()
