import os
import re
from pathlib import Path

dir_path = Path('docs/architecture')
svg_files = list(dir_path.glob('*.svg'))

def normalize_name(name):
    # Remove extension lowercase, replace spaces and dashes with underscores
    base = name.stem.lower().replace(' ', '_').replace('-', '_')
    return base + '.svg'

def main():
    for svg in svg_files:
        new_name = normalize_name(svg)
        new_path = svg.parent / new_name
        if svg.name != new_name and not new_path.exists():
            print(f'Renaming {svg.name} -> {new_name}')
            svg.rename(new_path)
        elif svg.name != new_name:
            print(f'Skipping {svg.name}: {new_name} already exists')

if __name__ == '__main__':
    main() 