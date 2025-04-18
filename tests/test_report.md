# Ontology Framework Test Report

## Overview
This report contains test results for the ontology framework, following the standards defined in guidance.ttl.

## Test Environment
- Environment: development
- Timeout: 300 seconds
- Report Format: markdown

## Test Categories

### Model Structure Tests
- Class definitions and hierarchy
- Property definitions with domain and range
- Individual instances validation
- SHACL pattern compliance

### Functional Tests
- Checkin process validation
- Error handling and recovery
- Git integration
- LLM client operations

### Test Steps
1. Setup - Environment preparation
2. Execution - Test case running
3. Validation - Result verification
4. Cleanup - Environment restoration

## Test Results
Test results will be appended here by the test runner.

## Test Session Summary
Session summary will be appended here by the test runner.

## Validation Rules
All tests must comply with:
- SHACL pattern syntax rules
- Model structure requirements
- Test procedure standards
- Documentation requirements

## Notes
- Test failures are documented with error details
- Each test run is timestamped
- Full stack traces are available in the test logs

## Test Run - 2025-04-16T15:14:33.168153

### full_checkin_process
- Status: PASSED
- Details: All steps completed successfully


## Test Run - 2025-04-16T15:14:34.068416

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-04-16T15:14:34.605997

### shacl_pattern_validation
- Status: PASSED
- Details: All SHACL patterns validated successfully


## Test Session Summary - 2025-04-16T15:14:37.356040

- Total tests: 17
- Passed: 16
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T15:18:14.231541

- Total tests: 176
- Passed: 175
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Run - 2025-04-16T15:19:04.616066

### full_checkin_process
- Status: PASSED
- Details: All steps completed successfully


## Test Run - 2025-04-16T15:19:05.351633

### model_structure_validation
- Status: FAILED
- Error: OntologyPatch must have patch_id
assert False
 +  where False = hasattr(OntologyPatch, 'patch_id')


## Test Run - 2025-04-16T15:19:05.433606

### shacl_pattern_validation
- Status: PASSED
- Details: All SHACL patterns validated successfully


## Test Session Summary - 2025-04-16T15:20:04.587847

- Total tests: 193
- Passed: 122
- Failed: 71
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T15:25:28.224315

- Total tests: 0
- Passed: -1
- Failed: 1
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T15:26:26.632355

- Total tests: 11
- Passed: 2
- Failed: 9
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T15:27:20.806083

- Total tests: 11
- Passed: 3
- Failed: 8
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T15:28:27.721444

- Total tests: 11
- Passed: 3
- Failed: 8
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T15:44:48.864804

- Total tests: 13
- Passed: 7
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T15:45:36.892214

- Total tests: 13
- Passed: 7
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T15:47:24.303208

- Total tests: 13
- Passed: 12
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T15:47:56.710320

- Total tests: 13
- Passed: 13
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T17:42:06.802407

- Total tests: 5
- Passed: 1
- Failed: 4
- Exit status: 3

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T20:24:39.645002

- Total tests: 5
- Passed: 2
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T20:25:04.809301

- Total tests: 5
- Passed: 2
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T20:26:29.846879

- Total tests: 5
- Passed: 2
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T20:28:39.025745

- Total tests: 6
- Passed: 3
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T20:29:46.034996

- Total tests: 6
- Passed: 4
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T20:30:31.227354

- Total tests: 6
- Passed: 4
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T20:31:28.591017

- Total tests: 6
- Passed: 3
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-16T20:31:58.441358

- Total tests: 6
- Passed: 4
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T07:55:12.437420

- Total tests: 10
- Passed: 4
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T07:56:39.334962

- Total tests: 10
- Passed: 3
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T07:58:14.994859

- Total tests: 10
- Passed: 3
- Failed: 7
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T07:59:57.376975

- Total tests: 10
- Passed: 9
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T08:01:00.461983

- Total tests: 10
- Passed: 8
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T08:02:29.118623

- Total tests: 10
- Passed: 4
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T08:37:24.211524

- Total tests: 7
- Passed: 6
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T08:37:53.168039

- Total tests: 7
- Passed: 1
- Failed: 6
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T08:39:02.990594

- Total tests: 7
- Passed: 2
- Failed: 5
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T08:39:56.239171

- Total tests: 7
- Passed: 7
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T08:44:27.497588

- Total tests: 2
- Passed: 2
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T13:21:49.759333

- Total tests: 3
- Passed: 1
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T14:06:26.743797

- Total tests: 2
- Passed: 1
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T14:06:55.599016

- Total tests: 2
- Passed: 2
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T14:11:00.322316

- Total tests: 1
- Passed: 1
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T14:11:26.185853

- Total tests: 1
- Passed: 1
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T14:41:30.724745

- Total tests: 200
- Passed: 192
- Failed: 8
- Exit status: 2

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T14:43:12.157712

- Total tests: 5
- Passed: 5
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T17:43:57.069736

- Total tests: 4
- Passed: 2
- Failed: 2
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T17:44:41.187377

- Total tests: 4
- Passed: 4
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T18:23:26.216682

- Total tests: 3
- Passed: 0
- Failed: 3
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T18:24:24.185642

- Total tests: 3
- Passed: 3
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T18:35:25.269336

- Total tests: 3
- Passed: 3
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T18:40:30.945256

- Total tests: 5
- Passed: 4
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T18:41:20.472940

- Total tests: 5
- Passed: 4
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T18:42:21.822784

- Total tests: 5
- Passed: 4
- Failed: 1
- Exit status: 1

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T18:43:11.713872

- Total tests: 5
- Passed: 5
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T19:48:06.783819

- Total tests: 5
- Passed: 5
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T19:51:31.827594

- Total tests: 5
- Passed: 5
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T19:53:57.247639

- Total tests: 5
- Passed: 5
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests


## Test Session Summary - 2025-04-17T19:55:08.264134

- Total tests: 5
- Passed: 5
- Failed: 0
- Exit status: 0

### Test Categories Summary
- Model Structure Tests: 0 tests
- SHACL Validation Tests: 0 tests
- Functional Tests: 0 tests

