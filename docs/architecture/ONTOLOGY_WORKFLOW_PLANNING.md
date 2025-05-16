# Ontology Framework Workflow Planning & Cleanup

## Why This Workflow Needs Tools

The architecture and workflow described in `bfg9k_mcp_architecture.md`—with its clear PDCA cycle, validation phases, and integration points—are ideal for tool support and automation.

- **PDCA Cycle**: Each phase (Plan, Do, Check, Adjust) is a discrete, automatable step.
- **Validation**: Multiple validation types (SHACL, semantic, phase order, etc.) can be run as tools/services.
- **Configuration**: Unified config files (`mcp.json`) are perfect for tool-driven management and validation.
- **Traceability & Audit**: Automated tools can log, track, and report on every phase and result.
- **Continuous Improvement**: Tools can automate feedback loops, enforce governance, and reduce manual error.

## Tooling Opportunities

### 1. PDCA Phase Runners
- CLI or API tools to run each phase (`plan`, `do`, `check`, `adjust`) individually or as a pipeline.
- Each phase can be a subcommand: `bfg9k-mcp plan`, `bfg9k-mcp do`, etc.

### 2. Validation Orchestrator
- A tool to run all validations (SHACL, semantic, config, phase order) and output a unified report.
- Can be triggered by CI/CD, pre-commit hooks, or manually.

### 3. Configuration Validator
- Tool to lint and validate `mcp.json` and related config files for completeness, correctness, and conformance to schema.

### 4. Audit & Traceability Reporter
- Tool to generate audit logs, traceability matrices, and compliance reports from validation runs.

### 5. Automated Adjust/Feedback
- Tool to suggest or even apply adjustments based on validation failures or audit findings.

### 6. Integration Hooks
- Tools or scripts to integrate with IDEs (e.g., Cursor), GitHub Actions, or other CI/CD systems for automated enforcement.

---

## Current State & Challenges

- Docs, diagrams, and traceability have drifted and become inconsistent as the project evolved.
- Multiple abstraction levels and rapid iteration have led to some messiness and redundancy.
- Some diagrams are out of date or not rendered as SVG; some docs reference embedded PlantUML blocks instead of images.
- Traceability from requirements to code, validation, and docs is incomplete.

---

## Cleanup & Refactor Plan

### A. Audit & Inventory
- List all current docs, diagrams, and key scripts/tools.
- Identify which are out of date, redundant, or missing.

### B. Documentation Refactor
- Update the main README and documentation index to reflect the current structure and navigation.
- Ensure every major workflow and tool is documented with a diagram and usage example.

### C. Diagram Pass
- For each PlantUML file: ensure there's a rendered SVG, and that it's referenced (not embedded) in the docs.
- Remove any stale or duplicate diagrams.

### D. Traceability Matrix
- Create (or update) a traceability matrix:
  - Map requirements → ontology files → scripts/tools → tests → docs.
- Use this to spot gaps and ensure every requirement is covered and documented.

### E. Tooling/Automation
- Add or update scripts to automate validation, diagram rendering, and doc checks.
- Consider a pre-commit or CI/CD check for doc/diagram consistency.

---

## Next Steps

- [ ] Create an inventory of all docs, diagrams, and key tools/scripts
- [ ] Update documentation index and navigation
- [ ] Render and link all diagrams as SVG (no embedded PlantUML)
- [ ] Draft or update a traceability matrix
- [ ] Add or update automation for validation and doc/diagram checks

---

## Strategic Principle: Purposeful Projection & Documentation

As we move toward a fully model-driven, DRY documentation and governance workflow, we recognize that:

- **Projection is a tool, not a goal.** We aim to generate documentation, diagrams, and navigation from our models only when it adds real value for users and maintainers.
- **Curation matters.** Automated docs should be curated, layered, and supplemented with human context, examples, and rationale.
- **Signal over noise.** We strive for documentation that is not just accurate, but also useful, discoverable, and actionable.
- **Separation of concerns.** Rendering and presentation metadata should be kept out of core semantic models, and managed in view/config layers or at projection time.
- **Feedback and evolution.** We will periodically review our documentation and projection practices to ensure they serve real user needs, not just automation completeness.

> These principles will guide our tooling, documentation, and modeling strategy as the project evolves. They are adjacent to DRY and model-driven development, and are documented here as a strategic target for the team.

---

> This document is a living plan for restoring and maintaining a DRY, traceable, and user-friendly ontology framework workflow. All contributors should reference and update this as the cleanup proceeds. 