"""Analyze model coverage in the codebase."""

from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef, Variable
from rdflib.namespace import RDF, RDFS, OWL
from rdflib.query import ResultRow
import logging
from typing import Dict, List, Set, Tuple, TypedDict, Any, Union
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
CODE = Namespace("http://example.org/code#")
MODEL = Namespace("http://example.org/model#")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

class AnalysisResults(TypedDict):
    missing_models: List[str]
    has_models: List[str]
    no_model_needed: List[str]
    errors: List[str]

def load_models() -> Graph:
    """Load all model information."""
    g = Graph()
    
    # Load guidance ontology
    if Path("guidance.ttl").exists():
        g.parse("guidance.ttl", format="turtle")
        logger.info("Loaded guidance.ttl")
    else:
        logger.warning("guidance.ttl not found")
        
    # Load existing models
    if Path("models.ttl").exists():
        g.parse("models.ttl", format="turtle")
        logger.info("Loaded models.ttl")
    else:
        logger.warning("models.ttl not found")
        
    return g

def get_modeled_files(graph: Graph) -> Set[str]:
    """Get all files that have models."""
    query = """
    PREFIX code: <http://example.org/code#>
    PREFIX model: <http://example.org/model#>
    
    SELECT DISTINCT ?path
    WHERE {
        ?module a code:Module ;
                code:path ?path .
    }
    """
    results = graph.query(query)
    paths: Set[str] = set()
    for result in results:
        if isinstance(result, ResultRow):
            path = result.get('path')
            if path:
                paths.add(str(path))
        elif isinstance(result, (tuple, list)) and len(result) > 0:
            path = result[0]
            if path:
                paths.add(str(path))
    return paths

def check_file_requires_model(graph: Graph, file_path: str) -> bool:
    """Check if a file requires a model."""
    query = """
    PREFIX code: <http://example.org/code#>
    PREFIX model: <http://example.org/model#>
    
    ASK {
        ?module a code:Module ;
                code:path ?path ;
                code:requiresModel true .
        FILTER(str(?path) = "%s")
    }
    """ % file_path
    
    result = graph.query(query)
    if hasattr(result, 'askAnswer'):
        return bool(result.askAnswer)
    elif isinstance(result, bool):
        return result
    return False

def analyze_codebase(root_dir: str = "src/ontology_framework") -> AnalysisResults:
    """Analyze which files lack required models."""
    graph = load_models()
    modeled_files = get_modeled_files(graph)
    
    results: AnalysisResults = {
        "missing_models": [],
        "has_models": [],
        "no_model_needed": [],
        "errors": []
    }
    
    # Convert root_dir to absolute path
    root_path = Path(root_dir).resolve()
    
    # Scan all Python files
    for py_file in root_path.rglob("*.py"):
        try:
            # Get path relative to root_dir
            rel_path = os.path.relpath(py_file, root_path)
            needs_model = check_file_requires_model(graph, rel_path)
            
            if needs_model:
                if rel_path in modeled_files:
                    results["has_models"].append(f"{rel_path}")
                else:
                    results["missing_models"].append(f"{rel_path}")
            else:
                results["no_model_needed"].append(f"{rel_path}")
        except Exception as e:
            results["errors"].append(f"Error processing {py_file}: {str(e)}")
            
    return results

def main():
    """Main analysis function."""
    print("\nAnalyzing model coverage in codebase...\n")
    results = analyze_codebase()
    
    print("Files Missing Required Models:")
    print("=============================")
    for file in sorted(results["missing_models"]):
        print(f"❌ {file}")
        
    print("\nFiles with Models:")
    print("=================")
    for file in sorted(results["has_models"]):
        print(f"✓ {file}")
        
    print("\nFiles Not Requiring Models:")
    print("=========================")
    for file in sorted(results["no_model_needed"]):
        print(f"- {file}")
        
    if results["errors"]:
        print("\nErrors:")
        print("=======")
        for error in results["errors"]:
            print(f"! {error}")

if __name__ == "__main__":
    main() 