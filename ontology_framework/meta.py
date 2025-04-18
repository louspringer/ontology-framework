from rdflib import Namespace, URIRef
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime

# Define namespaces
META = Namespace("http://example.org/guidance/modules/patch#")

# Define classes
PatchModel = URIRef(str(META) + "PatchModel")
PatchOperation = URIRef(str(META) + "PatchOperation")
AddOperation = URIRef(str(META) + "AddOperation")
RemoveOperation = URIRef(str(META) + "RemoveOperation")

# Define properties
hasOperation = URIRef(str(META) + "hasOperation")
hasSubject = URIRef(str(META) + "hasSubject")
hasPredicate = URIRef(str(META) + "hasPredicate")
hasObject = URIRef(str(META) + "hasObject")
hasTargetSpore = URIRef(str(META) + "hasTargetSpore")
createdAt = URIRef(str(META) + "createdAt")

class PatchType(Enum):
    """Types of patches that can be applied."""
    ADD = "ADD"
    REMOVE = "REMOVE"
    MODIFY = "MODIFY"
    VALIDATE = "VALIDATE"

class PatchStatus(Enum):
    """Status of a patch."""
    PENDING = "PENDING"
    APPLIED = "APPLIED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"

class OntologyPatch:
    """Represents a patch to be applied to an ontology."""
    
    def __init__(
        self,
        patch_id: str,
        patch_type: PatchType,
        target_ontology: str,
        content: str,
        status: PatchStatus = PatchStatus.PENDING,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        """Initialize an ontology patch.
        
        Args:
            patch_id: Unique identifier for the patch
            patch_type: Type of patch (ADD, REMOVE, MODIFY, VALIDATE)
            target_ontology: URI of the target ontology
            content: RDF content of the patch in Turtle format
            status: Current status of the patch
            created_at: ISO format timestamp of creation
            updated_at: ISO format timestamp of last update
        """
        self.patch_id = patch_id
        self.patch_type = patch_type
        self.target_ontology = target_ontology
        self.content = content
        self.status = status
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or self.created_at
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert patch to dictionary format."""
        return {
            "patch_id": self.patch_id,
            "patch_type": self.patch_type.value,
            "target_ontology": self.target_ontology,
            "content": self.content,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OntologyPatch':
        """Create patch from dictionary format."""
        return cls(
            patch_id=data["patch_id"],
            patch_type=PatchType(data["patch_type"]),
            target_ontology=data["target_ontology"],
            content=data["content"],
            status=PatchStatus(data["status"]),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        ) 