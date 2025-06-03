import sys
from pyshacl import validate
from pathlib import Path

def run_validation(data_file, shacl_file):
    conforms, report_graph, report_text = validate(
        data_graph=str(data_file),
        shacl_graph=str(shacl_file),
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=True,
        advanced=True,
        serialize_report_graph=True
    )
    print(report_text)
    if not conforms:
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate RDF against SHACL shapes")
    parser.add_argument("--data", required=True, help="TTL file to validate")
    parser.add_argument("--shapes", default="validation-shapes.ttl", help="SHACL shapes file")
    args = parser.parse_args()

    run_validation(Path(args.data), Path(args.shapes))
