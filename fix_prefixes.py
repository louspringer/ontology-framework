# !/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

def fix_prefixes(turtle_path, dry_run=True):
    base_uri = os.environ.get("GRAPHDB_BASE_URI", "http://example.org")
    with open(turtle_path) as f:
        content = f.read()
    changes = []
    # Fix relative prefixes
    prefix_pattern = re.compile(r'@prefix\s+([^:]+):\s*<\./([^>#]+)#>')
    def replace_prefix(match):
        prefix, frag = match.group(1), match.group(2)
        changes.append(f"[RELATIVE PREFIX] {prefix}: <./{frag}# > → {prefix}: <{base_uri}/{frag}#>")
        return f"@prefix {prefix}: <{base_uri}/{frag}#>"
    corrected = prefix_pattern.sub(replace_prefix, content)
    # Fix malformed IRIs in prefix declarations
    malformed_prefix_pattern = re.compile(r'(@prefix\s+[^:]+:\s*<)http:/([^/])')
    def fix_prefix_iri(match):
        before = match.group(0)
        after = match.group(1) + 'http://' + match.group(2)
        changes.append(f"[MALFORMED PREFIX IRI] {before} → {after}")
        return after
    corrected = malformed_prefix_pattern.sub(fix_prefix_iri, corrected)
    # Fix malformed IRIs elsewhere
    malformed_iri_pattern = re.compile(r'(<)http:/([^/])')
    def fix_iri(match):
        before = match.group(0)
        after = '<http://' + match.group(2)
        changes.append(f"[MALFORMED IRI] {before} → {after}")
        return after
    corrected = malformed_iri_pattern.sub(fix_iri, corrected)
    if dry_run:
        print("--- Prefixes/IRIs to be changed ---")
        for change in changes:
            print("  ", change)
        print("--- End of changes ---")
    else:
        backup_path = str(Path(turtle_path).with_suffix(".bak"))
        with open(backup_path, "w") as f:
            f.write(content)
        with open(turtle_path, "w") as f:
            f.write(corrected)
        print(f"Prefixes/IRIs fixed and file updated. Backup saved as {backup_path}.")
        if changes:
            print("Changes made:")
            for change in changes:
                print("  ", change)
    return changes

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fix relative and malformed prefixes/IRIs in a Turtle file.")
    parser.add_argument("turtle_file", help="Path to the Turtle file to fix.")
    parser.add_argument("--fix", action="store_true", help="Apply the fix (otherwise dry-run)")
    args = parser.parse_args()
    fix_prefixes(args.turtle_file, dry_run=not args.fix) 