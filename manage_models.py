import os
import sys
from datetime import datetime
import oracledb
from pathlib import Path
import uuid
import time
from rdflib import Graph, URIRef, Literal

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

def check_guidance():
    """Check guidance model in Oracle RDF."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print("\n=== Checking Guidance in Oracle RDF ===")
        
        # Check for guidance model
        print("\nLooking for guidance model...")
        cur.execute("""
            SELECT model_name, owner, table_name 
            FROM MDSYS.SEM_MODEL$ 
            WHERE UPPER(model_name) LIKE '%GUIDANCE%'
        """)
        models = cur.fetchall()
        if not models:
            print("No guidance model found")
        else:
            for model in models:
                print(f"Found model: {model[0]}")
                print(f"  Owner: {model[1]}")
                print(f"  Table: {model[2]}")
                
                # Check guidance contents
                print(f"\nChecking contents of {model[0]}...")
                cur.execute(f"""
                    SELECT s.triple.GET_SUBJECT(), 
                           s.triple.GET_PROPERTY(),
                           s.triple.GET_OBJECT()
                    FROM {model[1]}.{model[2]} s
                    ORDER BY 1, 2, 3
                """)
                triples = cur.fetchall()
                if not triples:
                    print("  No triples found")
                else:
                    for triple in triples:
                        print(f"  {triple[0]} {triple[1]} {triple[2]}")
    except Exception as e:
        print(f"Error checking guidance: {e}")
    finally:
        cur.close()
        conn.close()

def check_meta():
    """Check contents of META model in Oracle RDF."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print("\n=== Checking META Model Contents ===")
        
        # First verify META model exists
        cur.execute("""
            SELECT owner, table_name 
            FROM MDSYS.SEM_MODEL$ 
            WHERE model_name = 'META'
        """)
        meta = cur.fetchone()
        if not meta:
            print("META model not found")
            return
            
        print(f"Found META model in {meta[0]}.{meta[1]}")
        
        # Check for guidance-related triples
        print("\nLooking for guidance triples...")
        cur.execute(f"""
            SELECT s.triple.GET_SUBJECT(), 
                   s.triple.GET_PROPERTY(),
                   s.triple.GET_OBJECT()
            FROM {meta[0]}.{meta[1]} s
            WHERE 
                s.triple.GET_SUBJECT() LIKE '%guidance%'
                OR s.triple.GET_PROPERTY() LIKE '%guidance%'
                OR s.triple.GET_OBJECT() LIKE '%guidance%'
            ORDER BY 1, 2, 3
        """)
        
        triples = cur.fetchall()
        if not triples:
            print("No guidance-related triples found")
        else:
            print("\nGuidance-related triples:")
            for triple in triples:
                print(f"  {triple[0]} {triple[1]} {triple[2]}")
                
        # Also check for any meta:guidance predicates
        print("\nChecking for meta:guidance predicates...")
        cur.execute(f"""
            SELECT s.triple.GET_SUBJECT(), 
                   s.triple.GET_PROPERTY(),
                   s.triple.GET_OBJECT()
            FROM {meta[0]}.{meta[1]} s
            WHERE s.triple.GET_PROPERTY() LIKE '%meta%guidance%'
            ORDER BY 1, 2, 3
        """)
        
        triples = cur.fetchall()
        if not triples:
            print("No meta:guidance predicates found")
        else:
            print("\nTriples with meta:guidance predicates:")
            for triple in triples:
                print(f"  {triple[0]} {triple[1]} {triple[2]}")
                
    except Exception as e:
        print(f"Error checking META model: {e}")
    finally:
        cur.close()
        conn.close()

def show_model_contents(model_name, pattern=None, limit=50):
    """Show triples in a given model.
    
    Args:
        model_name: Name of the RDF model to check
        pattern: Optional pattern to filter triples (subject, predicate, or object)
        limit: Maximum number of triples to show
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # First verify model exists
        cur.execute("""
            SELECT owner, table_name 
            FROM MDSYS.SEM_MODEL$ 
            WHERE model_name = :1
        """, [model_name])
        model = cur.fetchone()
        if not model:
            print(f"Model {model_name} not found")
            return
            
        print(f"\n=== Contents of {model_name} Model ===")
        print(f"Location: {model[0]}.{model[1]}")
        
        # Get total count
        cur.execute(f"SELECT COUNT(*) FROM {model[0]}.{model[1]}")
        total = cur.fetchone()[0]
        print(f"\nTotal triples: {total}")
        
        # Build query based on pattern
        where_clause = ""
        if pattern:
            where_clause = f"""
                WHERE DBMS_LOB.INSTR(s.triple.GET_SUBJECT(), '{pattern}') > 0
                   OR DBMS_LOB.INSTR(s.triple.GET_PROPERTY(), '{pattern}') > 0
                   OR DBMS_LOB.INSTR(s.triple.GET_OBJECT(), '{pattern}') > 0
            """
            
        # Get filtered triples
        query = f"""
            SELECT s.triple.GET_SUBJECT(), 
                   s.triple.GET_PROPERTY(),
                   s.triple.GET_OBJECT()
            FROM {model[0]}.{model[1]} s
            {where_clause}
        """
        
        if limit:
            print(f"\nShowing first {limit} triples" + (" matching pattern" if pattern else ""))
            cur.execute(f"SELECT * FROM ({query}) WHERE ROWNUM <= {limit}")
        else:
            print("\nShowing all triples" + (" matching pattern" if pattern else ""))
            cur.execute(query)
        
        triples = cur.fetchall()
        if not triples:
            print("No matching triples found")
        else:
            for triple in triples:
                print(f"{triple[0]} {triple[1]} {triple[2]}")
                
    except Exception as e:
        print(f"Error reading model: {e}")
    finally:
        cur.close()
        conn.close()

def format_value(value):
    """Format a value for Oracle RDF.
    
    Args:
        value: The value to format (URI or literal)
    
    Returns:
        Formatted value string
    """
    if isinstance(value, URIRef):
        # Convert file:/// URIs to regular URIs
        uri = str(value)
        if uri.startswith('file:///'):
            uri = uri[7:]  # Remove file:///
        # Ensure URI is properly formatted
        if not uri.startswith('<') and not uri.endswith('>'):
            uri = f'<{uri}>'
        return uri
    elif isinstance(value, Literal):
        # Handle literals with language tags
        if value.language:
            return f'"{str(value)}"@{value.language}'
        # Handle typed literals
        elif value.datatype:
            return f'"{str(value)}"^^<{str(value.datatype)}>'
        # Plain literals
        else:
            return f'"{str(value)}"'
    else:
        return str(value)

def load_ttl_file(model_name, ttl_file):
    """Load a TTL file into an Oracle RDF model.
    
    Args:
        model_name: Name of the RDF model to load into
        ttl_file: Path to the TTL file
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # First verify model exists
        cur.execute("""
            SELECT owner, table_name 
            FROM MDSYS.SEM_MODEL$ 
            WHERE model_name = :1
        """, [model_name])
        model = cur.fetchone()
        if not model:
            print(f"Model {model_name} not found")
            return
            
        print(f"\n=== Loading {ttl_file} into {model_name} Model ===")
        
        # Read and parse TTL file
        print("\nParsing TTL file...")
        g = Graph()
        g.parse(ttl_file, format='turtle')
        
        # Insert triples directly into model
        print("\nLoading triples into model...")
        for s, p, o in g:
            # Format values
            subj = format_value(s)
            pred = format_value(p)
            obj = format_value(o)
            
            # Create RDF triple
            cur.execute(f"""
                INSERT INTO {model[0]}.{model[1]} (triple) VALUES (
                    SDO_RDF_TRIPLE_S(
                        '{model_name}',
                        :1,
                        :2,
                        :3
                    )
                )
            """, [subj, pred, obj])
            
        conn.commit()
        print(f"\nSuccessfully loaded {ttl_file} into {model_name} model")
        
    except Exception as e:
        print(f"Error loading TTL file: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def initialize_meta_model():
    """Initialize the META model with a permanent table."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print("\n=== Initializing META Model ===")
        
        # Check if META model exists
        cur.execute("""
            SELECT owner, table_name 
            FROM MDSYS.SEM_MODEL$ 
            WHERE model_name = 'META'
        """)
        meta = cur.fetchone()
        
        # If exists, drop it first
        if meta:
            print(f"Dropping existing META model using {meta[0]}.{meta[1]}")
            cur.execute("BEGIN SEM_APIS.DROP_SEM_MODEL('META'); END;")
            
            # Drop the table if it exists
            try:
                cur.execute(f"DROP TABLE {meta[1]}")
                print(f"Dropped table {meta[1]}")
            except:
                print(f"Table {meta[1]} already dropped or doesn't exist")
        
        # Create permanent table for META model
        print("\nCreating permanent table META_RDF_DATA...")
        cur.execute("""
            CREATE TABLE META_RDF_DATA (
                id NUMBER GENERATED ALWAYS AS IDENTITY,
                triple SDO_RDF_TRIPLE_S,
                CONSTRAINT meta_rdf_data_pk PRIMARY KEY (id)
            )
        """)
        
        # Create the model
        print("\nCreating META model...")
        cur.execute("""
            BEGIN
                SEM_APIS.CREATE_SEM_MODEL(
                    model_name => 'META',
                    table_name => 'META_RDF_DATA',
                    column_name => 'TRIPLE'
                );
            END;
        """)
        
        # Load meta.ttl if it exists
        meta_ttl = Path('meta.ttl')
        if meta_ttl.exists():
            print("\nLoading meta.ttl into META model...")
            load_ttl_file('META', meta_ttl)
        else:
            print("\nWarning: meta.ttl not found in current directory")
            
        conn.commit()
        print("\nMETA model initialized successfully")
        
    except Exception as e:
        print(f"Error initializing META model: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def create_model(model_name, force=True):
    """Create a new RDF model with a permanent table.
    
    Args:
        model_name: Name of the model to create
        force: Whether to force drop existing tables
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print(f"\n=== Creating {model_name} Model ===")
        
        # Check if model exists
        cur.execute("""
            SELECT owner, table_name 
            FROM MDSYS.SEM_MODEL$ 
            WHERE model_name = :1
        """, [model_name])
        model = cur.fetchone()
        
        # If exists, drop it first
        if model:
            print(f"Dropping existing model using {model[0]}.{model[1]}")
            try:
                cur.execute(f"BEGIN SEM_APIS.DROP_SEM_MODEL('{model_name}'); END;")
            except:
                print("Model may already be dropped")
        
        # Create permanent table with timestamp to avoid conflicts
        timestamp = int(time.time())
        table_name = f"{model_name}_RDF_DATA_{timestamp}"
        print(f"\nCreating permanent table {table_name}...")
        cur.execute(f"""
            CREATE TABLE {table_name} (
                id NUMBER GENERATED ALWAYS AS IDENTITY,
                triple SDO_RDF_TRIPLE_S,
                CONSTRAINT {model_name.lower()}_{timestamp}_pk PRIMARY KEY (id)
            )
        """)
        
        # Create the model
        print(f"\nCreating {model_name} model...")
        cur.execute("""
            BEGIN
                SEM_APIS.CREATE_SEM_MODEL(
                    model_name => :1,
                    table_name => :2,
                    column_name => 'TRIPLE'
                );
            END;
        """, [model_name, table_name])
        
        conn.commit()
        print(f"\n{model_name} model created successfully")
        
    except Exception as e:
        print(f"Error creating model: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def execute_sparql(model_name, query, is_update=False):
    """Execute a SPARQL query against an Oracle RDF model.
    
    Args:
        model_name: Name of the RDF model to query
        query: SPARQL query to execute
        is_update: Whether this is an update query (INSERT/DELETE)
    
    Returns:
        For SELECT queries: List of result rows
        For UPDATE queries: None
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # First verify model exists
        cur.execute("""
            SELECT owner, table_name 
            FROM MDSYS.SEM_MODEL$ 
            WHERE model_name = :1
        """, [model_name])
        model = cur.fetchone()
        if not model:
            print(f"Model {model_name} not found")
            return None
            
        if is_update:
            # Handle INSERT/DELETE queries
            sql = f"""
                BEGIN
                    SEM_APIS.UPDATE_MODEL(
                        models => SEM_MODELS('{model_name}'),
                        sparql_update => q'[{query}]',
                        options => 'USE_BIND_VAR=T'
                    );
                END;
            """
            cur.execute(sql)
            conn.commit()
            print("Update completed successfully")
            return None
        else:
            # Handle SELECT queries
            sql = f"""
                SELECT *
                FROM TABLE(SEM_MATCH(
                    q'[{query}]',
                    SEM_MODELS('{model_name}'),
                    null,
                    SEM_ALIASES(
                        SEM_ALIAS('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
                        SEM_ALIAS('rdfs', 'http://www.w3.org/2000/01/rdf-schema#'),
                        SEM_ALIAS('owl', 'http://www.w3.org/2002/07/owl#'),
                        SEM_ALIAS('meta', 'http://ontologies.louspringer.com/meta#')
                    ),
                    null,
                    null,
                    'USE_BIND_VAR=T'
                ))
            """
            cur.execute(sql)
            
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            
            if not rows:
                print("No results found")
                return []
                
            print("\nQuery Results:")
            for row in rows:
                print(", ".join(str(val) for val in row))
                
            return rows
                
    except Exception as e:
        print(f"Error executing SPARQL: {e}")
        if is_update:
            conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python manage_models.py [list|new-session|show-session|show-changes|export-ttl|show-model <name> [pattern] [limit]|init-meta|load-ttl <model> <file>|create-model <name>|sparql <model> <query> [--update]]")
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
    elif command == 'show-model':
        if len(sys.argv) < 3:
            print("Please provide model name")
            sys.exit(1)
        pattern = sys.argv[3] if len(sys.argv) > 3 else None
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 50
        show_model_contents(sys.argv[2], pattern, limit)
    elif command == 'init-meta':
        initialize_meta_model()
    elif command == 'load-ttl':
        if len(sys.argv) < 4:
            print("Please provide model name and TTL file")
            sys.exit(1)
        load_ttl_file(sys.argv[2], sys.argv[3])
    elif command == 'create-model':
        if len(sys.argv) < 3:
            print("Please provide model name")
            sys.exit(1)
        create_model(sys.argv[2])
    elif command == 'sparql':
        if len(sys.argv) < 4:
            print("Please provide model name and SPARQL query")
            sys.exit(1)
        is_update = len(sys.argv) > 4 and sys.argv[4] == '--update'
        execute_sparql(sys.argv[2], sys.argv[3], is_update)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1) 