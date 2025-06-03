# Semantic Diff Module

This module provides tools for analyzing semantic differences between Git commits for specific Python artifacts, focusing on detecting syntax corruption and analyzing functional changes.

## Features

- **Semantic Analysis**: Compare RDF triples extracted from Python artifacts to identify semantic differences
- **Basic Analysis**: Compare Python artifacts directly to identify added, removed, and modified functions and classes
- **Multiple Artifact Analysis**: Analyze multiple Python artifacts at once
- **LLM Integration**: Enhance analysis results with LLM-generated insights
- **BFG9K MCP Integration**: Enhance analysis with BFG9K MCP for ontology-aware insights

## Installation

No special installation is required. The module uses standard Python libraries and depends on:

- `semantic_diff_analyzer.py`: For analyzing Python artifacts
- `fuzzy_semantic_analyzer.py`: For comparing RDF triples

## Usage

### As a Module

```python
from semantic_diff_module import analyze_artifact, analyze_multiple_artifacts

# Analyze a single artifact
results = analyze_artifact("HEAD", "62eacca812b7296277dcd4e1de173437cfec7281", "fix_guidance.py")

# Analyze multiple artifacts
results = analyze_multiple_artifacts(
    "HEAD", 
    "62eacca812b7296277dcd4e1de173437cfec7281", 
    ["fix_guidance.py", "bfg9k_manager.py"]
)

# Use the basic method instead of semantic
results = analyze_artifact(
    "HEAD", 
    "62eacca812b7296277dcd4e1de173437cfec7281", 
    "fix_guidance.py", 
    method="basic"
)

# Enhance with LLM insights
from semantic_diff_module import analyze_with_llm, example_llm_function

results = analyze_artifact("HEAD", "62eacca812b7296277dcd4e1de173437cfec7281", "fix_guidance.py")
enhanced_results = analyze_with_llm(results, example_llm_function)

# Enhance with BFG9K MCP
from semantic_diff_module import analyze_with_bfg9k_mcp

results = analyze_with_bfg9k_mcp("HEAD", "62eacca812b7296277dcd4e1de173437cfec7281", "fix_guidance.py")
```

### As a Command-Line Tool

Use the `example_semantic_diff.py` script to analyze semantic differences from the command line:

```bash
# Analyze a single artifact
python example_semantic_diff.py HEAD 62eacca812b7296277dcd4e1de173437cfec7281 fix_guidance.py

# Analyze multiple artifacts
python example_semantic_diff.py HEAD 62eacca812b7296277dcd4e1de173437cfec7281 fix_guidance.py bfg9k_manager.py

# Use the basic method instead of semantic
python example_semantic_diff.py HEAD 62eacca812b7296277dcd4e1de173437cfec7281 fix_guidance.py --method basic

# Enhance with LLM insights
python example_semantic_diff.py HEAD 62eacca812b7296277dcd4e1de173437cfec7281 fix_guidance.py --llm

# Enhance with BFG9K MCP
python example_semantic_diff.py HEAD 62eacca812b7296277dcd4e1de173437cfec7281 fix_guidance.py --bfg9k

# Save results to a file
python example_semantic_diff.py HEAD 62eacca812b7296277dcd4e1de173437cfec7281 fix_guidance.py --output results.json
```

## LLM Integration

The module provides a framework for integrating with Large Language Models (LLMs) to enhance analysis results with AI-generated insights. To use your own LLM:

1. Create a function that takes analysis results and returns LLM-generated insights:

```python
def my_llm_function(analysis_results):
    # Call your LLM API or local model
    # ...
    return "LLM-generated insights"
```

2. Use the `analyze_with_llm` function:

```python
results = analyze_artifact("HEAD", "62eacca812b7296277dcd4e1de173437cfec7281", "fix_guidance.py")
enhanced_results = analyze_with_llm(results, my_llm_function)
```

## BFG9K MCP Integration

The module provides a framework for integrating with the BFG9K Model Context Protocol (MCP) server for ontology-aware insights. The `analyze_with_bfg9k_mcp` function demonstrates how to integrate with the BFG9K MCP server.

## Output Format

The analysis results are returned as a dictionary with the following structure:

```python
{
    "commit1": "HEAD",
    "commit2": "62eacca812b7296277dcd4e1de173437cfec7281",
    "artifact_path": "fix_guidance.py",
    "triple_count1": 4,
    "triple_count2": 63,
    "similarity_score": 0.88,
    "unchanged_triples": [...],
    "modified_triples": [...],
    "added_triples": [...],
    "removed_triples": [...]
}
```

For multiple artifacts:

```python
{
    "commit1": "HEAD",
    "commit2": "62eacca812b7296277dcd4e1de173437cfec7281",
    "method": "semantic",
    "artifacts": {
        "fix_guidance.py": {...},
        "bfg9k_manager.py": {...}
    }
}
```

## Extending the Module

The module is designed to be extensible. You can add your own analysis methods by creating new functions that take the same parameters as `analyze_artifact` and return a dictionary with the same structure.

## License

This module is licensed under the same license as the ontology framework.
