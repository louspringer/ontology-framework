import pytest
from ontology_framework.extensions.azure_openapi_to_shacl.azure_openapi_to_shacl import AzureOpenAPIToSHACL
from rdflib import Graph

def test_check_preconditions():
    AzureOpenAPIToSHACL.check_preconditions()

def test_generate_shacl_from_schema(tmp_path):
    # Setup
    api_spec_url = "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/compute/resource-manager/Microsoft.Compute/stable/2022-08-01/compute.json"
    converter = AzureOpenAPIToSHACL(api_spec_url, "VirtualMachine", output_dir=tmp_path)

    # Run pipeline
    converter.run()

    # Validate output
    g = Graph()
    g.parse(converter.shape_path, format="turtle")
    assert len(g) > 0
