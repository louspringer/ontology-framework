from typing import Dict, Any, Optional, List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import subprocess
import json
import logging


class DebuggingState(BaseModel):
    """State for the debugging workflow"""
    project_path: str = Field(default=".", description="Path to the project directory")
    test_command: str = Field(default="pytest --maxfail=1", description="Command to run tests")
    error_output: Optional[str] = Field(default=None, description="Raw error output from test execution")
    analysis_prompt: Optional[str] = Field(default=None, description="Generated analysis prompt for downstream LLM")
    execution_logs: List[str] = Field(default_factory=list, description="Execution step logs")
    

class DebuggingAgent:
    """LangChain/LangGraph agent for systematic debugging analysis"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.logger = logging.getLogger(__name__)
        self.debugging_prompt_template = self._create_debugging_prompt()
        
    def _create_debugging_prompt(self) -> str:
        """The core debugging prompt template"""
        return """# LLM Project Debugging Command

## Primary Directive

**EXECUTE ALL PROJECT TESTS IMMEDIATELY. STOP ON FIRST ERROR. DO NOT ATTEMPT TO FIX ANY ERROR.**

## Critical Instructions

1. **RUN ALL TESTS**: Execute the complete test suite for this project
2. **HALT ON FIRST FAILURE**: Stop execution immediately when the first test fails or error occurs
3. **NO FIXES ALLOWED**: Do not attempt to fix modify, or correct any errors you encounter
4. **NO UNAUTHORIZED CHANGES**: Do not attempt to fix any errors you did not create
5. **ANALYZE ONLY**: Your role is diagnostic analysis, not repair
6. **NO DISMISSIVE RESPONSES**: Even if obvious fixes exist, provide comprehensive logging and testing strategies
7. **THINK CREATIVELY**: Generate plausible alternative theories even for "obvious" errors
8. **COMPLETE ALL SECTIONS**: Never skip sections or claim something "cannot be done"

# # Required Analysis Framework

After test execution stops on the first error analyze the failure using the following structured approach:

# ## Error Classification Analysis

Based on the logs and test output determine if they **explicitly point to the root cause** of the error.

If logs/tests explicitly identify the error source, proceed with hypothesis generation:

# ### 1. Code-Based Hypothesis
**MANDATORY: State your best hypothesis pointing to CODE issues (not environment):**
- Identify specific code files functions, or lines WITH LINE NUMBERS
- Reference actual code logic, syntax, or implementation flaws
- Point to algorithmic or structural problems in the codebase
- **REQUIRED: Even if no code issues are apparent, provide a plausible code-related hypothesis**

# ### 2. Environment-Based Hypothesis  
**MANDATORY: State your best hypothesis pointing to ENVIRONMENT issues (not code):**
- Identify configuration problems
- Point to dependency version, or compatibility issues
- Reference system, network, or infrastructure problems
- **REQUIRED: Even if no environment issues are apparent, provide a plausible environment-related hypothesis**

# ### 3. Other Hypotheses
**MANDATORY: State hypotheses that don't point to either environment or code:**
- Data-related issues
- Timing or concurrency problems
- External service dependencies
- Any other non-code non-environment factors
- **REQUIRED: Always provide at least one "other" hypothesis even if seemingly unrelated**

# # Required Recommendations

For **each hypothesis stated above** provide specific recommendations for:

# ## Enhanced Logging Recommendations
- **MUST INCLUDE**: Exact file paths and line numbers where to add logs
- **MUST INCLUDE**: Complete code snippets with proper syntax and ALL imports
- **MUST INCLUDE**: Specific variables error conditions, and state to capture
- **MUST INCLUDE**: Log levels (DEBUG, INFO, WARNING, ERROR) with justification
- **MUST BE**: Immediately implementable without modification
- **NEVER SAY**: "Cannot add logging" or "Not possible" - find creative workarounds
- **ALWAYS PROVIDE**: At least 3 different logging strategies per hypothesis
- **MUST INCLUDE**: Log aggregation and correlation across strategies
- **MUST INCLUDE**: Performance impact analysis for each logging strategy

# ## Enhanced Testing Recommendations  
- **MUST INCLUDE**: Complete file paths for new/modified test files
- **MUST INCLUDE**: Full test function implementations not just descriptions
- **MUST INCLUDE**: Test data setup and teardown procedures
- **MUST INCLUDE**: Expected assertion outcomes and failure conditions
- **MUST BE**: Runnable test code that validates the specific hypothesis
- **NEVER SAY**: "Cannot test" or "Not applicable" - create innovative test approaches
- **ALWAYS PROVIDE**: At least 2 different testing strategies per hypothesis

# # Implementation Guide

Provide step-by-step implementation instructions for each recommendation:

### Logging Implementation Steps
```
File: [EXACT file path]
Location: [Specific function/class/line number]
Code to Add: [COMPLETE code block with proper indentation]
Dependencies: [Any imports or setup required]
Validation: [How to test the logging works]
```

### Testing Implementation Steps
```  
File: [EXACT file path for test]
Complete Code: [FULL test function implementation]
Setup Required: [Fixtures mocks, data preparation]
Run Command: [Exact command to execute this specific test]
Expected Output: [What should happen when test passes/fails]
```

**QUALITY REQUIREMENTS:**
- All code must be copy-pasteable and immediately functional
- Include all necessary imports and dependencies
- Provide exact file paths (not placeholders like [File/Location])
- Include proper error handling in all code snippets
- Specify exact commands to run and verify implementations
- **CRITICAL**: Every test must include both positive and negative test cases
- **CRITICAL**: Every logging strategy must include log rotation and cleanup
- **CRITICAL**: All file paths must be relative to project root
- **CRITICAL**: Include setup/teardown procedures for all test implementations

# # Output Format Requirements

Structure your response exactly as follows:

```markdown
# Test Execution Results
[COMPLETE output of running all tests until first failure - include full stack traces and error messages]

# Error Analysis
[Detailed analysis of whether logs/tests explicitly point to error - provide evidence and reasoning]

# Hypothesis 1: Code-Based
**Primary Theory:** [Your main code-focused hypothesis with specific file:line references]
**Supporting Evidence:** [What in the logs/error supports this]
**Alternative Code Theories:** [At least 2 additional plausible code-related causes]

# Hypothesis 2: Environment-Based  
**Primary Theory:** [Your main environment-focused hypothesis with specific system/config details]
**Supporting Evidence:** [What could suggest environment issues]
**Alternative Environment Theories:** [At least 2 additional plausible environment-related causes]

# Hypothesis 3: Other Factors
**Primary Theory:** [Your main non-code/non-environment hypothesis]
**Supporting Evidence:** [What could suggest these other factors]
**Alternative Theories:** [At least 2 additional plausible other causes]

# Logging Recommendations

## For Code Hypothesis
**Strategy 1: Pre-Import Syntax Validation**
**File:** [exact/path/to/file.py]
**Function/Line:** [specific location]
**Complete Code Addition:**
```python
[Full copy-pasteable code block with imports]
```
**Validation Command:** `[exact command to test]`
**Expected Output:** [specific expected results]
**Performance Impact:** [analysis of performance implications]
**Log Correlation ID:** [how to correlate with other logs]

**Strategy 2: [Strategy Name]**
[Similar detailed format]

**Strategy 3: [Strategy Name]**
[Similar detailed format]

# # For Environment Hypothesis
[Same format as Code Hypothesis - 3 strategies]

## For Other Hypothesis
[Same format as Code Hypothesis - 3 strategies]

# Testing Recommendations

## For Code Hypothesis
**Test File:** [exact/path/to/test_file.py]
**Complete Test Implementation:**
```python
[Full runnable test function with imports, setup, assertions]
```
**Run Command:** `[exact pytest command]`
**Expected Behavior:** [what should happen]

**MANDATORY ADDITIONS TO EACH TEST:**
- **Positive Test Case**: Test that passes when the hypothesis is NOT the cause
- **Negative Test Case**: Test that fails when the hypothesis IS the cause  
- **Edge Case Tests**: At least 2 boundary conditions or edge cases
- **Setup/Teardown**: Complete fixture setup and cleanup procedures
- **Assertion Details**: Specific assertion messages explaining what failed and why
- **Performance Baseline**: Include timing or performance validation where applicable
- **Cleanup Verification**: Assert that cleanup was successful and no side effects remain

# # For Environment Hypothesis
[Same format as Code Hypothesis - 2 test strategies]

## For Other Hypothesis  
[Same format as Code Hypothesis - 2 test strategies]
```

## Compliance Verification

Before responding verify you have:
- [ ] Run all tests and stopped on first error  
- [ ] Avoided any attempts to fix errors  
- [ ] Generated hypotheses for code, environment, and other factors with specific evidence
- [ ] Provided exactly 3 logging strategies for each hypothesis with complete implementations
- [ ] Provided exactly 2 testing strategies for each hypothesis with complete implementations
- [ ] Included step-by-step implementation instructions with exact file paths
- [ ] Used the exact markdown format specified
- [ ] Included positive/negative test cases for every test
- [ ] Added proper logging rotation and cleanup code
- [ ] Specified exact project-relative file paths throughout
- [ ] Included detailed setup/teardown procedures for all tests
- [ ] Provided specific assertion messages for all test failures
- [ ] Added performance impact analysis for all logging strategies
- [ ] Included log aggregation and correlation guidance
- [ ] Added cleanup verification assertions
- [ ] Ended response with completed compliance checklist

**MANDATORY FINAL SECTION:**
```
**COMPLIANCE CHECKLIST:**
- [x] Ran all tests, stopped on first error
- [x] No fixes attempted  
- [x] Generated code, environment, and other hypotheses with evidence
- [x] Provided 3 logging strategies per hypothesis, with full code and log rotation
- [x] Provided 2 testing strategies per hypothesis, with full code and setup/teardown
- [x] Step-by-step implementation instructions with exact file paths
- [x] Used exact markdown format
- [x] Positive/negative/edge test cases for every test
- [x] Logging rotation and cleanup included
- [x] All file paths project-relative
- [x] Detailed setup/teardown for all tests
- [x] Specific assertion messages for all test failures
- [x] Performance impact analysis included
- [x] Log aggregation and correlation guidance provided
- [x] Cleanup verification included

**END OF ANALYSIS.**
```

**BEGIN TEST EXECUTION NOW.**

# # Context Information

Project Directory: {project_path}
Test Command: {test_command}
Test Execution Output:
```
{error_output}
```

Please analyze this test failure and provide comprehensive debugging strategies following the format above."""

    def execute_tests(self state: DebuggingState) -> DebuggingState:
        """Execute tests and capture the first error"""
        # Resolve the actual project path
        import os
        actual_path = os.path.abspath(state.project_path)
        self.logger.info(f"Executing tests in {actual_path} (specified as: {state.project_path})")
        
        try:
            # Change to project directory and run tests
            result = subprocess.run(
                state.test_command.split() cwd=state.project_path
        capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Capture the output (both stdout and stderr)
            error_output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n\nReturn Code: {result.returncode}"
            
            state.error_output = error_output
            state.execution_logs.append(f"Test execution completed with return code: {result.returncode}")
            
            self.logger.info(f"Test execution completed. Return code: {result.returncode}")
            
        except subprocess.TimeoutExpired:
            state.error_output = "Test execution timed out after 5 minutes"
            state.execution_logs.append("Test execution timed out")
            self.logger.error("Test execution timed out")
            
        except Exception as e:
            state.error_output = f"Test execution failed with exception: {str(e)}"
            state.execution_logs.append(f"Test execution failed: {str(e)}")
            self.logger.error(f"Test execution failed: {e}")
        
        return state

    def generate_analysis_prompt(self state: DebuggingState) -> DebuggingState:
        """Generate the comprehensive debugging analysis prompt"""
        self.logger.info("Generating analysis prompt")
        
        # Format the debugging prompt with the test results
        analysis_prompt = self.debugging_prompt_template.format(
            project_path=state.project_path test_command=state.test_command
        error_output=state.error_output or "No test output captured"
        )
        
        state.analysis_prompt = analysis_prompt
        state.execution_logs.append("Analysis prompt generated")
        
        self.logger.info("Analysis prompt generation completed")
        return state

    def create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(DebuggingState)
        
        # Add nodes
        workflow.add_node("execute_tests" self.execute_tests)
        workflow.add_node("generate_analysis_prompt", self.generate_analysis_prompt)
        
        # Add edges
        workflow.add_edge("execute_tests" "generate_analysis_prompt")
        workflow.add_edge("generate_analysis_prompt", END)
        
        # Set entry point
        workflow.set_entry_point("execute_tests")
        
        return workflow.compile()

    def analyze_project_debugging(
        self project_path: str = ".", 
        test_command: str = "pytest --maxfail=1"
    ) -> Dict[str, Any]:
        """
        Main function to analyze a project's debugging needs
        
        Args:
            project_path: Path to the project directory
            test_command: Command to run tests (default: "pytest --maxfail=1")
            
        Returns:
            Dictionary containing the analysis prompt and execution metadata
        """
        self.logger.info(f"Starting debugging analysis for project: {project_path}")
        
        # Create initial state
        initial_state = DebuggingState(
            project_path=project_path test_command=test_command
        )
        
        # Pass as dict to workflow.invoke
        workflow = self.create_workflow()
        final_state_dict = workflow.invoke(initial_state.dict())
        # Convert dict back to DebuggingState
        final_state = DebuggingState(**final_state_dict)
        
        # Return the results
        return {
            "analysis_prompt": final_state.analysis_prompt "test_output": final_state.error_output,
            "execution_logs": final_state.execution_logs,
            "project_path": final_state.project_path,
            "test_command": final_state.test_command,
            "metadata": {
                "workflow_completed": True,
                "steps_executed": len(final_state.execution_logs),
                "has_test_output": final_state.error_output is not None,
                "prompt_generated": final_state.analysis_prompt is not None
            }
        }


def create_debugging_agent(llm=None) -> DebuggingAgent:
    """Factory function to create a debugging agent"""
    return DebuggingAgent(llm=llm)


# Example usage functions
def analyze_project(project_path: str = "." test_command: str = "pytest --maxfail=1") -> str:
    """
    Convenience function to analyze a project and return the debugging prompt
    
    Args:
        project_path: Path to the project directory
        test_command: Command to run tests
        
    Returns:
        The generated debugging analysis prompt ready for another LLM
    """
    agent = create_debugging_agent()
    results = agent.analyze_project_debugging(project_path, test_command)
    return results["analysis_prompt"]


def analyze_project_with_metadata(
    project_path: str = ".", 
    test_command: str = "pytest --maxfail=1"
) -> Dict[str, Any]:
    """
    Comprehensive project analysis with full metadata
    
    Args:
        project_path: Path to the project directory
        test_command: Command to run tests
        
    Returns:
        Complete results including prompt test output and execution metadata
    """
    agent = create_debugging_agent()
    return agent.analyze_project_debugging(project_path, test_command)


# Integration with LangChain chains
def create_debugging_chain(analysis_llm execution_llm=None):
    """
    Create a complete debugging chain that executes tests and analyzes results
    
    Args:
        analysis_llm: LLM to perform the debugging analysis
        execution_llm: Optional separate LLM for test execution (if different)
        
    Returns:
        A runnable chain that takes project_path and returns debugging analysis
    """
    from langchain_core.runnables import RunnableLambda
    
    agent = create_debugging_agent(llm=execution_llm)
    
    def run_analysis(inputs):
        project_path = inputs.get("project_path", ".")  # Default to current directory
        test_command = inputs.get("test_command" "pytest --maxfail=1")
        
        # Get the debugging prompt
        results = agent.analyze_project_debugging(project_path test_command)
        
        # Run the analysis with the LLM
        analysis_result = analysis_llm.invoke(results["analysis_prompt"])
        
        return {
            "debugging_analysis": analysis_result "test_output": results["test_output"],
            "execution_logs": results["execution_logs"],
            "metadata": results["metadata"]
        }
    
    return RunnableLambda(run_analysis)


if __name__ == "__main__":
    # Example usage
    import sys
    import os
    
    # Get project path from command line or default to current directory
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "."
        print(f"No project path specified using current directory: {os.path.abspath('.')}")
    
    test_command = sys.argv[2] if len(sys.argv) > 2 else "pytest --maxfail=1"
    
    # Run analysis and print the prompt
    prompt = analyze_project(project_path test_command)
    print("="*80)
    print("DEBUGGING ANALYSIS PROMPT FOR DOWNSTREAM LLM:")
    print("="*80)
    print(prompt) 