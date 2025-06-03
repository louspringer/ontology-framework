# Complete SHACL Validation Framework

## Core Lifecycle Validation Shapes

Your foundational shapes establish the validation architecture. Here's the complete framework:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix lifecycle: <./lifecycle#> .
@prefix session: <./session#> .
@prefix artifact: <./artifact#> .
@prefix trace: <./trace#> .
@prefix behavior: <./behavior#> .
@prefix validation: <./validation#> .

# 1. Valid Transition Constraint (Your Original)
lifecycle:ValidTransitionShape a sh:NodeShape ;
    sh:targetClass session:Event ;
    sh:property [
        sh:path session:triggersTransition ;
        sh:class lifecycle:LifecyclePhase ;
        sh:message "Triggered transition must be allowed from current artifact phase." ;
        sh:sparql [
            sh:message "Invalid lifecycle transition: not permitted from current phase." ;
            sh:select """
            SELECT $this
            WHERE {
              $this session:triggersTransition ?toPhase ;
                    session:affectsArtifact ?artifact .
              ?artifact lifecycle:hasLifecyclePhase ?fromPhase .
              FILTER NOT EXISTS {
                ?fromPhase lifecycle:allowsTransitionTo ?toPhase .
              }
            }
            """
        ]
    ] .

# 2. Twin Phase Alignment (Your Original)
lifecycle:TwinPhaseAlignmentShape a sh:NodeShape ;
    sh:targetClass artifact:PythonModule ;
    sh:property [
        sh:path artifact:hasTwin ;
        sh:class artifact:ManifestDocument ;
        sh:message "Twin must be in same lifecycle phase." ;
        sh:sparql [
            sh:message "Twin artifact is in a different lifecycle phase." ;
            sh:select """
            SELECT $this
            WHERE {
              $this lifecycle:hasLifecyclePhase ?phase1 .
              $this artifact:hasTwin ?twin .
              ?twin lifecycle:hasLifecyclePhase ?phase2 .
              FILTER(?phase1 != ?phase2)
            }
            """
        ]
    ] .
```

## Extended Validation Shape Library

### **3. Ontological Justification Requirement**
```turtle
trace:OntologicalJustificationShape a sh:NodeShape ;
    sh:targetClass artifact:Artifact ;
    sh:property [
        sh:path trace:hasJustification ;
        sh:minCount 1 ;
        sh:class trace:OntologicalJustification ;
        sh:message "Every artifact must have ontological justification." ;
        sh:sparql [
            sh:message "Artifact lacks required ontological justification for current lifecycle phase." ;
            sh:select """
            SELECT $this
            WHERE {
              $this lifecycle:hasLifecyclePhase ?phase .
              FILTER NOT EXISTS {
                $this trace:hasJustification ?justification .
                ?justification trace:appliesToPhase ?phase .
              }
            }
            """
        ]
    ] .
```

### **4. Behavioral Rule Compliance**
```turtle
behavior:BehavioralComplianceShape a sh:NodeShape ;
    sh:targetClass session:Event ;
    sh:property [
        sh:path session:eventType ;
        sh:message "Event must comply with behavioral rules for affected artifacts." ;
        sh:sparql [
            sh:message "Event violates behavioral rule constraints." ;
            sh:select """
            SELECT $this
            WHERE {
              $this session:affectsArtifact ?artifact ;
                    session:eventType ?eventType .
              ?artifact behavior:governedBy ?rule .
              ?rule behavior:prohibitsEventType ?eventType .
            }
            """
        ]
    ] .
```

### **5. Lifecycle Phase Temporal Constraints**
```turtle
lifecycle:PhaseTemporalShape a sh:NodeShape ;
    sh:targetClass lifecycle:LifecyclePhase ;
    sh:property [
        sh:path lifecycle:phaseStart ;
        sh:maxCount 1 ;
        sh:datatype xsd:dateTime ;
        sh:message "Phase must have exactly one start time."
    ] ;
    sh:property [
        sh:path lifecycle:phaseEnd ;
        sh:maxCount 1 ;
        sh:datatype xsd:dateTime ;
        sh:message "Phase can have at most one end time."
    ] ;
    sh:sparql [
        sh:message "Phase end time cannot be before start time." ;
        sh:select """
        SELECT $this
        WHERE {
          $this lifecycle:phaseStart ?start ;
                lifecycle:phaseEnd ?end .
          FILTER(?end < ?start)
        }
        """
    ] ;
    sh:sparql [
        sh:message "Phase duration exceeds maximum allowed for phase type." ;
        sh:select """
        SELECT $this
        WHERE {
          $this lifecycle:phaseStart ?start ;
                lifecycle:phaseEnd ?end ;
                a ?phaseType .
          BIND((?end - ?start) AS ?duration)
          
          # Phase-specific duration limits
          {
            ?phaseType rdfs:subClassOf* lifecycle:Planning .
            FILTER(?duration > "P7D"^^xsd:duration)
          } UNION {
            ?phaseType rdfs:subClassOf* lifecycle:Implementation .
            FILTER(?duration > "P14D"^^xsd:duration)
          } UNION {
            ?phaseType rdfs:subClassOf* lifecycle:Validation .
            FILTER(?duration > "P3D"^^xsd:duration)
          }
        }
        """
    ] .
```

### **6. Session Event Traceability**
```turtle
session:EventTraceabilityShape a sh:NodeShape ;
    sh:targetClass session:Event ;
    sh:property [
        sh:path session:timestamp ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:dateTime ;
        sh:message "Event must have exactly one timestamp."
    ] ;
    sh:property [
        sh:path session:affectsArtifact ;
        sh:minCount 1 ;
        sh:class artifact:Artifact ;
        sh:message "Event must affect at least one artifact."
    ] ;
    sh:sparql [
        sh:message "Event timestamp must be within current phase duration." ;
        sh:select """
        SELECT $this
        WHERE {
          $this session:timestamp ?eventTime ;
                session:affectsArtifact ?artifact .
          ?artifact lifecycle:hasLifecyclePhase ?phase .
          ?phase lifecycle:phaseStart ?phaseStart .
          OPTIONAL { ?phase lifecycle:phaseEnd ?phaseEnd }
          
          FILTER(
            ?eventTime < ?phaseStart ||
            (BOUND(?phaseEnd) && ?eventTime > ?phaseEnd)
          )
        }
        """
    ] .
```

### **7. Twin Artifact Semantic Consistency**
```turtle
artifact:TwinSemanticConsistencyShape a sh:NodeShape ;
    sh:targetClass artifact:PythonModule ;
    sh:property [
        sh:path artifact:hasTwin ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:class artifact:ManifestDocument ;
        sh:message "Python module must have exactly one manifest twin."
    ] ;
    sh:sparql [
        sh:message "Twin artifacts must share semantic purpose." ;
        sh:select """
        SELECT $this
        WHERE {
          $this artifact:hasTwin ?twin ;
                artifact:hasSemanticPurpose ?purpose1 .
          ?twin artifact:hasSemanticPurpose ?purpose2 .
          FILTER(?purpose1 != ?purpose2)
        }
        """
    ] ;
    sh:sparql [
        sh:message "Twin artifacts must have synchronized generation events." ;
        sh:select """
        SELECT $this
        WHERE {
          $this artifact:hasTwin ?twin .
          ?genEvent1 generation:produces $this .
          ?genEvent2 generation:produces ?twin .
          FILTER(?genEvent1 != ?genEvent2)
        }
        """
    ] .
```

### **8. PDCA Protocol Enforcement**
```turtle
behavior:PDCAProtocolShape a sh:NodeShape ;
    sh:targetClass artifact:Artifact ;
    sh:sparql [
        sh:message "Artifact must follow PDCA sequence: Planning → Implementation → Validation → (Refinement|Production)." ;
        sh:select """
        SELECT $this
        WHERE {
          $this lifecycle:hasLifecyclePhase ?currentPhase .
          
          # Check if current phase violates PDCA sequence
          {
            ?currentPhase a lifecycle:Implementation .
            FILTER NOT EXISTS {
              $this lifecycle:hasLifecyclePhase ?planPhase .
              ?planPhase a lifecycle:Planning .
              ?planPhase lifecycle:phaseEnd ?planEnd .
              ?currentPhase lifecycle:phaseStart ?implStart .
              FILTER(?planEnd <= ?implStart)
            }
          } UNION {
            ?currentPhase a lifecycle:Validation .
            FILTER NOT EXISTS {
              $this lifecycle:hasLifecyclePhase ?implPhase .
              ?implPhase a lifecycle:Implementation .
              ?implPhase lifecycle:phaseEnd ?implEnd .
              ?currentPhase lifecycle:phaseStart ?validStart .
              FILTER(?implEnd <= ?validStart)
            }
          }
        }
        """
    ] .
```

## Integration with AI Behavior

### **SHACL-Driven ClaudeReflector**
```turtle
behavior:ClaudeReflector a behavior:AIBehaviorProfile ;
    behavior:enforces (
        behavior:PDCAProtocol
        behavior:SemanticFirstPrinciple
        behavior:NoAssumptionsRule
        behavior:HaltOnMissingGuidance
        behavior:SHACLValidationEnforcement  # NEW
    ) ;
    behavior:usesShapes (
        lifecycle:ValidTransitionShape
        lifecycle:TwinPhaseAlignmentShape
        trace:OntologicalJustificationShape
        behavior:BehavioralComplianceShape
        lifecycle:PhaseTemporalShape
        session:EventTraceabilityShape
        artifact:TwinSemanticConsistencyShape
        behavior:PDCAProtocolShape
    ) ;
    behavior:validationMode behavior:HaltOnViolation .
```

## Validation Execution Workflow

1. **Pre-Action Validation**: Before any artifact modification or lifecycle transition
2. **Real-Time Monitoring**: Continuous validation during session events
3. **Post-Transition Verification**: Confirmation of valid state after changes
4. **Periodic Health Checks**: Scheduled validation of entire artifact corpus

This SHACL framework transforms your ontology into a **self-validating semantic system** that enforces integrity through formal constraints rather than procedural checks! 🛡️✨