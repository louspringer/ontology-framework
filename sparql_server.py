from pathlib import Path
import glob
from rdflib import Graph, Namespace
from flask import Flask, request, jsonify
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize the RDF graph with default in-memory store
graph = Graph()

def load_ttl_files():
    """Load all .ttl files from the current directory into the graph."""
    ttl_files = glob.glob("*.ttl")
    total_loaded = 0
    
    for ttl_file in ttl_files:
        try:
            logger.info(f"Loading {ttl_file}...")
            graph.parse(ttl_file, format="turtle")
            logger.info(f"Successfully loaded {ttl_file}")
            total_loaded += 1
        except Exception as e:
            logger.error(f"Error loading {ttl_file}: {str(e)}")
    
    logger.info(f"Successfully loaded {total_loaded} files with {len(graph)} total triples")

@app.route('/sparql', methods=['POST'])
def sparql_endpoint():
    """SPARQL endpoint that accepts queries via POST requests."""
    try:
        query = request.json.get('query')
        if not query:
            return jsonify({'error': 'No query provided'}), 400

        results = graph.query(query)
        
        # Convert results to a JSON-serializable format
        if results.type == 'SELECT':
            return jsonify({
                'head': {'vars': results.vars},
                'results': {
                    'bindings': [
                        {str(var): {'value': str(value)} for var, value in zip(results.vars, row)}
                        for row in results
                    ]
                }
            })
        elif results.type == 'ASK':
            return jsonify({'boolean': results.askAnswer})
        else:
            return jsonify({'results': [str(x) for x in results]})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/info', methods=['GET'])
def get_info():
    """Get information about the loaded graph."""
    return jsonify({
        'total_triples': len(graph),
        'namespaces': [{'prefix': prefix, 'uri': uri} for prefix, uri in graph.namespaces()]
    })

if __name__ == '__main__':
    # Load all .ttl files
    load_ttl_files()
    
    # Start the server
    app.run(host='0.0.0.0', port=5001) 