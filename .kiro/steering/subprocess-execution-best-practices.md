---
inclusion: always
---

# Subprocess Execution Best Practices for LLMs

## Core Principle

**"Use pipes and tees to handle shell parsing issues and subprocess execution oddities, especially on macOS with Zsh."**

## The Problem

LLMs often struggle with subprocess execution due to:
- Shell parsing differences between bash/zsh/fish
- Output buffering and capture issues
- Exit code handling inconsistencies
- Path resolution problems
- Environment variable propagation

## The Solution: Pipes and Tees Pattern

### Why Pipes and Tees Work Better

1. **Reliable Output Capture**: `tee` writes to both stdout and a file simultaneously
2. **Shell Parsing Isolation**: Reduces complex quoting and escaping issues
3. **Exit Code Preservation**: Explicit exit code capture via separate file
4. **Buffer Management**: `tee` handles output buffering more predictably
5. **Cross-Shell Compatibility**: Works consistently across bash, zsh, fish

### Implementation Pattern

```python
# ❌ PROBLEMATIC: Direct subprocess with complex arguments
cmd = ["/usr/bin/python3", "-m", "pytest", test_file, "-v", "--tb=short"]
process = await asyncio.create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)

# ✅ BETTER: Use pipes and tees for reliable execution
stdout_file = f"/tmp/output_{os.getpid()}.log"
exit_code_file = f"/tmp/exit_{os.getpid()}.log"

cmd = f'''
/usr/bin/python3 -m pytest "{test_file}" -v --tb=short 2>&1 | tee "{stdout_file}"
echo $? > "{exit_code_file}"
'''

process = await asyncio.create_subprocess_shell(
    cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)

await process.communicate()

# Read results from tee files for reliable capture
with open(stdout_file, 'r') as f:
    output = f.read()
with open(exit_code_file, 'r') as f:
    exit_code = int(f.read().strip())
```

### macOS/Zsh Specific Considerations

#### Path Resolution
```bash
# ✅ Use explicit paths to avoid PATH issues
/usr/bin/python3 instead of python3
/bin/bash instead of bash
```

#### Quoting and Escaping
```bash
# ✅ Use double quotes for file paths with spaces
"/path/to/file with spaces.py"

# ✅ Use tee to avoid complex argument passing
command 2>&1 | tee "/tmp/output.log"
```

#### Environment Variables
```python
# ✅ Explicitly set environment for subprocess
env = os.environ.copy()
env["PYTHONPATH"] = str(Path.cwd())
env["PATH"] = "/usr/bin:/bin:/usr/local/bin"
```

## Complete Implementation Template

```python
async def execute_with_pipes_and_tees(command: str, args: list = None) -> dict:
    """Execute command using pipes and tees for reliable output capture."""
    
    # Create temporary files for output capture
    pid = os.getpid()
    stdout_file = f"/tmp/cmd_stdout_{pid}.log"
    stderr_file = f"/tmp/cmd_stderr_{pid}.log" 
    exit_code_file = f"/tmp/cmd_exit_{pid}.log"
    
    try:
        # Build command with pipes and tees
        if args:
            full_command = f'{command} {" ".join(args)}'
        else:
            full_command = command
            
        shell_cmd = f'''
        {full_command} 2> >(tee "{stderr_file}" >&2) | tee "{stdout_file}"
        echo $? > "{exit_code_file}"
        '''
        
        # Execute with proper environment
        env = os.environ.copy()
        env["PATH"] = "/usr/bin:/bin:/usr/local/bin"
        
        process = await asyncio.create_subprocess_shell(
            shell_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        await process.communicate()
        
        # Read results from tee files
        stdout = ""
        stderr = ""
        exit_code = 1
        
        if Path(stdout_file).exists():
            with open(stdout_file, 'r') as f:
                stdout = f.read()
            os.unlink(stdout_file)
            
        if Path(stderr_file).exists():
            with open(stderr_file, 'r') as f:
                stderr = f.read()
            os.unlink(stderr_file)
            
        if Path(exit_code_file).exists():
            with open(exit_code_file, 'r') as f:
                exit_code = int(f.read().strip())
            os.unlink(exit_code_file)
        
        return {
            "success": exit_code == 0,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code
        }
        
    except Exception as e:
        # Cleanup temp files on error
        for temp_file in [stdout_file, stderr_file, exit_code_file]:
            try:
                if Path(temp_file).exists():
                    os.unlink(temp_file)
            except:
                pass
        
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1
        }
```

## Common Pitfalls to Avoid

### ❌ Don't Do This
```python
# Complex argument arrays with shell metacharacters
cmd = ["python3", "-c", "print('hello world')", ">", "output.txt"]

# Direct string concatenation without proper escaping
cmd = f"python3 {script_path} --arg={user_input}"

# Relying on subprocess PIPE for large outputs
process = subprocess.run(cmd, capture_output=True, text=True)
```

### ✅ Do This Instead
```python
# Use pipes and tees for reliable execution
cmd = f'''
python3 -c "print('hello world')" 2>&1 | tee output.txt
echo $? > exit_code.txt
'''

# Proper escaping with shell execution
cmd = f'python3 "{script_path}" --arg="{user_input}" 2>&1 | tee output.log'

# Use tee files for large outputs instead of PIPE
process = await asyncio.create_subprocess_shell(cmd)
```

## Platform-Specific Notes

### macOS with Zsh
- Default shell changed from bash to zsh in macOS Catalina+
- Different globbing and expansion behavior
- Use explicit `/bin/bash` if bash-specific features needed
- `tee` behavior is consistent across shells

### Linux with Various Shells
- Most distributions use bash by default
- `tee` available on all POSIX systems
- Watch for different `echo` implementations (`echo -e` vs `printf`)

### Windows Considerations
- Use `cmd.exe` or PowerShell explicitly
- Different path separators and quoting rules
- Consider using `subprocess.run` with `shell=True` on Windows

## Benefits for LLMs

1. **Reduced Complexity**: Less shell-specific code to generate
2. **Better Reliability**: Fewer subprocess execution failures
3. **Consistent Patterns**: Same approach works across platforms
4. **Easier Debugging**: Output captured in files for inspection
5. **Graceful Degradation**: Fallback strategies when pipes fail

## Implementation Checklist

- [ ] Use `tee` for output capture instead of subprocess PIPE
- [ ] Capture exit codes explicitly in separate files
- [ ] Use `shell=True` with proper command construction
- [ ] Set explicit environment variables
- [ ] Use absolute paths for executables
- [ ] Implement cleanup for temporary files
- [ ] Add error handling for file operations
- [ ] Test on target platform (macOS/Zsh, Linux/bash, etc.)

---

*This pattern significantly improves subprocess execution reliability for LLMs working with shell commands across different platforms and shells.*