import os
import re
from pathlib import Path

# Directories to scan
SEARCH_DIRS = [
    'docs/architecture',
    'docs',
    '.'
]

# Regex to find PlantUML code blocks and @startuml blocks
def extract_plantuml_blocks(text):
    # Matches ```plantuml ... @startuml ... @enduml ... ``` or just @startuml ... @enduml
    codeblock_pattern = re.compile(r'```plantuml(.*?)```', re.DOTALL)
    startuml_pattern = re.compile(r'@startuml.*?@enduml', re.DOTALL)
    blocks = []
    # First, extract from code blocks
    for match in codeblock_pattern.finditer(text):
        code = match.group(1)
        for block in startuml_pattern.finditer(code):
            blocks.append(block.group(0))
    # Then, extract any standalone @startuml blocks not in code blocks
    for block in startuml_pattern.finditer(text):
        if block.group(0) not in blocks:
            blocks.append(block.group(0))
    return blocks

def main():
    found = []
    for search_dir in SEARCH_DIRS:
        for root, dirs, files in os.walk(search_dir):
            for fname in files:
                if fname.endswith('.md'):
                    fpath = os.path.join(root, fname)
                    with open(fpath, 'r', encoding='utf-8') as f:
                        text = f.read()
                    blocks = extract_plantuml_blocks(text)
                    for i, block in enumerate(blocks, 1):
                        # Try to get a title from @startuml line
                        m = re.match(r'@startuml\s*([\w\- ]+)?', block)
                        if m and m.group(1):
                            base = m.group(1).strip().replace(' ', '_').replace('-', '_').lower()
                        else:
                            base = Path(fname).stem + f'_diagram_{i}'
                        puml_name = f'{base}.puml'
                        puml_path = os.path.join(root, puml_name)
                        # Avoid overwriting existing files
                        if os.path.exists(puml_path):
                            puml_path = os.path.join(root, f'{base}_{i}.puml')
                        with open(puml_path, 'w', encoding='utf-8') as pf:
                            pf.write(block + '\n')
                        found.append((fpath, puml_path))
    print('Extracted PlantUML diagrams:')
    for src, puml in found:
        print(f'  From {src} -> {puml}')
    print(f'Total diagrams extracted: {len(found)}')

if __name__ == '__main__':
    main() 