import os
import logging
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD
from typing import List, Optional, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from ontology_framework.meta import META
import uuid
from datetime import datetime
from .logging_config import OntologyFrameworkLogger

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define namespaces
TEST = Namespace("http://example.org/test#")
SPORE = Namespace("http://example.org/spore#")

class ConcurrentModificationError(Exception):
    """Raised when concurrent modifications are detected."""
    pass

class SporeIntegrator:
    """Integrates semantic spores into target models."""
    
    def __init__(self, data_dir: str):
        """Initialize the spore integrator.
        
        Args:
            data_dir: Directory for storing spore data
        """
        self.logger = OntologyFrameworkLogger.get_logger(__name__)
        self.graph = Graph()
        self.graph.bind("meta", META)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)
        self.data_dir = data_dir
        self.logger.info("SporeIntegrator initialized")

    def check_compatibility(self, spore_uri: str, model_uri: str) -> bool:
        """Check if a spore is compatible with a model.

        Args:
            spore_uri (str): URI of the spore.
            model_uri (str): URI of the model.

        Returns:
            bool: True if compatible, False otherwise.
        """
        try:
            self.logger.info(f"Checking compatibility of {spore_uri} with {model_uri}")
            
            # Load spore and model
            spore_graph = Graph()
            model_graph = Graph()
            
            try:
                spore_graph.parse(spore_uri, format="turtle")
                model_graph.parse(model_uri, format="turtle")
            except Exception as e:
                self.logger.error(f"Failed to load graphs: {str(e)}")
                return False

            # Check for required classes and properties
            for s, p, o in spore_graph.triples((None, RDF.type, RDFS.Class)):
                if not any(model_graph.triples((s, RDF.type, RDFS.Class))):
                    self.logger.warning(f"Missing required class in model: {s}")
                    return False

            self.logger.info("Compatibility check passed")
            return True

        except Exception as e:
            self.logger.error(f"Compatibility check failed: {str(e)}")
            return False

    def apply_patch(
        self,
        patch_uri: URIRef,
        model_uri: URIRef,
        author: str,
        version: str,
        changes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Apply a patch to a model.

        Args:
            patch_uri (URIRef): URI of the patch to apply.
            model_uri (URIRef): URI of the model to patch.
            author (str): Author of the patch.
            version (str): Version of the patch.
            changes (Optional[Dict[str, Any]]): Changes to apply. Defaults to None.

        Returns:
            bool: True if patch was applied successfully, False otherwise.

        Raises:
            ValueError: If patch or model URIs are invalid.
            ConcurrentModificationError: If model was modified since patch was created.
        """
        if not patch_uri or not model_uri:
            raise ValueError("Patch and model URIs are required")

        try:
            patch_graph = Graph()
            patch_graph.parse(str(patch_uri))
            model_graph = Graph()
            model_graph.parse(str(model_uri))

            # Check if model has been modified since patch was created
            patch_base = patch_graph.value(patch_uri, META.baseVersion)
            model_version = model_graph.value(model_uri, META.version)
            if patch_base != model_version:
                raise ConcurrentModificationError("Model has been modified since patch was created")

            # Apply changes
            if changes:
                for change in changes:
                    if change.get("type") == "add":
                        model_graph.add((
                            URIRef(change["subject"]),
                            URIRef(change["predicate"]),
                            URIRef(change["object"])
                        ))
                    elif change.get("type") == "remove":
                        model_graph.remove((
                            URIRef(change["subject"]),
                            URIRef(change["predicate"]),
                            URIRef(change["object"])
                        ))

            # Update model version
            model_graph.remove((model_uri, META.version, None))
            model_graph.add((model_uri, META.version, Literal(version)))

            # Save updated model
            model_graph.serialize(str(model_uri))
            self.logger.info(f"Successfully applied patch {patch_uri} to model {model_uri}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to apply patch: {str(e)}")
            return False

    def integrate_concurrent(self, spores: List[URIRef], target_model: URIRef) -> bool:
        """Integrate multiple spores concurrently.
        
        Args:
            spores: List of spore URIs to integrate
            target_model: The URI of the target model
            
        Returns:
            bool: True if all spores were integrated successfully
        """
        try:
            self.logger.info(f"Integrating {len(spores)} spores concurrently into {target_model}")
            
            # Check compatibility for all spores
            for spore in spores:
                if not self.check_model_compatibility(spore, target_model):
                    raise ValueError(f"Incompatible spore: {spore}")
                    
            # Get all patches
            patches = []
            for spore in spores:
                spore_patches = self._get_spore_patches(spore)
                patches.extend([(spore, patch) for patch in spore_patches])
                
            # Sort patches by dependencies
            sorted_patches = self._sort_patches_by_dependencies(patches)
            
            # Apply patches
            for spore, patch in sorted_patches:
                if not self.apply_patch(patch, target_model):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to integrate spores concurrently: {str(e)}")
            return False

    def _get_spore_patches(self, spore: URIRef) -> List[URIRef]:
        """Get all patches for a spore.
        
        Args:
            spore: The URI of the spore
            
        Returns:
            List[URIRef]: List of patch URIs
        """
        try:
            query = """
                SELECT ?patch
                WHERE {
                    <%s> meta:hasPatch ?patch .
                }
                ORDER BY ?patch
            """ % spore
            
            return [row.patch for row in self.graph.query(query)]
            
        except Exception as e:
            self.logger.error(f"Failed to get spore patches: {str(e)}")
            return []

    def _sort_patches_by_dependencies(self, patches: List[Tuple[URIRef, URIRef]]) -> List[Tuple[URIRef, URIRef]]:
        """Sort patches by their dependencies.
        
        Args:
            patches: List of (spore, patch) tuples
            
        Returns:
            List[Tuple[URIRef, URIRef]]: Sorted list of (spore, patch) tuples
        """
        try:
            # Build dependency graph
            dependency_graph = {}
            for spore, patch in patches:
                dependencies = self._get_patch_dependencies(patch)
                dependency_graph[patch] = dependencies
                
            # Topological sort
            sorted_patches = []
            visited = set()
            temp = set()
            
            def visit(patch):
                if patch in temp:
                    raise ValueError("Circular dependency detected")
                if patch in visited:
                    return
                    
                temp.add(patch)
                for dep in dependency_graph.get(patch, []):
                    visit(dep)
                temp.remove(patch)
                visited.add(patch)
                sorted_patches.append(patch)
                
            for spore, patch in patches:
                if patch not in visited:
                    visit(patch)
                    
            # Map back to (spore, patch) tuples
            patch_to_spore = dict(patches)
            return [(patch_to_spore[patch], patch) for patch in reversed(sorted_patches)]
            
        except Exception as e:
            self.logger.error(f"Failed to sort patches: {str(e)}")
            return []

    def _get_patch_dependencies(self, patch: URIRef) -> List[URIRef]:
        """Get dependencies for a patch.
        
        Args:
            patch: The URI of the patch
            
        Returns:
            List[URIRef]: List of dependency URIs
        """
        try:
            query = """
                SELECT ?dependency
                WHERE {
                    <%s> meta:dependsOn ?dependency .
                }
            """ % patch
            
            return [row.dependency for row in self.graph.query(query)]
            
        except Exception as e:
            self.logger.error(f"Failed to get patch dependencies: {str(e)}")
            return []

    def integrate_spore(self, spore: URIRef, target_model: URIRef) -> bool:
        """Integrate a spore into a target model.
        
        Args:
            spore: The spore to integrate
            target_model: The target model to integrate into
            
        Returns:
            bool: True if integration was successful
            
        Raises:
            ValueError: If spore or target_model is None or invalid
        """
        if not spore or not target_model:
            raise ValueError("Spore and target model must be provided")
            
        logger.info(f"Integrating spore {spore} into model {target_model}")
        try:
            # Validate spore
            if not self._validate_spore(spore):
                raise ValueError("Invalid spore")
                
            # Check compatibility
            if not self.check_compatibility(spore, target_model):
                raise ValueError("Incompatible spore and model")
                
            # Apply patches
            patches = self._get_spore_patches(spore)
            for patch in patches:
                if not self.apply_patch(patch, target_model):
                    raise ValueError(f"Failed to apply patch {patch}")
                    
            logger.info("Spore integration completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to integrate spore: {str(e)}")
            raise

    def migrate_version(self, spore: URIRef, new_version: str) -> bool:
        """Migrate a spore to a new version.
        
        Args:
            spore: The spore to migrate
            new_version: The new version string
            
        Returns:
            bool: True if migration was successful
        """
        logger.info(f"Migrating spore {spore} to version {new_version}")
        try:
            # Update version info
            self.graph.set((spore, OWL.versionInfo, Literal(new_version)))
            logger.info("Version migration completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to migrate version: {str(e)}")
            return False

    def resolve_dependencies(self, spore: URIRef) -> bool:
        """Resolve spore dependencies.
        
        Args:
            spore: The spore to resolve dependencies for
            
        Returns:
            bool: True if all dependencies were resolved
        """
        logger.info(f"Resolving dependencies for spore {spore}")
        try:
            # Get all imports
            imports = self.graph.objects(spore, OWL.imports)
            
            # Verify each import exists
            for imp in imports:
                if not self._validate_spore(imp):
                    raise ValueError(f"Invalid dependency: {imp}")
                    
            logger.info("Dependencies resolved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to resolve dependencies: {str(e)}")
            return False

    def _validate_spore(self, spore: URIRef) -> bool:
        """Validate a spore."""
        try:
            return (spore, RDF.type, META.TransformationPattern) in self.graph
        except Exception:
            return False

    def _apply_spore(self, spore: str, target_model: str) -> bool:
        """Apply a single spore to the target model."""
        try:
            self.logger.info(f"Applying spore {spore} to {target_model}")
            
            # Load spore and model graphs
            spore_graph = Graph()
            model_graph = Graph()
            
            spore_file = os.path.join(self.data_dir, f"{spore}.ttl")
            model_file = os.path.join(self.data_dir, f"{target_model}.ttl")
            
            spore_graph.parse(spore_file, format="turtle")
            model_graph.parse(model_file, format="turtle")
            
            # Apply spore changes
            for s, p, o in spore_graph:
                model_graph.add((s, p, o))
                
            # Save updated model
            model_graph.serialize(model_file, format="turtle")
            self.logger.info(f"Spore {spore} applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply spore: {str(e)}")
            raise

    def _find_conflicts(self, spore_graph: Graph, model_graph: Graph) -> List[str]:
        """Find conflicts between spore and model graphs."""
        conflicts = []
        
        # Check for class conflicts
        for s, p, o in spore_graph.triples((None, RDF.type, OWL.Class)):
            if (s, p, o) in model_graph:
                conflicts.append(f"Class conflict: {s}")
                
        # Check for property conflicts
        for s, p, o in spore_graph.triples((None, RDF.type, OWL.ObjectProperty)):
            if (s, p, o) in model_graph:
                conflicts.append(f"Property conflict: {s}")
                
        return conflicts 