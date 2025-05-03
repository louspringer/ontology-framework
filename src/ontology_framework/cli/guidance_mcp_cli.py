import argparse
import sys
import json
from ontology_framework.mcp.guidance_mcp_service import GuidanceMCPService

def main():
    parser = argparse.ArgumentParser(description="Guidance MCP CLI: Manage ontologies conforming to guidance.")
    parser.add_argument('--ontology', type=str, default='guidance.ttl', help='Path to the ontology file')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Add imports
    add_imports_parser = subparsers.add_parser('add-imports', help='Add owl:imports to the ontology')
    add_imports_parser.add_argument('imports', nargs='+', help='List of ontology IRIs to import')
    add_imports_parser.add_argument('--base-iri', type=str, default=None, help='Base ontology IRI (optional)')

    # Validate
    validate_parser = subparsers.add_parser('validate', help='Validate the ontology using SHACL and guidance rules')

    # Add validation rule
    add_rule_parser = subparsers.add_parser('add-rule', help='Add a validation rule to the ontology')
    add_rule_parser.add_argument('rule_id', type=str, help='Rule identifier')
    add_rule_parser.add_argument('type', type=str, help='Rule type (SHACL, SEMANTIC, SYNTAX, etc.)')
    add_rule_parser.add_argument('--rule', type=str, required=True, help='Rule configuration as JSON string')
    add_rule_parser.add_argument('--message', type=str, default=None, help='Optional message for the rule')
    add_rule_parser.add_argument('--priority', type=str, default='MEDIUM', help='Priority of the rule (HIGH, MEDIUM, LOW)')

    # Get validation rules
    get_rules_parser = subparsers.add_parser('get-rules', help='Get all validation rules')

    # Save
    save_parser = subparsers.add_parser('save', help='Save the ontology')
    save_parser.add_argument('--path', type=str, default=None, help='Path to save the ontology (optional)')

    # Load
    load_parser = subparsers.add_parser('load', help='Load an ontology file')
    load_parser.add_argument('path', type=str, help='Path to ontology file to load')

    args = parser.parse_args()
    mcp = GuidanceMCPService(args.ontology)

    if args.command == 'add-imports':
        mcp.add_imports(args.imports, args.base_iri)
        print(f"Added imports: {args.imports}")
    elif args.command == 'validate':
        result = mcp.validate()
        print(json.dumps(result, indent=2))
    elif args.command == 'add-rule':
        try:
            rule_dict = json.loads(args.rule)
        except Exception as e:
            print(f"Error parsing rule JSON: {e}", file=sys.stderr)
            sys.exit(1)
        mcp.add_validation_rule(
            args.rule_id,
            rule_dict,
            args.type,
            args.message,
            args.priority
        )
        print(f"Added rule {args.rule_id}")
    elif args.command == 'get-rules':
        rules = mcp.get_validation_rules()
        print(json.dumps(rules, indent=2))
    elif args.command == 'save':
        mcp.save(args.path)
        print(f"Ontology saved to {args.path if args.path else args.ontology}")
    elif args.command == 'load':
        mcp.load(args.path)
        print(f"Ontology loaded from {args.path}")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 