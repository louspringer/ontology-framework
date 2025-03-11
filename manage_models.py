import os
import sys
from datetime import datetime
import oracledb
from pathlib import Path
import uuid

def get_connection():
    """Get Oracle database connection."""
    return oracledb.connect(
        user=os.environ['ORACLE_USER'],
        password=os.environ['ORACLE_PASSWORD'],
        dsn=os.environ['ORACLE_DSN']
    )

def list_models():
    """List all RDF models in the database."""
    conn = get_connection()
    cur = conn.cursor()
    
    print("\n=== Current RDF Models ===")
    cur.execute("""
        SELECT model_name, owner, table_name 
        FROM MDSYS.SEM_MODEL$ 
        ORDER BY model_name
    """)
    models = cur.fetchall()
    if not models:
        print("No models found")
    else:
        for model in models:
            print(f"Model: {model[0]}")
            print(f"  Owner: {model[1]}")
            print(f"  Table: {model[2]}")
            print()
    
    cur.close()
    conn.close()

def create_session_model():
    """Create a new session model for tracking work."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Generate unique session name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_model = f"SESSION_{timestamp}"
    session_table = f"SESSION_DATA_{timestamp}"
    
    try:
        # Create the model table with enhanced tracking
        print(f"\nCreating session table {session_table}...")
        cur.execute(f"""
            CREATE TABLE {session_table} (
                id NUMBER GENERATED ALWAYS AS IDENTITY,
                triple SDO_RDF_TRIPLE_S,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                change_id VARCHAR2(36),
                change_type VARCHAR2(50),
                guidance_ref VARCHAR2(1000),
                change_comment VARCHAR2(4000),
                PRIMARY KEY (id)
            )
        """)
        
        # Grant necessary privileges
        print("Granting privileges...")
        cur.execute(f"""
            BEGIN
                EXECUTE IMMEDIATE 'GRANT SELECT, INSERT, UPDATE, DELETE ON {session_table} TO MDSYS';
                EXECUTE IMMEDIATE 'GRANT SELECT, INSERT ON {session_table} TO PUBLIC';
            END;
        """)
        
        # Create the model
        print(f"Creating session model {session_model}...")
        cur.execute("""
            BEGIN
                SEM_APIS.CREATE_RDF_MODEL(:1, :2, 'triple');
            END;
        """, [session_model, session_table])
        
        # Add session metadata with enhanced tracking
        change_id = str(uuid.uuid4())
        
        # Add session type
        print("Adding session metadata...")
        cur.execute(f"""
            INSERT INTO {session_table} (
                triple, change_id, change_type, guidance_ref, change_comment
            ) VALUES (
                SDO_RDF_TRIPLE_S('{session_model}',
                    '<{session_model}>',
                    '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
                    '<http://ontologies.louspringer.com/meta#Session>'
                ),
                :1, 'SESSION_CREATE', 'guidance.ttl#SessionCreation',
                'Session initialization'
            )
        """, [change_id])
        
        # Add session label
        cur.execute(f"""
            INSERT INTO {session_table} (
                triple, change_id, change_type, guidance_ref, change_comment
            ) VALUES (
                SDO_RDF_TRIPLE_S('{session_model}',
                    '<{session_model}>',
                    '<http://www.w3.org/2000/01/rdf-schema#label>',
                    '"Active development session"'
                ),
                :1, 'SESSION_CREATE', 'guidance.ttl#SessionCreation',
                'Session initialization'
            )
        """, [change_id])
        
        # Add session start time
        cur.execute(f"""
            INSERT INTO {session_table} (
                triple, change_id, change_type, guidance_ref, change_comment
            ) VALUES (
                SDO_RDF_TRIPLE_S('{session_model}',
                    '<{session_model}>',
                    '<http://ontologies.louspringer.com/meta#startTime>',
                    '"{timestamp}"'
                ),
                :1, 'SESSION_CREATE', 'guidance.ttl#SessionCreation',
                'Session initialization'
            )
        """, [change_id])
        
        conn.commit()
        print(f"\nSuccessfully created session model {session_model}")
        
        # Save session info to a file
        session_file = Path('.session')
        session_file.write_text(f"{session_model}\n{session_table}")
        print(f"Session info saved to {session_file}")
        
    except Exception as e:
        print(f"Error creating session: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def get_current_session():
    """Get the current session model name."""
    session_file = Path('.session')
    if not session_file.exists():
        return None, None
    
    lines = session_file.read_text().splitlines()
    if len(lines) != 2:
        return None, None
    
    return lines[0], lines[1]

def add_to_session(subject, predicate, object_val, change_type=None, guidance_ref=None, comment=None):
    """Add a triple to the current session with change tracking.
    
    Args:
        subject: RDF subject
        predicate: RDF predicate
        object_val: RDF object
        change_type: Type of change (e.g., ADD, MODIFY, DELETE)
        guidance_ref: Reference to guidance.ttl section
        comment: Optional comment about the change
    """
    session_model, session_table = get_current_session()
    if not session_model:
        print("No active session found")
        return False
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        change_id = str(uuid.uuid4())
        cur.execute(f"""
            INSERT INTO {session_table} (
                triple, change_id, change_type, guidance_ref, change_comment
            ) VALUES (
                SDO_RDF_TRIPLE_S(:1, :2, :3, :4),
                :5, :6, :7, :8
            )
        """, [session_model, subject, predicate, object_val, 
              change_id, change_type, guidance_ref, comment])
        conn.commit()
        print(f"Added triple to session {session_model}")
        return True
    except Exception as e:
        print(f"Error adding to session: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def show_session_contents(show_changes=True):
    """Show the contents of the current session.
    
    Args:
        show_changes: Whether to show change tracking info
    """
    session_model, session_table = get_current_session()
    if not session_model:
        print("No active session found")
        return
    
    conn = get_connection()
    cur = conn.cursor()
    
    print(f"\n=== Current Session: {session_model} ===")
    try:
        if show_changes:
            cur.execute(f"""
                SELECT s.triple.GET_SUBJECT(), 
                       s.triple.GET_PROPERTY(),
                       s.triple.GET_OBJECT(),
                       s.timestamp,
                       s.change_id,
                       s.change_type,
                       s.guidance_ref,
                       s.change_comment
                FROM {session_table} s
                ORDER BY s.timestamp
            """)
            
            rows = cur.fetchall()
            if not rows:
                print("Session is empty")
            else:
                current_change = None
                for row in rows:
                    if current_change != row[4]:  # New change_id
                        current_change = row[4]
                        print(f"\nChange ID: {row[4]}")
                        print(f"Type: {row[5] or 'N/A'}")
                        print(f"Guidance: {row[6] or 'N/A'}")
                        print(f"Comment: {row[7] or 'N/A'}")
                        print("Triples:")
                    print(f"  {row[0]} {row[1]} {row[2]}")
                    print(f"  Timestamp: {row[3]}")
        else:
            cur.execute(f"""
                SELECT s.triple.GET_SUBJECT(), 
                       s.triple.GET_PROPERTY(),
                       s.triple.GET_OBJECT(),
                       s.timestamp
                FROM {session_table} s
                ORDER BY s.timestamp
            """)
            
            rows = cur.fetchall()
            if not rows:
                print("Session is empty")
            else:
                for row in rows:
                    print(f"\nTimestamp: {row[3]}")
                    print(f"Subject:   {row[0]}")
                    print(f"Predicate: {row[1]}")
                    print(f"Object:    {row[2]}")
    except Exception as e:
        print(f"Error reading session: {e}")
    finally:
        cur.close()
        conn.close()

def export_session_ttl():
    """Export the current session to a TTL file."""
    session_model, session_table = get_current_session()
    if not session_model:
        print("No active session found")
        return
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get all triples
        cur.execute(f"""
            SELECT s.triple.GET_SUBJECT(), 
                   s.triple.GET_PROPERTY(),
                   s.triple.GET_OBJECT()
            FROM {session_table} s
            ORDER BY s.timestamp
        """)
        
        rows = cur.fetchall()
        if not rows:
            print("Session is empty, nothing to export")
            return
        
        # Create TTL file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ttl_file = Path(f"session_export_{timestamp}.ttl")
        
        with ttl_file.open('w') as f:
            # Write prefixes
            f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
            f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
            f.write("@prefix meta: <http://ontologies.louspringer.com/meta#> .\n")
            f.write("\n")
            
            # Write triples
            for row in rows:
                subject = row[0]
                predicate = row[1]
                obj = row[2]
                f.write(f"{subject} {predicate} {obj} .\n")
        
        print(f"Session exported to {ttl_file}")
        
    except Exception as e:
        print(f"Error exporting session: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python manage_models.py [list|new-session|show-session|show-changes|export-ttl]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == 'list':
        list_models()
    elif command == 'new-session':
        create_session_model()
    elif command == 'show-session':
        show_session_contents(show_changes=False)
    elif command == 'show-changes':
        show_session_contents(show_changes=True)
    elif command == 'export-ttl':
        export_session_ttl()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1) 