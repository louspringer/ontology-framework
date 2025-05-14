#!/usr/bin/env python3
import sys
import json
import argparse
from turtle_validation import validate_all

def main():
    parser = argparse.ArgumentParser(description="Validate a Turtle file for common ontology issues.")
    parser.add_argument("turtle_file", help="Path to the Turtle file to validate.")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    results = validate_all(args.turtle_file)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"{args.turtle_file}: No issues found. All checks passed.")
            sys.exit(0)
        print(f"Validation Report for {args.turtle_file}\n")
        for r in results:
            level = r['type'].upper()
            line = f" (line {r['line']})" if r['line'] else ""
            print(f"[{level}]{line} {r['message']}")
            if r.get('suggestion'):
                print(f"  Suggestion: {r['suggestion']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 