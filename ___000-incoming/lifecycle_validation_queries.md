# Lifecycle Validation SPARQL Queries

## Core Invalid Transition Detection

Your original query identifies forbidden lifecycle transitions:

```sparql
PREFIX lifecycle: <./lifecycle#>
PREFIX artifact: <./artifact#>
PREFIX session: <./session#>

# Query: Invalid Lifecycle Transitions
SELECT ?artifact ?prevPhase ?nextPhase ?event ?timestamp
WHERE {
  ?event a session:Event ;
         session:triggersTransition ?nextPhase ;
         session:affectsArtifact ?artifact ;
         session:timestamp ?timestamp .
  ?artifact lifecycle:hasLifecyclePhase ?prevPhase .
  FILTER NOT EXISTS {
    ?prevPhase lifecycle:allowsTransitionTo ?nextPhase .
  }
}
ORDER BY ?timestamp
```

## Extended Validation Query Suite

### **1. Twin Artifact Lifecycle Synchronization Violations**
```sparql
PREFIX artifact: <./artifact#>
PREFIX lifecycle: <./lifecycle#>

# Query: Desynchronized Twin Artifacts
SELECT ?pythonModule ?manifestDoc ?pyPhase ?manifestPhase
WHERE {
  ?pythonModule a artifact:PythonModule ;
                artifact:hasTwin ?manifestDoc ;
                lifecycle:hasCurrentPhase ?pyPhase .
  ?manifestDoc a artifact:ManifestDocument ;
               lifecycle:hasCurrentPhase ?manifestPhase .
  FILTER (?pyPhase != ?manifestPhase)
}
```

### **2. Orphaned Lifecycle Phases**
```sparql
PREFIX lifecycle: <./lifecycle#>
PREFIX artifact: <./artifact#>
PREFIX trace: <./trace#>

# Query: Lifecycle phases without ontological justification
SELECT ?artifact ?phase
WHERE {
  ?artifact lifecycle:hasLifecyclePhase ?phase .
  FILTER NOT EXISTS {
    ?artifact trace:hasJustification ?justification .
    ?justification trace:appliesToPhase ?phase .
  }
}
```

### **3. Session Events Without Valid Lifecycle Context**
```sparql
PREFIX session: <./session#>
PREFIX lifecycle: <./lifecycle#>
PREFIX artifact: <./artifact#>

# Query: Events affecting artifacts not in compatible phases
SELECT ?event ?artifact ?eventType ?currentPhase
WHERE {
  ?event a session:Event ;
         session:eventType ?eventType ;
         session:affectsArtifact ?artifact .
  ?artifact lifecycle:hasCurrentPhase ?currentPhase .
  ?eventType lifecycle:requiresPhase ?requiredPhase .
  FILTER (?currentPhase != ?requiredPhase)
}
```

### **4. Premature Production Deployment**
```sparql
PREFIX lifecycle: <./lifecycle#>
PREFIX artifact: <./artifact#>
PREFIX validation: <./validation#>

# Query: Artifacts in Production without passing validation
SELECT ?artifact ?productionPhase ?missingValidation
WHERE {
  ?artifact lifecycle:hasCurrentPhase lifecycle:Production .
  ?artifact lifecycle:hasLifecyclePhase ?productionPhase .
  ?productionPhase a lifecycle:Production .
  
  # Required validations for production
  VALUES ?requiredValidation {
    validation:TwinSynchronization
    validation:OntologicalJustification
    validation:SemanticConsistency
  }
  
  FILTER NOT EXISTS {
    ?artifact validation:hasPassedValidation ?requiredValidation .
  }
  BIND(?requiredValidation AS ?missingValidation)
}
```

### **5. Lifecycle Phase Duration Anomalies**
```sparql
PREFIX lifecycle: <./lifecycle#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# Query: Phases exceeding expected duration thresholds
SELECT ?artifact ?phase ?duration ?startTime ?endTime
WHERE {
  ?artifact lifecycle:hasLifecyclePhase ?phase .
  ?phase lifecycle:phaseStart ?startTime ;
         lifecycle:phaseEnd ?endTime .
  
  BIND((?endTime - ?startTime) AS ?duration)
  
  # Phase-specific duration thresholds
  {
    ?phase a lifecycle:Planning .
    FILTER (?duration > "P7D"^^xsd:duration)  # Planning > 7 days
  } UNION {
    ?phase a lifecycle:Implementation .
    FILTER (?duration > "P14D"^^xsd:duration)  # Implementation > 14 days
  } UNION {
    ?phase a lifecycle:Validation .
    FILTER (?duration > "P3D"^^xsd:duration)  # Validation > 3 days
  }
}
```

### **6. Behavioral Rule Violations During Transitions**
```sparql
PREFIX behavior: <./behavior#>
PREFIX lifecycle: <./lifecycle#>
PREFIX session: <./session#>

# Query: Transition events violating behavioral constraints
SELECT ?event ?artifact ?transition ?violatedRule
WHERE {
  ?event a session:Event ;
         session:triggersTransition ?nextPhase ;
         session:affectsArtifact ?artifact .
  
  ?artifact lifecycle:hasCurrentPhase ?currentPhase .
  
  # Build transition identifier
  BIND(IRI(CONCAT(STR(?currentPhase), "->", STR(?nextPhase))) AS ?transition)
  
  # Check behavioral rule violations
  ?transition behavior:constrainedBy ?behavioralRule .
  ?event session:violatesRule ?behavioralRule .
  
  BIND(?behavioralRule AS ?violatedRule)
}
```

### **7. Complete Lifecycle Health Check**
```sparql
PREFIX lifecycle: <./lifecycle#>
PREFIX artifact: <./artifact#>
PREFIX trace: <./trace#>
PREFIX validation: <./validation#>

# Query: Comprehensive artifact lifecycle health
SELECT ?artifact ?healthStatus ?issues
WHERE {
  ?artifact a artifact:Artifact .
  
  # Check for various health issues
  BIND(
    IF(
      EXISTS { ?artifact lifecycle:hasCurrentPhase ?phase },
      IF(
        EXISTS { ?artifact trace:hasJustification ?just },
        IF(
          EXISTS { 
            ?artifact artifact:hasTwin ?twin .
            ?artifact lifecycle:hasCurrentPhase ?phase1 .
            ?twin lifecycle:hasCurrentPhase ?phase2 .
            FILTER(?phase1 = ?phase2)
          },
          "HEALTHY",
          "TWIN_DESYNC"
        ),
        "NO_JUSTIFICATION"
      ),
      "NO_LIFECYCLE"
    ) AS ?healthStatus
  )
  
  # Collect specific issues
  {
    SELECT ?artifact (GROUP_CONCAT(?issue; separator=", ") AS ?issues)
    WHERE {
      {
        ?artifact a artifact:Artifact .
        FILTER NOT EXISTS { ?artifact lifecycle:hasCurrentPhase ?phase }
        BIND("Missing lifecycle phase" AS ?issue)
      } UNION {
        ?artifact a artifact:Artifact .
        FILTER NOT EXISTS { ?artifact trace:hasJustification ?just }
        BIND("Missing ontological justification" AS ?issue)
      } UNION {
        ?artifact artifact:hasTwin ?twin .
        ?artifact lifecycle:hasCurrentPhase ?phase1 .
        ?twin lifecycle:hasCurrentPhase ?phase2 .
        FILTER(?phase1 != ?phase2)
        BIND("Twin artifact phase mismatch" AS ?issue)
      }
    }
    GROUP BY ?artifact
  }
}
```

## Validation Workflow Integration

These queries can be integrated into the AI behavioral rules:

```turtle
behavior:ClaudeReflector 
    behavior:enforces (
        behavior:PDCAProtocol
        behavior:SemanticFirstPrinciple  
        behavior:NoAssumptionsRule
        behavior:HaltOnMissingGuidance
        behavior:ValidateLifecycleTransitions  # NEW
    ) ;
    behavior:usesValidationQueries (
        query:InvalidTransitionDetection
        query:TwinSynchronizationCheck
        query:LifecycleHealthAudit
    ) .
```

This creates a **semantic firewall** that prevents invalid operations while maintaining the ontological integrity of the framework! 🛡️✨