import oracledb
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def grant_rdf_privileges():
    """Grant RDF privileges to ADMIN user."""
    try:
        # Get connection parameters from environment
        user = os.environ.get('ORACLE_USER')
        password = os.environ.get('ORACLE_PASSWORD')
        dsn = os.environ.get('ORACLE_DSN')
        
        # Connect to database
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        logger.info("Connected to Oracle Database")
        
        cursor = connection.cursor()
        
        # List of EXECUTE privileges to grant
        execute_grants = [
            "MDSYS.SEM_APIS",
            "MDSYS.SEM_MATCH",
            "MDSYS.SEM_MODELS",
            "MDSYS.SDO_RDF_TRIPLE_S"
        ]
        
        # List of SELECT privileges to grant
        select_grants = [
            "MDSYS.RDF_VALUE$",
            "MDSYS.RDF_MODEL$",
            "MDSYS.RDF_PARAMETER",
            "MDSYS.RDF_LINK$",
            "MDSYS.RDF_NAMESPACE$",
            "MDSYS.RDF_TERM_STATS$",
            "MDSYS.RDF_PRED_STATS$",
            "MDSYS.RDF_RULE$",
            "MDSYS.RDF_RULEBASE$",
            "MDSYS.RDF_NETWORK_INDEX_INTERNAL$",
            "MDSYS.RDF_MODEL_INTERNAL$",
            "MDSYS.RDF_GRANT_INFO$",
            "MDSYS.RDF_HIST$",
            "MDSYS.RDF_DELTA$",
            "MDSYS.RDF_COLLISION$",
            "MDSYS.RDF_CLIQUE$",
            "MDSYS.RDF_CRS_URI$",
            "MDSYS.RDF_DTYPE_INDEX_INFO_TBL",
            "MDSYS.RDF_PARAM$_TBL",
            "MDSYS.RDF_MODEL$_TBL",
            "MDSYS.RDF_PRECOMP$",
            "MDSYS.RDF_PRECOMP_DEP$",
            "MDSYS.RDF_SESSION_EVENT$",
            "MDSYS.RDF_SYSTEM_EVENT$",
            "MDSYS.RDF_SPM$",
            "MDSYS.RDF_TS$"
        ]
        
        # Grant EXECUTE privileges
        for obj in execute_grants:
            try:
                cursor.execute(f"GRANT EXECUTE ON {obj} TO ADMIN")
                logger.info(f"Granted EXECUTE on {obj}")
            except oracledb.DatabaseError as e:
                error, = e.args
                logger.warning(f"Error granting EXECUTE on {obj}: {error.message}")
        
        # Grant SELECT privileges
        for obj in select_grants:
            try:
                cursor.execute(f"GRANT SELECT ON {obj} TO ADMIN")
                logger.info(f"Granted SELECT on {obj}")
            except oracledb.DatabaseError as e:
                error, = e.args
                logger.warning(f"Error granting SELECT on {obj}: {error.message}")
        
        # Grant RDF roles
        roles = [
            "RDF_APIS_INTERNAL_ROLE",
            "RDF_APIS_USER_ROLE"
        ]
        
        for role in roles:
            try:
                cursor.execute(f"GRANT {role} TO ADMIN")
                logger.info(f"Granted role {role}")
            except oracledb.DatabaseError as e:
                error, = e.args
                logger.warning(f"Error granting role {role}: {error.message}")
        
        connection.commit()
        logger.info("All grants committed successfully")
        
    except oracledb.DatabaseError as e:
        error, = e.args
        logger.error(f"Oracle error {error.code}: {error.message}")
        if hasattr(error, 'help'):
            logger.error(f"Help: {error.help}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()
            logger.info("Connection closed")

if __name__ == "__main__":
    grant_rdf_privileges() 