"""
Module for analyzing ontology structure and content.
"""

from typing import List, Dict, Optional, Set, Tuple, Any, Union, cast
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OntologyAnalyzer:
    """Comprehensive ontology analysis using RDFlib."""
    
    def __init__(self, ttl_file: str):
        """Initialize the analyzer with a TTL file."""
        self.graph = Graph()
        self.ttl_file = ttl_file
        self.load_ontology()
        
    def load_ontology(self) -> None:
        """Load the ontology file into the graph."""
        try:
            self.graph.parse(self.ttl_file, format="turtle")
            logger.info(f"Successfully loaded ontology from {self.ttl_file}")
        except Exception as e:
            logger.error(f"Failed to load ontology: {e}")
            raise
            
    def analyze_classes(self) -> Dict[str, Union[int, Dict[URIRef, Set[URIRef]], Set[Tuple[URIRef, URIRef]]]]:
        """Analyze classes in the ontology."""
        classes = set(self.graph.subjects(RDF.type, OWL.Class))
        class_info: Dict[str, Union[int, Dict[URIRef, Set[URIRef]], Set[Tuple[URIRef, URIRef]]]] = {
            'total': len(classes),
            'with_documentation': 0,
            'with_comments': 0,
            'subclasses': {},
            'disjoint_classes': set(),
            'equivalent_classes': set()
        }
        
        for cls in classes:
            # Check documentation
            if (cls, RDFS.label, None) in self.graph:
                class_info['with_documentation'] = cast(int, class_info['with_documentation']) + 1
            if (cls, RDFS.comment, None) in self.graph:
                class_info['with_comments'] = cast(int, class_info['with_comments']) + 1
                
            # Check subclass relationships
            for superclass in self.graph.objects(cls, RDFS.subClassOf):
                if superclass in classes:
                    subclasses = cast(Dict[URIRef, Set[URIRef]], class_info['subclasses'])
                    if cls not in subclasses:
                        subclasses[cls] = set()
                    subclasses[cls].add(superclass)
                    
            # Check disjoint classes
            for disjoint in self.graph.objects(cls, OWL.disjointWith):
                if disjoint in classes:
                    disjoint_classes = cast(Set[Tuple[URIRef, URIRef]], class_info['disjoint_classes'])
                    disjoint_classes.add((cls, disjoint))
                    
            # Check equivalent classes
            for equivalent in self.graph.objects(cls, OWL.equivalentClass):
                if equivalent in classes:
                    equivalent_classes = cast(Set[Tuple[URIRef, URIRef]], class_info['equivalent_classes'])
                    equivalent_classes.add((cls, equivalent))
                    
        return class_info
        
    def analyze_properties(self) -> Dict[str, Union[int, Set[URIRef]]]:
        """Analyze properties in the ontology."""
        object_props = set(self.graph.subjects(RDF.type, OWL.ObjectProperty))
        datatype_props = set(self.graph.subjects(RDF.type, OWL.DatatypeProperty))
        all_props = object_props | datatype_props
        
        prop_info: Dict[str, Union[int, Set[URIRef]]] = {
            'total': len(all_props),
            'object_properties': len(object_props),
            'datatype_properties': len(datatype_props),
            'with_documentation': 0,
            'with_comments': 0,
            'with_domain': 0,
            'with_range': 0,
            'functional': set(),
            'inverse_functional': set(),
            'transitive': set(),
            'symmetric': set(),
            'asymmetric': set(),
            'reflexive': set(),
            'irreflexive': set()
        }
        
        for prop in all_props:
            # Check documentation
            if (prop, RDFS.label, None) in self.graph:
                prop_info['with_documentation'] = cast(int, prop_info['with_documentation']) + 1
            if (prop, RDFS.comment, None) in self.graph:
                prop_info['with_comments'] = cast(int, prop_info['with_comments']) + 1
                
            # Check domain/range
            if (prop, RDFS.domain, None) in self.graph:
                prop_info['with_domain'] = cast(int, prop_info['with_domain']) + 1
            if (prop, RDFS.range, None) in self.graph:
                prop_info['with_range'] = cast(int, prop_info['with_range']) + 1
                
            # Check property characteristics
            if (prop, RDF.type, OWL.FunctionalProperty) in self.graph:
                functional = cast(Set[URIRef], prop_info['functional'])
                functional.add(prop)
            if (prop, RDF.type, OWL.InverseFunctionalProperty) in self.graph:
                inverse_functional = cast(Set[URIRef], prop_info['inverse_functional'])
                inverse_functional.add(prop)
            if (prop, RDF.type, OWL.TransitiveProperty) in self.graph:
                transitive = cast(Set[URIRef], prop_info['transitive'])
                transitive.add(prop)
            if (prop, RDF.type, OWL.SymmetricProperty) in self.graph:
                symmetric = cast(Set[URIRef], prop_info['symmetric'])
                symmetric.add(prop)
            if (prop, RDF.type, OWL.AsymmetricProperty) in self.graph:
                asymmetric = cast(Set[URIRef], prop_info['asymmetric'])
                asymmetric.add(prop)
            if (prop, RDF.type, OWL.ReflexiveProperty) in self.graph:
                reflexive = cast(Set[URIRef], prop_info['reflexive'])
                reflexive.add(prop)
            if (prop, RDF.type, OWL.IrreflexiveProperty) in self.graph:
                irreflexive = cast(Set[URIRef], prop_info['irreflexive'])
                irreflexive.add(prop)
                
        return prop_info
        
    def analyze_individuals(self) -> Dict[str, Union[int, Dict[URIRef, Set[URIRef]]]]:
        """Analyze individuals in the ontology."""
        individuals = set(self.graph.subjects(RDF.type, OWL.NamedIndividual))
        
        ind_info: Dict[str, Union[int, Dict[URIRef, Set[URIRef]]]] = {
            'total': len(individuals),
            'with_documentation': 0,
            'with_comments': 0,
            'with_types': {}
        }
        
        for ind in individuals:
            # Check documentation
            if (ind, RDFS.label, None) in self.graph:
                ind_info['with_documentation'] = cast(int, ind_info['with_documentation']) + 1
            if (ind, RDFS.comment, None) in self.graph:
                ind_info['with_comments'] = cast(int, ind_info['with_comments']) + 1
                
            # Check types
            for type_ in self.graph.objects(ind, RDF.type):
                if type_ != OWL.NamedIndividual:
                    with_types = cast(Dict[URIRef, Set[URIRef]], ind_info['with_types'])
                    if ind not in with_types:
                        with_types[ind] = set()
                    with_types[ind].add(type_)
                    
        return ind_info
        
    def analyze_imports(self) -> Dict[str, Union[int, Set[URIRef]]]:
        """Analyze imports in the ontology."""
        imports = set(self.graph.objects(None, OWL.imports))
        
        import_info: Dict[str, Union[int, Set[URIRef]]] = {
            'total': len(imports),
            'imports': imports,
            'accessible': set(),
            'inaccessible': set()
        }
        
        # TODO: Add actual import checking
        # For now, just categorize based on URL format
        for imp in imports:
            if str(imp).startswith(('http://', 'https://')):
                inaccessible = cast(Set[URIRef], import_info['inaccessible'])
                inaccessible.add(imp)
            else:
                accessible = cast(Set[URIRef], import_info['accessible'])
                accessible.add(imp)
                
        return import_info
        
    def analyze_shacl(self) -> Dict[str, Union[int, Set[URIRef], Dict[str, Set[URIRef]]]]:
        """Analyze SHACL constraints in the ontology."""
        shapes = set(self.graph.subjects(RDF.type, SH.NodeShape))
        
        shacl_info: Dict[str, Union[int, Set[URIRef], Dict[str, Set[URIRef]]]] = {
            'total_shapes': len(shapes),
            'property_shapes': set(),
            'target_classes': set(),
            'constraints': {
                'min_count': set(),
                'max_count': set(),
                'pattern': set(),
                'datatype': set(),
                'class': set(),
                'node': set(),
                'and': set(),
                'or': set(),
                'not': set()
            }
        }
        
        for shape in shapes:
            # Get target classes
            for target in self.graph.objects(shape, SH.targetClass):
                target_classes = cast(Set[URIRef], shacl_info['target_classes'])
                target_classes.add(target)
                
            # Get property shapes
            for prop_shape in self.graph.objects(shape, SH.property):
                property_shapes = cast(Set[URIRef], shacl_info['property_shapes'])
                property_shapes.add(prop_shape)
                
            # Get constraints
            constraints = cast(Dict[str, Set[URIRef]], shacl_info['constraints'])
            
            # Check each property shape for constraints
            for prop_shape in self.graph.objects(shape, SH.property):
                if (prop_shape, SH.minCount, None) in self.graph:
                    constraints['min_count'].add(prop_shape)
                if (prop_shape, SH.maxCount, None) in self.graph:
                    constraints['max_count'].add(prop_shape)
                if (prop_shape, SH.pattern, None) in self.graph:
                    constraints['pattern'].add(prop_shape)
                if (prop_shape, SH.datatype, None) in self.graph:
                    constraints['datatype'].add(prop_shape)
                if (prop_shape, SH.class_, None) in self.graph:
                    constraints['class'].add(prop_shape)
                if (prop_shape, SH.node, None) in self.graph:
                    constraints['node'].add(prop_shape)
                if (prop_shape, SH.and_, None) in self.graph:
                    constraints['and'].add(prop_shape)
                if (prop_shape, SH.or_, None) in self.graph:
                    constraints['or'].add(prop_shape)
                if (prop_shape, SH.not_, None) in self.graph:
                    constraints['not'].add(prop_shape)
                    
        return shacl_info
        
    def analyze(self) -> Dict[str, Dict[str, Any]]:
        """Run comprehensive analysis of the ontology."""
        return {
            'classes': self.analyze_classes(),
            'properties': self.analyze_properties(),
            'individuals': self.analyze_individuals(),
            'imports': self.analyze_imports(),
            'shacl': self.analyze_shacl()
        }
        
    def to_json(self, analysis: Optional[Dict[str, Dict[str, Any]]] = None) -> str:
        """Convert analysis results to JSON string."""
        if analysis is None:
            analysis = self.analyze()
            
        # Convert RDFLib types to strings for JSON serialization
        def convert_rdf_types(obj: Any) -> Any:
            if isinstance(obj, (URIRef, Literal, BNode)):
                return str(obj)
            elif isinstance(obj, (set, frozenset)):
                return sorted(convert_rdf_types(x) for x in obj)
            elif isinstance(obj, dict):
                return {str(k): convert_rdf_types(v) for k, v in obj.items()}
            elif isinstance(obj, tuple):
                return tuple(convert_rdf_types(x) for x in obj)
            return obj
            
        import json
        return json.dumps(convert_rdf_types(analysis), indent=2)
        
    def print_analysis(self, analysis: Optional[Dict[str, Dict[str, Any]]] = None, format: str = "json") -> None:
        """Print the analysis results in the specified format."""
        if analysis is None:
            analysis = self.analyze()
            
        if format.lower() == "json":
            print(self.to_json(analysis))
        elif format.lower() == "turtle":
            # Convert analysis to Turtle format
            g = Graph()
            ns = Namespace("http://example.org/analysis#")
            
            # Add analysis results as triples
            for section, data in analysis.items():
                section_node = ns[section]
                g.add((section_node, RDF.type, ns.AnalysisSection))
                
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (int, str, bool)):
                            g.add((section_node, ns[key], Literal(value)))
                        elif isinstance(value, (set, list)):
                            for item in value:
                                if isinstance(item, (URIRef, Literal, BNode)):
                                    g.add((section_node, ns[key], item))
                                else:
                                    g.add((section_node, ns[key], Literal(str(item))))
                                    
            print(g.serialize(format="turtle").decode())
        else:
            # Legacy pretty-print format
            print("\n=== Ontology Analysis ===")
            
            # Classes
            classes = cast(Dict[str, Any], analysis['classes'])
            print("\nClasses:")
            print(f"  Total: {classes['total']}")
            print(f"  With Documentation: {classes['with_documentation']}")
            print(f"  With Comments: {classes['with_comments']}")
            print(f"  Subclass Relationships: {len(cast(Dict[URIRef, Set[URIRef]], classes['subclasses']))}")
            print(f"  Disjoint Classes: {len(cast(Set[Tuple[URIRef, URIRef]], classes['disjoint_classes']))}")
            print(f"  Equivalent Classes: {len(cast(Set[Tuple[URIRef, URIRef]], classes['equivalent_classes']))}")
            
            # Properties
            properties = cast(Dict[str, Any], analysis['properties'])
            print("\nProperties:")
            print(f"  Total: {properties['total']}")
            print(f"  Object Properties: {properties['object_properties']}")
            print(f"  Datatype Properties: {properties['datatype_properties']}")
            print(f"  With Documentation: {properties['with_documentation']}")
            print(f"  With Comments: {properties['with_comments']}")
            print(f"  With Domain: {properties['with_domain']}")
            print(f"  With Range: {properties['with_range']}")
            print(f"  Functional: {len(cast(Set[URIRef], properties['functional']))}")
            print(f"  Inverse Functional: {len(cast(Set[URIRef], properties['inverse_functional']))}")
            print(f"  Transitive: {len(cast(Set[URIRef], properties['transitive']))}")
            print(f"  Symmetric: {len(cast(Set[URIRef], properties['symmetric']))}")
            print(f"  Asymmetric: {len(cast(Set[URIRef], properties['asymmetric']))}")
            print(f"  Reflexive: {len(cast(Set[URIRef], properties['reflexive']))}")
            print(f"  Irreflexive: {len(cast(Set[URIRef], properties['irreflexive']))}")
            
            # Individuals
            individuals = cast(Dict[str, Any], analysis['individuals'])
            print("\nIndividuals:")
            print(f"  Total: {individuals['total']}")
            print(f"  With Documentation: {individuals['with_documentation']}")
            print(f"  With Comments: {individuals['with_comments']}")
            print(f"  With Types: {sum(len(types) for types in cast(Dict[URIRef, Set[URIRef]], individuals['with_types']).values())}")
            
            # Imports
            imports = cast(Dict[str, Any], analysis['imports'])
            print("\nImports:")
            print(f"  Total: {imports['total']}")
            print(f"  Accessible: {len(cast(Set[URIRef], imports['accessible']))}")
            print(f"  Inaccessible: {len(cast(Set[URIRef], imports['inaccessible']))}")
            
            # SHACL
            shacl = cast(Dict[str, Any], analysis['shacl'])
            print("\nSHACL Constraints:")
            print(f"  Total Shapes: {shacl['total_shapes']}")
            print(f"  Property Shapes: {len(cast(Set[URIRef], shacl['property_shapes']))}")
            print(f"  Target Classes: {len(cast(Set[URIRef], shacl['target_classes']))}")
            print("  Constraint Types:")
            for constraint_type, constraints in cast(Dict[str, Set[URIRef]], shacl['constraints']).items():
                print(f"    {constraint_type}: {len(constraints)}")
                
def main() -> None:
    """Command-line interface for the ontology analyzer."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze an ontology file")
    parser.add_argument("ttl_file", help="Path to the TTL file to analyze")
    parser.add_argument("--format", choices=["json", "turtle", "pretty"], default="json",
                      help="Output format (default: json)")
    args = parser.parse_args()
    
    analyzer = OntologyAnalyzer(args.ttl_file)
    analysis = analyzer.analyze()
    analyzer.print_analysis(analysis, format=args.format)
    
if __name__ == "__main__":
    main() 