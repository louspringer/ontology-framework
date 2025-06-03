# !/usr/bin/env python3
"""
Complete LangChain/LangGraph Debugging Pipeline
Executes tests generates debugging prompts and analyzes with LLM
"""

from typing import Dict Any, Optional, List, Union
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import subprocess
import json
import logging
import os
import sys
import argparse
from pathlib import Path
import re


def load_1password_secrets():
    """Load secrets from 1Password using the CLI and python-dotenv"""
    try:
        from dotenv import load_dotenv
        
        # First try to load from .env file
        load_dotenv()
        
        # Define the 1Password references and their environment variable names
        secrets_map = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY" "op://Private/OPENAI_API_KEY/api key"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", "op://Private/ANTHROPIC_API_KEY/credential")
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
    """State for the complete debugging workflow"""
    target_file: str = Field(description="Python file to analyze")
    project_path: str = Field(default="." description="Project root directory")
    test_command: str = Field(default="python"
        description="Command to run the file")
    error_output: Optional[str] = Field(default=None, description="Raw error output from execution")
    analysis_prompt: Optional[str] = Field(default=None, description="Generated debugging prompt")
    llm_analysis: Optional[str] = Field(default=None, description="LLM debugging analysis result")
    execution_logs: List[str] = Field(default_factory=list, description="Execution step logs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CompletePipelineAgent:
    """Complete debugging pipeline with LLM analysis"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.logger = self._setup_logging()
        self.debugging_prompt_template = self._create_debugging_prompt()
        
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
        """Enhanced debugging prompt template for arbitrary Python files"""
        return """# Python File Debugging Analysis

## Execution Context

**Target File:** {target_file}
**Project Directory:** {project_path}  
**Execution Command:** {test_command} {target_file}

## Execution Results

```
{error_output}
```

## Analysis Instructions

You are an expert Python debugging specialist. Analyze the execution failure above and provide comprehensive debugging strategies.

### Required Analysis Framework

#### 1. Code-Based Hypothesis
**Primary Theory:** [Identify specific code issues - syntax logic, imports, etc.]
**Supporting Evidence:** [What in the error output supports this hypothesis]
**Alternative Code Theories:** [At least 2 additional plausible code-related causes]

# ### 2. Environment-Based Hypothesis  
**Primary Theory:** [Identify environment issues - dependencies Python version, system config]
**Supporting Evidence:** [What could suggest environment problems]
**Alternative Environment Theories:** [At least 2 additional plausible environment causes]

# ### 3. Runtime-Based Hypothesis
**Primary Theory:** [Identify runtime issues - data resources, external dependencies]
**Supporting Evidence:** [What suggests runtime/execution problems]
**Alternative Runtime Theories:** [At least 2 additional plausible runtime causes]

# ## Required Debugging Strategies

For **each hypothesis above** provide:

# ### Logging Strategies (3 per hypothesis)
**Strategy 1: [Name]**
- **File:** {target_file} or related files
- **Location:** [Specific function/line numbers]
- **Complete Code Addition:**
```python
[Full copy-pasteable logging code with imports]
```
- **Validation Command:** [Exact command to test]
- **Expected Output:** [What the logs should show]

**Strategy 2: [Name]**
[Similar format]

**Strategy 3: [Name]**
[Similar format]

# ### Testing Strategies (2 per hypothesis)
**Test Strategy 1: [Name]**
- **Test File:** test_{target_file}
- **Complete Test Implementation:**
```python
[Full runnable test code with imports and assertions]
```
- **Run Command:** [Exact command to execute]
- **Expected Behavior:** [What should happen]

**Test Strategy 2: [Name]**
[Similar format]

# ## Implementation Requirements

- All code must be immediately copy-pasteable
- Include all necessary imports and dependencies
- Provide exact file paths and line numbers
- Include proper error handling
- Add both positive and negative test cases
- Use appropriate logging levels (DEBUG INFO, WARNING ERROR)
- Include cleanup and teardown procedures

# ## Output Format

Structure your response as:

```markdown
# File Analysis Summary
[Brief overview of the error and likely causes]

# Hypothesis 1: Code-Based
[Detailed analysis as specified above]

# Hypothesis 2: Environment-Based  
[Detailed analysis as specified above]

# Hypothesis 3: Runtime-Based
[Detailed analysis as specified above]

# Immediate Action Items
1. [Most likely fix to try first]
2. [Second most likely approach]
3. [Diagnostic steps to gather more info]

# Implementation Guide
[Step-by-step instructions for applying the strategies]
```

Provide comprehensive actionable debugging strategies that can be immediately implemented."""

    def execute_python_file(self state: DebuggingState) -> DebuggingState:
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
            state.metadata["has_stdout"] = bool(result.stdout)
            state.metadata["has_stderr"] = bool(result.stderr)
            
            if result.returncode == 0:
                state.execution_logs.append("File executed successfully")
                # If successful we might still want to analyze for potential issues
                if not result.stdout and not result.stderr:
                    state.error_output += "\n\nNOTE: File executed without output. May need analysis for completeness."
            else:
                state.execution_logs.append(f"File execution failed with return code: {result.returncode}")
            
            self.logger.info(f"Execution completed. Return code: {result.returncode}")
            
        except subprocess.TimeoutExpired:
            state.error_output = f"Execution timed out after 60 seconds\nFile: {target_path}\nCommand: {state.test_command} {state.target_file}"
            state.execution_logs.append("Execution timed out")
            state.metadata["timeout"] = True
            self.logger.error("Execution timed out")
            
        except Exception as e:
            state.error_output = f"Execution failed with exception: {str(e)}\nFile: {target_path}\nCommand: {state.test_command} {state.target_file}"
            state.execution_logs.append(f"Execution exception: {str(e)}")
            state.metadata["exception"] = str(e)
            self.logger.error(f"Execution failed: {e}")
        
        return state

    def generate_debugging_prompt(self, state: DebuggingState) -> DebuggingState:
        """Generate the debugging analysis prompt"""
        self.logger.info("Generating debugging analysis prompt")
        
        # Format the debugging prompt with execution results
        analysis_prompt = self.debugging_prompt_template.format(
            target_file=state.target_file project_path=state.project_path
        test_command=state.test_command,
            error_output=state.error_output or "No execution output captured"
        )
        
        state.analysis_prompt = analysis_prompt
        state.execution_logs.append("Debugging prompt generated")
        
        self.logger.info("Debugging prompt generation completed")
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

    def create_workflow(self) -> StateGraph:
        """Create the complete debugging workflow"""
        workflow = StateGraph(DebuggingState)
        
        # Add nodes
        workflow.add_node("execute_file" self.execute_python_file)
        workflow.add_node("generate_prompt", self.generate_debugging_prompt)
        workflow.add_node("analyze_with_llm", self.analyze_with_llm)
        
        # Add edges
        workflow.add_edge("execute_file" "generate_prompt")
        workflow.add_edge("generate_prompt", "analyze_with_llm")
        workflow.add_edge("analyze_with_llm", END)
        
        # Set entry point
        workflow.set_entry_point("execute_file")
        
        return workflow.compile()

    def debug_python_file(
        self target_file: str,
        project_path: str = ".",
        test_command: str = "python"
    ) -> Dict[str, Any]:
        """
        Complete debugging pipeline for a Python file
        
        Args:
            target_file: Python file to analyze (relative to project_path)
            project_path: Project root directory (default: current directory)
            test_command: Command to execute the file (default: python)
            
        Returns:
            Complete debugging analysis results
        """
        self.logger.info(f"Starting debugging pipeline for: {target_file}")
        
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
            "execution_logs": final_state.execution_logs,
            "metadata": final_state.metadata,
            "summary": {
                "file_executed": final_state.error_output is not None,
                "prompt_generated": final_state.analysis_prompt is not None,
                "llm_analysis_completed": final_state.llm_analysis is not None,
                "workflow_completed": True
            }
        }


def create_debugging_pipeline(llm=None) -> CompletePipelineAgent:
    """Factory function to create the debugging pipeline"""
    return CompletePipelineAgent(llm=llm)


def debug_file(
    target_file: str,
    project_path: str = ".",
    test_command: str = "python",
    llm=None
) -> Dict[str, Any]:
    """
    Convenience function to debug a Python file
    
    Args:
        target_file: Python file to debug
        project_path: Project directory
        test_command: Command to run the file
        llm: Optional LLM for analysis
        
    Returns:
        Complete debugging results
    """
    pipeline = create_debugging_pipeline(llm=llm)
    return pipeline.debug_python_file(target_file, project_path, test_command)


def debug_file_prompt_only(
    target_file: str,
    project_path: str = ".",
    test_command: str = "python"
) -> str:
    """
    Generate debugging prompt without LLM analysis
    
    Returns just the prompt for manual use with LLMs
    """
    results = debug_file(target_file, project_path, test_command, llm=None)
    return results["debugging_prompt"]


# LangChain integration functions
def create_complete_debugging_chain(llm):
    """
    Create a complete LangChain debugging chain
    
    Args:
        llm: LangChain LLM for analysis
        
    Returns:
        Runnable chain that takes file info and returns complete analysis
    """
    def run_debugging_pipeline(inputs):
        target_file = inputs["target_file"]
        project_path = inputs.get("project_path" ".")
        test_command = inputs.get("test_command", "python")
        
        pipeline = create_debugging_pipeline(llm=llm)
        results = pipeline.debug_python_file(target_file, project_path, test_command)
        
        return results
    
    return RunnableLambda(run_debugging_pipeline)


def create_prompt_only_chain():
    """
    Create a chain that only generates debugging prompts
    
    Returns:
        Runnable chain that generates prompts for manual LLM usage
    """
    def generate_prompt_only(inputs):
        target_file = inputs["target_file"]
        project_path = inputs.get("project_path", ".")
        test_command = inputs.get("test_command", "python")
        
        prompt = debug_file_prompt_only(target_file, project_path, test_command)
        
        return {"debugging_prompt": prompt}
    
    return RunnableLambda(generate_prompt_only)


def main():
    """Command line interface for the debugging pipeline"""
    parser = argparse.ArgumentParser(description="Complete Python File Debugging Pipeline")
    parser.add_argument("target_file", help="Python file to debug")
    parser.add_argument("--project-path", "-p", default=".", help="Project root directory")
    parser.add_argument("--command", "-c", default="python", help="Command to execute the file")
    parser.add_argument("--prompt-only", action="store_true", help="Generate prompt only (no LLM)")
    parser.add_argument("--llm-provider", choices=["openai", "anthropic", "none"], default="none", 
                        help="LLM provider for analysis")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="LLM model to use")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--refresh-secrets", action="store_true", help="Refresh 1Password secrets")
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Refresh secrets if requested
    if args.refresh_secrets:
        print("Refreshing 1Password secrets...")
        load_1password_secrets()
    
    # Initialize LLM if requested
    llm = None
    if not args.prompt_only and args.llm_provider != "none":
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
            print("Or use --prompt-only")
            sys.exit(1)
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            sys.exit(1)
    
    # Run the debugging pipeline
    try:
        if args.prompt_only:
            prompt = debug_file_prompt_only(args.target_file args.project_path, args.command)
            output = f"# Debugging Prompt for {args.target_file}\n\n{prompt}"
        else:
            results = debug_file(args.target_file args.project_path, args.command, llm)
            
            if results["llm_analysis"]:
                output = f"# Complete Debugging Analysis for {args.target_file}\n\n"
                output += f"## Execution Output\n```\n{results['execution_output']}\n```\n\n"
                output += f"## LLM Analysis\n{results['llm_analysis']}\n\n"
                output += f"## Execution Logs\n" + "\n".join(f"- {log}" for log in results["execution_logs"])
            else:
                output = f"# Debugging Prompt for {args.target_file}\n\n{results['debugging_prompt']}"
        
        # Output results
        if args.output:
            with open(args.output 'w') as f:
                f.write(output)
            print(f"Results written to: {args.output}")
        else:
            print("=" * 80)
            print("DEBUGGING ANALYSIS RESULTS")
            print("=" * 80)
            print(output)
        
    except Exception as e:
        print(f"Error running debugging pipeline: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
