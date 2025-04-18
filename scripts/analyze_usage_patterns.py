#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import Dict, List, Set
import logging
from datetime import datetime
import json
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/usage_patterns.log'),
        logging.StreamHandler()
    ]
)

class UsagePatternAnalyzer:
    def __init__(self, inventory_file: str = 'docs/example_org_inventory.md'):
        self.inventory_file = Path(inventory_file)
        self.patterns = {
            'prefix_definition': re.compile(r'@prefix\s+(\w+):\s*<(http://example\.org/[^>]+)>'),
            'namespace_declaration': re.compile(r'Namespace\("(http://example\.org/[^"]+)"\)'),
            'test_data': re.compile(r'example\.org/test'),
            'configuration': re.compile(r'example\.org/config'),
            'documentation': re.compile(r'example\.org/docs'),
            'ontology_import': re.compile(r'owl:imports\s*<(http://example\.org/[^>]+)>'),
        }
        self.categories = defaultdict(lambda: defaultdict(set))
        self.migration_strategies = defaultdict(list)

    def analyze_patterns(self) -> None:
        """Analyze and categorize usage patterns from the inventory."""
        try:
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                current_file = None
                current_category = None
                
                for line in f:
                    if line.startswith('## '):
                        current_file = line[3:].strip()
                        # Determine file category
                        if current_file.endswith('.ttl'):
                            current_category = 'ontology'
                        elif current_file.endswith('.py'):
                            current_category = 'python'
                        elif current_file.endswith('.md'):
                            current_category = 'documentation'
                        else:
                            current_category = 'other'
                        continue
                    
                    if current_file and line.strip():
                        for pattern_name, pattern in self.patterns.items():
                            matches = pattern.findall(line)
                            if matches:
                                for match in matches:
                                    uri = match[1] if isinstance(match, tuple) else match
                                    self.categories[current_category][pattern_name].add((current_file, uri))
                                    logging.debug(f"Found {pattern_name} in {current_file}: {uri}")
        except Exception as e:
            logging.error(f"Error analyzing patterns: {str(e)}")
            raise

    def develop_migration_strategies(self) -> None:
        """Develop migration strategies based on usage patterns."""
        # Strategy for ontology files
        if self.categories['ontology']:
            self.migration_strategies['ontology'] = [
                "1. Update prefix declarations to use new namespace",
                "2. Update all entity IRIs",
                "3. Update imports if present",
                "4. Validate ontology after migration",
                "5. Update any dependent ontologies"
            ]

        # Strategy for Python files
        if self.categories['python']:
            self.migration_strategies['python'] = [
                "1. Update Namespace declarations",
                "2. Update test data URIs",
                "3. Update configuration references",
                "4. Run test suite to verify changes",
                "5. Update any import statements"
            ]

        # Strategy for documentation
        if self.categories['documentation']:
            self.migration_strategies['documentation'] = [
                "1. Update example URIs",
                "2. Update documentation references",
                "3. Verify all links still work",
                "4. Update any diagrams or visualizations"
            ]

    def generate_report(self) -> str:
        """Generate a detailed report of usage patterns and migration strategies."""
        report = []
        report.append("# Namespace Usage Pattern Analysis")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        # Usage Statistics
        report.append("## Usage Statistics")
        for category in self.categories:
            report.append(f"\n### {category.title()} Files")
            for pattern, occurrences in self.categories[category].items():
                report.append(f"\n#### {pattern.replace('_', ' ').title()}")
                for file, uri in sorted(occurrences):
                    report.append(f"- {file}: {uri}")

        # Migration Strategies
        report.append("\n## Migration Strategies")
        for category, strategies in self.migration_strategies.items():
            report.append(f"\n### {category.title()} Files")
            for strategy in strategies:
                report.append(f"- {strategy}")

        # Recommendations
        report.append("\n## Recommendations")
        report.append("1. Start migration with files having fewest dependencies")
        report.append("2. Implement automated validation for each category")
        report.append("3. Create backup of each file before migration")
        report.append("4. Update CI/CD pipeline to validate new namespace usage")
        report.append("5. Document all changes in migration log")

        return "\n".join(report)

    def save_report(self, output_file: str = 'docs/usage_patterns_analysis.md') -> None:
        """Save the analysis report to a file."""
        report = self.generate_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logging.info(f"Analysis report saved to {output_file}")

def main() -> None:
    """Main function to run the usage pattern analyzer."""
    analyzer = UsagePatternAnalyzer()
    logging.info("Starting usage pattern analysis...")
    analyzer.analyze_patterns()
    analyzer.develop_migration_strategies()
    analyzer.save_report()
    logging.info("Usage pattern analysis complete.")

if __name__ == "__main__":
    main() 