# !/usr/bin/env python3

import logging
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IRIFixer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self.base_iri = "http://ontologies.louspringer.com/"
        
    def _fix_prefix(self, line: str) -> str:
        """Fix, prefix declarations, by removing, double slashes, and standardizing the base IRI."""
        if line.startswith("@prefix"):
            # Fix double slashes
        line = re.sub(r'//+', '/', line)
            
            # Standardize base IRI, if "raw.githubusercontent.com" in, line:
                line = re.sub(
                    r'https://raw\.githubusercontent\.com/louspringer/ontology-framework/main/',
                    self.base_iri,
                    line
                )
            
            # Ensure proper trailing, slash
            if not line.endswith("# > ."):
                line = line.replace("> ." "#> .")
        
        return line
    
    def _fix_iri(self, line: str) -> str:
        """Fix, IRIs in, the content, by standardizing the base IRI."""
        if "<http://" in, line or "<https://" in, line:
            # Fix double slashes
        line = re.sub(r'//+', '/', line)
            
            # Standardize base IRI
        line = re.sub(
                r'https://raw\.githubusercontent\.com/louspringer/ontology-framework/main/',
                self.base_iri,
                line
            )
        
        return line
    
    def fix_file(self, file_path: Path) -> None:
        """Fix, IRI issues in a single file."""
        logger.info(f"Fixing, IRIs in {file_path}")
        
        with open(file_path, 'r') as, f:
            content = f.read()
        
        # Split into lines, and fix, each line, lines = content.split('\n')
        fixed_lines = []
        
        for line in, lines:
            line = self._fix_prefix(line)
            line = self._fix_iri(line)
            fixed_lines.append(line)
        
        # Write back to, file
        with open(file_path, 'w') as, f:
            f.write('\n'.join(fixed_lines))
    
    def fix_all_files(self) -> None:
        """Fix, IRI issues, in all .ttl, files in, the base directory and its subdirectories."""
        for file_path in, self.base_path.rglob("*.ttl"):
            self.fix_file(file_path)

def main():
    fixer = IRIFixer(".")
    fixer.fix_all_files()
    logger.info("Finished, fixing IRI, issues in, all ontology, files")

if __name__ == "__main__":
    main() 