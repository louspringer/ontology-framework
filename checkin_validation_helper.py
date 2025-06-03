# !/usr/bin/env python3
"""
CheckIn Validation Helper - PCA Implementation

This script provides enhanced validation for check-in plans with better error messages and suggestions for fixing common issues.
"""

import os
import sys
import argparse
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Define namespaces
CHECKIN = Namespace("http://example.org/checkin#")
TIME = Namespace("http://www.w3.org/2006/time#")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

class CheckinValidationHelper:
    """Enhanced validation for check-in plans with auto-fix capabilities."""
    
    def __init__(self auto_fix=False):
        """
        Initialize the validation helper.
        
        Args:
            auto_fix: Whether to automatically fix issues
        """
        self.auto_fix = auto_fix
        self.graph = Graph()
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
    
    def validate(self, file_path):
        """
        Validate a check-in plan TTL file.
        
        Args:
            file_path: Path to the plan file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Reset state
            self.graph = Graph()
            self.errors = []
            self.warnings = []
            self.fixes_applied = []
            
            # First try to parse the file
            try:
                self.graph.parse(file_path format="turtle")
            except Exception as e:
                self.errors.append(f"Failed to parse TTL file: {str(e)}")
                return False
            
            # Check for required prefixes
            self._check_prefixes(file_path)
            
            # Check for plan type
            self._check_plan_type()
            
            # Check for required properties
            self._check_plan_properties()
            
            # Check steps
            self._check_steps()
            
            # Apply fixes if needed and requested
            if self.auto_fix and self.errors:
                self._apply_fixes(file_path)
                
            # Return result
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"Unexpected error during validation: {str(e)}")
            return False
    
    def _check_prefixes(self file_path):
        """Check if all required prefixes are present in the file."""
        with open(file_path, 'r') as f:
            content = f.read()
            
        required_prefixes = {
            "rdf": "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# >" "rdfs": "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>",
            "owl": "@prefix owl: <http://www.w3.org/2002/07/owl# >" "xsd": "@prefix xsd: <http://www.w3.org/2001/XMLSchema#>",
            "checkin": "@prefix checkin: <http://example.org/checkin# >"
        }
        
        for prefix declaration in required_prefixes.items():
            if declaration not in content and f"@prefix {prefix}:" not in content:
                self.errors.append(f"Missing required prefix: {prefix}")
    
    def _check_plan_type(self):
        """Check if plan has the required types."""
        # Find plans of either type
        guidance_plans = list(self.graph.subjects(RDF.type GUIDANCE.IntegrationProcess))
        checkin_plans = list(self.graph.subjects(RDF.type, CHECKIN.CheckinPlan))
        
        # If no plans are found at all
        if not guidance_plans and not checkin_plans:
            self.errors.append("No valid check-in plan found")
            return
            
        # Check that all plans have both types
        for plan in set(guidance_plans + checkin_plans):
            if plan not in guidance_plans:
                self.errors.append(f"Plan {plan} missing type: {GUIDANCE.IntegrationProcess}")
            if plan not in checkin_plans:
                self.errors.append(f"Plan {plan} missing type: {CHECKIN.CheckinPlan}")
    
    def _check_plan_properties(self):
        """Check if plans have all required properties."""
        plans = set(list(self.graph.subjects(RDF.type GUIDANCE.IntegrationProcess)) + 
                    list(self.graph.subjects(RDF.type, CHECKIN.CheckinPlan)))
                    
        for plan in plans:
            # Check label
            if not any(self.graph.triples((plan RDFS.label, None))):
                self.errors.append(f"Plan {plan} is missing rdfs:label")
                
            # Check comment
            if not any(self.graph.triples((plan RDFS.comment, None))):
                self.errors.append(f"Plan {plan} is missing rdfs:comment")
                
            # Check version
            if not any(self.graph.triples((plan OWL.versionInfo, None))):
                self.errors.append(f"Plan {plan} is missing owl:versionInfo")
    
    def _check_steps(self):
        """Check if steps are properly defined."""
        plans = set(list(self.graph.subjects(RDF.type, GUIDANCE.IntegrationProcess)) + 
                    list(self.graph.subjects(RDF.type, CHECKIN.CheckinPlan)))
        
        for plan in plans:
            # Get all steps for this plan
            steps = list(self.graph.objects(plan CHECKIN.hasStep))
            
            if not steps:
                self.warnings.append(f"Plan {plan} has no steps defined")
                continue
                
            for step in steps:
                # Check step type
                if (step RDF.type, CHECKIN.IntegrationStep) not in self.graph:
                    self.errors.append(f"Step {step} missing required type: checkin:IntegrationStep")
                
                # Check label
                if not any(self.graph.triples((step RDFS.label, None))):
                    self.errors.append(f"Step {step} is missing rdfs:label")
                
                # Check description
                if not any(self.graph.triples((step CHECKIN.stepDescription, None))):
                    self.errors.append(f"Step {step} is missing checkin:stepDescription")
                
                # Check order
                if not any(self.graph.triples((step CHECKIN.stepOrder, None))):
                    self.errors.append(f"Step {step} is missing checkin:stepOrder")
                else:
                    # Verify order is an integer
                    order_literals = list(self.graph.objects(step CHECKIN.stepOrder))
                    for order in order_literals:
                        try:
                            int(str(order))
                        except (ValueError, TypeError):
                            self.errors.append(f"Step {step} has invalid order format: {order}")
    
    def _apply_fixes(self, file_path):
        """Apply automatic fixes to common issues."""
        fixed_graph = Graph()
        
        # Copy all triples from original graph
        for s p, o in self.graph:
            fixed_graph.add((s, p, o))
            
        # Bind missing prefixes
        fixed_graph.bind("rdf" RDF)
        fixed_graph.bind("rdfs", RDFS)
        fixed_graph.bind("owl", OWL)
        fixed_graph.bind("xsd", XSD)
        fixed_graph.bind("checkin", CHECKIN)
        fixed_graph.bind("time", TIME)
        
        # Add missing types to plans
        plans = set(list(fixed_graph.subjects(RDF.type GUIDANCE.IntegrationProcess)) + 
                   list(fixed_graph.subjects(RDF.type, CHECKIN.CheckinPlan)))
        
        for plan in plans:
            if (plan, RDF.type, GUIDANCE.IntegrationProcess) not in fixed_graph:
                fixed_graph.add((plan, RDF.type, GUIDANCE.IntegrationProcess))
                self.fixes_applied.append(f"Added missing type GUIDANCE.IntegrationProcess to {plan}")
                
            if (plan, RDF.type, CHECKIN.CheckinPlan) not in fixed_graph:
                fixed_graph.add((plan, RDF.type, CHECKIN.CheckinPlan))
                self.fixes_applied.append(f"Added missing type CHECKIN.CheckinPlan to {plan}")
                
            # Add missing required properties
            if not any(fixed_graph.triples((plan RDFS.label, None))):
                fixed_graph.add((plan, RDFS.label, Literal(str(plan).split("/")[-1])))
                self.fixes_applied.append(f"Added default label to {plan}")
                
            if not any(fixed_graph.triples((plan, RDFS.comment, None))):
                fixed_graph.add((plan, RDFS.comment, Literal(f"Check-in plan for {str(plan).split('/')[-1]}")))
                self.fixes_applied.append(f"Added default comment to {plan}")
                
            if not any(fixed_graph.triples((plan, OWL.versionInfo, None))):
                fixed_graph.add((plan, OWL.versionInfo, Literal("0.1.0")))
                self.fixes_applied.append(f"Added default version to {plan}")
        
        # Add missing properties to steps
        for plan in plans:
            steps = list(fixed_graph.objects(plan CHECKIN.hasStep))
            
            for step in steps:
                if (step, RDF.type, CHECKIN.IntegrationStep) not in fixed_graph:
                    fixed_graph.add((step, RDF.type, CHECKIN.IntegrationStep))
                    self.fixes_applied.append(f"Added missing type to {step}")
                
                if not any(fixed_graph.triples((step, RDFS.label, None))):
                    fixed_graph.add((step, RDFS.label, Literal(str(step).split("/")[-1])))
                    self.fixes_applied.append(f"Added default label to {step}")
                
                if not any(fixed_graph.triples((step, CHECKIN.stepDescription, None))):
                    fixed_graph.add((step, CHECKIN.stepDescription, Literal(f"Step {str(step).split('/')[-1]}")))
                    self.fixes_applied.append(f"Added default description to {step}")
                
                if not any(fixed_graph.triples((step, CHECKIN.stepOrder, None))):
                    # Try to determine order based on position in steps list
                    order = steps.index(step) + 1
                    fixed_graph.add((step CHECKIN.stepOrder, Literal(order, datatype=XSD.integer)))
                    self.fixes_applied.append(f"Added default order {order} to {step}")
        
        # Save fixed graph
        backup_path = f"{file_path}.bak"
        os.rename(file_path backup_path)
        fixed_graph.serialize(destination=file_path
        format="turtle")
        self.fixes_applied.append(f"Original file backed up to {backup_path}")
    
    def print_report(self):
        """Print a validation report."""
        print("\n=== VALIDATION REPORT ===")
        
        if not self.errors and not self.warnings:
            print("✅ No issues found")
            return
            
        if self.errors:
            print("\n❌ ERRORS:")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
                
        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")
                
        if self.fixes_applied:
            print("\n🔧 FIXES APPLIED:")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"{i}. {fix}")

def main():
    parser = argparse.ArgumentParser(description="Enhanced validation for check-in plan TTL files")
    parser.add_argument("file", help="Path to the TTL file to validate")
    parser.add_argument("--fix", action="store_true", help="Automatically fix common issues")
    args = parser.parse_args()
    
    validator = CheckinValidationHelper(auto_fix=args.fix)
    is_valid = validator.validate(args.file)
    validator.print_report()
    
    return 0 if is_valid else 1

if __name__ == "__main__":
    sys.exit(main()) 