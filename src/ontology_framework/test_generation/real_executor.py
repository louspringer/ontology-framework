"""Real test execution using subprocess - macOS/Zsh compatible"""

import asyncio
import subprocess
import tempfile
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from .data_models import TestCase, TestResult, TestStatus


class RealTestExecutor:
    """Execute actual pytest/unittest tests using subprocess - macOS compatible"""
    
    def __init__(self):
        self.temp_dir = None
    
    async def execute_real_test(self, test_case: TestCase) -> TestResult:
        """Execute a real test case using subprocess"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create temporary test file
            test_file_path = await self._create_test_file(test_case)
            
            # Execute test using subprocess (macOS/Zsh compatible)
            result = await self._run_pytest(test_file_path)
            
            duration = asyncio.get_event_loop().time() - start_time
            
            return TestResult(
                test_name=test_case.name,
                status=TestStatus.PASSED if result["success"] else TestStatus.FAILED,
                duration=duration,
                error_message=result.get("error"),
                output=result.get("output")
            )
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return TestResult(
                test_name=test_case.name,
                status=TestStatus.ERROR,
                duration=duration,
                error_message=str(e)
            )
        finally:
            # Cleanup temp file
            if hasattr(self, '_current_test_file') and self._current_test_file:
                try:
                    os.unlink(self._current_test_file)
                except:
                    pass
    
    async def _create_test_file(self, test_case: TestCase) -> str:
        """Create a temporary test file for the test case"""
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix="ontology_tests_")
        
        # Create test file content
        test_content = self._generate_test_file_content(test_case)
        
        # Write to temporary file
        test_file = Path(self.temp_dir) / f"{test_case.name}.py"
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        self._current_test_file = str(test_file)
        return str(test_file)
    
    def _generate_test_file_content(self, test_case: TestCase) -> str:
        """Generate complete test file content"""
        imports = "\n".join(test_case.imports) if test_case.imports else ""
        
        # Basic test file template
        content = f"""# Generated test file for {test_case.name}
{imports}
import pytest

def {test_case.name}():
    \"\"\"
    {test_case.description}
    \"\"\"
{self._indent_code(test_case.test_code, 4)}

if __name__ == "__main__":
    {test_case.name}()
"""
        return content
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code by specified number of spaces"""
        indent = " " * spaces
        lines = code.strip().split('\n')
        return '\n'.join(indent + line for line in lines)
    
    async def _run_pytest(self, test_file_path: str) -> Dict[str, Any]:
        """Run pytest using pipes and tees for better shell compatibility"""
        try:
            # Create temporary files for output capture
            stdout_file = f"/tmp/pytest_stdout_{os.getpid()}.log"
            stderr_file = f"/tmp/pytest_stderr_{os.getpid()}.log"
            
            # Use shell=True with pipes and tees for better compatibility
            # This approach handles shell parsing issues better on macOS/Zsh
            cmd = f"""
            /usr/bin/python3 -m pytest "{test_file_path}" -v --tb=short 2>&1 | tee "{stdout_file}"
            echo $? > /tmp/pytest_exit_code_{os.getpid()}
            """
            
            # Set up environment
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path.cwd())
            
            # Execute with shell=True and pipe handling
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(Path.cwd())
            )
            
            stdout, stderr = await process.communicate()
            
            # Read output from tee files for more reliable capture
            output = ""
            error = ""
            exit_code = process.returncode
            
            try:
                if Path(stdout_file).exists():
                    with open(stdout_file, 'r') as f:
                        output = f.read()
                    os.unlink(stdout_file)
                
                # Check actual exit code from pytest
                exit_code_file = f"/tmp/pytest_exit_code_{os.getpid()}"
                if Path(exit_code_file).exists():
                    with open(exit_code_file, 'r') as f:
                        exit_code = int(f.read().strip())
                    os.unlink(exit_code_file)
                    
            except Exception as cleanup_error:
                # If file operations fail, use subprocess output
                output = stdout.decode('utf-8') if stdout else ""
                error = stderr.decode('utf-8') if stderr else ""
            
            success = exit_code == 0
            
            return {
                "success": success,
                "output": output,
                "error": error if not success else None,
                "return_code": exit_code
            }
            
        except Exception as e:
            # Fallback to direct execution
            return await self._run_python_directly(test_file_path)
    
    async def _run_python_directly(self, test_file_path: str) -> Dict[str, Any]:
        """Fallback: run test file directly with python3 using pipes"""
        try:
            # Use pipes and tees for better output capture
            stdout_file = f"/tmp/python_stdout_{os.getpid()}.log"
            
            # Shell command with pipe and tee for reliable output capture
            cmd = f"""
            /usr/bin/python3 "{test_file_path}" 2>&1 | tee "{stdout_file}"
            echo $? > /tmp/python_exit_code_{os.getpid()}
            """
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(Path.cwd())
            )
            
            stdout, stderr = await process.communicate()
            
            # Read from tee file for more reliable output
            output = ""
            exit_code = process.returncode
            
            try:
                if Path(stdout_file).exists():
                    with open(stdout_file, 'r') as f:
                        output = f.read()
                    os.unlink(stdout_file)
                
                exit_code_file = f"/tmp/python_exit_code_{os.getpid()}"
                if Path(exit_code_file).exists():
                    with open(exit_code_file, 'r') as f:
                        exit_code = int(f.read().strip())
                    os.unlink(exit_code_file)
                    
            except Exception:
                # Fallback to subprocess output
                output = stdout.decode('utf-8') if stdout else ""
            
            success = exit_code == 0
            error = stderr.decode('utf-8') if stderr and not success else None
            
            return {
                "success": success,
                "output": output,
                "error": error,
                "return_code": exit_code
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Direct Python execution failed: {str(e)}",
                "return_code": -1
            }
    
    def cleanup(self):
        """Clean up temporary files and directories"""
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass  # Best effort cleanup
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()