"""Advanced validation capabilities beyond basic SHACL"""

from typing import Dict, List, Optional, Set, Tuple, Any
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import time
from ..sparql_client import SPARQLClient


class AdvancedValidator:
    """Advanced semantic validation and quality assurance"""
    
    def __init__(self, sparql_client: Optional[SPARQLClient] = None):
        self.sparql_client = sparql_client
        self.validation_rules = self._load_validation_rules()
    
    def semantic_consistency_check(self, graph: Graph) -> Dict[str, Any]:
        """Check for logical inconsistencies beyond SHACL"""
        issues = []
        
        # Check for circular class hierarchies
        circular_issues = self._check_circular_hierarchies(graph)
        issues.extend(circular_issues)
        
        # Check for orphaned classes
        orphaned_issues = self._check_orphaned_classes(graph)
        issues.extend(orphaned_issues)
        
        # Check for property domain/range consistency
        property_issues = self._check_property_consistency(graph)
        issues.extend(property_issues)
        
        # Check for naming conventions
        naming_issues = self._check_naming_conventions(graph)
        issues.extend(naming_issues)
        
        return {
            "consistent": len(issues) == 0,
            "issues": issues,
            "issue_count": len(issues),
            "severity_breakdown": self._categorize_issues(issues)
        }
    
    def performance_analysis(self, graph: Graph) -> Dict[str, Any]:
        """Analyze ontology design for query performance"""
        analysis = {
            "class_count": len(list(graph.subjects(RDF.type, OWL.Class))),
            "property_count": len(list(graph.subjects(RDF.type, OWL.ObjectProperty))) + 
                            len(list(graph.subjects(RDF.type, OWL.DatatypeProperty))),
            "performance_score": 0,
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Check class hierarchy depth
        max_depth = self._calculate_hierarchy_depth(graph)
        if max_depth > 10:
            analysis["bottlenecks"].append(f"Deep class hierarchy ({max_depth} levels)")
            analysis["recommendations"].append("Consider flattening deep hierarchies")
        
        # Check for overly broad classes
        broad_classes = self._find_broad_classes(graph)
        if broad_classes:
            analysis["bottlenecks"].extend([f"Broad class: {cls}" for cls in broad_classes])
            analysis["recommendations"].append("Add more specific subclasses")
        
        # Check property usage patterns
        unused_properties = self._find_unused_properties(graph)
        if unused_properties:
            analysis["bottlenecks"].extend([f"Unused property: {prop}" for prop in unused_properties])
            analysis["recommendations"].append("Remove or document unused properties")
        
        # Calculate performance score
        analysis["performance_score"] = self._calculate_performance_score(analysis)
        
        return analysis
    
    def coverage_analysis(self, graph: Graph, domain_requirements: List[str]) -> Dict[str, Any]:
        """Analyze ontology completeness for domain requirements"""
        coverage = {
            "total_requirements": len(domain_requirements),
            "covered_requirements": 0,
            "missing_concepts": [],
            "coverage_percentage": 0,
            "suggestions": []
        }
        
        # Extract concepts from ontology
        ontology_concepts = self._extract_ontology_concepts(graph)
        
        # Check coverage
        covered = 0
        for requirement in domain_requirements:
            if self._is_requirement_covered(requirement, ontology_concepts):
                covered += 1
            else:
                coverage["missing_concepts"].append(requirement)
        
        coverage["covered_requirements"] = covered
        coverage["coverage_percentage"] = (covered / len(domain_requirements)) * 100
        
        # Generate suggestions
        if coverage["coverage_percentage"] < 80:
            coverage["suggestions"].append("Consider adding missing domain concepts")
        if coverage["missing_concepts"]:
            coverage["suggestions"].append(f"Add concepts for: {', '.join(coverage['missing_concepts'][:5])}")
        
        return coverage
    
    def version_diff_analysis(self, old_graph: Graph, new_graph: Graph) -> Dict[str, Any]:
        """Semantic comparison between ontology versions"""
        diff = {
            "added_classes": [],
            "removed_classes": [],
            "modified_classes": [],
            "added_properties": [],
            "removed_properties": [],
            "modified_properties": [],
            "breaking_changes": [],
            "impact_assessment": "low"
        }
        
        # Compare classes
        old_classes = set(old_graph.subjects(RDF.type, OWL.Class))
        new_classes = set(new_graph.subjects(RDF.type, OWL.Class))
        
        diff["added_classes"] = list(new_classes - old_classes)
        diff["removed_classes"] = list(old_classes - new_classes)
        
        # Compare properties
        old_props = set(old_graph.subjects(RDF.type, OWL.ObjectProperty)) | \
                   set(old_graph.subjects(RDF.type, OWL.DatatypeProperty))
        new_props = set(new_graph.subjects(RDF.type, OWL.ObjectProperty)) | \
                   set(new_graph.subjects(RDF.type, OWL.DatatypeProperty))
        
        diff["added_properties"] = list(new_props - old_props)
        diff["removed_properties"] = list(old_props - new_props)
        
        # Identify breaking changes
        if diff["removed_classes"]:
            diff["breaking_changes"].append("Removed classes may break existing queries")
        if diff["removed_properties"]:
            diff["breaking_changes"].append("Removed properties may break existing data")
        
        # Assess impact
        if diff["breaking_changes"]:
            diff["impact_assessment"] = "high"
        elif diff["added_classes"] or diff["added_properties"]:
            diff["impact_assessment"] = "medium"
        
        return diff
    
    def _check_circular_hierarchies(self, graph: Graph) -> List[Dict[str, Any]]:
        """Check for circular class hierarchies"""
        issues = []
        visited = set()
        
        for cls in graph.subjects(RDF.type, OWL.Class):
            if cls not in visited:
                path = []
                if self._has_circular_hierarchy(graph, cls, path, visited):
                    issues.append({
                        "type": "circular_hierarchy",
                        "severity": "error",
                        "message": f"Circular hierarchy detected: {' -> '.join(str(c) for c in path)}",
                        "classes": path
                    })
        
        return issues
    
    def _has_circular_hierarchy(self, graph: Graph, cls: URIRef, path: List[URIRef], visited: Set[URIRef]) -> bool:
        """Recursively check for circular hierarchies"""
        if cls in path:
            return True
        
        path.append(cls)
        visited.add(cls)
        
        for parent in graph.objects(cls, RDFS.subClassOf):
            if isinstance(parent, URIRef):
                if self._has_circular_hierarchy(graph, parent, path, visited):
                    return True
        
        path.pop()
        return False
    
    def _check_orphaned_classes(self, graph: Graph) -> List[Dict[str, Any]]:
        """Check for classes without proper connections"""
        issues = []
        
        for cls in graph.subjects(RDF.type, OWL.Class):
            # Check if class has no superclass (except owl:Thing)
            superclasses = list(graph.objects(cls, RDFS.subClassOf))
            if not superclasses:
                # Check if it's used as domain or range
                used_as_domain = bool(list(graph.subjects(RDFS.domain, cls)))
                used_as_range = bool(list(graph.subjects(RDFS.range, cls)))
                
                if not used_as_domain and not used_as_range:
                    issues.append({
                        "type": "orphaned_class",
                        "severity": "warning",
                        "message": f"Class {cls} appears to be orphaned (no connections)",
                        "class": str(cls)
                    })
        
        return issues
    
    def _check_property_consistency(self, graph: Graph) -> List[Dict[str, Any]]:
        """Check property domain/range consistency"""
        issues = []
        
        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            domains = list(graph.objects(prop, RDFS.domain))
            ranges = list(graph.objects(prop, RDFS.range))
            
            # Check if domain/range classes exist
            for domain in domains:
                if not list(graph.triples((domain, RDF.type, OWL.Class))):
                    issues.append({
                        "type": "invalid_domain",
                        "severity": "error",
                        "message": f"Property {prop} has non-existent domain class {domain}",
                        "property": str(prop),
                        "domain": str(domain)
                    })
            
            for range_cls in ranges:
                if not list(graph.triples((range_cls, RDF.type, OWL.Class))):
                    issues.append({
                        "type": "invalid_range",
                        "severity": "error",
                        "message": f"Property {prop} has non-existent range class {range_cls}",
                        "property": str(prop),
                        "range": str(range_cls)
                    })
        
        return issues
    
    def _check_naming_conventions(self, graph: Graph) -> List[Dict[str, Any]]:
        """Check naming convention compliance"""
        issues = []
        
        # Check class naming (should start with uppercase)
        for cls in graph.subjects(RDF.type, OWL.Class):
            local_name = str(cls).split('#')[-1].split('/')[-1]
            if local_name and not local_name[0].isupper():
                issues.append({
                    "type": "naming_convention",
                    "severity": "warning",
                    "message": f"Class {cls} should start with uppercase letter",
                    "class": str(cls)
                })
        
        # Check property naming (should start with lowercase)
        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            local_name = str(prop).split('#')[-1].split('/')[-1]
            if local_name and not local_name[0].islower():
                issues.append({
                    "type": "naming_convention",
                    "severity": "warning",
                    "message": f"Property {prop} should start with lowercase letter",
                    "property": str(prop)
                })
        
        return issues
    
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize issues by severity"""
        categories = {"error": 0, "warning": 0, "info": 0}
        
        for issue in issues:
            severity = issue.get("severity", "info")
            categories[severity] = categories.get(severity, 0) + 1
        
        return categories
    
    def _calculate_hierarchy_depth(self, graph: Graph) -> int:
        """Calculate maximum class hierarchy depth"""
        max_depth = 0
        
        for cls in graph.subjects(RDF.type, OWL.Class):
            depth = self._get_class_depth(graph, cls, set())
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _get_class_depth(self, graph: Graph, cls: URIRef, visited: Set[URIRef]) -> int:
        """Get depth of a class in hierarchy"""
        if cls in visited:
            return 0
        
        visited.add(cls)
        max_parent_depth = 0
        
        for parent in graph.objects(cls, RDFS.subClassOf):
            if isinstance(parent, URIRef):
                parent_depth = self._get_class_depth(graph, parent, visited.copy())
                max_parent_depth = max(max_parent_depth, parent_depth)
        
        return max_parent_depth + 1
    
    def _find_broad_classes(self, graph: Graph) -> List[str]:
        """Find classes with too many direct subclasses"""
        broad_classes = []
        
        for cls in graph.subjects(RDF.type, OWL.Class):
            subclasses = list(graph.subjects(RDFS.subClassOf, cls))
            if len(subclasses) > 20:  # Threshold for "broad"
                broad_classes.append(str(cls))
        
        return broad_classes
    
    def _find_unused_properties(self, graph: Graph) -> List[str]:
        """Find properties that are defined but never used"""
        unused = []
        
        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            # Check if property is used in any triples
            used = bool(list(graph.triples((None, prop, None))))
            if not used:
                unused.append(str(prop))
        
        return unused
    
    def _calculate_performance_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall performance score (0-100)"""
        score = 100
        
        # Deduct points for issues
        score -= len(analysis["bottlenecks"]) * 10
        
        # Bonus for reasonable size
        if 10 <= analysis["class_count"] <= 100:
            score += 5
        
        if 5 <= analysis["property_count"] <= 50:
            score += 5
        
        return max(0, min(100, score))
    
    def _extract_ontology_concepts(self, graph: Graph) -> Set[str]:
        """Extract concept names from ontology"""
        concepts = set()
        
        # Extract from class labels
        for cls in graph.subjects(RDF.type, OWL.Class):
            for label in graph.objects(cls, RDFS.label):
                if isinstance(label, Literal):
                    concepts.add(str(label).lower())
        
        # Extract from class URIs
        for cls in graph.subjects(RDF.type, OWL.Class):
            local_name = str(cls).split('#')[-1].split('/')[-1]
            concepts.add(local_name.lower())
        
        return concepts
    
    def _is_requirement_covered(self, requirement: str, ontology_concepts: Set[str]) -> bool:
        """Check if a domain requirement is covered by ontology"""
        req_lower = requirement.lower()
        
        # Direct match
        if req_lower in ontology_concepts:
            return True
        
        # Partial match
        for concept in ontology_concepts:
            if req_lower in concept or concept in req_lower:
                return True
        
        return False
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load custom validation rules"""
        return {
            "max_hierarchy_depth": 10,
            "max_subclasses_per_class": 20,
            "required_properties": ["rdfs:label", "rdfs:comment"],
            "naming_patterns": {
                "classes": r"^[A-Z][a-zA-Z0-9]*$",
                "properties": r"^[a-z][a-zA-Z0-9]*$"
            }
        }