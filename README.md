# Ontology Framework

A flexible ontology framework designed to leverage LLMs for semantic constraint enforcement and rich domain modeling capabilities, with lossless transformations between modeling formats.

## Overview

This framework provides:

- Semantic constraint enforcement for LLM responses
- Rich domain modeling with lossless transformations
- Tiered architecture promoting reuse
- Extensible model structures
- Multi-format projections (Turtle, UML, ERD, etc.)

## Implementation Flow

![Implementation Flow](diagrams/implementation_flow.svg)

The implementation is organized into four main layers:
1. Infrastructure: Core repository setup and testing framework
2. Core Features: Validation, performance, and transformations
3. Advanced Features: Vector DB, collaboration, and suggestions
4. Examples: Reference ontologies and demonstrations

## Installation

> **Note:** This project is currently in early development. The Python implementation is not yet available - see the [TODO section](#todo) for planned features and progress tracking.

```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate ontology-framework
```

## Related Work

This project builds upon several recent advances in combining ontologies with LLMs:

1. **Ontology-based Query Checking** [^1]: Demonstrates using ontologies to:

   - Validate LLM-generated queries
   - Provide semantic error detection
   - Enable query repair through LLM feedback loops
   - Improve accuracy from 54% to 72% through ontological validation

2. **LLMs4OL Framework** [^2]: Provides capabilities for:

   - Term typing
   - Taxonomy discovery
   - Non-taxonomic relation extraction
   - Evaluation across multiple knowledge domains

Our framework extends these approaches by focusing specifically on semantic constraint enforcement and lossless transformations between modeling formats.

## Implementation Status

### Infrastructure Layer
- [x] GitHub workflow setup (#20)
- [ ] Repository structure refactor (#2)
- [ ] Integration testing framework (#9)

### Core Features
- [ ] Enhanced constraint validation (#7)
- [ ] Performance optimization (#8)
- [ ] Format transformations (#6)

### Advanced Features
- [ ] Vector database integration (#5)
- [ ] Collaborative development (#10)
- [ ] Vocabulary suggestions (#11)

### Examples
- [ ] Root ontology alignment (#1)
- [ ] Elvis Porkenheimer ontology (#3)
- [ ] LLM-generated example (#4)

## License

AGPL License - see [LICENSE](LICENSE "AGPL license.") file for details.

## References

[^1]: Allemang, D., & Sequeda, J. (2024). Increasing the LLM Accuracy for Question Answering: Ontologies to the Rescue! [arXiv:2405.11706](https://arxiv.org/abs/2405.11706)
    
[^2]: Babaei Giglou, H., D'Souza, J., & Auer, S. (2023). LLMs4OL: Large Language Models for Ontology Learning. [ISWC 2023](https://link.springer.com/chapter/10.1007/978-3-031-47240-4_22)
