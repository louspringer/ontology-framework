# Testing & Observability Task: Ontology Framework Debugging Prompt

## Task Overview
You are tasked with systematically improving the observability and testing infrastructure of the Ontology Framework project. Your primary goal is to establish clear, reliable test execution and logging that reveals the actual state of the system BEFORE making any functional changes.

## Core Principle: **Observe First, Fix Second**
- NO functional changes to application code until tests and logs clearly reveal what's broken
- Tests must provide clear, actionable error messages
- Logs must be comprehensive enough to trace issues to their root cause
- Every fix must be validated by tests running cleanly

## Execution Strategy

### Phase 1: Establish Baseline Test Execution
```bash
pytest -v tests/ -x
```

**Your iterative process:**
```
UNTIL no test errors:
    1. Fix logs and tests to reveal error root cause
    2. Fix the revealed error (not symptoms)
    3. Re-run tests
    REPEAT
```

### Phase 2: Systematic Test Analysis

For EACH failing test, follow this sequence:

#### A. Enhance Test Observability
1. **Improve Test Logging**:
   - Add debug logging to show test setup state
   - Log all inputs, expected outputs, and actual outputs
   - Add timestamps and execution context
   - Include environment state (Python version, dependencies, etc.)

2. **Enhance Error Messages**:
   - Replace generic assertions with descriptive ones
   - Include context about what the test was trying to validate  
   - Show the path taken through the code
   - Display relevant configuration values

3. **Add Test Fixtures Debugging**:
   - Log fixture creation and teardown
   - Validate fixture state before test execution
   - Check for fixture isolation issues

#### B. Investigate Root Causes
1. **Trace Execution Path**:
   - Add logging at function entry/exit points
   - Log parameter values and return values
   - Identify where execution diverges from expected path

2. **Check Dependencies**:
   - Verify all required packages are installed with correct versions
   - Check for missing system dependencies
   - Validate configuration files and environment variables

3. **Analyze Import Issues**:
   - Check for circular imports
   - Verify module structure and __init__.py files
   - Test imports in isolation

#### C. Fix Revealed Issues
Only after the above steps clearly reveal the root cause:
1. Make minimal, targeted fixes
2. Run the specific failing test to verify the fix
3. Run the full test suite to check for regressions
4. Document what was fixed and why

### Phase 3: Test Infrastructure Improvements

#### Required Enhancements:
1. **Logging Configuration**:
   ```python
   # Add to conftest.py or test setup
   import logging
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('test_debug.log'),
           logging.StreamHandler()
       ]
   )
   ```

2. **Environment Validation**:
   - Add tests that verify the test environment is properly configured
   - Check for required files, directories, and permissions
   - Validate database connections and external dependencies

3. **Test Data Management**:
   - Ensure test data is properly isolated
   - Add cleanup procedures for test artifacts
   - Validate test data integrity

4. **Error Categorization**:
   - Classify errors as: Configuration, Import, Logic, Data, or Infrastructure
   - Create specific handling for each category
   - Add metadata to test failures for better analysis

### Phase 4: Validation and Documentation

1. **Clean Test Run**:
   ```bash
   pytest -v tests/ --tb=long --capture=no
   ```
   - All tests must pass
   - No warnings or deprecation messages
   - Clean log output

2. **Documentation Updates**:
   - Document test execution requirements
   - Update README with testing procedures  
   - Create troubleshooting guide for common issues

## Specific Areas of Focus

### Priority 1: Core Framework Tests
- Test the ontology loading and validation pipeline
- Verify SHACL validation functionality
- Check prefix management and namespace handling

### Priority 2: Integration Tests  
- Database connectivity (Oracle RDF, GraphDB)
- MCP integration components
- Azure deployment configuration

### Priority 3: Module-Specific Tests
- Spore validation system
- Semantic difference analysis
- Error handling and recovery

## Success Criteria

### Must Achieve:
1. **Zero Test Failures**: `pytest -v tests/ -x` runs completely clean
2. **Clear Error Messages**: Any future test failures provide actionable debugging information
3. **Comprehensive Logging**: Full execution trace available for debugging
4. **Reproducible Results**: Tests pass consistently across multiple runs
5. **Clean Environment**: No test pollution or interference between tests

### Quality Gates:
- [ ] All imports resolve successfully
- [ ] All fixtures initialize properly  
- [ ] All database connections can be established (or gracefully skipped)
- [ ] All configuration files are valid
- [ ] All test data is accessible and valid
- [ ] No hanging processes or unclosed resources

## Tools and Commands

### Essential Commands:
```bash
# Basic test run with stop on first failure
pytest -v tests/ -x

# Detailed output with full tracebacks
pytest -v tests/ --tb=long --capture=no

# Run with coverage to identify untested code
pytest -v tests/ --cov=src --cov-report=term-missing

# Run specific test categories
pytest -v tests/unit/ -x
pytest -v tests/integration/ -x  
pytest -v tests/validation/ -x
```

### Debugging Commands:
```bash
# Check Python environment
python -c "import sys; print(sys.path)"
pip list | grep -E "(rdflib|pyshacl|oracledb)"

# Validate configuration
python -c "from ontology_framework import __init__; print('Imports OK')"
```

## Constraints and Guidelines

### DO NOT:
- Change application logic until tests clearly show what's broken
- Skip failing tests without understanding why they fail
- Make assumptions about what's wrong without evidence
- Fix symptoms instead of root causes

### DO:
- Add extensive logging to understand execution flow
- Enhance test assertions to be more descriptive
- Validate assumptions with additional tests
- Document every fix with reasoning
- Run tests after every change

### Communication:
- Report progress after each test is fixed
- Explain what was discovered and how it was resolved
- Highlight any systemic issues that need broader attention
- Recommend improvements to prevent similar issues

## Expected Outcome

At the end of this task, the project should have:
1. A completely clean test suite that passes without errors
2. Comprehensive logging that enables rapid debugging of future issues
3. Clear test documentation and execution procedures
4. Identified and resolved root causes of current test failures
5. A robust foundation for making functional improvements with confidence

Remember: **The goal is not just to make tests pass, but to create a reliable testing and observability foundation that will support the project's continued development.**