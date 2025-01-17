# Secure Ontologist Prompt Ontology

The Secure Ontologist Prompt Ontology (`sop`) defines the structure and requirements for secure ontology development. It emphasizes security practices, package management, and ontology component requirements.

## Integration

Uses standard prefixes:

- meta, metameta, problem, solution, conversation
- rdf, rdfs, owl, sh, xsd

## SPARQL Generation Example

The following SPARQL query generates this documentation from the ontology:

```sparql
PREFIX sop: <./secure-ontologist-prompt#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

SELECT ?markdown
WHERE {
  {
    # Title and Overview
    sop:SecureOntologistPrompt rdfs:label ?title ;
                              dc:description ?desc .
    BIND(CONCAT("# ", ?title, "

", ?desc, "

") AS ?markdown)
  } UNION {
    # Core Classes
    ?class a owl:Class ;
          sop:markdownRepresentation ?markdown .
    FILTER(?class != sop:Documentation && ?class != sop:Section && ?class != sop:TodoEnhancement)
  } UNION {
    # Properties
    ?prop a owl:ObjectProperty ;
         sop:markdownRepresentation ?markdown .
    FILTER(?prop != sop:hasSection && ?prop != sop:hasExample)
  } UNION {
    # Examples and Sections
    ?section a sop:Section ;
            sop:markdownRepresentation ?markdown .
  }
}
ORDER BY ?markdown
```

This query:

1. Extracts title and overview from ontology metadata
1. Collects class definitions and their examples
1. Gathers property definitions
1. Assembles documentation sections in order

## Usage Example

```turtle
sop:CredentialSecurity rdf:type sop:SecurityRequirement ;
    rdfs:label "Credential Security" ;
    rdfs:comment "Avoid including sensitive information in code/configurations" ;
    sop:priority "HIGH" .
```

## Validation Rules

The ontology supports SHACL validation for ensuring:

- Required labels and comments
- Property domain and range constraints
- Priority assignments for security requirements

### DocumentationRequirement

Requirements for ontology documentation.

### OntologyComponent

Core components required in ontology development.

### PackageManagement

Package management requirements and configurations.

### SecurityRequirement

Security-related requirements for ontology development.

### ValidationRule

Rules for validating ontology structure and content.

- `sop:hasPackageConfig` (Domain: SecureOntologistPrompt, Range: PackageManagement)
- `sop:hasRequirement` (Domain: SecureOntologistPrompt, Range: SecurityRequirement)
- `sop:requiresComponent` (Domain: SecureOntologistPrompt, Range: OntologyComponent)
