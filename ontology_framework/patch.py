from dataclasses import dataclass
from typing import List, Optional
from rdflib import URIRef
from enum import Enum

class PatchType(Enum):
    """Type of patch."""
    ADD = "ADD"
    REMOVE = "REMOVE"
    MODIFY = "MODIFY"

class PatchStatus(Enum):
    """Status of a patch."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"

@dataclass
class Change:
    """Represents a single change in an ontology patch."""
    type: str  # "add" or "remove"
    subject: str
    predicate: str
    object: str

@dataclass
class OntologyPatch:
    """Represents a set of changes to an ontology."""
    patch_id: str
    patch_type: PatchType
    target_ontology: str
    content: str
    changes: List[Change]
    version: Optional[str] = None
    status: PatchStatus = PatchStatus.PENDING 