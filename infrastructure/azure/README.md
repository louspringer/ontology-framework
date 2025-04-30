# Infrastructure Ontology

This directory contains the infrastructure ontology for Azure resources, generated using RDFLib.

## Files

- `infrastructure.py`: Python script to generate the infrastructure ontology
- `infrastructure.ttl`: Generated Turtle ontology file
- `requirements.txt`: Python dependencies

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Python script to generate the ontology:
```bash
python infrastructure.py
```

## Ontology Structure

The ontology models Azure infrastructure components including:

- Virtual Machine
- Network Security Group
- Virtual Network
- Public IP Address
- Network Interface
- Security Rules
- Subnets
- Spot Instance configuration
- Auto Shutdown configuration

## Usage

The generated `infrastructure.ttl` file can be used to:

1. Validate infrastructure configurations
2. Generate ARM templates
3. Document infrastructure requirements
4. Query infrastructure relationships

## SPARQL Queries

Example SPARQL queries to validate the infrastructure:

```sparql
# Get all VM configurations
PREFIX inf: <http://example.org/infrastructure#>
SELECT ?vm ?name ?size ?location
WHERE {
    ?vm a inf:VirtualMachine .
    ?vm inf:hasName ?name .
    ?vm inf:hasSize ?size .
    ?vm inf:hasLocation ?location .
}

# Get security rules
PREFIX inf: <http://example.org/infrastructure#>
SELECT ?rule ?name ?port ?protocol
WHERE {
    ?rule a inf:SecurityRule .
    ?rule inf:hasName ?name .
    ?rule inf:hasPort ?port .
    ?rule inf:hasProtocol ?protocol .
}
```

## Validation

The ontology follows the guidance from `guidance.ttl` and includes:

- Proper class and property definitions
- Labels and comments for all entities
- Clear relationships between components
- Validation rules for infrastructure constraints 