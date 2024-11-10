# Ontology Framework

A flexible ontology framework designed to leverage LLMs for semantic constraint enforcement and rich domain modeling capabilities, with lossless transformations between modeling formats.

## Overview

This framework provides:

- Semantic constraint enforcement for LLM responses
- Rich domain modeling with lossless transformations
- Tiered architecture promoting reuse
- Extensible model structures
- Multi-format projections (Turtle, UML, ERD, etc.)

## Architecture Diagram

![Ontology Framework Architecture](Ontology%20Framework.svg)


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

## TODO

- [ ] [Vector database integration](https://github.com/louspringer/ontology-framework/issues/5)
- [ ] [Create LLM-generated ontology example](https://github.com/louspringer/ontology-framework/issues/4)
- [ ] [Create Elvis Porkenheimer ontology](https://github.com/louspringer/ontology-framework/issues/3)
- [ ] [Refactor artifacts into src/models layout](https://github.com/louspringer/ontology-framework/issues/2)
- [ ] [Align examples with root ontologies](https://github.com/louspringer/ontology-framework/issues/1)
- [ ] [Add CI/CD pipeline](https://github.com/louspringer/ontology-framework/issues/6)
- [ ] [Create documentation site](https://github.com/louspringer/ontology-framework/issues/7) 
- [ ] [Implement format conversion utilities](https://github.com/louspringer/ontology-framework/issues/8)
- [ ] [Add validation test suite](https://github.com/louspringer/ontology-framework/issues/9)
- [ ] [Create getting started guide](https://github.com/louspringer/ontology-framework/issues/10)


## License

MIT License - see [LICENSE](LICENSE.md "MIT license.") file for details.

## References

[^1]: Allemang, D., & Sequeda, J. (2024). Increasing the LLM Accuracy for Question Answering: Ontologies to the Rescue! [arXiv:2405.11706](https://arxiv.org/abs/2405.11706)
    
[^2]: Babaei Giglou, H., D'Souza, J., & Auer, S. (2023). LLMs4OL: Large Language Models for Ontology Learning. [ISWC 2023](https://link.springer.com/chapter/10.1007/978-3-031-47240-4_22)
