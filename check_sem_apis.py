import os
import oracledb

def check_sem_apis():
    conn = oracledb.connect(
        user=os.environ['ORACLE_USER'],
        password=os.environ['ORACLE_PASSWORD'],
        dsn=os.environ['ORACLE_DSN']
    )
    cur = conn.cursor()
    
    print("Checking current user and privileges...")
    cur.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_USER') FROM DUAL")
    print(f"Current user: {cur.fetchone()[0]}")
    
    print("\nChecking SEM_APIS visibility...")
    cur.execute("""
        SELECT owner, object_name object_type status 
        FROM all_objects 
        WHERE object_name = 'SEM_APIS'
    """)
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"Found: {row[0]}.{row[1]} ({row[2]}) - Status: {row[3]}")
    else:
        print("No SEM_APIS object found")
        
    print("\nChecking MDSYS objects...")
    cur.execute("""
        SELECT object_name object_type status 
        FROM all_objects 
        WHERE owner = 'MDSYS'
        AND object_name LIKE 'SEM%'
    """)
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"Found: {row[0]} ({row[1]}) - Status: {row[2]}")
    else:
        print("No SEM* objects found in MDSYS schema")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    check_sem_apis() 