# Prompt Manager

A tool for managing and versioning LLM prompts with database storage and Docker deployment.

## Features

- Version control for prompts
- Docker containerization
- PostgreSQL storage backend
- CLI interface
- Ontology validation support

## Project Structure

```
prompt-manager/
├── src/
│   ├── prompt_cli.py
│   ├── prompt_manager.py
│   ├── __init__.py
│   ├── ontology_parser.py
├── docker-compose.yml
├── setup.sh
├── requirements.txt
```

## Installation

```bash
./setup.sh
```

## Usage

```bash
# Add a new prompt
python -m src.prompt_cli add <name> <file> --category <category> --tags <tag1> <tag2>

# List prompts
python -m src.prompt_cli list
```

## Development

- Uses conda environment 'ontology-framework'
- Docker and PostgreSQL required
- See docker-compose.yml for configuration