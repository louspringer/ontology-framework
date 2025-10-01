"""CI/CD pipeline for automated ontology testing and deployment"""

from typing import Dict, List, Optional, Any
import subprocess
import json
import yaml
from pathlib import Path
from datetime import datetime
from ..validation.advanced_validator import AdvancedValidator
from ..ontology_validator import OntologyValidator
from ..sparql_client import SPARQLClient


class CICDPipeline:
    """Automated CI/CD pipeline for ontology development"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.validator = OntologyValidator()
        self.advanced_validator = AdvancedValidator()
        self.results = {}
    
    def run_pipeline(self, ontology_files: List[str], branch: str = "main") -> Dict[str, Any]:
        """Run the complete CI/CD pipeline"""
        pipeline_result = {
            "timestamp": datetime.now().isoformat(),
            "branch": branch,
            "files": ontology_files,
            "stages": {},
            "overall_status": "success",
            "deployment_ready": False
        }
        
        try:
            # Stage 1: Validation
            validation_result = self._run_validation_stage(ontology_files)
            pipeline_result["stages"]["validation"] = validation_result
            
            if not validation_result["passed"]:
                pipeline_result["overall_status"] = "failed"
                return pipeline_result
            
            # Stage 2: Testing
            testing_result = self._run_testing_stage(ontology_files)
            pipeline_result["stages"]["testing"] = testing_result
            
            if not testing_result["passed"]:
                pipeline_result["overall_status"] = "failed"
                return pipeline_result
            
            # Stage 3: Quality Checks
            quality_result = self._run_quality_stage(ontology_files)
            pipeline_result["stages"]["quality"] = quality_result
            
            # Stage 4: Security Scan
            security_result = self._run_security_stage(ontology_files)
            pipeline_result["stages"]["security"] = security_result
            
            # Stage 5: Performance Analysis
            performance_result = self._run_performance_stage(ontology_files)
            pipeline_result["stages"]["performance"] = performance_result
            
            # Determine deployment readiness
            pipeline_result["deployment_ready"] = self._assess_deployment_readiness(pipeline_result)
            
            # Stage 6: Deployment (if ready and on main branch)
            if pipeline_result["deployment_ready"] and branch == "main":
                deployment_result = self._run_deployment_stage(ontology_files)
                pipeline_result["stages"]["deployment"] = deployment_result
        
        except Exception as e:
            pipeline_result["overall_status"] = "error"
            pipeline_result["error"] = str(e)
        
        return pipeline_result
    
    def create_pipeline_config(self, project_path: str) -> Dict[str, Any]:
        """Create a CI/CD pipeline configuration file"""
        config = {
            "pipeline": {
                "name": "ontology-ci-cd",
                "version": "1.0",
                "stages": ["validation", "testing", "quality", "security", "performance", "deployment"]
            },
            "validation": {
                "enabled": True,
                "tools": ["shacl", "owl", "turtle"],
                "fail_on_error": True,
                "fail_on_warning": False
            },
            "testing": {
                "enabled": True,
                "test_directories": ["tests/", "test/"],
                "coverage_threshold": 80,
                "timeout": 300
            },
            "quality": {
                "enabled": True,
                "max_hierarchy_depth": 10,
                "max_classes": 1000,
                "naming_conventions": True
            },
            "security": {
                "enabled": True,
                "scan_for_sensitive_data": True,
                "check_access_controls": True
            },
            "performance": {
                "enabled": True,
                "query_timeout": 30,
                "memory_limit": "2GB"
            },
            "deployment": {
                "environments": ["staging", "production"],
                "approval_required": True,
                "rollback_enabled": True
            },
            "notifications": {
                "slack_webhook": "",
                "email_recipients": [],
                "on_failure": True,
                "on_success": False
            }
        }
        
        # Write config file
        config_path = Path(project_path) / ".ontology-ci.yml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return config
    
    def generate_github_workflow(self, project_path: str) -> str:
        """Generate GitHub Actions workflow file"""
        workflow = """
name: Ontology CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run ontology validation
      run: |
        python -m ontology_framework.tools.validate_turtle_tool *.ttl
    
    - name: Run SHACL validation
      run: |
        python -m ontology_framework.validation.shacl_validator
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
  
  quality-check:
    needs: validate
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run quality analysis
      run: |
        python -m ontology_framework.validation.advanced_validator
    
    - name: Check naming conventions
      run: |
        python -m ontology_framework.tools.check_naming_conventions
  
  deploy:
    needs: [validate, quality-check]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to staging
      run: |
        python -m ontology_framework.integration.deploy --environment staging
    
    - name: Run smoke tests
      run: |
        python -m ontology_framework.tests.smoke_tests --environment staging
    
    - name: Deploy to production
      if: success()
      run: |
        python -m ontology_framework.integration.deploy --environment production
"""
        
        # Write workflow file
        workflow_dir = Path(project_path) / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_path = workflow_dir / "ontology-ci.yml"
        with open(workflow_path, 'w') as f:
            f.write(workflow)
        
        return str(workflow_path)
    
    def _run_validation_stage(self, ontology_files: List[str]) -> Dict[str, Any]:
        """Run validation stage of pipeline"""
        result = {
            "stage": "validation",
            "passed": True,
            "errors": [],
            "warnings": [],
            "files_processed": len(ontology_files)
        }
        
        for file_path in ontology_files:
            try:
                validation_result = self.validator.validate_file(file_path)
                
                if not validation_result.get("valid", False):
                    result["passed"] = False
                    result["errors"].extend(validation_result.get("errors", []))
                
                result["warnings"].extend(validation_result.get("warnings", []))
                
            except Exception as e:
                result["passed"] = False
                result["errors"].append(f"Validation failed for {file_path}: {str(e)}")
        
        return result
    
    def _run_testing_stage(self, ontology_files: List[str]) -> Dict[str, Any]:
        """Run testing stage of pipeline"""
        result = {
            "stage": "testing",
            "passed": True,
            "test_results": {},
            "coverage": 0
        }
        
        try:
            # Run pytest
            test_cmd = ["python", "-m", "pytest", "tests/", "--cov=src", "--cov-report=json", "-v"]
            test_process = subprocess.run(test_cmd, capture_output=True, text=True)
            
            result["test_results"]["exit_code"] = test_process.returncode
            result["test_results"]["stdout"] = test_process.stdout
            result["test_results"]["stderr"] = test_process.stderr
            
            if test_process.returncode != 0:
                result["passed"] = False
            
            # Parse coverage if available
            try:
                with open("coverage.json", "r") as f:
                    coverage_data = json.load(f)
                    result["coverage"] = coverage_data.get("totals", {}).get("percent_covered", 0)
            except FileNotFoundError:
                pass
                
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
        
        return result
    
    def _run_quality_stage(self, ontology_files: List[str]) -> Dict[str, Any]:
        """Run quality analysis stage"""
        result = {
            "stage": "quality",
            "passed": True,
            "quality_score": 0,
            "issues": []
        }
        
        total_score = 0
        file_count = 0
        
        for file_path in ontology_files:
            try:
                from rdflib import Graph
                graph = Graph()
                graph.parse(file_path)
                
                # Run advanced validation
                quality_analysis = self.advanced_validator.semantic_consistency_check(graph)
                performance_analysis = self.advanced_validator.performance_analysis(graph)
                
                file_score = performance_analysis.get("performance_score", 0)
                total_score += file_score
                file_count += 1
                
                if not quality_analysis.get("consistent", True):
                    result["issues"].extend(quality_analysis.get("issues", []))
                
            except Exception as e:
                result["issues"].append(f"Quality check failed for {file_path}: {str(e)}")
        
        if file_count > 0:
            result["quality_score"] = total_score / file_count
        
        # Determine if quality stage passed
        if result["quality_score"] < self.config.get("quality", {}).get("min_score", 70):
            result["passed"] = False
        
        return result
    
    def _run_security_stage(self, ontology_files: List[str]) -> Dict[str, Any]:
        """Run security scanning stage"""
        result = {
            "stage": "security",
            "passed": True,
            "vulnerabilities": [],
            "sensitive_data_found": False
        }
        
        # Basic security checks
        for file_path in ontology_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for sensitive patterns
                sensitive_patterns = [
                    "password", "secret", "key", "token", 
                    "credential", "private", "confidential"
                ]
                
                for pattern in sensitive_patterns:
                    if pattern.lower() in content.lower():
                        result["sensitive_data_found"] = True
                        result["vulnerabilities"].append({
                            "file": file_path,
                            "type": "sensitive_data",
                            "pattern": pattern,
                            "severity": "medium"
                        })
                
            except Exception as e:
                result["vulnerabilities"].append({
                    "file": file_path,
                    "type": "scan_error",
                    "error": str(e),
                    "severity": "low"
                })
        
        # Fail if high severity vulnerabilities found
        high_severity = [v for v in result["vulnerabilities"] if v.get("severity") == "high"]
        if high_severity:
            result["passed"] = False
        
        return result
    
    def _run_performance_stage(self, ontology_files: List[str]) -> Dict[str, Any]:
        """Run performance analysis stage"""
        result = {
            "stage": "performance",
            "passed": True,
            "metrics": {},
            "bottlenecks": []
        }
        
        try:
            from rdflib import Graph
            
            total_triples = 0
            total_classes = 0
            total_properties = 0
            
            for file_path in ontology_files:
                graph = Graph()
                graph.parse(file_path)
                
                total_triples += len(graph)
                total_classes += len(list(graph.subjects(None, None)))  # Simplified
                
            result["metrics"] = {
                "total_triples": total_triples,
                "total_classes": total_classes,
                "total_properties": total_properties,
                "files_processed": len(ontology_files)
            }
            
            # Check performance thresholds
            max_triples = self.config.get("performance", {}).get("max_triples", 100000)
            if total_triples > max_triples:
                result["bottlenecks"].append(f"Too many triples: {total_triples} > {max_triples}")
                result["passed"] = False
                
        except Exception as e:
            result["passed"] = False
            result["error"] = str(e)
        
        return result
    
    def _run_deployment_stage(self, ontology_files: List[str]) -> Dict[str, Any]:
        """Run deployment stage"""
        result = {
            "stage": "deployment",
            "passed": True,
            "environments": [],
            "rollback_plan": None
        }
        
        environments = self.config.get("deployment", {}).get("environments", ["staging"])
        
        for env in environments:
            env_result = self._deploy_to_environment(ontology_files, env)
            result["environments"].append(env_result)
            
            if not env_result.get("success", False):
                result["passed"] = False
                break
        
        return result
    
    def _deploy_to_environment(self, ontology_files: List[str], environment: str) -> Dict[str, Any]:
        """Deploy ontology files to specific environment"""
        result = {
            "environment": environment,
            "success": True,
            "deployed_files": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # This would typically involve:
            # 1. Uploading files to GraphDB
            # 2. Running smoke tests
            # 3. Updating environment configuration
            
            for file_path in ontology_files:
                # Simulate deployment
                result["deployed_files"].append({
                    "file": file_path,
                    "status": "deployed",
                    "size": Path(file_path).stat().st_size if Path(file_path).exists() else 0
                })
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    def _assess_deployment_readiness(self, pipeline_result: Dict[str, Any]) -> bool:
        """Assess if ontology is ready for deployment"""
        stages = pipeline_result.get("stages", {})
        
        # All critical stages must pass
        critical_stages = ["validation", "testing"]
        for stage in critical_stages:
            if not stages.get(stage, {}).get("passed", False):
                return False
        
        # Quality score must meet threshold
        quality_stage = stages.get("quality", {})
        min_quality = self.config.get("quality", {}).get("min_score", 70)
        if quality_stage.get("quality_score", 0) < min_quality:
            return False
        
        return True
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load pipeline configuration"""
        default_config = {
            "validation": {"fail_on_error": True},
            "testing": {"coverage_threshold": 80},
            "quality": {"min_score": 70},
            "performance": {"max_triples": 100000},
            "deployment": {"environments": ["staging"]}
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config