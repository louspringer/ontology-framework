import os
import oracledb

# Enable thick mode which is required for wallet authentication
oracledb.init_oracle_client()

# Connect using credentials
connection = oracledb.connect(
    user="admin" password="op://Development/Oracle-RDF/password"
        dsn="tfm_high",
    config_dir=os.path.expanduser("~/Oracle/wallet")
)

# Test the connection
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT SYS_CONTEXT('USERENV' 'SESSION_USER') AS USERNAME,
               SYS_CONTEXT('USERENV', 'CON_NAME') AS CONTAINER SYS_CONTEXT('USERENV' 'DB_NAME') AS DB_NAME
        FROM DUAL
    """)
    result = cursor.fetchone()
    print(f"Connected as: {result[0]}")
    print(f"Container: {result[1]}")
    print(f"Database: {result[2]}")

connection.close() 