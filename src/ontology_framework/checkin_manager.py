#!/usr/bin/env python3
"""
Checkin manager implementation with LLM integration.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import subprocess
from enum import Enum
import json
import openai
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
import sys

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD

from .meta import OntologyPatch, PatchType, PatchStatus
from .patch_management import PatchManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('checkin.log')
    ]
)
logger = logging.getLogger(__name__)

class StepStatus(Enum):
    """Status of a checkin step."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"

class LLMClient:
    """Client for interacting with the LLM."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """Initialize the LLM client."""
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized LLM client with model: {model}")
    
    async def analyze_errors(self, error_output: str, test_context: str) -> Dict[str, Any]:
        """Analyze test failures and suggest fixes.
        
        Args:
            error_output: The error output from tests
            test_context: Context about the tests being run
            
        Returns:
            Dict[str, Any]: Analysis containing:
                - root_cause: str
                - fixes: List[str]
                - code_changes: List[str]
                - model_changes: List[str]
                - error: Optional[str]
        """
        self.logger.info("Starting error analysis")
        self.logger.debug(f"Test context: {test_context}")
        self.logger.debug(f"Error output: {error_output}")
        
        if not error_output:
            return {
                "root_cause": "No error output provided",
                "fixes": [],
                "code_changes": [],
                "model_changes": [],
                "error": "No error output provided"
            }
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """
                    You are an expert Python developer and test analyst. 
                    Analyze test failures and suggest specific fixes.
                    Consider both code and model changes.
                    """},
                    {"role": "user", "content": f"""
                    Analyze these test failures and suggest fixes:
                    
                    Test Context:
                    {test_context}
                    
                    Error Output:
                    {error_output}
                    
                    Provide a structured response with:
                    1. Root cause analysis
                    2. Specific fixes needed
                    3. Suggested code changes
                    4. Suggested model changes
                    """}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            self.logger.info("Error analysis completed")
            self.logger.debug(f"Analysis result: {json.dumps(analysis, indent=2)}")
            
            # Ensure the analysis has the expected structure
            return {
                "root_cause": analysis.get("root_cause", "Unknown"),
                "fixes": analysis.get("fixes", []),
                "code_changes": analysis.get("code_changes", []),
                "model_changes": analysis.get("model_changes", []),
                "error": None
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing test failures: {str(e)}")
            return {
                "root_cause": "Error during analysis",
                "fixes": [],
                "code_changes": [],
                "model_changes": [],
                "error": str(e)
            }
    
    async def generate_commit_message(self, patch: OntologyPatch, changes: List[str]) -> Optional[str]:
        """Generate a commit message for the changes."""
        self.logger.info("Starting commit message generation")
        self.logger.debug(f"Patch details: {patch.patch_id}, {patch.patch_type}")
        self.logger.debug(f"Changes: {changes}")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """
                    You are an expert at writing clear, concise commit messages.
                    Use markdown format and include relevant emoji.
                    Reference the guidance file when appropriate.
                    """},
                    {"role": "user", "content": f"""
                    Create a commit message for these changes:
                    
                    Patch Details:
                    - ID: {patch.patch_id}
                    - Type: {patch.patch_type}
                    - Target: {patch.target_ontology}
                    - Description: {patch.content}
                    
                    Changes Made:
                    {chr(10).join(f'- {change}' for change in changes)}
                    
                    Format:
                    - Use markdown
                    - Include relevant emoji
                    - Reference guidance.ttl
                    - Keep it concise but informative
                    """}
                ],
                temperature=0.3
            )
            
            message = response.choices[0].message.content
            self.logger.info("Commit message generated")
            self.logger.debug(f"Generated message: {message}")
            return message
            
        except Exception as e:
            self.logger.error(f"Error generating commit message: {str(e)}")
            return None

class CheckinManager:
    """Manages the checkin process with LLM integration."""
    
    def __init__(self, llm_client: LLMClient, patch_manager: PatchManager):
        """Initialize the checkin manager."""
        self.llm_client = llm_client
        self.patch_manager = patch_manager
        self.logger = logging.getLogger(__name__)
        
        # Load checkin process model
        self.checkin_model = Graph()
        self.checkin_model.parse("guidance/modules/checkin.ttl", format="turtle")
        self.logger.info("Loaded checkin process model")
        
        # Initialize step status
        self.step_status: Dict[str, StepStatus] = {
            "run_tests": StepStatus.PENDING,
            "fix_errors": StepStatus.PENDING,
            "git_add": StepStatus.PENDING,
            "create_message": StepStatus.PENDING,
            "commit": StepStatus.PENDING
        }
        self.logger.debug(f"Initialized step status: {self.step_status}")
        
        # Track changes for commit message
        self.changes: List[str] = []
        self.last_test_output: Optional[str] = None
    
    async def checkin(self, patch: OntologyPatch) -> StepStatus:
        """Run the checkin process for a patch.
        
        Args:
            patch: The patch to check in
            
        Returns:
            StepStatus: The final status of the checkin process
        """
        self.logger.info(f"Starting checkin process for patch: {patch.patch_id}")
        
        try:
            # Step 1: Run tests
            self.logger.info("Running tests")
            test_status = await self._run_tests()
            
            # If tests fail, try to fix them
            if test_status == StepStatus.FAILED:
                self.logger.info("Tests failed, attempting fixes")
                fix_status = await self._fix_errors(self.last_test_output)
                if fix_status != StepStatus.SUCCESS:
                    self.logger.error("Error fixing failed")
                    return StepStatus.FAILED
                
                # Rerun tests after fixes
                test_status = await self._run_tests()
                if test_status != StepStatus.COMPLETED:
                    self.logger.error("Tests still failing after fixes")
                    return StepStatus.FAILED
            
            # Step 3: Add changes to git
            self.logger.info("Adding changes to git")
            add_status = await self._git_add()
            if add_status != StepStatus.COMPLETED:
                self.logger.error("Git add failed")
                return StepStatus.FAILED
            
            # Step 4: Create commit message
            self.logger.info("Creating commit message")
            message = await self._create_commit_message(patch)
            if not message:
                self.logger.error("Failed to create commit message")
                return StepStatus.FAILED
            
            # Step 5: Commit changes
            self.logger.info("Committing changes")
            commit_status = await self._commit(message)
            if commit_status != StepStatus.COMPLETED:
                self.logger.error("Commit failed")
                return StepStatus.FAILED
            
            self.logger.info("Checkin process completed successfully")
            return StepStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Checkin process failed: {str(e)}")
            return StepStatus.FAILED
    
    async def _run_tests(self) -> StepStatus:
        """Run the test suite."""
        self.step_status["run_tests"] = StepStatus.IN_PROGRESS
        self.logger.info("Running test suite")
        
        try:
            result = subprocess.run(
                ["pytest", "-v"],
                capture_output=True,
                text=True
            )
            
            self.last_test_output = result.stdout + result.stderr or "No output from test run"
            
            if result.returncode == 0:
                self.step_status["run_tests"] = StepStatus.COMPLETED
                self.logger.info("All tests passed")
                return StepStatus.COMPLETED
            else:
                self.step_status["run_tests"] = StepStatus.FAILED
                self.logger.error(f"Tests failed: {self.last_test_output}")
                return StepStatus.FAILED
                
        except Exception as e:
            self.step_status["run_tests"] = StepStatus.FAILED
            self.last_test_output = f"Error running tests: {str(e)}"
            self.logger.error(self.last_test_output)
            return StepStatus.FAILED
    
    async def _fix_errors(self, error_output: str) -> StepStatus:
        """Fix test failures using LLM analysis."""
        self.step_status["fix_errors"] = StepStatus.IN_PROGRESS
        self.logger.info("Analyzing test failures")
        
        try:
            analysis = await self.llm_client.analyze_errors(
                error_output=error_output,
                test_context="Fixing test failures in checkin process"
            )
            
            if analysis.get("error"):
                self.step_status["fix_errors"] = StepStatus.FAILED
                self.logger.error(f"LLM analysis failed: {analysis['error']}")
                return StepStatus.FAILED
            
            # Check if analysis is empty or missing required fields
            if not analysis.get("root_cause") or not analysis.get("fixes"):
                self.step_status["fix_errors"] = StepStatus.FAILED
                self.logger.error("LLM analysis returned empty or incomplete result")
                return StepStatus.FAILED
            
            # Log root cause
            self.logger.info(f"Root cause: {analysis['root_cause']}")
            
            # Apply fixes
            for fix in analysis.get("fixes", []):
                self.logger.info(f"Applying fix: {fix}")
                self.changes.append(fix)
            
            # Track code changes
            for change in analysis.get("code_changes", []):
                self.logger.info(f"Applying code change: {change}")
                self.changes.append(f"Code: {change}")
            
            # Track model changes
            for change in analysis.get("model_changes", []):
                self.logger.info(f"Applying model change: {change}")
                self.changes.append(f"Model: {change}")
            
            self.step_status["fix_errors"] = StepStatus.SUCCESS
            self.logger.info("Error fixes applied")
            return StepStatus.SUCCESS
            
        except Exception as e:
            self.step_status["fix_errors"] = StepStatus.FAILED
            self.logger.error(f"Error fixing test failures: {str(e)}")
            return StepStatus.FAILED
    
    async def _git_add(self) -> StepStatus:
        """Add changes to git."""
        self.step_status["git_add"] = StepStatus.IN_PROGRESS
        self.logger.info("Adding changes to git")
        
        try:
            result = subprocess.run(
                ["git", "add", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.step_status["git_add"] = StepStatus.COMPLETED
                self.logger.info("Changes added to git")
                return StepStatus.COMPLETED
            else:
                self.step_status["git_add"] = StepStatus.FAILED
                self.logger.error(f"Git add failed: {result.stderr}")
                return StepStatus.FAILED
                
        except Exception as e:
            self.step_status["git_add"] = StepStatus.FAILED
            self.logger.error(f"Error adding changes to git: {str(e)}")
            return StepStatus.FAILED
    
    async def _create_commit_message(self, patch: OntologyPatch) -> Optional[str]:
        """Create a commit message using LLM."""
        self.step_status["create_message"] = StepStatus.IN_PROGRESS
        self.logger.info("Creating commit message")
        
        try:
            message = await self.llm_client.generate_commit_message(
                patch=patch,
                changes=self.changes
            )
            
            if message:
                self.step_status["create_message"] = StepStatus.COMPLETED
                self.logger.info("Commit message created")
                return message
            else:
                self.step_status["create_message"] = StepStatus.FAILED
                self.logger.error("Failed to create commit message")
                return None
                
        except Exception as e:
            self.step_status["create_message"] = StepStatus.FAILED
            self.logger.error(f"Error creating commit message: {str(e)}")
            return None
    
    async def _commit(self, message: str) -> StepStatus:
        """Commit changes to git."""
        self.step_status["commit"] = StepStatus.IN_PROGRESS
        self.logger.info("Committing changes")
        
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.step_status["commit"] = StepStatus.COMPLETED
                self.logger.info("Changes committed")
                return StepStatus.COMPLETED
            else:
                self.step_status["commit"] = StepStatus.FAILED
                self.logger.error(f"Commit failed: {result.stderr}")
                return StepStatus.FAILED
                
        except Exception as e:
            self.step_status["commit"] = StepStatus.FAILED
            self.logger.error(f"Error committing changes: {str(e)}")
            return StepStatus.FAILED 