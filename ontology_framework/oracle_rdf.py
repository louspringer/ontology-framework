"""Oracle RDF store integration."""

import logging
import os
from typing import Any, List, Optional

import oracledb
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.plugins.stores.sparqlstore import SPARQLStore

from ontology_framework.prefix_map import default_prefix_map

logger = logging.getLogger(__name__)


class OracleRDFStore:
    """Oracle RDF store implementation."""

    def __init__(self, model_name: str = "TEST_MODEL"):
        """Initialize Oracle RDF store.

        Args:
            model_name: Name of the RDF model to use
        """
        self.model_name = model_name
        self.connection = None
        self._setup_connection()
        self._setup_model()

    def _setup_connection(self) -> None:
        """Set up Oracle database connection."""
        try:
            self.connection = oracledb.connect(
                user=os.environ["ORACLE_USER"],
                password=os.environ["ORACLE_PASSWORD"],
                dsn=os.environ["ORACLE_DSN"],
            )
            logger.info("Successfully connected to Oracle database")
        except Exception as e:
            logger.error(f"Failed to connect to Oracle: {e}")
            raise

    def _setup_model(self) -> None:
        """Set up RDF model in Oracle."""
        cursor = self.connection.cursor()

        try:
            # Check if model exists
            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM MDSYS.SEM_MODEL$ 
                WHERE MODEL_NAME = :1
            """,
                [self.model_name],
            )
            model_exists = cursor.fetchone()[0] > 0

            if model_exists:
                logger.info(f"Dropping existing model {self.model_name}")
                cursor.execute(
                    """
                    BEGIN
                        SEM_APIS.DROP_RDF_MODEL(:1);
                    END;
                """,
                    [self.model_name],
                )
                self.connection.commit()

            # Create new model
            logger.info(f"Creating new model {self.model_name}")
            cursor.execute(
                """
                BEGIN
                    SEM_APIS.CREATE_RDF_MODEL(:1);
                END;
            """,
                [self.model_name],
            )
            self.connection.commit()
            logger.info(f"Successfully created model {self.model_name}")

        except Exception as e:
            logger.error(f"Failed to set up RDF model: {e}")
            raise
        finally:
            cursor.close()

    def load_data(self, graph: Graph) -> None:
        """Load RDF data into Oracle store.

        Args:
            graph: RDF graph to load
        """
        cursor = self.connection.cursor()

        try:
            # Convert graph to N-Triples format
            ntriples = graph.serialize(format="ntriples").decode("utf-8")

            # Load data into model
            cursor.execute(
                """
                BEGIN
                    SEM_APIS.BULK_LOAD_FROM_STRING(
                        model_name => :1,
                        rdf_string => :2,
                        format => 'N-TRIPLE'
                    );
                END;
            """,
                [self.model_name, ntriples],
            )
            self.connection.commit()
            logger.info(f"Successfully loaded data into model {self.model_name}")

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
        finally:
            cursor.close()

    def execute_sparql(self, query: str) -> List[Any]:
        """Execute SPARQL query against Oracle store.

        Args:
            query: SPARQL query to execute

        Returns:
            List of query results
        """
        cursor = self.connection.cursor()

        try:
            # Execute query
            cursor.execute(
                """
                SELECT SEM_APIS.SPARQL_TO_SQL(
                    sparql_query => :1,
                    model_name => :2
                ) FROM DUAL
            """,
                [query, self.model_name],
            )
            sql_query = cursor.fetchone()[0]

            # Execute generated SQL
            cursor.execute(sql_query)
            results = cursor.fetchall()
            logger.info(f"Successfully executed SPARQL query: {query}")

            return results

        except Exception as e:
            logger.error(f"Failed to execute SPARQL query: {e}")
            raise
        finally:
            cursor.close()

    def add_triple(self, subject: URIRef, predicate: URIRef, object: Any) -> None:
        """Add triple to Oracle store.

        Args:
            subject: Subject URI
            predicate: Predicate URI
            object: Object (URI or literal)
        """
        cursor = self.connection.cursor()

        try:
            # Convert object to string representation
            if isinstance(object, Literal):
                obj_str = f'"{object}"'
            else:
                obj_str = str(object)

            # Add triple
            cursor.execute(
                """
                BEGIN
                    SEM_APIS.ADD_TRIPLE(
                        model_name => :1,
                        subject => :2,
                        predicate => :3,
                        object => :4
                    );
                END;
            """,
                [self.model_name, str(subject), str(predicate), obj_str],
            )
            self.connection.commit()
            logger.info(f"Successfully added triple: {subject} {predicate} {object}")

        except Exception as e:
            logger.error(f"Failed to add triple: {e}")
            raise
        finally:
            cursor.close()

    def remove_triple(self, subject: URIRef, predicate: URIRef, object: Any) -> None:
        """Remove triple from Oracle store.

        Args:
            subject: Subject URI
            predicate: Predicate URI
            object: Object (URI or literal)
        """
        cursor = self.connection.cursor()

        try:
            # Convert object to string representation
            if isinstance(object, Literal):
                obj_str = f'"{object}"'
            else:
                obj_str = str(object)

            # Remove triple
            cursor.execute(
                """
                BEGIN
                    SEM_APIS.REMOVE_TRIPLE(
                        model_name => :1,
                        subject => :2,
                        predicate => :3,
                        object => :4
                    );
                END;
            """,
                [self.model_name, str(subject), str(predicate), obj_str],
            )
            self.connection.commit()
            logger.info(f"Successfully removed triple: {subject} {predicate} {object}")

        except Exception as e:
            logger.error(f"Failed to remove triple: {e}")
            raise
        finally:
            cursor.close()

    def close(self) -> None:
        """Close Oracle connection."""
        if self.connection:
            self.connection.close()
            logger.info("Closed Oracle connection") 