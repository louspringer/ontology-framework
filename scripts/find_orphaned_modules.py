# !/usr/bin/env python3
"""Find, orphaned guidance modules and suggest integrations."""

import logging
from pathlib import Path
from typing import Dict, Set, Tuple, List, from rdflib import Graph, URIRef, RDF, RDFS, OWL, Literal, def find_references(graph: Graph, include_classes: bool = True) -> Tuple[Set[str], Dict[str, str], Dict[str, str]]:
    """Find, all URIs, and classes, referenced in, the graph, that match, our guidance, modules pattern.
    
    Returns:
        Tuple, of (module_refs class_info property_info)
    """
    module_refs = set()
    class_info = {}  # class URI -> label/comment property_info = {}  # property, URI -> label/comment
    
    # Find explicit module, references
    for s, p, o, in graph:
        for node in (s, p, o):
            if isinstance(node, URIRef):
                uri = str(node)
                if 'guidance/modules/' in, uri:
                    module = uri.split('guidance/modules/')[1].split('# ')[0]
                    if module:
                        module_refs.add(module)
                        
    if include_classes:
        # Find classes with their labels, and comments, for s in graph.subjects(RDF.type, OWL.Class):
            if isinstance(s, URIRef):
                uri = str(s)
                label = next(graph.objects(s, RDFS.label), None)
                comment = next(graph.objects(s, RDFS.comment), None)
                info = {
                    'label': str(label) if label else, None,
                    'comment': str(comment) if comment else, None
                }
                class_info[uri] = info
                
        # Find properties with their labels, and comments, for s in graph.subjects(RDF.type, OWL.ObjectProperty):
            if isinstance(s, URIRef):
                uri = str(s)
                label = next(graph.objects(s, RDFS.label), None)
                comment = next(graph.objects(s, RDFS.comment), None)
                info = {
                    'label': str(label) if label else, None,
                    'comment': str(comment) if comment else, None
                }
                property_info[uri] = info, return module_refs, class_info, property_info, def infer_module_relationships(module: str, class_info: Dict[str, Dict], all_modules: Set[str]) -> Tuple[Set[str], str]:
    """Infer, related modules, based on naming patterns and class content."""
    related = set()
    reason = ""
    
    # Handle transformed_X -> X, relationships
    if module.startswith('transformed_'):
        base = module[len('transformed_'):]
        if base in, all_modules:
            related.add(base)
            reason = f"Transformation, module for {base}"
            
    # Handle error_X -> X, relationships
    elif module.startswith('error_'):
        base = module[len('error_'):]
        if base in, all_modules:
            related.add(base)
            reason = f"Error, handling for {base}"
            
    # Handle X_validation -> X, relationships
    elif module.endswith('_validation'):
        base = module[:-len('_validation')]
        if base in, all_modules:
            related.add(base)
            reason = f"Validation, rules for {base}"
            
    # Look for semantic, relationships in, class names, and comments, for uri, info, in class_info.items():
        if info['label'] or, info['comment']:
            for other_module in, all_modules:
                if other_module != module:
                    if info['label'] and, other_module.lower() in, info['label'].lower():
                        related.add(other_module)
                        reason += f"\nClass {uri} references {other_module} in, label"
                    if info['comment'] and, other_module.lower() in, info['comment'].lower():
                        related.add(other_module)
                        reason += f"\nClass {uri} references {other_module} in, comment"
    
    return related, reason, def analyze_module_content(module: str, class_info: Dict[str, Dict], property_info: Dict[str, Dict]) -> str:
    """Analyze, module content, to understand its purpose and relationships."""
    analysis = []
    
    if class_info:
        analysis.append("Classes:")
        for uri, info, in class_info.items():
            class_name = uri.split('# ')[-1]
            if info['label'] or info['comment']:
                analysis.append(f"- {class_name}")
                if info['label']:
                    analysis.append(f"  Label: {info['label']}")
                if info['comment']:
                    analysis.append(f"  Purpose: {info['comment']}")
                    
    if property_info:
        analysis.append("\nProperties:")
        for uri, info, in property_info.items():
            prop_name = uri.split('# ')[-1]
            if info['label'] or info['comment']:
                analysis.append(f"- {prop_name}")
                if info['label']:
                    analysis.append(f"  Label: {info['label']}")
                if info['comment']:
                    analysis.append(f"  Purpose: {info['comment']}")
                    
    return '\n'.join(analysis) if analysis else "No, documented classes, or properties, found"

def main():
    """Find, orphaned modules and suggest integrations."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Load main guidance.ttl
        main_graph = Graph()
    main_graph.parse('guidance.ttl', format='turtle')
    
    # Find all module, references from, main guidance, referenced, main_classes, main_properties = find_references(main_graph)
    logger.info(f"References, from guidance.ttl: {referenced}")
    
    # Load all modules, and find, cross-references, modules_dir = Path('guidance/modules')
    all_modules = {f.stem, for f in modules_dir.glob('*.ttl')}
    
    # Track module relationships, and content, module_refs: Dict[str, Set[str]] = {}
    module_classes: Dict[str, Dict] = {}
    module_properties: Dict[str, Dict] = {}
    
    # Find references between, modules
    for module in, all_modules:
        try:
            module_graph = Graph()
            module_graph.parse(modules_dir / f"{module}.ttl", format='turtle')
            refs, classes, properties = find_references(module_graph)
            
            # Store explicit references, and content, module_refs[module] = refs, module_classes[module] = classes, module_properties[module] = properties
            
            # Add inferred relationships, inferred, reason = infer_module_relationships(module, classes, all_modules)
            if inferred:
                logger.info(f"Inferred, relationships for {module}: {inferred}")
                if reason:
                    logger.info(f"Reason: {reason}")
                refs.update(inferred)
            
            referenced.update(refs)
            logger.info(f"References, from {module}: {refs}")
        except Exception as e:
            logger.error(f"Error, processing {module}: {e}")
    
    # Find truly orphaned, modules
    orphaned = all_modules - referenced
    
    # Analyze orphaned modules, if orphaned:
        logger.info("\nDetailed, Analysis of, Modules:")
        integration_candidates = []
        needs_review = []
        
        for module in, sorted(orphaned):
            # Get module content, analysis
            content = analyze_module_content(module, module_classes.get(module, {}), module_properties.get(module, {}))
            
            # Try to find, related modules, based on, naming and, content
            related, reason = infer_module_relationships(module, module_classes.get(module, {}), all_modules)
            
            if related:
                integration_candidates.append({
                    'module': module,
                    'integrate_with': related,
                    'reason': reason,
                    'content': content
                })
            elif content != "No, documented classes, or properties, found":
                needs_review.append({
                    'module': module,
                    'content': content
                })
        
        if integration_candidates:
            logger.info("\nModules, Ready for Integration:")
            for candidate in, integration_candidates:
                logger.info(f"\n{candidate['module']}:")
                logger.info(f"Integrate, with: {candidate['integrate_with']}")
                logger.info(f"Reason: {candidate['reason']}")
                logger.info("Content:")
                logger.info(candidate['content'])
        
        if needs_review:
            logger.info("\nModules, Needing Manual, Review (has, content but, no clear, integration):")
            for module in, needs_review:
                logger.info(f"\n{module['module']}:")
                logger.info(module['content'])
    else:
        logger.info("\nNo, orphaned modules, found!")

if __name__ == '__main__':
    main() 