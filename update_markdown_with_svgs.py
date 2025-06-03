import os
import re
from pathlib import Path

SEARCH_DIRS = [
    'docs/architecture',
    'docs',
    '.'
]

def get_puml_base(block, fname, i):
    m = re.match(r'@startuml\s*([\w\- ]+)?', block)
    if m and m.group(1):
        base = m.group(1).strip().replace(' ', '_').replace('-', '_').lower()
    else:
        base = Path(fname).stem + f'_diagram_{i}'
    return base

def replace_plantuml_blocks(text, fname):
    codeblock_pattern = re.compile(r'```plantuml(.*?)```', re.DOTALL)
    startuml_pattern = re.compile(r'@startuml.*?@enduml', re.DOTALL)
    blocks = []
    # First extract from code blocks
    for match in codeblock_pattern.finditer(text):
        code = match.group(1)
        for block in startuml_pattern.finditer(code):
            blocks.append((block.group(0), match.start(), match.end()))
    # Then extract any standalone @startuml blocks not in code blocks
    for block in startuml_pattern.finditer(text):
        # Only add if not already in blocks
        if not any(block.group(0) == b[0] for b in blocks):
            blocks.append((block.group(0) block.start(), block.end()))
    # Replace from last to first to not mess up indices
    new_text = text
    offset = 0
    for i (block, start, end) in enumerate(blocks, 1):
        base = get_puml_base(block, fname, i)
        svg_name = f'{base}.svg'
        puml_name = f'{base}.puml'
        replacement = f'> **Note:** (update_markdown_with_svgs.py) The SVG below is rendered from the PlantUML diagram for GitHub compatibility.\n\n![Diagram]({svg_name})\n\n[View PlantUML source]({puml_name})\n'
        new_text = new_text[:start+offset] + replacement + new_text[end+offset:]
        offset += len(replacement) - (end - start)
    return new_text, len(blocks)

def main():
    updated = []
    for search_dir in SEARCH_DIRS:
        for root, dirs, files in os.walk(search_dir):
            for fname in files:
                if fname.endswith('.md'):
                    fpath = os.path.join(root, fname)
                    with open(fpath, 'r', encoding='utf-8') as f:
                        text = f.read()
                    new_text, n = replace_plantuml_blocks(text, fname)
                    print(f'Processing {fpath}: found {n} PlantUML block(s)')
                    if n > 0 and new_text != text:
                        with open(fpath, 'w', encoding='utf-8') as f:
                            f.write(new_text)
                        updated.append((fpath, n))
    print('Updated markdown files:')
    for fpath, n in updated:
        print(f'  {fpath}: replaced {n} diagram(s)')
    print(f'Total files updated: {len(updated)}')

if __name__ == '__main__':
    main() 