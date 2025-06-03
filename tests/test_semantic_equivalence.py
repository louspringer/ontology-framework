import unittest
import os
import oracledb
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, BNode
from rdflib.namespace import XSD
from ontology_framework.register_ontology import register_ontology, load_ontology
import re
from collections import defaultdict
from rdflib.term import Node

# Define SHACL namespace
SHACL = Namespace('http://www.w3.org/ns/shacl#')

class TestSemanticEquivalence(unittest.TestCase):
    def setUp(self):
        # Check if Oracle environment variables are set
        oracle_user = os.environ.get('ORACLE_USER')
        oracle_password = os.environ.get('ORACLE_PASSWORD')
        oracle_dsn = os.environ.get('ORACLE_DSN')
        
        if not all([oracle_user, oracle_password, oracle_dsn]):
            self.skipTest("Oracle environment variables not set")
            return
        
        # Initialize thick mode for Oracle
        try:
            oracledb.init_oracle_client()
        except oracledb.ProgrammingError:
            # Client already initialized
            pass
        
        # Set up database connection
        self.connection = oracledb.connect(
            user=oracle_user,
            password=oracle_password,
            dsn=oracle_dsn
        )
        self.cursor = self.connection.cursor()

    def tearDown(self):
        # Close database connection
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def normalize_literal(self, value):
        """Normalize a literal value by handling quotes and whitespace consistently."""
        if not value:
            return value
        
        # Remove surrounding quotes if present (including double-double quotes)
        value = value.strip()
        if value.startswith('""') and value.endswith('""'):
            value = value[2:-2]
        elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        
        # Handle multi-line strings
        if '\n' in value:
            # Split into lines and normalize each line
            lines = []
            for line in value.split('\n'):
                # Normalize the line
                line = line.strip()
                # Remove bullet points and normalize list markers
                line = re.sub(r'^[-•]\s*', '- ', line)  # Convert all bullet points to '-'
                line = re.sub(r'^\d+[).]\s*', '', line)  # Remove numbered list markers
                # Remove excessive whitespace
                line = ' '.join(line.split())
                if line:
                    lines.append(line)
            
            # Remove empty lines at start and end
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()
            
            # Join with normalized newlines
            return '\n'.join(lines)
        else:
            # For single-line strings, collapse whitespace
            return ' '.join(value.split())

    def is_shacl_related(self, s, p, o):
        """Check if a triple is related to SHACL."""
        return (
            str(p).startswith(str(SHACL)) or str(o).startswith(str(SHACL)) or str(s).startswith(str(SHACL))
        )

    def normalize_shacl_statements(self, g):
        """Normalize SHACL statements by focusing on semantic properties rather than node identifiers."""
        normalized = Graph()
        
        # First pass - collect SHACL shape properties
        shape_properties = {}
        for s, p, o in g:
            if any(str(p).startswith(str(SHACL)) for _, p, _ in g.triples((s, None, None))):
                if s not in shape_properties:
                    shape_properties[s] = set()
                shape_properties[s].add((p, o))
        
        # Second pass - group shapes by their properties
        shape_groups = {}
        for shape, props in shape_properties.items():
            # Create a key based on the shape's properties
            key = frozenset((str(p), str(o)) for p, o in props)
            if key not in shape_groups:
                shape_groups[key] = []
            shape_groups[key].append(shape)
        
        # Third pass - map shapes with same properties to consistent identifiers
        shape_map = {}
        for shapes in shape_groups.values():
            base_node = BNode()
            for shape in shapes:
                shape_map[shape] = base_node
        
        # Final pass - add normalized statements
        for s, p, o in g:
            # Map subject if it's a SHACL shape node
            subj = shape_map.get(s, s) if isinstance(s, BNode) else s
            # Map object if it's a SHACL shape node
            obj = shape_map.get(o, o) if isinstance(o, BNode) else o
            
            # Normalize SPARQL queries in literals
            if isinstance(obj, Literal):
                obj = self.normalize_literal(str(obj))
            
            # Add the normalized statement
            normalized.add((subj, p, obj))
        
        return normalized

    def normalize_graph(self, g):
        """Normalize a graph by mapping blank nodes to stable identifiers and normalizing literals."""
        # Create a new graph for the normalized statements
        norm_g = Graph()
        
        # Helper function to normalize literals
        def normalize_literal(lit):
            if isinstance(lit, Literal):
                # Remove quotes and normalize whitespace for string literals
                value = str(lit).strip('"\'').strip()
                if lit.datatype:
                    return Literal(value, datatype=lit.datatype)
                elif lit.language:
                    return Literal(value, lang=lit.language)
                return Literal(value)
            return lit

        # Helper function to get a stable signature for a node
        def get_node_signature(node, visited=None):
            if visited is None:
                visited = set()
            
            if node in visited:
                return []
            
            visited.add(node)
            signature = []
            
            # Collect all properties and their values
            for p, o in sorted(g.predicate_objects(node)):
                if isinstance(o, BNode):
                    if o not in visited:
                        # Recursively get signature for blank node objects
                        o_sig = get_node_signature(o, visited)
                        signature.append((str(p), tuple(o_sig)))
                else:
                    # For non-blank nodes, use the normalized value
                    o_norm = normalize_literal(o) if isinstance(o, Literal) else o
                    signature.append((str(p), str(o_norm)))
            
            # Also collect incoming properties
            for s, p in sorted(g.subject_predicates(node)):
                if isinstance(s, BNode) and s not in visited:
                    s_sig = get_node_signature(s, visited)
                    signature.append(('incoming', str(p), tuple(s_sig)))
            
            visited.remove(node)
            return sorted(signature)

        # First pass: collect all blank nodes and their signatures
        blank_nodes = {}
        for s in g.subjects():
            if isinstance(s, BNode):
                sig = get_node_signature(s)
                blank_nodes[s] = sig

        # Create stable mapping for blank nodes
        node_map = {}
        counter = 1
        
        # First map SHACL shape nodes and their properties
        shape_nodes = []
        shape_properties = {}
        
        # Collect all SHACL shapes and their properties
        for s, p, o in g:
            if str(p) == "http://www.w3.org/ns/shacl#property":
                if isinstance(s, BNode):
                    shape_nodes.append((s, blank_nodes.get(s, [])))
                if isinstance(o, BNode):
                    # Store the shape that owns this property
                    shape_properties[o] = s
                    shape_nodes.append((o, blank_nodes.get(o, [])))
        
        # Sort shape nodes by their signatures for stable ordering
        shape_nodes.sort(key=lambda x: str(x[1]))
        
        # Map shape nodes first
        for node, _ in shape_nodes:
            if node not in node_map:
                node_map[node] = BNode(f"node_{counter}")
                counter += 1
        
        # Then map remaining blank nodes
        remaining_nodes = [(node, sig) for node, sig in blank_nodes.items() if node not in node_map]
        remaining_nodes.sort(key=lambda x: str(x[1]))
        
        for node, _ in remaining_nodes:
            if node not in node_map:
                node_map[node] = BNode(f"node_{counter}")
                counter += 1

        # Add normalized statements to the new graph
        seen_statements = set()  # Track seen statements to avoid duplicates
        
        # First add SHACL shape statements
        for s, p, o in g:
            if str(p) == "http://www.w3.org/ns/shacl#property":
                s_norm = node_map.get(s, s) if isinstance(s, BNode) else s
                o_norm = node_map.get(o, o) if isinstance(o, BNode) else o
                
                stmt_key = (str(s_norm), str(p), str(o_norm))
                if stmt_key not in seen_statements:
                    norm_g.add((s_norm, p, o_norm))
                    seen_statements.add(stmt_key)
                
                # Add all properties of the property node
                if isinstance(o, BNode):
                    for p2, o2 in g.predicate_objects(o):
                        o2_norm = node_map.get(o2, o2) if isinstance(o2, BNode) else normalize_literal(o2)
                        stmt_key = (str(o_norm), str(p2), str(o2_norm))
                        if stmt_key not in seen_statements:
                            norm_g.add((o_norm, p2, o2_norm))
                            seen_statements.add(stmt_key)
        
        # Then add all other statements
        for s, p, o in g:
            if str(p) != "http://www.w3.org/ns/shacl#property":
                s_norm = node_map.get(s, s) if isinstance(s, BNode) else s
                o_norm = node_map.get(o, o) if isinstance(o, BNode) else normalize_literal(o)
                
                stmt_key = (str(s_norm), str(p), str(o_norm))
                if stmt_key not in seen_statements:
                    norm_g.add((s_norm, p, o_norm))
                    seen_statements.add(stmt_key)
        
        # Finally ensure all SHACL property relationships are preserved
        for prop_node, shape_node in shape_properties.items():
            if isinstance(prop_node, BNode) and isinstance(shape_node, BNode):
                prop_norm = node_map.get(prop_node)
                shape_norm = node_map.get(shape_node)
                if prop_norm and shape_norm:
                    stmt_key = (str(shape_norm), "http://www.w3.org/ns/shacl#property", str(prop_norm))
                    if stmt_key not in seen_statements:
                        norm_g.add((shape_norm, URIRef("http://www.w3.org/ns/shacl#property"), prop_norm))
                        seen_statements.add(stmt_key)
        
        # Add any missing SHACL property relationships from the original graph
        for s, p, o in g:
            if str(p) == "http://www.w3.org/ns/shacl#property":
                s_norm = node_map.get(s, s) if isinstance(s, BNode) else s
                o_norm = node_map.get(o, o) if isinstance(o, BNode) else o
                
                stmt_key = (str(s_norm), str(p), str(o_norm))
                if stmt_key not in seen_statements:
                    norm_g.add((s_norm, p, o_norm))
                    seen_statements.add(stmt_key)
        
        # Create a new graph for the final normalized statements
        final_g = Graph()
        
        # Add all statements from the normalized graph to the final graph
        # This ensures that all statements are properly normalized and deduplicated
        for s, p, o in norm_g:
            final_g.add((s, p, o))
        
        return final_g

    def inspect_network_structure(self):
        # Query to get all RDF/SEM views and tables
        sql = """
        SELECT owner, table_name, column_name FROM ALL_TAB_COLUMNS WHERE owner IN ('ADMIN', 'MDSYS')
        AND (
            table_name LIKE '%RDF%'
            OR table_name LIKE '%SEM%'
            OR table_name LIKE '%TRIPLE%'
            OR table_name LIKE '%META%'
        )
        ORDER BY owner, table_name, column_name
        """
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        current_table = None
        for row in rows:
            owner, table_name, column_name = row
            if current_table != f"{owner}.{table_name}":
                current_table = f"{owner}.{table_name}"
                print(f"\n{current_table}:")
            print(f"  {column_name}")

        # Print SEM_MATCH result columns
        print("\nSEM_MATCH result columns:")
        sql = """
        SELECT *
        FROM TABLE(SEM_MATCH(
            'SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5',
            SEM_MODELS('META'),
            null, null, null, null, 'ORACLE_SEM_NETWORK_OWNER=ADMIN ORACLE_SEM_NETWORK=ONTOLOGY_FRAMEWORK')) t
        """
        self.cursor.execute(sql)
        columns = [col[0] for col in self.cursor.description]
        for col in columns:
            print(f"  {col}")

        # Print first few rows from SEM_MATCH
        print("\nFirst few rows from SEM_MATCH:")
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def get_oracle_graph(self):
        """Load the Oracle model into an RDF graph."""
        g = Graph()
        
        # Query Oracle semantic store using SEM_MATCH
        sql = """
        SELECT t.s, t.p, t.o, t.o$rdfvtyp, t.o$rdflang, t.o$rdfltyp FROM TABLE(SEM_MATCH(
            'SELECT ?s ?p ?o WHERE { ?s ?p ?o }',
            SEM_MODELS('META'),
            null, null, null, null, 'ORACLE_SEM_NETWORK_OWNER=ADMIN ORACLE_SEM_NETWORK=ONTOLOGY_FRAMEWORK')) t
        """
        self.cursor.execute(sql)
        
        for row in self.cursor:
            # Handle subject (can be URI or blank node)
            s_value = row[0]
            subj = URIRef(s_value) if s_value.startswith('http') or s_value.startswith('file:') else BNode(s_value)
            
            # Handle predicate (always a URI)
            pred = URIRef(row[1])
            
            # Handle object based on its type
            o_value = row[2]
            o_type = row[3]
            o_lang = row[4]
            o_datatype = row[5]
            
            if o_type == 'URI':
                obj = URIRef(o_value)
            elif o_type == 'BNODE':
                obj = BNode(o_value)
            else:  # Literal
                # Normalize the literal value
                o_value = self.normalize_literal(o_value)
                if o_datatype:
                    obj = Literal(o_value, datatype=URIRef(o_datatype))
                elif o_lang:
                    obj = Literal(o_value, lang=o_lang)
                else:
                    obj = Literal(o_value)
            
            g.add((subj, pred, obj))
        
        return g

    def inspect_loaded_data(self, g):
        """Inspect what data is actually loaded in the graph."""
        # Check available classes
        class_query = """
        SELECT DISTINCT ?type (COUNT(?instance) as ?count)
        WHERE {
            ?instance a ?type .
        }
        GROUP BY ?type ORDER BY ?type
        """
        print("\nAvailable classes and instance counts:")
        for row in g.query(class_query):
            print(f"{row.type}: {row.count}")

        # Check available properties
        prop_query = """
        SELECT DISTINCT ?prop (COUNT(*) as ?count)
        WHERE {
            ?s ?prop ?o .
        }
        GROUP BY ?prop ORDER BY ?prop
        """
        print("\nAvailable properties and usage counts:")
        for row in g.query(prop_query):
            print(f"{row.prop}: {row.count}")

    def normalize_query_results(self, results):
        """Normalize a set of query results by normalizing all literals."""
        normalized = set()
        for row in results:
            # Convert row to list for modification
            norm_row = list(row)
            # Normalize any literals in the row
            for i, item in enumerate(norm_row):
                if isinstance(item, Literal):
                    # Create new literal with normalized value but preserve language/datatype
                    norm_value = self.normalize_literal(str(item))
                    if item.language:
                        norm_row[i] = Literal(norm_value, lang=item.language)
                    elif item.datatype:
                        norm_row[i] = Literal(norm_value, datatype=item.datatype)
                    else:
                        norm_row[i] = Literal(norm_value)
            normalized.add(tuple(norm_row))
        return normalized

    def test_semantic_equivalence(self):
        """Test that the Oracle model maintains semantic equivalence with the original TTL."""
        # Load both graphs
        original_g = Graph()
        original_g.parse("meta.ttl", format="turtle")
        oracle_g = self.get_oracle_graph()

        # Bind namespaces
        META = Namespace('file:///Users/lou/Documents/ontology-framework/meta#')
        original_g.bind('meta', META)
        oracle_g.bind('meta', META)

        # Inspect what's actually loaded
        print("\nOriginal TTL Data:")
        self.inspect_loaded_data(original_g)
        print("\nOracle Model Data:")
        self.inspect_loaded_data(oracle_g)

        # Basic Class Structure Test
        class_query = """
        SELECT ?class ?superclass WHERE {
            ?class a owl:Class .
            OPTIONAL { ?class rdfs:subClassOf ?superclass }
        }
        ORDER BY ?class ?superclass
        """
        original_classes = self.normalize_query_results(original_g.query(class_query))
        oracle_classes = self.normalize_query_results(oracle_g.query(class_query))
        self.assertEqual(original_classes, oracle_classes, "Class hierarchy differs")

        # Basic Property Structure Test
        property_query = """
        SELECT ?prop ?type WHERE {
            ?prop a ?type .
            FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty, rdf:Property))
        }
        ORDER BY ?prop ?type
        """
        original_props = self.normalize_query_results(original_g.query(property_query))
        oracle_props = self.normalize_query_results(oracle_g.query(property_query))
        self.assertEqual(original_props, oracle_props, "Property definitions differ")

        # Domain and Range Definitions
        domain_range_query = """
        SELECT ?prop ?domain ?range WHERE {
            ?prop a ?type .
            OPTIONAL { ?prop rdfs:domain ?domain }
            OPTIONAL { ?prop rdfs:range ?range }
            FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty, rdf:Property))
        }
        ORDER BY ?prop ?domain ?range
        """
        original_domains = self.normalize_query_results(original_g.query(domain_range_query))
        oracle_domains = self.normalize_query_results(oracle_g.query(domain_range_query))
        self.assertEqual(original_domains, oracle_domains, "Property domains and ranges differ")

        # Basic Instance Data Test
        instance_query = """
        SELECT ?instance ?type ?label WHERE {
            ?instance a ?type .
            OPTIONAL { ?instance rdfs:label ?label }
            FILTER(?type != owl:Class && ?type != owl:ObjectProperty && ?type != owl:DatatypeProperty)
        }
        ORDER BY ?instance ?type ?label
        """
        original_instances = self.normalize_query_results(original_g.query(instance_query))
        oracle_instances = self.normalize_query_results(oracle_g.query(instance_query))
        self.assertEqual(original_instances, oracle_instances, "Instance data differs")

        # Documentation and Labels
        doc_query = """
        SELECT ?entity ?label ?comment WHERE {
            ?entity a ?type .
            OPTIONAL { ?entity rdfs:label ?label }
            OPTIONAL { ?entity rdfs:comment ?comment }
        }
        ORDER BY ?entity ?label
        """
        original_docs = self.normalize_query_results(original_g.query(doc_query))
        oracle_docs = self.normalize_query_results(oracle_g.query(doc_query))
        self.assertEqual(original_docs, oracle_docs, "Documentation and labels differ")

        # Only run more complex queries if relevant data is present
        if any(isinstance(o, URIRef) and str(o) == str(META.SecurityConcept) 
               for _, _, o in oracle_g.triples((None, RDF.type, None))):
            # Security concept relationships
            security_query = """
            SELECT ?concept ?related WHERE {
                ?concept a <file:///Users/lou/Documents/ontology-framework/meta#SecurityConcept> .
                OPTIONAL { ?concept ?rel ?related .
                          ?related a <file:///Users/lou/Documents/ontology-framework/meta#SecurityConcept> }
            }
            ORDER BY ?concept ?related
            """
            original_security = self.normalize_query_results(original_g.query(security_query))
            oracle_security = self.normalize_query_results(oracle_g.query(security_query))
            self.assertEqual(original_security, oracle_security, "Security concept relationships differ")

        # Check for SHACL shapes if present
        if any(isinstance(o, URIRef) and str(o) == str(SHACL.NodeShape) 
               for _, _, o in oracle_g.triples((None, RDF.type, None))):
            # Basic SHACL shape test
            shape_query = """
            SELECT ?shape ?targetClass WHERE {
                ?shape a sh:NodeShape ;
                       sh:targetClass ?targetClass .
            }
            ORDER BY ?shape ?targetClass
            """
            original_shapes = self.normalize_query_results(original_g.query(shape_query))
            oracle_shapes = self.normalize_query_results(oracle_g.query(shape_query))
            self.assertEqual(original_shapes, oracle_shapes, "SHACL shapes differ")

if __name__ == '__main__':
    unittest.main()
