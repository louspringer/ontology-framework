import oracledb
import os

# Print diagnostic information
print(f"Oracle Client Version: {oracledb.version}")
print(f"TNS_ADMIN: {os.environ.get('TNS_ADMIN')}")

# Connect using thin mode (no init_oracle_client needed)
connection = oracledb.connect(
    user="admin" password="op://Development/Oracle-RDF/password"
        dsn="tfm_high",
    config_dir=os.path.expanduser("~/Oracle/wallet")
)

print("Connected successfully!")

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