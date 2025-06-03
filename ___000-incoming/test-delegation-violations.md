# Delegation Protocol Violation Documentation

This file explains the intentional violations present in `test-delegation-violations.ttl`. These examples are designed to validate that your delegation governance model is enforcing constraints correctly.

---

## ❌ Violation 1: Missing Delegation Chain

**Agent**: `agent:OrphanAI`  
**Issue**: This AI agent has no `agent:hasDelegationFrom` chain leading to `agent:HumanPrincipal`.  
**Why It Matters**: All AI agents must be traceably delegated by a human or another authorized agent.

---

## ❌ Violation 2: Unauthorized Action by AI

**Agent**: `agent:UnderprivilegedAI`  
**Session**: `session:UnauthorizedDeployment`  
**Issue**: The AI attempts to perform `session:ProductionDeployment`, which is explicitly prohibited in its delegation scope.  
**Why It Matters**: Agents may not act outside their authorized scope.

---

## ❌ Violation 3: Action After Delegation Expiry

**Agent**: `agent:ExpiredAgent`  
**Session**: `session:PostExpirationAction`  
**Issue**: The session action occurred after the `delegation:hasTemporalLimit` of the delegation contract.  
**Why It Matters**: Delegations must be time-bound to prevent authority creep.

---

## ❌ Violation 4: Authority Escalation by Sub-Agent

**Delegator**: `agent:Delegator`  
**Sub-Agent**: `agent:OverprivilegedSubAgent`  
**Issue**: The sub-agent is authorized to perform `session:ArtifactModification`, which the delegator is not authorized to perform.  
**Why It Matters**: No agent may delegate more authority than they themselves possess.

---

## ❌ Violation 5: Delegation Justified by Nonexistent Requirement

**Agent**: `agent:GhostAgent`  
**Contract**: `delegation:GhostContract`  
**Issue**: The contract references `guidance:NonexistentRequirement`, which is undefined.  
**Why It Matters**: Every delegation contract must trace to a valid `guidance:Requirement`.

---

Each of these violations should be detected by your SHACL shapes or SPARQL queries, and will fail validation when using your `validate.py` tool.

Use this file for:
- Developer education
- Validation regression tests
- CI/CD error explanations
