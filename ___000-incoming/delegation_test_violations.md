# Delegation Test Violations

```turtle
# test-delegation-violations.ttl
# Intentionally non-conformant delegation protocol examples for validation testing

@prefix agent: <./agent#> .
@prefix delegation: <./delegation#> .
@prefix session: <./session#> .
@prefix guidance: <./guidance#> .
@prefix artifact: <./artifact#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Valid agents for comparison
agent:HumanPrincipal a agent:Human ;
    rdfs:label "Human Principal Authority" ;
    agent:hasFullAuthority true ;
    agent:canAuthorize session:ArtifactCreation ,
                       session:ArtifactModification ,
                       session:LifecycleTransition ,
                       session:DelegationGrant ,
                       session:ProductionDeployment .

agent:ValidAI a agent:AI ;
    rdfs:label "Valid AI Agent" ;
    agent:hasDelegationFrom agent:HumanPrincipal ;
    agent:canAuthorize session:ArtifactCreation ,
                       session:ArtifactModification ;
    agent:operatesUnder delegation:ValidContract .

delegation:ValidContract a agent:DelegationContract ;
    delegation:grantsAuthority agent:ValidAI ;
    delegation:grantedBy agent:HumanPrincipal ;
    delegation:hasScope delegation:ValidScope ;
    delegation:justifiedByRequirement guidance:TraceabilityEnforcementRequirement .

delegation:ValidScope a delegation:DelegationScope ;
    delegation:hasTemporalLimit "2025-12-31T23:59:59Z"^^xsd:dateTime ;
    delegation:authorizedForArtifact artifact:PythonModule ;
    delegation:prohibitedAction session:ProductionDeployment .

# VIOLATION 1: Missing Delegation Chain
agent:OrphanAI a agent:AI ;
    rdfs:label "Orphaned AI Agent" ;
    agent:canAuthorize session:ArtifactCreation .
    # MISSING: agent:hasDelegationFrom (no chain to human principal)

# VIOLATION 2: Unauthorized Action by AI
agent:UnderprivilegedAI a agent:AI ;
    rdfs:label "Underprivileged AI Agent" ;
    agent:hasDelegationFrom agent:HumanPrincipal ;
    agent:canAuthorize session:ArtifactCreation ;  # Only authorized for creation
    agent:operatesUnder delegation:UnderprivilegedContract .

delegation:UnderprivilegedContract a agent:DelegationContract ;
    delegation:grantsAuthority agent:UnderprivilegedAI ;
    delegation:grantedBy agent:HumanPrincipal ;
    delegation:hasScope delegation:UnderprivilegedScope ;
    delegation:justifiedByRequirement guidance:TraceabilityEnforcementRequirement .

delegation:UnderprivilegedScope a delegation:DelegationScope ;
    delegation:hasTemporalLimit "2025-12-31T23:59:59Z"^^xsd:dateTime ;
    delegation:authorizedForArtifact artifact:PythonModule ;
    delegation:prohibitedAction session:ProductionDeployment .  # Explicitly prohibited

# Session attempting prohibited action
session:UnauthorizedDeployment a session:Event ;
    session:timestamp "2025-05-26T13:00:00Z"^^xsd:dateTime ;
    session:eventType session:ProductionDeployment ;  # VIOLATION: Prohibited action!
    session:performedBy agent:UnderprivilegedAI ;
    session:affectsArtifact artifact:TestModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

artifact:TestModule a artifact:PythonModule ;
    rdfs:label "Test Module" .

# VIOLATION 3: Action After Delegation Expiry
agent:ExpiredAgent a agent:AI ;
    rdfs:label "Expired Delegation Agent" ;
    agent:hasDelegationFrom agent:HumanPrincipal ;
    agent:canAuthorize session:ArtifactCreation ;
    agent:operatesUnder delegation:ExpiredContract .

delegation:ExpiredContract a agent:DelegationContract ;
    delegation:grantsAuthority agent:ExpiredAgent ;
    delegation:grantedBy agent:HumanPrincipal ;
    delegation:hasScope delegation:ExpiredScope ;
    delegation:justifiedByRequirement guidance:TraceabilityEnforcementRequirement .

delegation:ExpiredScope a delegation:DelegationScope ;
    delegation:hasTemporalLimit "2025-05-25T23:59:59Z"^^xsd:dateTime ;  # Already expired!
    delegation:authorizedForArtifact artifact:PythonModule .

# Session after expiration
session:PostExpirationAction a session:Event ;
    session:timestamp "2025-05-26T14:00:00Z"^^xsd:dateTime ;  # AFTER expiry!
    session:eventType session:ArtifactCreation ;
    session:performedBy agent:ExpiredAgent ;
    session:affectsArtifact artifact:PostExpiryModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

artifact:PostExpiryModule a artifact:PythonModule ;
    rdfs:label "Post-Expiry Module" .

# VIOLATION 4: Authority Escalation by Sub-Agent
agent:Delegator a agent:AI ;
    rdfs:label "Delegating Agent" ;
    agent:hasDelegationFrom agent:HumanPrincipal ;
    agent:canAuthorize session:ArtifactCreation ;  # Only has creation authority
    agent:operatesUnder delegation:DelegatorContract .

delegation:DelegatorContract a agent:DelegationContract ;
    delegation:grantsAuthority agent:Delegator ;
    delegation:grantedBy agent:HumanPrincipal ;
    delegation:hasScope delegation:DelegatorScope ;
    delegation:justifiedByRequirement guidance:TraceabilityEnforcementRequirement .

delegation:DelegatorScope a delegation:DelegationScope ;
    delegation:hasTemporalLimit "2025-12-31T23:59:59Z"^^xsd:dateTime ;
    delegation:authorizedForArtifact artifact:PythonModule .

# Sub-agent with escalated privileges
agent:OverprivilegedSubAgent a agent:AI ;
    rdfs:label "Overprivileged Sub-Agent" ;
    agent:hasDelegationFrom agent:Delegator ;  # Delegated by limited agent
    agent:canAuthorize session:ArtifactCreation ,
                       session:ArtifactModification ;  # VIOLATION: More authority than delegator!
    agent:operatesUnder delegation:EscalationContract .

delegation:EscalationContract a agent:DelegationContract ;
    delegation:grantsAuthority agent:OverprivilegedSubAgent ;
    delegation:grantedBy agent:Delegator ;  # Grantor lacks modification authority
    delegation:hasScope delegation:EscalationScope ;
    delegation:justifiedByRequirement guidance:TraceabilityEnforcementRequirement .

delegation:EscalationScope a delegation:DelegationScope ;
    delegation:hasTemporalLimit "2025-12-31T23:59:59Z"^^xsd:dateTime ;
    delegation:authorizedForArtifact artifact:PythonModule .

# Session demonstrating escalated authority
session:EscalatedAction a session:Event ;
    session:timestamp "2025-05-26T15:00:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactModification ;  # Action delegator can't authorize
    session:performedBy agent:OverprivilegedSubAgent ;
    session:affectsArtifact artifact:EscalatedModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

artifact:EscalatedModule a artifact:PythonModule ;
    rdfs:label "Escalated Authority Module" .

# VIOLATION 5: Delegation Justified by Nonexistent Requirement
agent:GhostAgent a agent:AI ;
    rdfs:label "Ghost Justified Agent" ;
    agent:hasDelegationFrom agent:HumanPrincipal ;
    agent:canAuthorize session:ArtifactCreation ;
    agent:operatesUnder delegation:GhostContract .

delegation:GhostContract a agent:DelegationContract ;
    delegation:grantsAuthority agent:GhostAgent ;
    delegation:grantedBy agent:HumanPrincipal ;
    delegation:hasScope delegation:GhostScope ;
    delegation:justifiedByRequirement guidance:NonexistentRequirement .  # VIOLATION: Broken link!

delegation:GhostScope a delegation:DelegationScope ;
    delegation:hasTemporalLimit "2025-12-31T23:59:59Z"^^xsd:dateTime ;
    delegation:authorizedForArtifact artifact:PythonModule .

# Session by ghost-justified agent
session:GhostAction a session:Event ;
    session:timestamp "2025-05-26T16:00:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactCreation ;
    session:performedBy agent:GhostAgent ;
    session:affectsArtifact artifact:GhostModule ;
    session:justifiedBy guidance:NonexistentRequirement .  # Also broken!

artifact:GhostModule a artifact:PythonModule ;
    rdfs:label "Ghost Justified Module" .

# VIOLATION 6: Agent Without Delegation Contract
agent:ContractlessAgent a agent:AI ;
    rdfs:label "Agent Without Contract" ;
    agent:hasDelegationFrom agent:HumanPrincipal ;
    agent:canAuthorize session:ArtifactCreation .
    # MISSING: agent:operatesUnder (no formal contract)

session:ContractlessAction a session:Event ;
    session:timestamp "2025-05-26T17:00:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactCreation ;
    session:performedBy agent:ContractlessAgent ;
    session:affectsArtifact artifact:ContractlessModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

artifact:ContractlessModule a artifact:PythonModule ;
    rdfs:label "Contractless Module" .

# VIOLATION 7: Action Requiring Approval Without Approval
agent:ApprovalRequiredAgent a agent:AI ;
    rdfs:label "Agent Requiring Approval" ;
    agent:hasDelegationFrom agent:HumanPrincipal ;
    agent:canAuthorize session:ArtifactCreation ,
                       session:LifecycleTransition ;
    agent:operatesUnder delegation:ApprovalContract .

delegation:ApprovalContract a agent:DelegationContract ;
    delegation:grantsAuthority agent:ApprovalRequiredAgent ;
    delegation:grantedBy agent:HumanPrincipal ;
    delegation:hasScope delegation:ApprovalScope ;
    delegation:justifiedByRequirement guidance:TraceabilityEnforcementRequirement .

delegation:ApprovalScope a delegation:DelegationScope ;
    delegation:hasTemporalLimit "2025-12-31T23:59:59Z"^^xsd:dateTime ;
    delegation:authorizedForArtifact artifact:PythonModule ;
    delegation:requiresApproval session:LifecycleTransition .  # Requires approval

# Session without required approval
session:UnapprovedTransition a session:Event ;
    session:timestamp "2025-05-26T18:00:00Z"^^xsd:dateTime ;
    session:eventType session:LifecycleTransition ;  # Requires approval but missing!
    session:performedBy agent:ApprovalRequiredAgent ;
    session:affectsArtifact artifact:UnapprovedModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .
    # MISSING: session:approvedBy

artifact:UnapprovedModule a artifact:PythonModule ;
    rdfs:label "Unapproved Transition Module" .

# VIOLATION 8: Circular Delegation Chain
agent:CircularA a agent:AI ;
    rdfs:label "Circular Agent A" ;
    agent:hasDelegationFrom agent:CircularB ;  # Creates circular dependency
    agent:canAuthorize session:ArtifactCreation .

agent:CircularB a agent:AI ;
    rdfs:label "Circular Agent B" ;
    agent:hasDelegationFrom agent:CircularA ;  # VIOLATION: Circular chain!
    agent:canAuthorize session:ArtifactCreation .

session:CircularAction a session:Event ;
    session:timestamp "2025-05-26T19:00:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactCreation ;
    session:performedBy agent:CircularA ;
    session:affectsArtifact artifact:CircularModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

artifact:CircularModule a artifact:PythonModule ;
    rdfs:label "Circular Delegation Module" .
```

## Expected Validation Results

When running `python validate.py --data test-delegation-violations.ttl --focus delegation`, you should see:

```
❌ Delegation Protocol Violations Detected - 8 violations found:

1. Missing Delegation Chain: agent:OrphanAI
   - AI agent without delegation chain to human principal

2. Unauthorized Action: session:UnauthorizedDeployment
   - Agent performed prohibited ProductionDeployment action

3. Expired Delegation: session:PostExpirationAction  
   - Action performed after delegation temporal limit

4. Authority Escalation: agent:OverprivilegedSubAgent
   - Sub-agent granted more authority than delegator possesses

5. Broken Justification: delegation:GhostContract
   - Contract references nonexistent requirement

6. Missing Contract: agent:ContractlessAgent
   - Agent lacks formal delegation contract

7. Missing Approval: session:UnapprovedTransition
   - Action requiring approval performed without authorization

8. Circular Delegation: agent:CircularA ↔ agent:CircularB
   - Agents delegate authority to each other (circular dependency)
```

This test suite validates all major delegation protocol constraints and proves your governance framework works correctly! 🧪✨