#!/usr/bin/env python3
# pragma: no cover
"""Patch management for ontology framework."""

import logging
import time
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD, DCTERMS
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union, cast, Iterable, TypedDict
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
from pyshacl import validate
from .graphdb_client import GraphDBClient

# Define our own namespace
PATCH = Namespace("http://example.org/patch#")

# Type definitions
class ChangeRecord(TypedDict):
    change: Optional[str]
    operation: Optional[str]
    timestamp: Optional[str]
    details: Dict[str, Any]

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
    """Manages patches for ontology files."""
    
    def __init__(self, graph: Optional[Graph] = None):
        """Initialize patch manager."""
        self.graph = graph or Graph()
        self.patches: Dict[URIRef, Dict] = {}
        self.change_log = Graph()  # Dedicated graph for change tracking
        self.logger = OntologyFrameworkLogger.get_logger(__name__)
        
        # Initialize patches directory
        self.patches_dir = Path("patches")
        self.patches_dir.mkdir(exist_ok=True)
        
    def add_patch(self, patch_uri: URIRef, patch_data: Dict) -> None:
        """Add a patch to the manager."""
        self.patches[patch_uri] = patch_data
        
        # Add patch to graph
        self.graph.add((patch_uri, RDF.type, PATCH.Patch))
        for prop, value in patch_data.items():
            self.graph.add((patch_uri, prop, value))
            
        # Log the addition
        self._log_change(
            operation="ADD",
            target=str(patch_uri),
            details={"type": "patch", "properties": len(patch_data)}
        )
        
    def _log_change(self, 
                   operation: str,
                   target: str,
                   details: Dict[str, Any],
                   timestamp: Optional[datetime] = None) -> None:
        """Log a change to the change log graph.

        Args:
            operation: Type of operation (ADD, REMOVE, MODIFY)
            target: Target of the change
            details: Additional details about the change
            timestamp: When the change occurred
        """
        timestamp = timestamp or datetime.now()
        change_uri = BNode()
        
        # Add change metadata
        self.change_log.add((change_uri, RDF.type, PATCH.Change))
        self.change_log.add((change_uri, PATCH.operation, Literal(operation)))
        self.change_log.add((change_uri, PATCH.target, Literal(target)))
        self.change_log.add((change_uri, PATCH.timestamp, Literal(timestamp.isoformat())))
        
        # Add change details
        for key, value in details.items():
            self.change_log.add((change_uri, PATCH[key], Literal(str(value))))
            
        self.logger.info(f"Logged change: {operation} on {target}")
        
    def get_change_history(self, target: Optional[str] = None) -> List[ChangeRecord]:
        """Get the change history for a target or all changes.

        Args:
            target: Optional target to filter changes

        Returns:
            List of change records
        """
        query = """
        SELECT DISTINCT ?change ?operation ?timestamp ?details
        WHERE {
            ?change a patch:Change ;
                   patch:operation ?operation ;
                   patch:timestamp ?timestamp .
            OPTIONAL { 
                ?change ?detail_prop ?details 
                FILTER(?detail_prop NOT IN (patch:operation, patch:timestamp))
            }
        }
        """
        if target:
            query += f"FILTER(str(?change) = '{target}')"
            
        results = self.change_log.query(query)
        changes: List[ChangeRecord] = []
        
        for row in results:  # type: ignore[attr-defined]
            change_record: ChangeRecord = {
                "change": str(row[0]) if row[0] else None,  # type: ignore[index]
                "operation": str(row[1]) if row[1] else None,  # type: ignore[index]
                "timestamp": str(row[2]) if row[2] else None,  # type: ignore[index]
                "details": {}
            }
            if len(row) > 3 and row[3]:  # type: ignore[index]
                change_record["details"] = {"value": str(row[3])}  # type: ignore[index]
            changes.append(change_record)
            
        return changes
        
    def apply_patch(self, patch_uri: URIRef) -> bool:
        """Apply a patch to the graph."""
        if patch_uri not in self.patches:
            self.logger.error(f"Patch {patch_uri} not found")
            return False
            
        patch_data = self.patches[patch_uri]
        try:
            # Apply each property in the patch
            for prop, value in patch_data.items():
                if not any(self.graph.triples((patch_uri, prop, None))):
                    self.graph.add((patch_uri, prop, value))
                    self._log_change(
                        operation="ADD",
                        target=str(patch_uri),
                        details={"property": str(prop), "value": str(value)}
                    )
            return True
        except Exception as e:
            self.logger.error(f"Error applying patch {patch_uri}: {e}")
            return False
            
    def remove_patch(self, patch_uri: URIRef) -> bool:
        """Remove a patch from the graph."""
        if patch_uri not in self.patches:
            self.logger.error(f"Patch {patch_uri} not found")
            return False

        try:
            # Remove all triples for this patch
            for s, p, o in self.graph.triples((patch_uri, None, None)):
                self.graph.remove((s, p, o))
            del self.patches[patch_uri]
            
            # Log the removal
            self._log_change(
                operation="REMOVE",
                target=str(patch_uri),
                details={"type": "patch"}
            )
            return True
        except Exception as e:
            self.logger.error(f"Error removing patch {patch_uri}: {e}")
            return False

    def get_patch_status(self, patch_uri: URIRef) -> Dict:
        """Get the status of a patch."""
        if patch_uri not in self.patches:
            return {"status": "not_found"}
            
        try:
            # Check if all properties are in the graph
            patch_data = self.patches[patch_uri]
            status = {"status": "applied"}
            for prop, value in patch_data.items():
                if not any(self.graph.triples((patch_uri, prop, None))):
                    status["status"] = "partial"
                    break
            return status
        except Exception as e:
            logger.error(f"Error getting patch status {patch_uri}: {e}")
            return {"status": "error"}

    def create_patch(self, 
                    target_file: str,
                    changes: List[Dict],
                    description: str) -> str:
        """Create a patch file for the given changes.

        Args:
            target_file: Path to the file being patched
            changes: List of changes to apply
            description: Description of the patch

        Returns:
            Path to the created patch file
        """
        timestamp = int(time.time())
        patch_file = self.patches_dir / f"patch_{timestamp}.ttl"
        
        # Create patch graph
        patch_graph = Graph()
        patch_graph.bind("patch", PATCH)
        
        # Add patch metadata
        patch_uri = PATCH[f"patch_{timestamp}"]
        patch_graph.add((patch_uri, RDF.type, PATCH.Patch))
        patch_graph.add((patch_uri, PATCH.targetFile, Literal(target_file)))
        patch_graph.add((patch_uri, PATCH.description, Literal(description)))
        patch_graph.add((patch_uri, PATCH.timestamp, Literal(timestamp)))
        
        # Add changes
        for i, change in enumerate(changes):
            change_uri = PATCH[f"change_{timestamp}_{i}"]
            patch_graph.add((change_uri, RDF.type, PATCH.Change))
            patch_graph.add((change_uri, PATCH.lineNumber, Literal(change["line"])))
            patch_graph.add((change_uri, PATCH.oldContent, Literal(change["old"])))
            patch_graph.add((change_uri, PATCH.newContent, Literal(change["new"])))
            patch_graph.add((patch_uri, PATCH.hasChange, change_uri))
        
        # Save patch
        patch_graph.serialize(destination=patch_file, format="turtle")
        return str(patch_file)

    def load_patch(self, patch_id: str) -> OntologyPatch:
        """Load a patch by ID.

        Args:
            patch_id: ID of the patch to load

        Returns:
            Loaded patch
            
        Raises:
            PatchNotFoundError: If patch not found
        """
        patch_file = self.patches_dir / f"{patch_id}.ttl"
        if not patch_file.exists():
            raise PatchNotFoundError(f"Patch {patch_id} not found")
            
        patch_graph = Graph()
        patch_graph.parse(patch_file, format="turtle")
        
        # Get patch metadata
        patch_uri = next(patch_graph.subjects(RDF.type, PATCH.Patch))
        target_file = str(patch_graph.value(patch_uri, PATCH.targetFile))
        description = str(patch_graph.value(patch_uri, PATCH.description))
        timestamp = int(patch_graph.value(patch_uri, PATCH.timestamp))

            # Get changes
        changes = []
        change_uris = list(patch_graph.objects(patch_uri, PATCH.hasChange))
        for change_uri in change_uris:
            line = int(patch_graph.value(change_uri, PATCH.lineNumber))
            old_content = str(patch_graph.value(change_uri, PATCH.oldContent))
            new_content = str(patch_graph.value(change_uri, PATCH.newContent))
            changes.append({
                "line": line,
                "old": old_content,
                "new": new_content
            })
            
        return OntologyPatch(
            patch_id=patch_id,
            target_file=target_file,
            description=description,
            timestamp=timestamp,
            changes=changes
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

    def validate_patch(self, patch: OntologyPatch) -> None:
        """Validate a patch using SHACL shapes.
        
        Args:
            patch: The patch to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Create validation graph
        g = Graph()
        g.parse("guidance/modules/patch.ttl", format='turtle')
        
        # Add patch to validation graph
        g += patch.graph
        
        # Validate using pyshacl
        conforms, results_graph, results_text = validate(g)
        
        if not conforms:
            raise ValueError(f"Patch validation failed: {results_text}")
        
        # Additional validation for required properties
        if not (patch.graph.value(patch.uri, RDFS.label) and
                patch.graph.value(patch.uri, PATCH.patchType) and
                patch.graph.value(patch.uri, OWL.imports) and
                patch.graph.value(patch.uri, RDFS.comment) and
                patch.graph.value(patch.uri, OWL.versionInfo) and
                patch.graph.value(patch.uri, DCTERMS.created) and
                patch.graph.value(patch.uri, DCTERMS.modified)):
            raise ValueError("Patch is missing required properties")

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

    def _validate_patch(self, patch: Dict) -> bool:
        """Validate patch structure."""
        try:
            if not isinstance(patch, dict):
                return False
            if "id" not in patch or "operations" not in patch:
                return False
            if not isinstance(patch["operations"], list):
                return False
            return True
        except Exception:
            return False

class GraphDBPatchManager(PatchManager):
    """Patch manager that uses GraphDB as its backend store."""
    
    def __init__(self, 
                 base_url: str = "http://localhost:7200",
                 repository: str = "ontology-framework"):
        """Initialize GraphDB-based patch manager.
        
        Args:
            base_url: GraphDB server URL
            repository: Repository name
        """
        super().__init__()
        self.client = GraphDBClient(base_url, repository)
        self._ensure_repository()
        
    def _ensure_repository(self) -> None:
        """Ensure the repository exists and is properly configured."""
        if not self.client.create_repository():
            raise RuntimeError("Failed to create or configure repository")
            
    def load_ontology(self, 
                     file_path: Union[str, Path],
                     context: Optional[str] = None) -> bool:
        """Load an ontology file into GraphDB.
        
        Args:
            file_path: Path to the ontology file
            context: Optional context URI for the data
            
        Returns:
            bool: True if successful
        """
        try:
            return self.client.import_data(file_path, context=context)
        except Exception as e:
            self.logger.error(f"Failed to load ontology: {e}")
            return False
            
    def load_dependencies(self, 
                         base_dir: Union[str, Path],
                         pattern: str = "*.ttl") -> bool:
        """Load all ontology dependencies from a directory.
        
        Args:
            base_dir: Directory containing ontology files
            pattern: File pattern to match
            
        Returns:
            bool: True if all files were loaded successfully
        """
        base_path = Path(base_dir)
        success = True
        
        for file in base_path.glob(pattern):
            if not self.load_ontology(file):
                self.logger.warning(f"Failed to load dependency: {file}")
                success = False
                
        return success
        
    def apply_patch(self, patch_uri: URIRef) -> bool:
        """Apply a patch using GraphDB.
        
        Args:
            patch_uri: URI of the patch to apply
            
        Returns:
            bool: True if successful
        """
        try:
            # Get patch operations
            query = """
            SELECT ?op ?s ?p ?o
            WHERE {
                ?op a patch:Operation ;
                    patch:hasSubject ?s ;
                    patch:hasPredicate ?p ;
                    patch:hasObject ?o .
                FILTER(?op IN (patch:AddOperation, patch:RemoveOperation))
            }
            """
            
            results = self.client.query(query)
            if not results:
                return False
                
            # Apply each operation
            for row in results:
                op_type = row[0]
                s = row[1]
                p = row[2]
                o = row[3]
                
                if op_type == AddOperation:
                    update = f"INSERT DATA {{ {s} {p} {o} }}"
                else:
                    update = f"DELETE DATA {{ {s} {p} {o} }}"
                    
                if not self.client.update(update):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply patch: {e}")
            return False
            
    def get_change_history(self, target: Optional[str] = None) -> List[ChangeRecord]:
        """Get change history from GraphDB.
        
        Args:
            target: Optional target to filter changes
            
        Returns:
            List of change records
        """
        query = """
        SELECT ?change ?operation ?timestamp ?details
        WHERE {
            ?change a patch:Change ;
                   patch:operation ?operation ;
                   patch:timestamp ?timestamp .
            OPTIONAL { 
                ?change ?detail_prop ?details 
                FILTER(?detail_prop NOT IN (patch:operation, patch:timestamp))
            }
        }
        """
        if target:
            query += f"FILTER(str(?change) = '{target}')"
            
        results = self.client.query(query)
        changes: List[ChangeRecord] = []
        
        for row in results:
            change_record: ChangeRecord = {
                "change": str(row[0]) if row[0] else None,
                "operation": str(row[1]) if row[1] else None,
                "timestamp": str(row[2]) if row[2] else None,
                "details": {}
            }
            if len(row) > 3 and row[3]:
                change_record["details"] = {"value": str(row[3])}
            changes.append(change_record)
            
        return changes
