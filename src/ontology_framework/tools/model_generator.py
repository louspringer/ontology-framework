"""Model generator for Python files."""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL

# Define namespaces
CODE = Namespace("http://example.org/code#")
MODEL = Namespace("http://example.org/model#")

class ModelGenerator:
    """Generates ontology models for Python files."""
    
    def __init__(self):
        """Initialize the model generator."""
        self.graph = Graph()
        self._setup_namespaces()
        
        # Load existing models if available
        if Path("models.ttl").exists():
            self.graph.parse("models.ttl", format="turtle")
            
    def _setup_namespaces(self):
        """Initialize namespaces in the graph."""
        self.graph.bind("code", CODE)
        self.graph.bind("model", MODEL)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        
    def analyze_file(self, file_path: Union[str, Path]) -> Dict[str, List[str]]:
        """Analyze a Python file to extract model information.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dict containing extracted information
        """
        file_path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            
        info = {
            'imports': [],
            'classes': [],
            'functions': [],
            'dependencies': set(),
            'ontology_refs': set()
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    info['imports'].append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    info['imports'].append(node.module)
            elif isinstance(node, ast.ClassDef):
                info['classes'].append(node.name)
            elif isinstance(node, ast.FunctionDef):
                info['functions'].append(node.name)
            elif isinstance(node, ast.Str):
                # Look for ontology references in strings
                if any(term in node.s for term in ['rdf', 'owl', 'shacl', 'ontology']):
                    info['ontology_refs'].add(node.s)
                    
        return info
        
    def generate_model(self, file_path: Union[str, Path], info: Optional[Dict] = None) -> URIRef:
        """Generate a model for a Python file.
        
        Args:
            file_path: Path to the Python file
            info: Optional pre-analyzed file information
            
        Returns:
            URIRef of the generated model
        """
        file_path = Path(file_path)
        if info is None:
            info = self.analyze_file(file_path)
            
        # Create module URI
        module_name = file_path.stem
        module_uri = URIRef(f"{CODE}{module_name}")
        
        # Add basic module information
        self.graph.add((module_uri, RDF.type, CODE.Module))
        self.graph.add((module_uri, CODE.name, Literal(module_name)))
        self.graph.add((module_uri, CODE.path, Literal(str(file_path))))
        
        # Add classes
        for class_name in info['classes']:
            class_uri = URIRef(f"{CODE}{module_name}_{class_name}")
            self.graph.add((class_uri, RDF.type, CODE.Class))
            self.graph.add((class_uri, CODE.name, Literal(class_name)))
            self.graph.add((class_uri, CODE.definedIn, module_uri))
            
        # Add functions
        for func_name in info['functions']:
            func_uri = URIRef(f"{CODE}{module_name}_{func_name}")
            self.graph.add((func_uri, RDF.type, CODE.Function))
            self.graph.add((func_uri, CODE.name, Literal(func_name)))
            self.graph.add((func_uri, CODE.definedIn, module_uri))
            
        # Add imports as dependencies
        for import_name in info['imports']:
            self.graph.add((module_uri, CODE.imports, Literal(import_name)))
            
        # Add ontology references
        for ref in info['ontology_refs']:
            self.graph.add((module_uri, CODE.hasOntologyReference, Literal(ref)))
            
        # Create model metadata
        model_uri = URIRef(f"{MODEL}{module_name}_model")
        self.graph.add((model_uri, RDF.type, MODEL.CodeModel))
        self.graph.add((model_uri, MODEL.implements, module_uri))
        self.graph.add((model_uri, RDFS.label, Literal(f"Model for {module_name}")))
        
        return model_uri
        
    def save_models(self, file_path: str = "models.ttl"):
        """Save all models to a file.
        
        Args:
            file_path: Path to save the models
        """
        self.graph.serialize(file_path, format="turtle")
        
    def generate_models_for_directory(self, directory: Union[str, Path], pattern: str = "*.py") -> List[URIRef]:
        """Generate models for all Python files in a directory.
        
        Args:
            directory: Directory to scan
            pattern: File pattern to match
            
        Returns:
            List of generated model URIs
        """
        directory = Path(directory)
        models: List[URIRef] = []
        
        for py_file in directory.rglob(pattern):
            try:
                info = self.analyze_file(py_file)
                model_uri = self.generate_model(py_file, info)
                models.append(model_uri)
            except Exception as e:
                print(f"Error processing {py_file}: {e}")
                
        return models 