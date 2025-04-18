import logging
import time
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD, DCTERMS
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union, cast, Iterable
import traceback
from rdflib.term import Node
from .meta import (
    META, PatchModel, PatchOperation, AddOperation, RemoveOperation, 
    hasOperation, hasSubject, hasPredicate, hasObject, hasTargetSpore, 
    createdAt, PatchType, OntologyPatch, PatchStatus
)
from rdflib.query import Result, ResultRow
from .logging_config import OntologyFrameworkLogger
from rdflib.plugins.sparql.processor import SPARQLProcessor
from rdflib.plugins.stores.sparqlstore import SPARQLStore

# Define our own namespace
PATCH = Namespace("http://example.org/patch#")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("patch_management.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

class PatchNotFoundError(Exception):
    """Exception raised when a patch cannot be found."""
    pass

class PatchManager:
    """Manages ontology patches."""

    def __init__(self, workspace_dir: str):
        """Initialize the patch manager.
        
        Args:
            workspace_dir: Path to workspace directory
        """
        self.workspace_dir = Path(workspace_dir)
        self.patches_dir = self.workspace_dir / "patches"
        self.patches_dir.mkdir(parents=True, exist_ok=True)
        self.graph = Graph()
        self.graph.bind("patch", PATCH)
        self.logger = logging.getLogger(__name__)

    def create_patch(self, 
                    patch_type: PatchType,
                    target_ontology: str,
                    content: str,
                    patch_id: Optional[str] = None) -> OntologyPatch:
        """Create a new ontology patch.
        
        Args:
            patch_type: Type of patch
            target_ontology: Target ontology file
            content: Patch content
            patch_id: Optional patch ID (generated if not provided)
            
        Returns:
            Created patch
        """
        if not patch_id:
            patch_id = f"patch-{uuid.uuid4()}"
            
        patch = OntologyPatch(
            patch_id=patch_id,
            patch_type=patch_type,
            target_ontology=target_ontology,
            content=content,
            status=PatchStatus.PENDING,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self._save_patch(patch)
        return patch

    def load_patch(self, patch_id: str) -> OntologyPatch:
        """Load a patch from storage.
        
        Args:
            patch_id: ID of patch to load
            
        Returns:
            Loaded patch
            
        Raises:
            PatchNotFoundError: If patch doesn't exist
        """
        patch_file = self.patches_dir / f"{patch_id}.ttl"
        if not patch_file.exists():
            raise PatchNotFoundError(f"Patch {patch_id} not found")
            
        self.graph.parse(str(patch_file), format="turtle")
        patch_node = self.graph.value(predicate=RDF.type, object=PATCH.Patch)
        if not patch_node:
            raise PatchNotFoundError(f"No patch found in {patch_file}")
            
        return OntologyPatch(
            patch_id=str(self.graph.value(patch_node, RDFS.label)),
            patch_type=PatchType[str(self.graph.value(patch_node, PATCH.patchType))],
            target_ontology=str(self.graph.value(patch_node, OWL.imports)),
            content=str(self.graph.value(patch_node, RDFS.comment)),
            status=PatchStatus[str(self.graph.value(patch_node, OWL.versionInfo))],
            created_at=str(self.graph.value(patch_node, DCTERMS.created)),
            updated_at=str(self.graph.value(patch_node, DCTERMS.modified))
        )

    def _save_patch(self, patch: OntologyPatch) -> None:
        """Save a patch to storage.
        
        Args:
            patch: Patch to save
        """
        patch_file = self.patches_dir / f"{patch.patch_id}.ttl"
        
        # Create patch RDF
        patch_node = BNode()
        self.graph.add((patch_node, RDF.type, PATCH.Patch))
        self.graph.add((patch_node, RDFS.label, Literal(patch.patch_id)))
        self.graph.add((patch_node, PATCH.patchType, Literal(patch.patch_type.name)))
        self.graph.add((patch_node, OWL.imports, Literal(patch.target_ontology)))
        self.graph.add((patch_node, RDFS.comment, Literal(patch.content)))
        self.graph.add((patch_node, OWL.versionInfo, Literal(patch.status.name)))
        self.graph.add((patch_node, DCTERMS.created, Literal(patch.created_at)))
        self.graph.add((patch_node, DCTERMS.modified, Literal(patch.updated_at)))
        
        # Save to file
        self.graph.serialize(destination=str(patch_file), format="turtle")

    def validate_patch(self, patch_uri: URIRef) -> bool:
        """Validate a patch against the SHACL rules in the ontology.
        
        Args:
            patch_uri (URIRef): URI of the patch to validate
            
        Returns:
            bool: True if patch is valid
            
        Raises:
            ValueError: If validation fails
        """
        # Check if patch exists in graph
        if not any(self.graph.triples((patch_uri, RDF.type, PATCH.Patch))):
            raise ValueError(f"Patch {patch_uri} not found in graph")
            
        # Check required properties
        required_props = [
            (RDFS.label, "label"),
            (PATCH.patchType, "patch type"),
            (OWL.imports, "target ontology"),
            (RDFS.comment, "content"),
            (OWL.versionInfo, "status"),
            (DCTERMS.created, "creation timestamp"),
            (DCTERMS.modified, "modification timestamp")
        ]
        
        for prop, name in required_props:
            if not any(self.graph.triples((patch_uri, prop, None))):
                raise ValueError(f"Missing required property: {name}")
                
        return True
        
    def apply_patch(self, spore: Graph, patch_uri: URIRef) -> Graph:
        """Apply a patch to a spore following the PatchModel ontology.
        
        Args:
            spore (Graph): The spore to patch
            patch_uri (URIRef): URI of the patch to apply
            
        Returns:
            Graph: The patched spore
            
        Raises:
            ValueError: If patch application fails
        """
        if not self.validate_patch(patch_uri):
            raise ValueError("Cannot apply invalid patch")
            
        # Create new graph with same store
        patched = Graph(store=spore.store)
        
        # Copy spore triples
        for s, p, o in spore:
            patched.add((s, p, o))
            
        # Apply operations
        for op in self.graph.objects(patch_uri, hasOperation):
            op_type = next(self.graph.objects(op, RDF.type))
            s = next(self.graph.objects(op, hasSubject))
            p = next(self.graph.objects(op, hasPredicate))
            o = next(self.graph.objects(op, hasObject))
            
            if op_type == AddOperation:
                patched.add((s, p, o))
            else:
                patched.remove((s, p, o))
                
        return patched
        
    def rollback_patch(self, spore: Graph, patch_uri: URIRef) -> Graph:
        """Rollback a patch from a spore following the PatchModel ontology.
        
        Args:
            spore (Graph): The spore to rollback
            patch_uri (URIRef): URI of the patch to rollback
            
        Returns:
            Graph: The rolled back spore
            
        Raises:
            ValueError: If patch rollback fails
        """
        if not self.validate_patch(patch_uri):
            raise ValueError("Cannot rollback invalid patch")
            
        # Create new graph with same store
        rolled_back = Graph(store=spore.store)
        
        # Copy spore triples
        for s, p, o in spore:
            rolled_back.add((s, p, o))
            
        # Apply reverse operations
        for op in self.graph.objects(patch_uri, hasOperation):
            op_type = next(self.graph.objects(op, RDF.type))
            s = next(self.graph.objects(op, hasSubject))
            p = next(self.graph.objects(op, hasPredicate))
            o = next(self.graph.objects(op, hasObject))
            
            if op_type == AddOperation:
                rolled_back.remove((s, p, o))
            else:
                rolled_back.add((s, p, o))
                
        return rolled_back
        
    def close(self) -> None:
        """Close the patch manager and clean up resources."""
        self.graph.close()

    def update_version(self, patch_uri: URIRef, new_version: str) -> bool:
        """Update the version of a semantic patch.

        Args:
            patch_uri: The URI of the patch to update
            new_version: The new version string

        Returns:
            bool: True if version was updated successfully

        Raises:
            ValueError: If the patch is invalid or version is invalid
        """
        if not patch_uri:
            raise ValueError("Patch URI cannot be None")
        if not new_version:
            raise ValueError("New version cannot be None")

        try:
            # Validate patch
            if not self.validate_patch(patch_uri):
                self.logger.error(f"Invalid patch: {patch_uri}")
                return False

            # Get current version
            current_version = None
            for _, _, version in self.graph.triples((patch_uri, OWL.versionInfo, None)):
                current_version = str(version)
                break

            if not current_version:
                self.logger.error(f"No current version found for patch: {patch_uri}")
                return False

            # Remove old version
            self.graph.remove((patch_uri, OWL.versionInfo, Literal(current_version)))

            # Add new version
            self.graph.add((patch_uri, OWL.versionInfo, Literal(new_version)))

            # Add version history
            history_node = BNode()
            self.graph.add((patch_uri, META.hasVersionHistory, history_node))
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
            patch_file = self.patches_dir / f"{patch_uri.split('/')[-1]}.ttl"
            self.graph.serialize(patch_file, format="turtle")

            self.logger.info(
                f"Successfully updated patch {patch_uri} version from {current_version} to {new_version}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to update patch version: {str(e)}")
            return False
