# Problem Ontology Documentation

## Overview
The Problem Ontology provides a framework for representing and structuring business needs, their context, and constraints. It is designed to capture the essential elements of business requirements and opportunities in a structured way.

## Core Classes

### BusinessNeed
- **Type**: `owl:Class`
- **Description**: Represents fundamental business requirements or opportunities
- **Subclass of**: `metameta:AbstractionDimension`
- **Properties**:
  - `hasValue` (string)
  - `hasPriority` (integer 1-5)
  - `hasContext` (Context)
  - `hasConstraint` (Constraint)

### Context
- **Type**: `owl:Class`
- **Description**: Represents environmental or situational factors
- **Used by**: `BusinessNeed` through `hasContext` property

### Constraint
- **Type**: `owl:Class`
- **Description**: Represents limiting factors or boundaries
- **Used by**: `BusinessNeed` through `hasConstraint` property

## Core Properties

### hasValue
- **Type**: `owl:DatatypeProperty`
- **Domain**: `BusinessNeed`
- **Range**: `xsd:string`
- **Description**: Captures the textual description of the business need

### hasPriority
- **Type**: `owl:DatatypeProperty`
- **Domain**: `BusinessNeed`
- **Range**: `xsd:integer`
- **Constraints**: Values must be between 1 and 5 inclusive
- **Description**: Indicates the priority level of the business need

### hasContext
- **Type**: `owl:ObjectProperty`
- **Domain**: `BusinessNeed`
- **Range**: `Context`
- **Description**: Links a business need to its contextual factors

### hasConstraint
- **Type**: `owl:ObjectProperty`
- **Domain**: `BusinessNeed`
- **Range**: `Constraint`
- **Description**: Links a business need to its constraints

## Validation Rules
- Priority values are restricted to integers between 1 and 5
- Every BusinessNeed must have at least one Context and one Constraint

## TODO
1. Add more specific types of Context and Constraint subclasses
2. Consider adding temporal aspects to business needs
3. Implement validation rules for Context and Constraint relationships
4. Add support for interdependencies between business needs
5. Consider adding success criteria properties 