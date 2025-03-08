"""Tests for Oracle RDF store integration."""

import os
import subprocess
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional

import oracledb
import pytest
from rdflib import Graph

from ontology_framework.prefix_map import default_prefix_map, PrefixCategory

class StorageType(Enum):
    """Storage type for RDF data."""
    LOCAL = 1
    ORACLE = 2

def is_oracle_java_available() -> bool:
    """Check if Java is available in Oracle DB.
    
    Returns:
        True if Java is available, False otherwise
    """
    try:
        connection = get_oracle_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL WHERE EXISTS (SELECT * FROM ALL_OBJECTS WHERE OBJECT_NAME = 'JAVA_INFO')")
        return bool(cursor.fetchone())
    except Exception:
        return False

def get_oracle_connection() -> Optional[oracledb.Connection]:
    """Get Oracle database connection.
    
    Returns:
        Oracle connection if successful, None otherwise
    """
    try:
        connection = oracledb.connect(
            user=os.getenv("ORACLE_USER", "ADMIN"),
            password=os.getenv("ORACLE_PASSWORD", "your_password"),
            dsn=os.getenv("ORACLE_DSN", "tfm_medium")
        )
        return connection
    except Exception as e:
        print(f"Error connecting to Oracle: {e}")
        return None

def setup_semantic_network(connection: oracledb.Connection) -> None:
    """Set up Oracle semantic network.
    
    Args:
        connection: Oracle database connection
    """
    try:
        print("Creating semantic network...")
        cursor = connection.cursor()
        cursor.execute("""
            BEGIN
                SEM_APIS.CREATE_SEM_NETWORK();
            END;
        """)
    except oracledb.DatabaseError as e:
        if "ORA-55321" in str(e):  # Network already exists
            print("Semantic network already exists, continuing with setup...")
        else:
            raise

def ensure_model_empty(connection: oracledb.Connection, model_name: str) -> None:
    """Ensure RDF model is empty before testing.
    
    Args:
        connection: Oracle database connection
        model_name: Name of the RDF model
    """
    cursor = connection.cursor()
    cursor.execute("""
        BEGIN
            SEM_APIS.DROP_RDF_MODEL(:1);
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -55505 THEN
                    RAISE;
                END IF;
        END;
    """, [model_name])
    
    print("Creating model...")
    cursor.execute("""
        BEGIN
            SEM_APIS.CREATE_RDF_MODEL(:1, 'TEST_RDF_DATA');
        END;
    """, [model_name])

def safe_execute_sparql_oracle(connection: oracledb.Connection, query: str) -> List[Any]:
    """Safely execute SPARQL query on Oracle.
    
    Args:
        connection: Oracle database connection
        query: SPARQL query to execute
        
    Returns:
        Query results
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"""
            SELECT * FROM TABLE(SEM_MATCH(
                '{query}',
                SEM_MODELS('TEST_MODEL'),
                null,
                SEM_APIS.SPARQL,
                null,
                null,
                'PLUS_RDFT=T'
            ))
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"SPARQL execution error: {e}")
        raise

def execute_sparql(store: Any, query: str, store_type: StorageType) -> List[Any]:
    """Execute SPARQL query on appropriate store.
    
    Args:
        store: RDF store (Graph or Oracle connection)
        query: SPARQL query to execute
        store_type: Type of storage
        
    Returns:
        Query results
    """
    if store_type == StorageType.LOCAL:
        return list(store.query(query))
    else:
        return safe_execute_sparql_oracle(store, query)

@pytest.fixture
def rdf_store(request):
    """Fixture for RDF store setup."""
    store_type = request.param
    
    if store_type == StorageType.LOCAL:
        g = Graph()
        default_prefix_map.bind_to_graph(g)
        print("Loading test ontology...")
        test_data = Path(__file__).parent / "test_data" / "test_ontology.ttl"
        g.parse(test_data, format="turtle")
        return g
    else:
        if not is_oracle_java_available():
            pytest.skip("Oracle RDF store requires Java")
        
        connection = get_oracle_connection()
        if not connection:
            pytest.skip("Oracle connection not available")
            
        setup_semantic_network(connection)
        ensure_model_empty(connection, "TEST_MODEL")
        
        # Load test data
        print("Loading test ontology...")
        test_data = Path(__file__).parent / "test_data" / "test_ontology.ttl"
        g = Graph()
        g.parse(test_data, format="turtle")
        
        # Convert to Oracle format and load
        # TODO: Implement Oracle data loading
        
        return connection

class TestOntologyQueries:
    """Test ontology queries."""
    
    @pytest.mark.parametrize("rdf_store,store_type", [
        (StorageType.LOCAL, StorageType.LOCAL),
        (StorageType.ORACLE, StorageType.ORACLE)
    ], indirect=["rdf_store"])
    def test_security_concepts(self, rdf_store, store_type):
        """Test listing security concepts."""
        query = """
            SELECT ?concept ?label
            WHERE {
                ?concept a meta:SecurityConcept ;
                        rdfs:label ?label .
            }
            ORDER BY ?label
        """
        results = execute_sparql(rdf_store, query, store_type)
        assert len(results) > 0, "Should find security concepts"
        
        meta_ns = str(default_prefix_map.get_namespace("meta"))
        if store_type == StorageType.LOCAL:
            assert all(str(r[0]).startswith(meta_ns) for r in results), "All concepts should be in meta namespace"

    @pytest.mark.parametrize("rdf_store,store_type", [
        (StorageType.LOCAL, StorageType.LOCAL),
        (StorageType.ORACLE, StorageType.ORACLE)
    ], indirect=["rdf_store"])
    def test_rca_issues(self, rdf_store, store_type):
        """Test RCA issues and solutions."""
        query = """
            SELECT ?issue ?issueName ?solution ?solutionDesc
            WHERE {
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
            SELECT ?label
            WHERE {
                meta:TestSecurityConcept rdfs:label ?label .
            }
        """
        results = execute_sparql(rdf_store, read_query, StorageType.ORACLE)
        assert len(results) == 1, "Should find created concept"
        assert str(results[0][0]) == "Test Security Concept", "Label should match"

@pytest.mark.parametrize("rdf_store,store_type", [
    (StorageType.LOCAL, StorageType.LOCAL),
    (StorageType.ORACLE, StorageType.ORACLE)
], indirect=["rdf_store"])
def test_component_dependencies(rdf_store, store_type):
    """Test component dependency relationships."""
    query = """
        SELECT ?component ?dependsOn ?implements
        WHERE {
            ?component a meta:Component ;
                      rdfs:label ?name .
            OPTIONAL { ?component meta:dependsOn ?dependsOn }
            OPTIONAL { ?component meta:implements ?implements }
        }
        ORDER BY ?component
    """
    results = execute_sparql(rdf_store, query, store_type)
    assert len(results) > 0, "Should find components" 