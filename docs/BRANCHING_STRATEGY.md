# Branching Strategy

This document outlines the branching strategy for the Ontology Framework project.

## Main Branches

- `main`: Production-ready code
- `develop`: Integration branch for feature development

## Supporting Branches

### Feature Branches

- Branch from: `develop`
- Merge back into: `develop`
- Naming convention: `feature/description-of-feature`

### Hotfix Branches

- Branch from: `main`
- Merge back into: `main` and `develop`
- Naming convention: `hotfix/description-of-fix`

### Release Branches

- Branch from: `develop`
- Merge back into: `main` and `develop`
- Naming convention: `release/version-number`

## Branch Protection

The `develop` branch is protected and requires:

- Pull request review before merging
- Up-to-date branch status before merging
- Passing status checks
- No direct pushes (all changes through PRs)

## Workflow

1. Create a feature branch from `develop`
2. Develop and test your changes
3. Create a pull request to merge back into `develop`
4. Address review comments
5. Merge after approval

## Best Practices

- Keep feature branches short-lived
- Regularly sync with `develop`
- Write clear commit messages
- Reference issues in commits and PRs
- Delete feature branches after merging

## Ontology-Specific Considerations

- All ontology changes must include validation results
- Document any new classes, properties, or relationships
- Include impact analysis for significant changes
- Update relevant documentation
