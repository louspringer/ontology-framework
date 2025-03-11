#!/usr/bin/env python3
"""Script to check which ontologies have been loaded into Oracle."""

import oracledb
import os
from tabulate import tabulate

def main():
    # Connect to Oracle
    wallet_location = os.getenv('WALLET_LOCATION')
    oracle_user = os.getenv('ORACLE_USER')
    oracle_password = os.getenv('ORACLE_PASSWORD')

    oracledb.init_oracle_client(config_dir=wallet_location)
    connection = oracledb.connect(
        user=oracle_user,
        password=oracle_password,
        dsn='tfm_high',
        config_dir=wallet_location,
        wallet_location=wallet_location
    )

    cursor = connection.cursor()

    # Query tracking table
    cursor.execute("""
        SELECT 
            file_name, 
            model_name, 
            load_status, 
            TO_CHAR(load_timestamp, 'YYYY-MM-DD HH24:MI:SS') as timestamp,
            SUBSTR(error_message, 1, 100) as error_preview
        FROM ONTOLOGY_LOAD_TRACKING
        ORDER BY load_timestamp DESC
    """)

    # Get column names
    columns = [desc[0] for desc in cursor.description]
    
    # Fetch all rows
    rows = cursor.fetchall()

    # Print results using tabulate
    print(tabulate(rows, headers=columns, tablefmt='pipe'))

    # Print summary
    cursor.execute("""
        SELECT load_status, COUNT(*) 
        FROM ONTOLOGY_LOAD_TRACKING 
        GROUP BY load_status
    """)
    print("\nSummary:")
    for status, count in cursor.fetchall():
        print(f"{status}: {count}")

    connection.close()

if __name__ == "__main__":
    main() 