"""Change impact analysis for ontology modifications"""

from typing import Dict, List, Set, Any, Optional
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from ..sparql_client import SPARQLClient
import json
from datetime import datetime


class ChangeImpactAnalyzer:
    """Analyze the impact of ontology changes on dependent systems"""
    
    def __init__(self, sparql_client: Optional[SPARQLClient] = None):
        self.sparql_client = sparql_client
        self.dependency_graph = self._build_dependency_graph()
    
    def analyze_change_impact(self, old_graph: Graph, new_graph: Graph) -> Dict[str, Any]:
        """Comprehensive impact analysis of ontology changes"""
        changes = self._detect_changes(old_graph, new_graph)
        
        impact_analysis = {
            "timestamp": datetime.now().isoformat(),
            "changes_summary": changes,
            "impact_assessment": {},
            "affected_systems": [],
            "risk_level": "low",
            "recommendations": [],
            "migration_steps": []
        }
        
        # Analyze each type of change
        for change_type, items in changes.items():
            if items:
                impact = self._assess_change_impact(change_type, items, old_graph, new_graph)
                impact_analysis["impact_assessment"][change_type] = impact
        
        # Determine overall risk level
        impact_analysis["risk_level"] = self._calculate_risk_level(impact_analysis["impact_assessment"])
        
        # Find affected systems
        impact_analysis["affected_systems"] = self._find_affected_systems(changes)
        
        # Generate recommendations
        impact_analysis["recommendations"] = self._generate_recommendations(impact_analysis)
        
        # Create migration steps
        impact_analysis["migration_steps"] = self._create_migration_steps(changes)
        
        return impact_analysis
    
    def predict_query_impact(self, changes: Dict[str, List], sample_queries: List[str]) -> Dict[str, Any]:
        """Predict how changes will affect existing SPARQL queries"""
        query_impact = {
            "total_queries": len(sample_queries),
            "affected_queries": 0,
            "broken_queries": [],
            "modified_queries": [],
            "impact_details": []
        }
        
        for i, query in enumerate(sample_queries):
            impact = self._analyze_query_impact(query, changes)
            if impact["affected"]:
                query_impact["affected_queries"] += 1
                query_impact["impact_details"].append({
                    "query_index": i,
                    "query": query,
                    "impact": impact
                })
                
                if impact["severity"] == "broken":
                    query_impact["broken_queries"].append(i)
                else:
                    query_impact["modified_queries"].append(i)
        
        return query_impact
    
    def analyze_data_migration_needs(self, changes: Dict[str, List]) -> Dict[str, Any]:
        """Analyze what data migration is needed for changes"""
        migration_needs = {
            "requires_migration": False,
            "migration_tasks": [],
            "estimated_effort": "low",
            "data_at_risk": [],
            "backup_recommended": False
        }
        
        # Check for breaking changes that require migration
        if changes.get("removed_classes") or changes.get("removed_properties"):
            migration_needs["requires_migration"] = True
            migration_needs["backup_recommended"] = True
            migration_needs["estimated_effort"] = "high"
        
        # Analyze specific migration tasks
        for removed_class in changes.get("removed_classes", []):
            migration_needs["migration_tasks"].append({
                "type": "class_removal",
                "action": f"Migrate instances of {removed_class}",
                "priority": "high",
                "estimated_time": "2-4 hours"
            })
        
        for removed_prop in changes.get("removed_properties", []):
            migration_needs["migration_tasks"].append({
                "type": "property_removal", 
                "action": f"Migrate data using property {removed_prop}",
                "priority": "high",
                "estimated_time": "1-2 hours"
            })
        
        # Check for renamed items
        renamed_items = self._detect_renames(changes)
        for old_name, new_name in renamed_items:
            migration_needs["migration_tasks"].append({
                "type": "rename",
                "action": f"Update references from {old_name} to {new_name}",
                "priority": "medium",
                "estimated_time": "30 minutes"
            })
        
        return migration_needs
    
    def generate_rollback_plan(self, changes: Dict[str, List]) -> Dict[str, Any]:
        """Generate a rollback plan for ontology changes"""
        rollback_plan = {
            "rollback_steps": [],
            "estimated_time": "30 minutes",
            "complexity": "low",
            "prerequisites": [],
            "validation_steps": []
        }
        
        # Create rollback steps in reverse order
        if changes.get("added_classes"):
            rollback_plan["rollback_steps"].append({
                "step": 1,
                "action": "Remove added classes",
                "classes": changes["added_classes"],
                "command": "Remove class definitions from ontology"
            })
        
        if changes.get("removed_classes"):
            rollback_plan["rollback_steps"].append({
                "step": 2,
                "action": "Restore removed classes",
                "classes": changes["removed_classes"],
                "command": "Add back class definitions"
            })
        
        if changes.get("modified_classes"):
            rollback_plan["rollback_steps"].append({
                "step": 3,
                "action": "Revert class modifications",
                "classes": changes["modified_classes"],
                "command": "Restore original class definitions"
            })
        
        # Add validation steps
        rollback_plan["validation_steps"] = [
            "Run ontology validation tests",
            "Verify SPARQL queries still work",
            "Check dependent system functionality",
            "Validate data integrity"
        ]
        
        return rollback_plan
    
    def _detect_changes(self, old_graph: Graph, new_graph: Graph) -> Dict[str, List]:
        """Detect all changes between two ontology versions"""
        changes = {
            "added_classes": [],
            "removed_classes": [],
            "modified_classes": [],
            "added_properties": [],
            "removed_properties": [],
            "modified_properties": [],
            "added_individuals": [],
            "removed_individuals": []
        }
        
        # Compare classes
        old_classes = set(old_graph.subjects(RDF.type, OWL.Class))
        new_classes = set(new_graph.subjects(RDF.type, OWL.Class))
        
        changes["added_classes"] = [str(c) for c in new_classes - old_classes]
        changes["removed_classes"] = [str(c) for c in old_classes - new_classes]
        
        # Check for modified classes (same URI, different properties)
        common_classes = old_classes & new_classes
        for cls in common_classes:
            if self._class_modified(old_graph, new_graph, cls):
                changes["modified_classes"].append(str(cls))
        
        # Compare properties
        old_props = (set(old_graph.subjects(RDF.type, OWL.ObjectProperty)) |
                    set(old_graph.subjects(RDF.type, OWL.DatatypeProperty)))
        new_props = (set(new_graph.subjects(RDF.type, OWL.ObjectProperty)) |
                    set(new_graph.subjects(RDF.type, OWL.DatatypeProperty)))
        
        changes["added_properties"] = [str(p) for p in new_props - old_props]
        changes["removed_properties"] = [str(p) for p in old_props - new_props]
        
        # Check for modified properties
        common_props = old_props & new_props
        for prop in common_props:
            if self._property_modified(old_graph, new_graph, prop):
                changes["modified_properties"].append(str(prop))
        
        return changes
    
    def _assess_change_impact(self, change_type: str, items: List[str], 
                            old_graph: Graph, new_graph: Graph) -> Dict[str, Any]:
        """Assess the impact of a specific type of change"""
        impact = {
            "severity": "low",
            "breaking_change": False,
            "affected_components": [],
            "mitigation_required": False
        }
        
        if change_type in ["removed_classes", "removed_properties"]:
            impact["severity"] = "high"
            impact["breaking_change"] = True
            impact["mitigation_required"] = True
            impact["affected_components"] = self._find_dependent_components(items)
        
        elif change_type in ["modified_classes", "modified_properties"]:
            impact["severity"] = "medium"
            impact["breaking_change"] = self._is_breaking_modification(items, old_graph, new_graph)
            impact["affected_components"] = self._find_dependent_components(items)
        
        elif change_type in ["added_classes", "added_properties"]:
            impact["severity"] = "low"
            impact["breaking_change"] = False
        
        return impact
    
    def _calculate_risk_level(self, impact_assessment: Dict[str, Any]) -> str:
        """Calculate overall risk level from impact assessment"""
        high_risk_count = 0
        medium_risk_count = 0
        
        for change_type, impact in impact_assessment.items():
            if impact["severity"] == "high":
                high_risk_count += 1
            elif impact["severity"] == "medium":
                medium_risk_count += 1
        
        if high_risk_count > 0:
            return "high"
        elif medium_risk_count > 2:
            return "medium"
        else:
            return "low"
    
    def _find_affected_systems(self, changes: Dict[str, List]) -> List[Dict[str, Any]]:
        """Find systems that might be affected by changes"""
        affected_systems = []
        
        # This would typically query a registry of dependent systems
        # For now, return example systems
        if any(changes.values()):
            affected_systems.extend([
                {
                    "system": "Data Pipeline",
                    "impact": "Query modifications may be needed",
                    "contact": "data-team@example.com"
                },
                {
                    "system": "Web Application",
                    "impact": "UI updates may be required",
                    "contact": "web-team@example.com"
                }
            ])
        
        return affected_systems
    
    def _generate_recommendations(self, impact_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on impact analysis"""
        recommendations = []
        
        if impact_analysis["risk_level"] == "high":
            recommendations.extend([
                "Create backup before applying changes",
                "Plan maintenance window for deployment",
                "Notify all affected system owners",
                "Prepare rollback plan"
            ])
        
        if impact_analysis["affected_systems"]:
            recommendations.append("Coordinate with dependent system teams")
        
        if any(impact["breaking_change"] for impact in impact_analysis["impact_assessment"].values()):
            recommendations.extend([
                "Version the ontology appropriately",
                "Provide migration documentation",
                "Consider deprecation period for removed elements"
            ])
        
        return recommendations
    
    def _create_migration_steps(self, changes: Dict[str, List]) -> List[Dict[str, Any]]:
        """Create step-by-step migration plan"""
        steps = []
        step_num = 1
        
        if changes.get("removed_classes"):
            steps.append({
                "step": step_num,
                "action": "Backup existing data",
                "description": "Create backup of all data before removing classes",
                "estimated_time": "15 minutes"
            })
            step_num += 1
        
        if changes.get("added_classes"):
            steps.append({
                "step": step_num,
                "action": "Deploy new classes",
                "description": "Add new class definitions to ontology",
                "estimated_time": "5 minutes"
            })
            step_num += 1
        
        if changes.get("modified_classes"):
            steps.append({
                "step": step_num,
                "action": "Update class definitions",
                "description": "Apply modifications to existing classes",
                "estimated_time": "10 minutes"
            })
            step_num += 1
        
        steps.append({
            "step": step_num,
            "action": "Validate changes",
            "description": "Run validation tests and verify functionality",
            "estimated_time": "20 minutes"
        })
        
        return steps
    
    def _analyze_query_impact(self, query: str, changes: Dict[str, List]) -> Dict[str, Any]:
        """Analyze how changes affect a specific SPARQL query"""
        impact = {
            "affected": False,
            "severity": "none",
            "issues": [],
            "suggested_fixes": []
        }
        
        # Check if query references removed classes
        for removed_class in changes.get("removed_classes", []):
            if removed_class in query:
                impact["affected"] = True
                impact["severity"] = "broken"
                impact["issues"].append(f"References removed class: {removed_class}")
                impact["suggested_fixes"].append(f"Replace or remove references to {removed_class}")
        
        # Check if query references removed properties
        for removed_prop in changes.get("removed_properties", []):
            if removed_prop in query:
                impact["affected"] = True
                impact["severity"] = "broken"
                impact["issues"].append(f"References removed property: {removed_prop}")
                impact["suggested_fixes"].append(f"Replace or remove references to {removed_prop}")
        
        return impact
    
    def _class_modified(self, old_graph: Graph, new_graph: Graph, cls: URIRef) -> bool:
        """Check if a class has been modified between versions"""
        old_triples = set(old_graph.triples((cls, None, None)))
        new_triples = set(new_graph.triples((cls, None, None)))
        return old_triples != new_triples
    
    def _property_modified(self, old_graph: Graph, new_graph: Graph, prop: URIRef) -> bool:
        """Check if a property has been modified between versions"""
        old_triples = set(old_graph.triples((prop, None, None)))
        new_triples = set(new_graph.triples((prop, None, None)))
        return old_triples != new_triples
    
    def _find_dependent_components(self, items: List[str]) -> List[str]:
        """Find components that depend on the given ontology items"""
        # This would typically query a dependency registry
        # For now, return example dependencies
        return ["SPARQL Queries", "Data Validation Rules", "UI Components"]
    
    def _is_breaking_modification(self, items: List[str], old_graph: Graph, new_graph: Graph) -> bool:
        """Check if modifications are breaking changes"""
        # Simple heuristic - could be more sophisticated
        return len(items) > 0
    
    def _detect_renames(self, changes: Dict[str, List]) -> List[tuple]:
        """Detect potential renames (removed + added with similar names)"""
        renames = []
        removed = changes.get("removed_classes", []) + changes.get("removed_properties", [])
        added = changes.get("added_classes", []) + changes.get("added_properties", [])
        
        for removed_item in removed:
            for added_item in added:
                # Simple similarity check
                if self._are_similar_names(removed_item, added_item):
                    renames.append((removed_item, added_item))
        
        return renames
    
    def _are_similar_names(self, name1: str, name2: str) -> bool:
        """Check if two names are similar (potential rename)"""
        # Extract local names
        local1 = name1.split('#')[-1].split('/')[-1].lower()
        local2 = name2.split('#')[-1].split('/')[-1].lower()
        
        # Simple similarity check
        return abs(len(local1) - len(local2)) <= 2 and (local1 in local2 or local2 in local1)
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build a graph of ontology dependencies"""
        # This would typically be loaded from a configuration file or registry
        return {
            "systems": ["data_pipeline", "web_app", "mobile_app"],
            "queries": ["user_queries", "system_queries", "report_queries"],
            "components": ["validators", "transformers", "exporters"]
        }