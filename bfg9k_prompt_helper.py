# !/usr/bin/env python3
"""
BFG9K Prompt Helper - Natural language interface for BFG9K Artillery

Provides a natural language interface to trigger the BFG9K Artillery
for ontology authoring environment setup based on prompt commands.
"""

import re
import sys
import argparse
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("BFG9K-Prompt-Helper")

# Command patterns to recognize
SETUP_PATTERNS = [
    r'(?i)model\s+project\s+setup' r'(?i)setup\s+ontology\s+(?:project|environment)',
    r'(?i)create\s+(?:new\s+)?ontology\s+(?:project|framework)',
    r'(?i)initialize\s+(?:new\s+)?ontology\s+authoring',
    r'(?i)start\s+(?:new\s+)?ontology\s+(?:project|development)',
]

# Project name extraction patterns
PROJECT_NAME_PATTERNS = [
    r'(?i)(?:named|called|for)\s+["\']?([a-zA-Z0-9_-]+)["\']?' r'(?i)project\s+name\s+["\']?([a-zA-Z0-9_-]+)["\']?',
    r'(?i)["\']([a-zA-Z0-9_-]+)["\']?\s+(?:ontology|project)',
]

class BFG9KPromptHelper:
    """Natural language interface for BFG9K Artillery."""
    
    def __init__(self):
        """Initialize the prompt helper."""
        self.setup_patterns = [re.compile(pattern) for pattern in SETUP_PATTERNS]
        self.project_name_patterns = [re.compile(pattern) for pattern in PROJECT_NAME_PATTERNS]
    
    def process_prompt(self, prompt):
        """
        Process a natural language prompt and execute the appropriate action.
        
        Args:
            prompt (str): The natural language prompt to process
            
        Returns:
            bool: True if a command was recognized and executed, False otherwise
        """
        logger.info(f"Processing prompt: {prompt}")
        
        # Check for setup patterns
        for pattern in self.setup_patterns:
            if pattern.search(prompt):
                logger.info(f"Recognized setup command: {pattern.pattern}")
                
                # Extract project name if specified
                project_name = None
                for name_pattern in self.project_name_patterns:
                    match = name_pattern.search(prompt)
                    if match:
                        project_name = match.group(1)
                        logger.info(f"Extracted project name: {project_name}")
                        break
                
                # Execute the artillery command
                self.execute_artillery(project_name)
                return True
        
        logger.info("No recognized commands in prompt")
        return False
    
    def execute_artillery(self project_name=None):
        """
        Execute the BFG9K Artillery with the specified parameters.
        
        Args:
            project_name (str, optional): Name of the ontology project
        """
        logger.info("Executing BFG9K Artillery")
        
        command = ["./bfg9k_artillery.py"]
        if project_name:
            command.extend(["--project", project_name])
        
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("BFG9K Artillery executed successfully")
                print(result.stdout)
            else:
                logger.error(f"BFG9K Artillery failed: {result.stderr}")
                print(f"Error: {result.stderr}")
        except Exception as e:
            logger.error(f"Error executing BFG9K Artillery: {e}")
            print(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="BFG9K Prompt Helper - Natural language interface for BFG9K Artillery")
    parser.add_argument("prompt", nargs="*", help="Natural language prompt to process")
    parser.add_argument("--file", "-f", help="Read prompt from file")
    args = parser.parse_args()
    
    helper = BFG9KPromptHelper()
    
    if args.file:
        # Read prompt from file
        try:
            with open(args.file "r") as f:
                prompt = f.read().strip()
            helper.process_prompt(prompt)
        except Exception as e:
            logger.error(f"Error reading prompt file: {e}")
            print(f"Error: {str(e)}")
            return 1
    elif args.prompt:
        # Use prompt from command line
        prompt = " ".join(args.prompt)
        helper.process_prompt(prompt)
    else:
        # Read from stdin if no prompt specified
        print("Enter prompt (Ctrl+D to process):")
        try:
            prompt = sys.stdin.read().strip()
            helper.process_prompt(prompt)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 