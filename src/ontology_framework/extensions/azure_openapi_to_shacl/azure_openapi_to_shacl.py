"""
Azure OpenAPI to SHACL converter module.

This module defines the AzureOpenAPIToSHACL class which fetches an OpenAPI specification
from Microsoft's GitHub, extracts a named definition and converts it into SHACL shapes
for RDF-based validation. The class is structured to support reuse, testing and logging.
"""

import os
import json
import logging
import requests
from pathlib import Path
from rdflib import (
    Graph,
    Namespace,
    URIRef,
    BNode,
    Literal,
    RDF,
    RDFS,
    XSD
)
from rdflib.term import Node
import importlib.util

class AzureOpenAPIToSHACL:
    def __init__(self, api_spec_url: str, definition_name: str, output_dir="schemas"):
        self.api_spec_url = api_spec_url
        self.definition_name = definition_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.compute_json_path = self.output_dir / "api_spec.json"
        self.schema_path = self.output_dir / f"{self.definition_name}.json"
        self.shape_path = self.output_dir / f"{self.definition_name}.shape.ttl"

        self.class_uri = f"https://docs.microsoft.com/azure/{self.definition_name}"
        self.SH = Namespace("http://www.w3.org/ns/shacl#")
        self.MS = Namespace("https://docs.microsoft.com/azure/")
        self.SCHEMA = Namespace("http://schema.org/")

        self.logger = logging.getLogger("AzureOpenAPIToSHACL")
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    def fetch_openapi_spec(self):
        if not self.compute_json_path.exists():
            self.logger.info(f"Downloading OpenAPI spec from: {self.api_spec_url}")
            try:
                response = requests.get(self.api_spec_url)
                response.raise_for_status()
                with open(self.compute_json_path, "w") as f:
                    f.write(response.text)
                self.logger.info("OpenAPI spec downloaded.")
            except requests.RequestException as e:
                self.logger.error(f"Failed to download OpenAPI spec: {e}")
                raise
        else:
            self.logger.debug("OpenAPI spec already exists.")

    def extract_schema(self):
        try:
            with open(self.compute_json_path, "r") as f:
                openapi = json.load(f)
            schema = openapi["definitions"][self.definition_name]
            with open(self.schema_path, "w") as f:
                json.dump(schema, f, indent=2)
            self.logger.info(f"Extracted schema: {self.definition_name}")
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Failed to extract schema '{self.definition_name}': {e}")
            raise
            
    def generate_shacl_from_schema(self) -> Graph:
        with open(self.schema_path, "r") as f:
            schema = json.load(f)

        g = Graph()
        g.bind("sh", self.SH)
        g.bind("ms", self.MS)
        g.bind("schema", self.SCHEMA)

        shape_uri = URIRef(f"{self.class_uri}Shape")
        target_class = URIRef(self.class_uri)

        g.add((shape_uri, RDF.type, self.SH.NodeShape))
        g.add((shape_uri, self.SH.targetClass, target_class))
        g.add((shape_uri, RDFS.label, Literal(f"{self.definition_name} SHACL Shape")))

        properties = schema.get("properties", {})

        for prop, details in properties.items():
            prop_uri = URIRef(f"{self.class_uri}/{prop}")
            property_shape = BNode()
            g.add((shape_uri, self.SH.property, property_shape))
            g.add((property_shape, self.SH.path, prop_uri))

            if "type" in details:
                dtype = details["type"]
                xsd_map = {
                    "string": XSD.string,
                    "boolean": XSD.boolean,
                    "integer": XSD.integer,
                    "number": XSD.decimal
                }
                if dtype in xsd_map:
                    g.add((property_shape, self.SH.datatype, xsd_map[dtype]))

        return g

    def save_shacl_graph(self, graph: Graph):
        graph.serialize(destination=str(self.shape_path), format="turtle")
        self.logger.info(f"SHACL saved to: {self.shape_path.resolve()}")

    def run(self):
        self.logger.info(f"Running SHACL generation for '{self.definition_name}'...")
        self.fetch_openapi_spec()
        self.extract_schema()
        graph = self.generate_shacl_from_schema()
        self.save_shacl_graph(graph)
        self.logger.info("Done.")

    @staticmethod
    def check_preconditions():
        logger = logging.getLogger("AzureOpenAPIToSHACL")
        required = ["requests", "rdflib"]
        missing = [(pkg) for pkg in required if importlib.util.find_spec(pkg) is None]

        if missing:
            logger.warning("Missing packages:")
            for pkg in missing:
                logger.warning(f"  - {pkg}")
            logger.warning(f"Run: pip install {' '.join(missing)}")
        else:
            logger.info("All required packages installed.")
