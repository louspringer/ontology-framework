import logging
import time
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union, cast, Iterable
import traceback
from rdflib.term import Node
from .meta import META
from rdflib.query import Result, ResultRow
from .logging_config import OntologyFrameworkLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("patch_management.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class PatchManager:
    """Manages the creation and application of patches to ontologies."""

    def __init__(self, patch_directory: str):
        """Initialize the patch manager.

        Args:
            patch_directory (str): Directory to store patches.
        """
        self.patch_directory: Path = Path(patch_directory)
        self.logger = OntologyFrameworkLogger.get_logger(__name__)
        self.graph: Graph = Graph()
        os.makedirs(patch_directory, exist_ok=True)
        self._load_patches()
        self.logger.info(
            f"Initialized PatchManager with patch directory: {patch_directory}"
        )

    def _load_patches(self) -> None:
        """Load all patches from the patch directory."""
        try:
            for patch_file in self.patch_directory.glob("*.ttl"):
                self.graph.parse(patch_file, format="turtle")
                self.logger.debug(f"Loaded patch file: {patch_file}")
        except Exception as e:
            self.logger.error(f"Error loading patches: {e}")
            raise

    def create_patch(
        self,
        spore_uri: URIRef,
        label: str,
        comment: str,
        version: str,
        changes: Optional[List[Dict[str, Any]]] = None,
    ) -> URIRef:
        """Create a new patch.

        Args:
            spore_uri (URIRef): URI of the SPORE to patch.
            label (str): Label for the patch.
            comment (str): Description of the patch.
            version (str): Version of the patch.
            changes (Optional[List[Dict[str, Any]]]): List of changes to apply.

        Returns:
            URIRef: The URI of the created patch.
        """
        if not spore_uri:
            raise ValueError("SPORE URI is required")

        patch_uri = URIRef(f"{str(spore_uri)}/patches/{uuid.uuid4()}")

        # Add patch metadata
        self.graph.add((patch_uri, RDF.type, META.ConceptPatch))
        self.graph.add((patch_uri, RDFS.label, Literal(label)))
        self.graph.add((patch_uri, RDFS.comment, Literal(comment)))
        self.graph.add((patch_uri, OWL.versionInfo, Literal(version)))
        self.graph.add((patch_uri, META.targetSpore, spore_uri))
        self.graph.add(
            (
                patch_uri,
                META.createdAt,
                Literal(datetime.now().isoformat(), datatype=XSD.dateTime),
            )
        )

        # Add changes if provided
        if changes:
            for change_dict in changes:
                change_node = BNode()
                self.graph.add((patch_uri, META.hasChange, change_node))
                self.graph.add((change_node, RDF.type, META.PatchChange))
                for key, value in change_dict.items():
                    self.graph.add((change_node, META[key], Literal(value)))

        # Save patch to file
        patch_file = self.patch_directory / f"{patch_uri.split('/')[-1]}.ttl"
        self.graph.serialize(patch_file, format="turtle")

        self.logger.info(f"Created patch {patch_uri} for SPORE {spore_uri}")
        return patch_uri

    def validate_patch(self, patch: URIRef) -> bool:
        """Validate a semantic patch.

        Args:
            patch: The URI of the patch to validate

        Returns:
            bool: True if patch is valid
        """
        if not patch:
            raise ValueError("Patch URI cannot be None")

        try:
            # Check patch type
            if (patch, RDF.type, META.ConceptPatch) not in self.graph:
                self.logger.error(f"Patch {patch} is not of type ConceptPatch")
                return False

            # Check required properties
            required_props = [
                (RDFS.label, "label"),
                (RDFS.comment, "comment"),
                (OWL.versionInfo, "version"),
                (META.targetSpore, "target SPORE"),
                (META.createdAt, "creation timestamp"),
            ]

            for prop, name in required_props:
                if not any(self.graph.triples((patch, prop, None))):
                    self.logger.error(
                        f"Patch {patch} is missing required property: {name}"
                    )
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Failed to validate patch: {str(e)}")
            return False

    def check_dependencies(self, patch: URIRef) -> bool:
        """Check if patch dependencies are satisfied.

        Args:
            patch: The URI of the patch to check

        Returns:
            bool: True if all dependencies are satisfied (exist and are valid)
        """
        if not patch:
            raise ValueError("Patch URI cannot be None")

        try:
            # Get dependencies
            query = (
                """
                SELECT ?dependency
                WHERE {
                    <%s> meta:dependsOn ?dependency .
                }
            """
                % patch
            )

            result: Result = self.graph.query(query)
            dependencies: List[URIRef] = []
            for row in result:
                if isinstance(row, ResultRow):
                    dependency = cast(URIRef, row[0])
                    dependencies.append(dependency)

            # If no dependencies, consider it satisfied
            if not dependencies:
                return True

            # Check each dependency exists and is valid
            for dependency in dependencies:
                if not (dependency, RDF.type, META.ConceptPatch) in self.graph:
                    self.logger.error(f"Dependency {dependency} not found or invalid")
                    return False
                if not self.validate_patch(dependency):
                    self.logger.error(f"Dependency {dependency} is not valid")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Failed to check dependencies: {str(e)}")
            return False

    def apply_patch(self, patch: URIRef, target_model: URIRef) -> bool:
        """Apply a semantic patch to a target model.

        Args:
            patch: The URI of the patch to apply
            target_model: The URI of the target model

        Returns:
            bool: True if patch was applied successfully
        """
        if not patch or not target_model:
            raise ValueError("Patch URI and target model URI are required")

        try:
            # Validate patch
            if not self.validate_patch(patch):
                self.logger.error(f"Invalid patch: {patch}")
                return False

            # Check dependencies
            if not self.check_dependencies(patch):
                self.logger.error(f"Patch dependencies not satisfied for: {patch}")
                return False

            # Get changes
            query = (
                """
                SELECT ?subject ?predicate ?object
                WHERE {
                    <%s> meta:hasChange ?change .
                    ?change a meta:PatchChange ;
                           meta:subject ?subject ;
                           meta:predicate ?predicate ;
                           meta:object ?object .
                }
            """
                % patch
            )

            # Apply changes
            target_graph = Graph()
            target_graph.parse(target_model)

            result: Result = self.graph.query(query)
            for row in result:
                if isinstance(row, ResultRow):
                    subject = cast(Node, row[0])
                    predicate = cast(Node, row[1])
                    obj = cast(Node, row[2])
                    target_graph.add((subject, predicate, obj))

            # Save changes
            target_graph.serialize(target_model, format="turtle")

            self.logger.info(f"Applied patch {patch} to {target_model}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to apply patch: {str(e)}")
            return False

    def get_dependencies(self, patch_id: str) -> List[str]:
        """Get the dependencies of a patch."""
        try:
            patch_path = self.patch_directory / f"{patch_id}.json"
            if not patch_path.exists():
                logger.error(f"Patch {patch_id} not found")
                return []

            with open(patch_path) as f:
                patch_data = json.load(f)

            return patch_data.get("dependencies", [])
        except Exception as e:
            logger.error(f"Error getting dependencies for patch {patch_id}: {str(e)}")
            return []

    def get_patch_operations(self, patch_uri: URIRef) -> List[Tuple[Node, Node, Node]]:
        """Get all operations for a patch."""
        try:
            query = """
            SELECT ?s ?p ?o WHERE {
                ?patch a meta:Patch ;
                       meta:addTriple ?triple .
                ?triple rdf:subject ?s ;
                        rdf:predicate ?p ;
                        rdf:object ?o .
                FILTER (?patch = ?patch_uri)
            }
            """
            result: Result = self.graph.query(query, initBindings={"patch_uri": patch_uri})
            operations: List[Tuple[Node, Node, Node]] = []
            for row in result:
                if isinstance(row, ResultRow):
                    s = cast(Node, row[0])
                    p = cast(Node, row[1])
                    o = cast(Node, row[2])
                    operations.append((s, p, o))
            return operations
        except Exception as e:
            logger.error(f"Error getting patch operations: {e}")
            return []

    def close(self) -> None:
        """Close the patch manager and clean up resources."""
        self.graph.close()

    def rollback_patch(self, patch: URIRef, target_model: URIRef) -> bool:
        """Roll back a semantic patch from a target model.

        Args:
            patch: The URI of the patch to roll back
            target_model: The URI of the target model

        Returns:
            bool: True if patch was rolled back successfully
        """
        if not patch or not target_model:
            raise ValueError("Patch URI and target model URI are required")

        try:
            # Validate patch
            if not self.validate_patch(patch):
                self.logger.error(f"Invalid patch: {patch}")
                return False

            # Get changes
            query = """
            SELECT ?subject ?predicate ?object
            WHERE {
                <%s> meta:hasChange ?change .
                ?change a meta:PatchChange ;
                       meta:subject ?subject ;
                       meta:predicate ?predicate ;
                       meta:object ?object .
            }
            """ % patch

            # Remove changes
            target_graph = Graph()
            target_graph.parse(target_model)

            result: Result = self.graph.query(query)
            for row in result:
                if isinstance(row, ResultRow):
                    subject = cast(Node, row[0])
                    predicate = cast(Node, row[1])
                    obj = cast(Node, row[2])
                    if (subject, predicate, obj) in target_graph:
                        target_graph.remove((subject, predicate, obj))

            # Save changes
            target_graph.serialize(target_model, format="turtle")

            # Update patch status
            self.graph.add((patch, META.status, Literal("rolled_back")))
            self.graph.add(
                (
                    patch,
                    META.rolledBackAt,
                    Literal(datetime.now().isoformat(), datatype=XSD.dateTime),
                )
            )

            # Save patch status
            patch_file = self.patch_directory / f"{patch.split('/')[-1]}.ttl"
            self.graph.serialize(patch_file, format="turtle")

            self.logger.info(f"Successfully rolled back patch: {patch}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to roll back patch: {str(e)}")
            return False

    def update_version(self, patch: URIRef, new_version: str) -> bool:
        """Update the version of a semantic patch.

        Args:
            patch: The URI of the patch to update
            new_version: The new version string

        Returns:
            bool: True if version was updated successfully
        """
        if not patch:
            raise ValueError("Patch URI cannot be None")
        if not new_version:
            raise ValueError("New version cannot be None")

        try:
            # Validate patch
            if not self.validate_patch(patch):
                self.logger.error(f"Invalid patch: {patch}")
                return False

            # Get current version
            current_version = None
            for _, _, version in self.graph.triples((patch, OWL.versionInfo, None)):
                current_version = str(version)
                break

            if not current_version:
                self.logger.error(f"No current version found for patch: {patch}")
                return False

            # Remove old version
            self.graph.remove((patch, OWL.versionInfo, Literal(current_version)))

            # Add new version
            self.graph.add((patch, OWL.versionInfo, Literal(new_version)))

            # Add version history
            history_node = BNode()
            self.graph.add((patch, META.hasVersionHistory, history_node))
            self.graph.add((history_node, RDF.type, META.VersionHistory))
            self.graph.add((history_node, META.previousVersion, Literal(current_version)))
            self.graph.add((history_node, META.newVersion, Literal(new_version)))
            self.graph.add(
                (
                    history_node,
                    META.updatedAt,
                    Literal(datetime.now().isoformat(), datatype=XSD.dateTime),
                )
            )

            # Save changes
            patch_file = self.patch_directory / f"{patch.split('/')[-1]}.ttl"
            self.graph.serialize(patch_file, format="turtle")

            self.logger.info(
                f"Successfully updated patch {patch} version from {current_version} to {new_version}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to update patch version: {str(e)}")
            return False
