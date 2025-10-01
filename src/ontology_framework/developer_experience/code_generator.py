"""Generate Python classes and code from ontology definitions"""

from typing import Dict, List, Optional, Set, Any
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from pathlib import Path
import re
from ..prefix_map import default_prefix_map


class CodeGenerator:
    """Generate Python code from ontology definitions"""
    
    def __init__(self):
        self.graph = Graph()
        self.generated_classes = {}
        self.imports = set()
    
    def generate_python_classes(self, ontology_file: str, output_dir: str = "generated") -> Dict[str, Any]:
        """Generate Python classes from ontology"""
        self.graph.parse(ontology_file)
        
        result = {
            "generated_files": [],
            "classes": [],
            "properties": [],
            "summary": {}
        }
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate classes
        classes = list(self.graph.subjects(RDF.type, OWL.Class))
        for cls in classes:
            class_code = self._generate_class_code(cls)
            if class_code:
                result["classes"].append(class_code)
        
        # Generate properties as mixins or utilities
        properties = (list(self.graph.subjects(RDF.type, OWL.ObjectProperty)) +
                     list(self.graph.subjects(RDF.type, OWL.DatatypeProperty)))
        
        for prop in properties:
            prop_code = self._generate_property_code(prop)
            if prop_code:
                result["properties"].append(prop_code)
        
        # Write files
        main_file = self._write_main_module(result, output_path)
        init_file = self._write_init_file(result, output_path)
        utils_file = self._write_utils_file(result, output_path)
        
        result["generated_files"] = [main_file, init_file, utils_file]
        result["summary"] = {
            "classes_count": len(result["classes"]),
            "properties_count": len(result["properties"]),
            "output_directory": str(output_path)
        }
        
        return result
    
    def generate_pydantic_models(self, ontology_file: str, output_file: str = "models.py") -> str:
        """Generate Pydantic models from ontology"""
        self.graph.parse(ontology_file)
        
        code_lines = [
            "\"\"\"Generated Pydantic models from ontology\"\"\"",
            "",
            "from typing import Optional, List, Union, Any",
            "from pydantic import BaseModel, Field, validator",
            "from datetime import datetime",
            "from enum import Enum",
            "",
        ]
        
        # Generate enums for classes with limited instances
        enums = self._generate_enums()
        code_lines.extend(enums)
        
        # Generate base model
        code_lines.extend([
            "class OntologyBase(BaseModel):",
            "    \"\"\"Base class for all ontology models\"\"\"",
            "    uri: Optional[str] = Field(None, description='URI of the resource')",
            "    label: Optional[str] = Field(None, description='Human-readable label')",
            "    comment: Optional[str] = Field(None, description='Description or comment')",
            "",
            "    class Config:",
            "        extra = 'allow'",
            "        validate_assignment = True",
            "",
        ])
        
        # Generate model classes
        classes = list(self.graph.subjects(RDF.type, OWL.Class))
        for cls in classes:
            model_code = self._generate_pydantic_model(cls)
            code_lines.extend(model_code)
            code_lines.append("")
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(code_lines))
        
        return output_file
    
    def generate_sparql_queries(self, ontology_file: str, output_file: str = "queries.py") -> str:
        """Generate common SPARQL queries for the ontology"""
        self.graph.parse(ontology_file)
        
        code_lines = [
            "\"\"\"Generated SPARQL queries for ontology\"\"\"",
            "",
            "from typing import Dict, List, Optional",
            "",
            "class OntologyQueries:",
            "    \"\"\"Common SPARQL queries for the ontology\"\"\"",
            "",
        ]
        
        # Generate queries for each class
        classes = list(self.graph.subjects(RDF.type, OWL.Class))
        for cls in classes:
            query_methods = self._generate_class_queries(cls)
            code_lines.extend(query_methods)
        
        # Generate utility queries
        utility_queries = self._generate_utility_queries()
        code_lines.extend(utility_queries)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(code_lines))
        
        return output_file
    
    def generate_rest_api(self, ontology_file: str, output_dir: str = "api") -> Dict[str, str]:
        """Generate REST API endpoints for ontology"""
        self.graph.parse(ontology_file)
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        generated_files = {}
        
        # Generate FastAPI main file
        main_api = self._generate_fastapi_main()
        main_file = output_path / "main.py"
        with open(main_file, 'w') as f:
            f.write(main_api)
        generated_files["main"] = str(main_file)
        
        # Generate routers for each class
        classes = list(self.graph.subjects(RDF.type, OWL.Class))
        for cls in classes:
            router_code = self._generate_class_router(cls)
            class_name = self._get_class_name(cls)
            router_file = output_path / f"{class_name.lower()}_router.py"
            with open(router_file, 'w') as f:
                f.write(router_code)
            generated_files[class_name] = str(router_file)
        
        # Generate schemas
        schemas_code = self._generate_api_schemas()
        schemas_file = output_path / "schemas.py"
        with open(schemas_file, 'w') as f:
            f.write(schemas_code)
        generated_files["schemas"] = str(schemas_file)
        
        return generated_files
    
    def _generate_class_code(self, cls: URIRef) -> Optional[Dict[str, Any]]:
        """Generate Python class code for an OWL class"""
        class_name = self._get_class_name(cls)
        if not class_name:
            return None
        
        # Get class properties
        properties = self._get_class_properties(cls)
        superclasses = list(self.graph.objects(cls, RDFS.subClassOf))
        
        # Generate class definition
        class_def = {
            "name": class_name,
            "uri": str(cls),
            "superclasses": [self._get_class_name(sc) for sc in superclasses if isinstance(sc, URIRef)],
            "properties": properties,
            "code": self._format_class_code(class_name, cls, properties, superclasses)
        }
        
        return class_def
    
    def _generate_property_code(self, prop: URIRef) -> Optional[Dict[str, Any]]:
        """Generate code for an OWL property"""
        prop_name = self._get_property_name(prop)
        if not prop_name:
            return None
        
        domain = list(self.graph.objects(prop, RDFS.domain))
        range_vals = list(self.graph.objects(prop, RDFS.range))
        
        prop_def = {
            "name": prop_name,
            "uri": str(prop),
            "domain": [str(d) for d in domain],
            "range": [str(r) for r in range_vals],
            "type": "ObjectProperty" if (prop, RDF.type, OWL.ObjectProperty) in self.graph else "DatatypeProperty"
        }
        
        return prop_def
    
    def _generate_pydantic_model(self, cls: URIRef) -> List[str]:
        """Generate Pydantic model for a class"""
        class_name = self._get_class_name(cls)
        if not class_name:
            return []
        
        lines = [
            f"class {class_name}(OntologyBase):",
            f'    """Model for {class_name}"""',
        ]
        
        # Add class-specific properties
        properties = self._get_class_properties(cls)
        for prop in properties:
            prop_line = self._format_pydantic_property(prop)
            lines.append(f"    {prop_line}")
        
        if not properties:
            lines.append("    pass")
        
        return lines
    
    def _generate_class_queries(self, cls: URIRef) -> List[str]:
        """Generate SPARQL query methods for a class"""
        class_name = self._get_class_name(cls)
        if not class_name:
            return []
        
        lines = [
            f"    @staticmethod",
            f"    def get_all_{class_name.lower()}s() -> str:",
            f'        """Get all instances of {class_name}"""',
            f'        return """',
            f'        SELECT ?instance ?label WHERE {{',
            f'            ?instance a <{cls}> .',
            f'            OPTIONAL {{ ?instance rdfs:label ?label }}',
            f'        }}',
            f'        """',
            "",
            f"    @staticmethod",
            f"    def get_{class_name.lower()}_by_uri(uri: str) -> str:",
            f'        """Get specific {class_name} by URI"""',
            f'        return f"""',
            f'        DESCRIBE <{{uri}}> WHERE {{',
            f'            <{{uri}}> a <{cls}> .',
            f'        }}',
            f'        """',
            "",
        ]
        
        return lines
    
    def _generate_fastapi_main(self) -> str:
        """Generate main FastAPI application"""
        return '''"""Generated FastAPI application for ontology"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI(
    title="Ontology API",
    description="Auto-generated API for ontology access",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Ontology API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers here
# from .class_router import router as class_router
# app.include_router(class_router, prefix="/api/v1")
'''
    
    def _generate_class_router(self, cls: URIRef) -> str:
        """Generate FastAPI router for a class"""
        class_name = self._get_class_name(cls)
        
        return f'''"""Router for {class_name} endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from .schemas import {class_name}Schema, {class_name}CreateSchema

router = APIRouter(prefix="/{class_name.lower()}", tags=["{class_name}"])

@router.get("/", response_model=List[{class_name}Schema])
async def get_{class_name.lower()}s():
    """Get all {class_name} instances"""
    # Implementation would query the ontology
    return []

@router.get("/{{item_id}}", response_model={class_name}Schema)
async def get_{class_name.lower()}(item_id: str):
    """Get specific {class_name} by ID"""
    # Implementation would query the ontology
    raise HTTPException(status_code=404, detail="{class_name} not found")

@router.post("/", response_model={class_name}Schema)
async def create_{class_name.lower()}(item: {class_name}CreateSchema):
    """Create new {class_name}"""
    # Implementation would add to ontology
    return item

@router.put("/{{item_id}}", response_model={class_name}Schema)
async def update_{class_name.lower()}(item_id: str, item: {class_name}CreateSchema):
    """Update {class_name}"""
    # Implementation would update ontology
    return item

@router.delete("/{{item_id}}")
async def delete_{class_name.lower()}(item_id: str):
    """Delete {class_name}"""
    # Implementation would remove from ontology
    return {{"message": "{class_name} deleted"}}
'''
    
    def _get_class_name(self, cls: URIRef) -> Optional[str]:
        """Extract class name from URI"""
        uri_str = str(cls)
        
        # Try to get from fragment or last path segment
        if '#' in uri_str:
            name = uri_str.split('#')[-1]
        else:
            name = uri_str.split('/')[-1]
        
        # Clean up the name
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        if name and name[0].isalpha():
            return name.capitalize()
        
        return None
    
    def _get_property_name(self, prop: URIRef) -> Optional[str]:
        """Extract property name from URI"""
        uri_str = str(prop)
        
        # Try to get from fragment or last path segment
        if '#' in uri_str:
            name = uri_str.split('#')[-1]
        else:
            name = uri_str.split('/')[-1]
        
        # Clean up the name
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        if name and name[0].isalpha():
            return name.lower()
        
        return None
    
    def _get_class_properties(self, cls: URIRef) -> List[Dict[str, Any]]:
        """Get properties that have this class as domain"""
        properties = []
        
        for prop in self.graph.subjects(RDFS.domain, cls):
            prop_name = self._get_property_name(prop)
            if prop_name:
                range_vals = list(self.graph.objects(prop, RDFS.range))
                prop_type = "ObjectProperty" if (prop, RDF.type, OWL.ObjectProperty) in self.graph else "DatatypeProperty"
                
                properties.append({
                    "name": prop_name,
                    "uri": str(prop),
                    "range": [str(r) for r in range_vals],
                    "type": prop_type
                })
        
        return properties
    
    def _format_class_code(self, class_name: str, cls: URIRef, properties: List[Dict], superclasses: List[URIRef]) -> str:
        """Format the complete class code"""
        lines = [
            f"class {class_name}:",
            f'    """Generated class for {cls}"""',
            f'    URI = "{cls}"',
            "",
        ]
        
        # Add constructor
        lines.extend([
            "    def __init__(self, uri=None, **kwargs):",
            "        self.uri = uri or self.URI",
            "        for key, value in kwargs.items():",
            "            setattr(self, key, value)",
            "",
        ])
        
        # Add property methods
        for prop in properties:
            prop_method = self._format_property_method(prop)
            lines.extend(prop_method)
        
        return '\n'.join(lines)
    
    def _format_property_method(self, prop: Dict[str, Any]) -> List[str]:
        """Format a property method"""
        prop_name = prop["name"]
        
        return [
            f"    def get_{prop_name}(self):",
            f'        """Get {prop_name} property"""',
            f"        return getattr(self, '{prop_name}', None)",
            "",
            f"    def set_{prop_name}(self, value):",
            f'        """Set {prop_name} property"""',
            f"        setattr(self, '{prop_name}', value)",
            "",
        ]
    
    def _format_pydantic_property(self, prop: Dict[str, Any]) -> str:
        """Format a Pydantic property field"""
        prop_name = prop["name"]
        prop_type = "str"  # Default type
        
        # Determine type based on range
        if prop["range"]:
            range_uri = prop["range"][0]
            if "string" in range_uri.lower() or "literal" in range_uri.lower():
                prop_type = "str"
            elif "int" in range_uri.lower():
                prop_type = "int"
            elif "float" in range_uri.lower() or "double" in range_uri.lower():
                prop_type = "float"
            elif "bool" in range_uri.lower():
                prop_type = "bool"
        
        return f"{prop_name}: Optional[{prop_type}] = Field(None, description='{prop_name} property')"
    
    def _generate_enums(self) -> List[str]:
        """Generate enum classes for classes with limited instances"""
        # This would analyze the ontology for classes that should be enums
        return []
    
    def _generate_utility_queries(self) -> List[str]:
        """Generate utility SPARQL queries"""
        return [
            "    @staticmethod",
            "    def get_all_classes() -> str:",
            '        """Get all classes in the ontology"""',
            '        return """',
            '        SELECT ?class ?label WHERE {',
            '            ?class a owl:Class .',
            '            OPTIONAL { ?class rdfs:label ?label }',
            '        }',
            '        """',
            "",
            "    @staticmethod",
            "    def get_class_hierarchy() -> str:",
            '        """Get class hierarchy"""',
            '        return """',
            '        SELECT ?class ?superClass WHERE {',
            '            ?class rdfs:subClassOf ?superClass .',
            '        }',
            '        """',
            "",
        ]
    
    def _generate_api_schemas(self) -> str:
        """Generate API schemas"""
        return '''"""API schemas for ontology entities"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BaseSchema(BaseModel):
    uri: Optional[str] = Field(None, description="Resource URI")
    label: Optional[str] = Field(None, description="Human-readable label")
    comment: Optional[str] = Field(None, description="Description")

class BaseCreateSchema(BaseModel):
    label: str = Field(..., description="Human-readable label")
    comment: Optional[str] = Field(None, description="Description")

# Add specific schemas for each class here
'''
    
    def _write_main_module(self, result: Dict[str, Any], output_path: Path) -> str:
        """Write the main module file"""
        main_file = output_path / "ontology_classes.py"
        
        lines = [
            '"""Generated ontology classes"""',
            "",
            "from typing import Optional, List, Any",
            "",
        ]
        
        # Add all class codes
        for class_info in result["classes"]:
            lines.append(class_info["code"])
            lines.append("")
        
        with open(main_file, 'w') as f:
            f.write('\n'.join(lines))
        
        return str(main_file)
    
    def _write_init_file(self, result: Dict[str, Any], output_path: Path) -> str:
        """Write the __init__.py file"""
        init_file = output_path / "__init__.py"
        
        lines = ['"""Generated ontology package"""', ""]
        
        # Add imports for all classes
        class_names = [class_info["name"] for class_info in result["classes"]]
        if class_names:
            lines.append(f"from .ontology_classes import {', '.join(class_names)}")
            lines.append("")
            lines.append(f"__all__ = {class_names}")
        
        with open(init_file, 'w') as f:
            f.write('\n'.join(lines))
        
        return str(init_file)
    
    def _write_utils_file(self, result: Dict[str, Any], output_path: Path) -> str:
        """Write utilities file"""
        utils_file = output_path / "utils.py"
        
        utils_code = '''"""Utilities for generated ontology classes"""

from typing import Dict, List, Any, Type
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

class OntologyUtils:
    """Utility functions for ontology classes"""
    
    @staticmethod
    def create_instance(class_type: Type, uri: str, **properties) -> Any:
        """Create an instance of an ontology class"""
        instance = class_type(uri=uri)
        for prop, value in properties.items():
            setattr(instance, prop, value)
        return instance
    
    @staticmethod
    def to_rdf(instance: Any) -> Graph:
        """Convert instance to RDF graph"""
        graph = Graph()
        instance_uri = URIRef(instance.uri)
        
        # Add type assertion
        if hasattr(instance.__class__, 'URI'):
            graph.add((instance_uri, RDF.type, URIRef(instance.__class__.URI)))
        
        # Add properties
        for attr_name in dir(instance):
            if not attr_name.startswith('_') and attr_name not in ['uri', 'URI']:
                value = getattr(instance, attr_name)
                if value is not None and not callable(value):
                    # This would need proper property URI mapping
                    prop_uri = URIRef(f"http://example.org/property/{attr_name}")
                    if isinstance(value, str):
                        graph.add((instance_uri, prop_uri, Literal(value)))
                    else:
                        graph.add((instance_uri, prop_uri, URIRef(str(value))))
        
        return graph
    
    @staticmethod
    def from_rdf(graph: Graph, class_type: Type, uri: str) -> Any:
        """Create instance from RDF graph"""
        instance_uri = URIRef(uri)
        instance = class_type(uri=uri)
        
        # Extract properties from graph
        for pred, obj in graph.predicate_objects(instance_uri):
            prop_name = str(pred).split('/')[-1].split('#')[-1]
            if isinstance(obj, Literal):
                setattr(instance, prop_name, str(obj))
            else:
                setattr(instance, prop_name, str(obj))
        
        return instance
'''
        
        with open(utils_file, 'w') as f:
            f.write(utils_code)
        
        return str(utils_file)