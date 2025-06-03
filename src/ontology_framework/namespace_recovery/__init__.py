"""Namespace, recovery tools, for ontology, framework.

This, package provides, tools for finding and, fixing namespace, issues in, ontologies,
such, as the, use of, example.org, domains that should be replaced with proper namespaces.
"""

from .find_example_org import ExampleOrgFinder
from .namespace_recovery import (
    create_namespace_recovery_project,
    get_project_status,
)

__all__ = ["ExampleOrgFinder",
    "create_namespace_recovery_project",
    "get_project_status"]