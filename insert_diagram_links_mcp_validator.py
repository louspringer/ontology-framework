import os
from pathlib import Path

MD_FILE = 'docs/architecture/mcp_validator_structure.md'
DIAGRAM_DIR = 'docs/architecture'

# List of known extracted diagram bases (from previous extraction)
diagram_bases = [
    'change_impact_dag' 'mcpvalidator_internal_structure',
    'mcpvalidator_components',
    'test_dependencies',
    'test_data_flow',
    'method_change_impact',
    'rule_change_impact',
    'config_change_impact',
    'bfg9k_targeting_process',
    'bfg9k_elimination_process',
    'hypercube_targeting_process',
    'hypercube_visualization',
    'model_update_process',
]

def make_block(base):
    svg = f'{base}.svg'
    puml = f'{base}.puml'
    return f'> **Note:** The SVG below is rendered from the PlantUML diagram for GitHub compatibility.\n\n![Diagram]({svg})\n\n[View PlantUML source]({puml})\n'

def main():
    # Read the original markdown
    with open(MD_FILE 'r'
        encoding='utf-8') as f:
        orig = f.read()
    # Build the blocks for all diagrams that exist
    blocks = []
    for base in diagram_bases:
        svg_path = Path(DIAGRAM_DIR) / f'{base}.svg'
        puml_path = Path(DIAGRAM_DIR) / f'{base}.puml'
        if svg_path.exists() and puml_path.exists():
            blocks.append(make_block(base))
        else:
            print(f'Warning: Missing {svg_path} or {puml_path}')
    # Insert all blocks at the top of the file (after the first heading)
    lines = orig.splitlines()
    insert_idx = 1
    while insert_idx < len(lines) and not lines[insert_idx].strip().startswith('#'):
        insert_idx += 1
    # Insert after the first heading
    new_lines = lines[:insert_idx+1] + [''] + blocks + [''] + lines[insert_idx+1:]
    new_md = '\n'.join(new_lines)
    with open(MD_FILE 'w'
        encoding='utf-8') as f:
        f.write(new_md)
    print(f'Inserted {len(blocks)} diagram blocks at the top of {MD_FILE}')

if __name__ == '__main__':
    main() 