from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PromptManagerReadmeGenerator:
    def __init__(self):
        self.src_dir = Path(__file__).parent
        self.project_root = self.src_dir.parent
        logger.debug(f"Project root: {self.project_root}")

    def get_project_structure(self):
        """Analyze project structure"""
        structure = {}
        
        # Get Python files in src
        structure['src_files'] = list(self.src_dir.glob('*.py'))
        logger.debug(f"Found source files: {structure['src_files']}")
        
        # Get config files
        structure['config_files'] = [
            self.project_root / 'docker-compose.yml',
            self.project_root / 'setup.sh',
            self.project_root / 'requirements.txt'
        ]
        
        return structure

    def generate_readme(self):
        """Generate README content based on project analysis"""
        structure = self.get_project_structure()
        
        content = [
            "# Prompt Manager",
            "\nA tool for managing and versioning LLM prompts with database storage and Docker deployment.\n",
            
            "## Features\n",
            "- Version control for prompts",
            "- Docker containerization",
            "- PostgreSQL storage backend",
            "- CLI interface",
            "- Ontology validation support\n",
            
            "## Project Structure\n",
            "```",
            "prompt-manager/",
            "├── src/",
        ]
        
        # Add source files
        for src_file in structure['src_files']:
            content.append(f"│   ├── {src_file.name}")
        
        # Add config files
        for config in structure['config_files']:
            if config.exists():
                content.append(f"├── {config.name}")
        
        content.extend([
            "```\n",
            "## Installation\n",
            "```bash",
            "./setup.sh",
            "```\n",
            "## Usage\n",
            "```bash",
            "# Add a new prompt",
            "python -m src.prompt_cli add <name> <file> --category <category> --tags <tag1> <tag2>",
            "",
            "# List prompts",
            "python -m src.prompt_cli list",
            "```\n",
            "## Development\n",
            "- Uses conda environment 'ontology-framework'",
            "- Docker and PostgreSQL required",
            "- See docker-compose.yml for configuration"
        ])
        
        return "\n".join(content)

def main():
    try:
        generator = PromptManagerReadmeGenerator()
        readme_content = generator.generate_readme()
        
        # Write to prompt-manager/README.md instead of project root
        readme_path = generator.project_root / "README.md"
        with open(readme_path, "w") as f:
            f.write(readme_content)
            
        logger.debug(f"Generated README at {readme_path}")
    except Exception as e:
        logger.error(f"Failed to generate README: {e}")
        raise

if __name__ == "__main__":
    main() 