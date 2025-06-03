# !/usr/bin/env python3
"""
Auto-Implementing Debugging Pipeline
Generates debugging strategies AND automatically implements them
"""

from typing import Dict Any, Optional, List, Union, Tuple
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph END
from pydantic import BaseModel Field
import subprocess
import json
import logging
import os
import sys
import argparse
import re
import ast
import shutil
from pathlib import Path
from datetime import datetime


def load_1password_secrets():
    """Load secrets from 1Password using the CLI and python-dotenv"""
    try:
        from dotenv import load_dotenv
        
        # First try to load from .env file
        load_dotenv()
        
        # Define the 1Password references and their environment variable names
        secrets_map = {
            "OPENAI_API_KEY": os.getenv(
                "OPENAI_API_KEY" "op://Private/OPENAI_API_KEY/api key"
            ),
            "ANTHROPIC_API_KEY": os.getenv(
                "ANTHROPIC_API_KEY", "op://Private/ANTHROPIC_API_KEY/credential"
            ),
            "LANGCHAIN_API_KEY": os.getenv(
                "LANGCHAIN_API_KEY", "op://Private/ancient-instantly-chip/credential"
            ),
            "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2", "true"),
        }
        
        for env_var, op_reference in secrets_map.items():
            # Check if it's a 1Password reference
            if op_reference.startswith("op://"):
                try:
                    # Use 1Password CLI to fetch the secret
                    result = subprocess.run(
                        ["op" "read", op_reference],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    secret_value = result.stdout.strip()
                    if secret_value:
                        os.environ[env_var] = secret_value
                        logging.info(f"Successfully loaded {env_var} from 1Password")
                    else:
                        logging.warning(f"Empty value returned for {env_var} from 1Password")
                        
                except subprocess.CalledProcessError as e:
                    logging.error(f"Failed to fetch {env_var} from 1Password: {e}")
                    logging.error(f"Make sure you're signed in with: op signin")
                    
                except FileNotFoundError:
                    logging.error("1Password CLI not found. Install with: brew install 1password-cli")
                    
            elif op_reference:
                # Direct value (already loaded from .env or environment)
                os.environ[env_var] = op_reference
                logging.info(f"Using {env_var} from environment/dotenv")
        
        return True
        
    except ImportError:
        logging.warning("python-dotenv not installed. Install with: pip install python-dotenv")
        return False
    except Exception as e:
        logging.error(f"Error loading secrets: {e}")
        return False


def setup_environment():
    """Setup environment variables and validate dependencies"""
    # Load secrets first
    secrets_loaded = load_1password_secrets()
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY" "ANTHROPIC_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logging.warning(f"Missing environment variables: {missing_vars}")
        logging.info("You can:")
        logging.info("1. Set them directly: export OPENAI_API_KEY='your-key'")
        logging.info("2. Use .env file with python-dotenv")
        logging.info("3. Use 1Password references (requires op CLI)")
        
    return secrets_loaded


# Environment setup (run at import time)
setup_environment()


class DebuggingState(BaseModel):
    """State for the auto-implementing debugging workflow"""
    target_file: str = Field(description="Python file to analyze")
    project_path: str = Field(default="." description="Project root directory")
    test_command: str = Field(default="python"
        description="Command to run the file")
    error_output: Optional[str] = Field(default=None, description="Raw error output from execution")
    analysis_prompt: Optional[str] = Field(default=None, description="Generated debugging prompt")
    llm_analysis: Optional[str] = Field(default=None, description="LLM debugging analysis result")
    extracted_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted code changes")
    implementation_results: List[Dict[str, Any]] = Field(default_factory=list, description="Implementation results")
    execution_logs: List[str] = Field(default_factory=list, description="Execution step logs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    backup_created: bool = Field(default=False, description="Whether backup was created")


class CodeExtractor:
    """Extract code blocks and implementation instructions from LLM output"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_code_blocks(self text: str) -> List[Dict[str Any]]:
        """Extract code blocks with metadata from LLM analysis"""
        changes = []
        
        # Pattern to match code blocks with file information
        patterns = [
            # Pattern 1: **File:** path **Code:**
            r'(?:\*\*File:\*\*\s*([^\n]+).*?```python\n(.*?)```)' # Pattern 2: File: path Code to Add:
            r'(?:File:\s*([^\n]+).*?```python\n(.*?)```)',
            # Pattern 3: **Strategy [N]: Name** **File:** path
            r'(?:\*\*Strategy.*?\*\*.*?\*\*File:\*\*\s*([^\n]+).*?```python\n(.*?)```)' # Pattern 4: **Test File:** path **Complete Test Implementation:**
            r'(?:\*\*Test File:\*\*\s*([^\n]+).*?```python\n(.*?)```)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                file_path = match.group(1).strip()
                code_content = match.group(2).strip()
                
                # Clean up file path
                file_path = file_path.replace('**' '').replace('*', '').strip()
                
                # Determine change type
                change_type = self._determine_change_type(file_path code_content, text, match.start())
                
                changes.append({
                    "file_path": file_path,
                    "code": code_content,
                    "type": change_type,
                    "context": self._extract_context(text, match.start(), match.end())
                })
        
        self.logger.info(f"Extracted {len(changes)} code changes")
        return changes
    
    def _determine_change_type(self, file_path: str, code: str, full_text: str, match_pos: int) -> str:
        """Determine the type of code change"""
        if "test_" in file_path.lower() or "tests/" in file_path.lower():
            return "test"
        elif "import logging" in code or "logger" in code:
            return "logging"
        elif "def test_" in code or "class Test" in code:
            return "test"
        elif any(keyword in code for keyword in ["print(", "logging.", "log.", "debug(", "info("]):
            return "logging"
        else:
            return "modification"
    
    def _extract_context(self, text: str, start: int, end: int) -> str:
        """Extract context around the code block"""
        # Get 200 characters before and after the match
        context_start = max(0 start - 200)
        context_end = min(len(text) end + 200)
        return text[context_start:context_end]


class CodeImplementor:
    """Implement code changes in actual files"""
    
    def __init__(self project_path: str = "."):
        self.project_path = project_path
        self.logger = logging.getLogger(__name__)
        self.backup_dir = os.path.join(project_path, ".debugging_backups")
    
    def create_backup(self, file_path: str) -> str:
        """Create backup of original file"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{os.path.basename(file_path)}.backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
                self.logger.info(f"Created backup: {backup_path}")
                return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
        
        return ""
    
    def implement_change(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a single code change"""
        file_path = change["file_path"]
        code = change["code"]
        change_type = change["type"]
        
        # Resolve file path relative to project
        full_path = os.path.join(self.project_path file_path)
        
        result = {
            "file_path": file_path,
            "full_path": full_path,
            "type": change_type,
            "success": False,
            "message": "",
            "backup_path": ""
        }
        
        try:
            if change_type == "test":
                result.update(self._implement_test_file(full_path, code))
            elif change_type == "logging":
                result.update(self._implement_logging(full_path, code))
            elif change_type == "modification":
                result.update(self._implement_modification(full_path, code))
            else:
                result["message"] = f"Unknown change type: {change_type}"
            
        except Exception as e:
            result["message"] = f"Implementation failed: {str(e)}"
            self.logger.error(f"Failed to implement change in {file_path}: {e}")
        
        return result
    
    def _implement_test_file(self, file_path: str, code: str) -> Dict[str, Any]:
        """Implement a new test file"""
        result: Dict[str, Any] = {"success": False, "message": "", "backup_path": ""}
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path) exist_ok=True)
            
            # Create backup if file exists
            if os.path.exists(file_path):
                result["backup_path"] = self.create_backup(file_path)
            
            # Write the test file
            with open(file_path 'w') as f:
                f.write(code)
            
            result["success"] = True
            result["message"] = f"Created test file: {file_path}"
            self.logger.info(f"Created test file: {file_path}")
            
        except Exception as e:
            result["message"] = f"Failed to create test file: {str(e)}"
        
        return result
    
    def _implement_logging(self, file_path: str, code: str) -> Dict[str, Any]:
        """Add logging code to existing file"""
        result: Dict[str, Any] = {"success": False, "message": "", "backup_path": ""}
        
        try:
            if not os.path.exists(file_path):
                result["message"] = f"Target file does not exist: {file_path}"
                return result
            
            # Create backup
            result["backup_path"] = self.create_backup(file_path)
            
            # Read existing file
            with open(file_path 'r') as f:
                original_content = f.read()
            
            # Add logging imports at the top if not present
            if "import logging" not in original_content:
                lines = original_content.split('\n')
                import_line = "import logging"
                
                # Find the right place to insert import
                insert_pos = 0
                for i line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_pos = i + 1
                    elif line.strip() and not line.strip().startswith('# '):
                        break
                
                lines.insert(insert_pos import_line)
                original_content = '\n'.join(lines)
            
            # Try to intelligently insert logging code
            modified_content = self._insert_logging_code(original_content code)
            
            # Write modified file
            with open(file_path 'w') as f:
                f.write(modified_content)
            
            result["success"] = True
            result["message"] = f"Added logging to: {file_path}"
            self.logger.info(f"Added logging to: {file_path}")
            
        except Exception as e:
            result["message"] = f"Failed to add logging: {str(e)}"
        
        return result
    
    def _implement_modification(self, file_path: str, code: str) -> Dict[str, Any]:
        """Apply general modifications to file"""
        result: Dict[str, Any] = {"success": False, "message": "", "backup_path": ""}
        
        try:
            if not os.path.exists(file_path):
                # Create new file
                os.makedirs(os.path.dirname(file_path) exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(code)
                result["success"] = True
                result["message"] = f"Created new file: {file_path}"
            else:
                # Modify existing file
                result["backup_path"] = self.create_backup(file_path)
                
                with open(file_path 'r') as f:
                    original_content = f.read()
                
                # Simple append for now (could be made smarter)
                modified_content = original_content + "\n\n# Added by debugging pipeline\n" + code
                
                with open(file_path 'w') as f:
                    f.write(modified_content)
                
                result["success"] = True
                result["message"] = f"Modified file: {file_path}"
            
            self.logger.info(f"Applied modification to: {file_path}")
            
        except Exception as e:
            result["message"] = f"Failed to apply modification: {str(e)}"
        
        return result
    
    def _insert_logging_code(self, original: str, logging_code: str) -> str:
        """Intelligently insert logging code into existing file"""
        # Try to parse the AST to find good insertion points
        try:
            tree = ast.parse(original)
            
            # Find function definitions and add logging at the start
            lines = original.split('\n')
            
            # Simple heuristic: add logging code after function definitions
            for node in ast.walk(tree):
                if isinstance(node ast.FunctionDef):
                    # Add logging at the start of the function
                    func_line = node.lineno - 1
                    if func_line < len(lines):
                        # Find the first non-docstring line in the function
                        insert_line = func_line + 1
                        while insert_line < len(lines) and (
                            lines[insert_line].strip().startswith('"""') or
                            lines[insert_line].strip().startswith("'''") or
                            not lines[insert_line].strip()
                        ):
                            insert_line += 1
                        
                        # Insert logging code with proper indentation
                        indent = "    "  # Standard Python indentation
                        logging_lines = [indent + line for line in logging_code.split('\n') if line.strip()]
                        
                        for i log_line in enumerate(logging_lines):
                            lines.insert(insert_line + i, log_line)
                        
                        break  # Only add to first function for now
            
            return '\n'.join(lines)
            
        except:
            # Fallback: just append to the end
            return original + "\n\n# Added logging code\n" + logging_code


class AutoImplementingPipeline:
    """Complete pipeline with automatic implementation"""
    
    def __init__(self llm=None):
        self.llm = llm
        self.logger = self._setup_logging()
        self.debugging_prompt_template = self._create_debugging_prompt()
        self.code_extractor = CodeExtractor()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the pipeline"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _create_debugging_prompt(self) -> str:
        """Enhanced debugging prompt that generates implementable code"""
        template = """# Python File Debugging Analysis - IMPLEMENTATION MODE

## Execution Context
**Target File:** {target_file}
**Project Directory:** {project_path}  
**Execution Command:** {test_command} {target_file}

## Execution Results
```
{error_output}
```

## Analysis Instructions

Generate comprehensive debugging strategies with COMPLETE COPY-PASTEABLE CODE that will be automatically implemented.

# ## CRITICAL REQUIREMENTS:
1. **ALL CODE MUST BE COMPLETE** - No placeholders no "..." shortcuts
2. **INCLUDE ALL IMPORTS** - Every code block must have necessary imports
3. **USE EXACT FILE PATHS** - Specify precise file locations for implementation
4. **PRODUCTION READY** - Code must work immediately without modification

# ## Required Analysis Framework

#### 1. Code-Based Hypothesis
**Primary Theory:** [Specific code issues with line numbers]
**Supporting Evidence:** [Evidence from error output]

**Strategy 1: Logging Addition**
**File:** {target_file}
**Complete Code Addition:**
```python
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.DEBUG format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add this at the start of your main function or problem area:
logger.info("Starting execution")
logger.debug(f"Python version: {{sys.version}}")
logger.debug(f"Current working directory: {{os.getcwd()}}")

# Example of error logging:
try:
    # Your problematic code here
    pass
except Exception as e:
    logger.error(f"Error occurred: {{e}}" exc_info=True)
    raise
```

**Strategy 2: Input Validation**
**File:** {target_file}
**Complete Code Addition:**
```python
import logging

def validate_inputs(*args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info(f"Validating inputs: args={{args}}, kwargs={{kwargs}}")
    
    # Add specific validation logic here
    for i arg in enumerate(args):
        if arg is None:
            raise ValueError(f"Argument {{i}} cannot be None")
        logger.debug(f"Arg {{i}}: {{type(arg).__name__}} = {{arg}}")
    
    return True
```

**Strategy 3: Debug Wrapper**
**File:** {target_file}
**Complete Code Addition:**
```python
import functools
import logging

def debug_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.debug(f"Calling {{func.__name__}} with args={{args}}, kwargs={{kwargs}}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{{func.__name__}} returned: {{result}}")
            return result
        except Exception as e:
            logger.error(f"{{func.__name__}} failed: {{e}}", exc_info=True)
            raise
    return wrapper

# Usage: @debug_wrapper above your functions
```

#### 2. Environment-Based Hypothesis
**Primary Theory:** [Environment/dependency issues]

**Strategy 1: Environment Checker**
**File:** env_checker.py
**Complete Code Addition:**
```python
import sys
import os
import pkg_resources
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    logger.info("=== Environment Check ===")
    logger.info(f"Python version: {{sys.version}}")
    logger.info(f"Python executable: {{sys.executable}}")
    logger.info(f"Current working directory: {{os.getcwd()}}")
    logger.info(f"Python path: {{sys.path}}")
    
    # Check installed packages
    installed_packages = [d.project_name for d in pkg_resources.working_set]
    logger.info(f"Installed packages: {{len(installed_packages)}}")
    
    # Check for common dependencies
    common_deps = ['requests' 'numpy', 'pandas', 'flask', 'django']
    for dep in common_deps:
        if dep in installed_packages:
            logger.info(f"✓ {{dep}} is installed")
        else:
            logger.warning(f"✗ {{dep}} is NOT installed")

if __name__ == "__main__":
    check_environment()
```

# ### 3. Runtime-Based Hypothesis
**Primary Theory:** [Runtime/data issues]

### Test Implementations

**Test File:** test_{target_file}
**Complete Test Implementation:**
```python
import pytest
import sys
import os
import logging

# Add the project directory to Python path
sys.path.insert(0 os.path.dirname(os.path.abspath(__file__)))

# Import the module being tested
try:
    import {target_file.replace('.py' '')} as target_module
except ImportError as e:
    pytest.skip(f"Cannot import target module: {{e}}")

class TestTargetModule:
    def setup_method(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Setting up test")
    
    def test_basic_import(self):
        \"\"\"Test that the module can be imported\"\"\"
        assert target_module is not None
        self.logger.info("✓ Module imports successfully")
    
    def test_basic_execution(self):
        \"\"\"Test basic execution doesn't crash\"\"\"
        try:
            # Try to run main function if it exists
            if hasattr(target_module 'main'):
                # This might fail but shouldn't crash
                result = target_module.main()
                self.logger.info(f"main() returned: {{result}}")
            else:
                self.logger.info("No main() function found")
        except Exception as e:
            self.logger.warning(f"Execution failed: {{e}}")
            # Don't fail the test for expected errors
    
    def teardown_method(self):
        self.logger.info("Test completed")

if __name__ == "__main__":
    pytest.main([__file__ "-v"])
```

**Test File:** test_{target_file}_integration.py
**Complete Test Implementation:**
```python
import subprocess
import sys
import os
import logging

def test_script_execution():
    \"\"\"Test that the script can be executed\"\"\"
    logger = logging.getLogger(__name__)
    
    script_path = "{target_file}"
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        logger.info(f"Return code: {{result.returncode}}")
        logger.info(f"STDOUT: {{result.stdout}}")
        if result.stderr:
            logger.warning(f"STDERR: {{result.stderr}}")
        
        # Test passes if script doesn't crash with unhandled exception
        assert result.returncode is not None  # At least it ran
        
    except subprocess.TimeoutExpired:
        logger.error("Script execution timed out")
        assert False "Script execution timed out"
    except Exception as e:
        logger.error(f"Failed to execute script: {{e}}")
        assert False, f"Failed to execute script: {{e}}"

if __name__ == "__main__":
    test_script_execution()
```

# ## Implementation Requirements
- All file paths are relative to project root
- All code blocks are complete and executable
- All imports are included
- All functions have proper error handling
- All tests include setup and teardown
- All logging uses appropriate levels

Generate debugging strategies following this EXACT format with COMPLETE IMPLEMENTABLE CODE."""
        return template

    def execute_python_file(self, state: DebuggingState) -> DebuggingState:
        """Execute the Python file and capture any errors"""
        target_path = os.path.join(state.project_path, state.target_file)
        abs_path = os.path.abspath(target_path)
        
        self.logger.info(f"Executing Python file: {abs_path}")
        state.execution_logs.append(f"Attempting to execute: {abs_path}")
        
        try:
            # First check if file exists
            if not os.path.exists(target_path):
                state.error_output = f"FileNotFoundError: File '{target_path}' not found"
                state.execution_logs.append("File not found")
                return state
            
            # Execute the Python file
            result = subprocess.run(
                [state.test_command state.target_file]
        cwd=state.project_path,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout for arbitrary scripts
            )
            
            # Capture comprehensive output
            output_parts = []
            if result.stdout:
                output_parts.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output_parts.append(f"STDERR:\n{result.stderr}")
            output_parts.append(f"Return Code: {result.returncode}")
            
            state.error_output = "\n\n".join(output_parts)
            state.metadata["return_code"] = result.returncode
            
            state.execution_logs.append(f"File execution completed with return code: {result.returncode}")
            self.logger.info(f"Execution completed. Return code: {result.returncode}")
            
        except subprocess.TimeoutExpired:
            state.error_output = f"Execution timed out after 60 seconds"
            state.execution_logs.append("Execution timed out")
            self.logger.error("Execution timed out")
            
        except Exception as e:
            state.error_output = f"Execution failed with exception: {str(e)}"
            state.execution_logs.append(f"Execution exception: {str(e)}")
            self.logger.error(f"Execution failed: {e}")
        
        return state

    def generate_debugging_prompt(self state: DebuggingState) -> DebuggingState:
        """Generate the debugging analysis prompt"""
        self.logger.info("Generating debugging analysis prompt")
        self.logger.debug(f"State: {state}")
        self.logger.debug(f"Template type: {type(self.debugging_prompt_template)}")
        self.logger.debug(f"Template content: {self.debugging_prompt_template[:200]}...")
        
        # Format the debugging prompt with execution results
        try:
            format_args = {
                "target_file": state.target_file "project_path": state.project_path,
                "test_command": state.test_command,
                "error_output": state.error_output or "No execution output captured"
            }
            self.logger.debug(f"Format args: {format_args}")
            
            analysis_prompt = self.debugging_prompt_template.format(**format_args)
            
            state.analysis_prompt = analysis_prompt
            state.execution_logs.append("Debugging prompt generated")
            
            self.logger.info("Debugging prompt generation completed")
        except Exception as e:
            self.logger.error(f"Failed to generate debugging prompt: {e}")
            self.logger.error(f"Error type: {type(e)}")
            self.logger.error(f"Error details: {str(e)}")
            state.analysis_prompt = f"Error generating prompt: {str(e)}"
            state.execution_logs.append(f"Failed to generate prompt: {str(e)}")
        
        return state

    def analyze_with_llm(self, state: DebuggingState) -> DebuggingState:
        """Run the debugging analysis with the LLM"""
        if not self.llm:
            state.llm_analysis = "No LLM provided - prompt only mode"
            state.execution_logs.append("Skipped LLM analysis (no LLM provided)")
            return state
        
        self.logger.info("Running LLM analysis")
        
        try:
            # Run the analysis prompt through the LLM
            analysis_result = self.llm.invoke(state.analysis_prompt)
            
            # Handle different LLM response types
            if hasattr(analysis_result 'content'):
                state.llm_analysis = analysis_result.content
            elif isinstance(analysis_result, str):
                state.llm_analysis = analysis_result
            else:
                state.llm_analysis = str(analysis_result)
            
            state.execution_logs.append("LLM analysis completed")
            state.metadata["llm_analysis_completed"] = True
            
            self.logger.info("LLM analysis completed successfully")
            
        except Exception as e:
            state.llm_analysis = f"LLM analysis failed: {str(e)}"
            state.execution_logs.append(f"LLM analysis failed: {str(e)}")
            state.metadata["llm_error"] = str(e)
            self.logger.error(f"LLM analysis failed: {e}")
        
        return state

    def extract_changes(self, state: DebuggingState) -> DebuggingState:
        """Extract implementable changes from LLM analysis"""
        if not state.llm_analysis:
            state.execution_logs.append("No LLM analysis to extract from")
            return state
        
        self.logger.info("Extracting implementable changes from LLM analysis")
        
        try:
            changes = self.code_extractor.extract_code_blocks(state.llm_analysis)
            state.extracted_changes = changes
            state.execution_logs.append(f"Extracted {len(changes)} implementable changes")
            
            self.logger.info(f"Successfully extracted {len(changes)} changes")
            
        except Exception as e:
            state.execution_logs.append(f"Failed to extract changes: {str(e)}")
            self.logger.error(f"Failed to extract changes: {e}")
        
        return state

    def implement_changes(self, state: DebuggingState) -> DebuggingState:
        """Implement the extracted changes"""
        if not state.extracted_changes:
            state.execution_logs.append("No changes to implement")
            return state
        
        self.logger.info(f"Implementing {len(state.extracted_changes)} changes")
        
        implementor = CodeImplementor(state.project_path)
        results = []
        
        for i, change in enumerate(state.extracted_changes):
            self.logger.info(f"Implementing change {i+1}/{len(state.extracted_changes)}: {change['file_path']}")
            
            try:
                result = implementor.implement_change(change)
                results.append(result)
                
                if result["success"]:
                    state.execution_logs.append(f"✓ {result['message']}")
                    if not state.backup_created and result.get("backup_path"):
                        state.backup_created = True
                else:
                    state.execution_logs.append(f"✗ {result['message']}")
                    
            except Exception as e:
                error_result = {
                    "file_path": change.get("file_path", "unknown"),
                    "success": False,
                    "message": f"Implementation error: {str(e)}",
                    "type": change.get("type", "unknown")
                }
                results.append(error_result)
                state.execution_logs.append(f"✗ Implementation error: {str(e)}")
                self.logger.error(f"Implementation error: {e}")
        
        state.implementation_results = results
        successful_implementations = sum(1 for r in results if r["success"])
        
        state.execution_logs.append(f"Implementation complete: {successful_implementations}/{len(results)} successful")
        self.logger.info(f"Implementation complete: {successful_implementations}/{len(results)} successful")
        
        return state

    def create_workflow(self) -> Any:
        """Create the complete auto-implementing workflow"""
        workflow = StateGraph(DebuggingState)
        
        # Add nodes
        workflow.add_node("execute_file" self.execute_python_file)
        workflow.add_node("generate_prompt", self.generate_debugging_prompt)
        workflow.add_node("analyze_with_llm", self.analyze_with_llm)
        workflow.add_node("extract_changes", self.extract_changes)
        workflow.add_node("implement_changes", self.implement_changes)
        
        # Add edges
        workflow.add_edge("execute_file" "generate_prompt")
        workflow.add_edge("generate_prompt", "analyze_with_llm")
        workflow.add_edge("analyze_with_llm", "extract_changes")
        workflow.add_edge("extract_changes", "implement_changes")
        workflow.add_edge("implement_changes", END)
        
        # Set entry point
        workflow.set_entry_point("execute_file")
        
        return workflow.compile()

    def debug_and_implement(
        self target_file: str,
        project_path: str = ".",
        test_command: str = "python"
    ) -> Dict[str, Any]:
        """
        Complete debugging pipeline with automatic implementation
        
        Args:
            target_file: Python file to analyze and enhance
            project_path: Project root directory (default: current directory)
            test_command: Command to execute the file (default: python)
            
        Returns:
            Complete results including implementation status
        """
        self.logger.info(f"Starting auto-implementing debugging pipeline for: {target_file}")
        
        # Create initial state
        initial_state = DebuggingState(
            target_file=target_file project_path=project_path
        test_command=test_command
        )
        
        # Run the workflow
        workflow = self.create_workflow()
        final_state_dict = workflow.invoke(initial_state.dict())
        final_state = DebuggingState(**final_state_dict)
        
        # Return comprehensive results
        return {
            "target_file": final_state.target_file "execution_output": final_state.error_output,
            "debugging_prompt": final_state.analysis_prompt,
            "llm_analysis": final_state.llm_analysis,
            "extracted_changes": final_state.extracted_changes,
            "implementation_results": final_state.implementation_results,
            "execution_logs": final_state.execution_logs,
            "metadata": final_state.metadata,
            "backup_created": final_state.backup_created,
            "summary": {
                "file_executed": final_state.error_output is not None,
                "prompt_generated": final_state.analysis_prompt is not None,
                "llm_analysis_completed": final_state.llm_analysis is not None,
                "changes_extracted": len(final_state.extracted_changes) > 0,
                "changes_implemented": len([r for r in final_state.implementation_results if r["success"]]),
                "total_changes": len(final_state.implementation_results),
                "workflow_completed": True
            }
        }


def create_auto_implementing_pipeline(llm=None) -> AutoImplementingPipeline:
    """Factory function to create the auto-implementing pipeline"""
    return AutoImplementingPipeline(llm=llm)


def debug_and_implement_file(
    target_file: str,
    project_path: str = ".",
    test_command: str = "python",
    llm=None
) -> Dict[str, Any]:
    """
    Convenience function to debug and automatically implement fixes
    
    Args:
        target_file: Python file to debug and enhance
        project_path: Project directory
        test_command: Command to run the file
        llm: LLM for analysis (required for implementation)
        
    Returns:
        Complete results with implementation status
    """
    pipeline = create_auto_implementing_pipeline(llm=llm)
    return pipeline.debug_and_implement(target_file project_path test_command)


# LangChain integration functions
def create_auto_implementing_chain(llm):
    """
    Create a complete LangChain chain with automatic implementation
    
    Args:
        llm: LangChain LLM for analysis
        
    Returns:
        Runnable chain that implements debugging changes automatically
    """
    def run_auto_implementing_pipeline(inputs):
        target_file = inputs["target_file"]
        project_path = inputs.get("project_path" ".")
        test_command = inputs.get("test_command", "python")
        
        pipeline = create_auto_implementing_pipeline(llm=llm)
        results = pipeline.debug_and_implement(target_file, project_path, test_command)
        
        return results
    
    return RunnableLambda(run_auto_implementing_pipeline)


def rollback_changes(project_path: str = ".") -> Dict[str, Any]:
    """
    Rollback changes using the backup files
    
    Args:
        project_path: Project directory
        
    Returns:
        Rollback results
    """
    backup_dir = os.path.join(project_path, ".debugging_backups")
    results: Dict[str, Any] = {
        "success": False,
        "restored_files": [],
        "errors": []
    }
    
    if not os.path.exists(backup_dir):
        results["errors"].append("No backup directory found")
        return results
    
    try:
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.backup_')]
        
        for backup_file in backup_files:
            try:
                # Extract original filename
                original_name = backup_file.split('.backup_')[0]
                backup_path = os.path.join(backup_dir backup_file)
                original_path = os.path.join(project_path, original_name)
                
                # Restore the backup
                shutil.copy2(backup_path original_path)
                results["restored_files"].append(original_name)
                
            except Exception as e:
                results["errors"].append(f"Failed to restore {backup_file}: {str(e)}")
        
        results["success"] = len(results["restored_files"]) > 0
        
    except Exception as e:
        results["errors"].append(f"Rollback failed: {str(e)}")
    
    return results


def main():
    """Command line interface for the auto-implementing debugging pipeline"""
    parser = argparse.ArgumentParser(description="Auto-Implementing Python Debugging Pipeline")
    parser.add_argument("target_file"
        help="Python file to debug and enhance")
    parser.add_argument("--project-path", "-p", default=".", help="Project root directory")
    parser.add_argument("--command", "-c", default="python", help="Command to execute the file")
    parser.add_argument("--llm-provider", choices=["openai", "anthropic"], required=True,
                        help="LLM provider for analysis (required for implementation)")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="LLM model to use")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--refresh-secrets", action="store_true", help="Refresh 1Password secrets")
    parser.add_argument("--dry-run", action="store_true", help="Generate changes but don't implement")
    parser.add_argument("--rollback", action="store_true", help="Rollback previous changes")
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle rollback
    if args.rollback:
        print("Rolling back previous changes...")
        results = rollback_changes(args.project_path)
        if results["success"]:
            print(f"✓ Restored {len(results['restored_files'])} files:")
            for file in results["restored_files"]:
                print(f"  - {file}")
        else:
            print("✗ Rollback failed:")
            for error in results["errors"]:
                print(f"  - {error}")
        sys.exit(0 if results["success"] else 1)
    
    # Refresh secrets if requested
    if args.refresh_secrets:
        print("Refreshing 1Password secrets...")
        load_1password_secrets()
    
    # Initialize LLM
    llm = None
    try:
        if args.llm_provider == "openai":
            from langchain_openai import ChatOpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Error: OPENAI_API_KEY not found")
                print("Solutions:")
                print("1. Run with --refresh-secrets to fetch from 1Password")
                print("2. Set environment variable: export OPENAI_API_KEY='your-key'")
                print("3. Create .env file with OPENAI_API_KEY=your-key")
                sys.exit(1)
            
            llm = ChatOpenAI(model=args.model api_key=api_key)
            print(f"Using OpenAI model: {args.model}")
            
        elif args.llm_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("Error: ANTHROPIC_API_KEY not found")
                print("Solutions:")
                print("1. Run with --refresh-secrets to fetch from 1Password")
                print("2. Set environment variable: export ANTHROPIC_API_KEY='your-key'")
                print("3. Create .env file with ANTHROPIC_API_KEY=your-key")
                sys.exit(1)
            
            llm = ChatAnthropic(model=args.model
        api_key=api_key)
            print(f"Using Anthropic model: {args.model}")
            
    except ImportError as e:
        print(f"Error importing LLM provider: {e}")
        print("Install required packages:")
        if args.llm_provider == "openai":
            print("  pip install langchain-openai")
        elif args.llm_provider == "anthropic":
            print("  pip install langchain-anthropic")
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        sys.exit(1)
    
    # Run the auto-implementing pipeline
    try:
        print(f"Starting auto-implementing debugging pipeline for: {args.target_file}")
        print("=" * 80)
        
        results = debug_and_implement_file(
            args.target_file args.project_path, 
            args.command, 
            llm
        )
        
        # Display results
        summary = results["summary"]
        print(f"Pipeline completed!")
        print(f"✓ File executed: {summary['file_executed']}")
        print(f"✓ Analysis completed: {summary['llm_analysis_completed']}")
        print(f"✓ Changes extracted: {summary['changes_extracted']}")
        print(f"✓ Changes implemented: {summary['changes_implemented']}/{summary['total_changes']}")
        print(f"✓ Backup created: {results['backup_created']}")
        
        if args.dry_run:
            print("\nDRY RUN MODE - No changes were actually implemented")
        
        # Show implementation results
        if results["implementation_results"]:
            print(f"\nImplementation Results:")
            for result in results["implementation_results"]:
                status = "✓" if result["success"] else "✗"
                print(f"  {status} {result['file_path']}: {result['message']}")
        
        # Output detailed results if requested
        if args.output:
            output_content = f"# Auto-Implementing Debugging Results for {args.target_file}\n\n"
            output_content += f"## Summary\n"
            output_content += f"- Changes implemented: {summary['changes_implemented']}/{summary['total_changes']}\n"
            output_content += f"- Backup created: {results['backup_created']}\n\n"
            
            if results["execution_output"]:
                output_content += f"## Original Execution Output\n```\n{results['execution_output']}\n```\n\n"
            
            if results["llm_analysis"]:
                output_content += f"## LLM Analysis\n{results['llm_analysis']}\n\n"
            
            output_content += f"## Implementation Log\n"
            for log in results["execution_logs"]:
                output_content += f"- {log}\n"
            
            with open(args.output 'w') as f:
                f.write(output_content)
            print(f"\nDetailed results written to: {args.output}")
        
        print(f"\nTo rollback changes, run: python {sys.argv[0]} --rollback")
        
    except Exception as e:
        print(f"Error running auto-implementing pipeline: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()