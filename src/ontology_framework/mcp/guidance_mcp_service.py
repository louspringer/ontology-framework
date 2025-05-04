from ontology_framework.tools.guidance_manager import GuidanceManager
from typing import List, Optional, Dict, Any

class GuidanceMCPService:
    """MCP service for managing ontologies conforming to guidance."""
    def __init__(self, ontology_path: str = 'guidance.ttl'):
        self.manager = GuidanceManager(ontology_path)

    def add_imports(self, import_iris: List[str], base_iri: Optional[str] = None) -> None:
        """Add owl:imports to the ontology."""
        self.manager.add_imports(import_iris, base_iri)
        self.manager.save()

    def validate(self) -> Dict[str, Any]:
        """Validate the ontology using SHACL and guidance rules."""
        return self.manager.validate_guidance()

    def add_validation_rule(self, rule_id: str, rule: Dict[str, Any], type: str, message: Optional[str] = None, priority: str = 'MEDIUM') -> None:
        """Add a validation rule to the ontology."""
        self.manager.add_validation_rule(rule_id, rule, type, message, priority)
        self.manager.save()

    def get_validation_rules(self) -> Any:
        """Get all validation rules."""
        return self.manager.get_validation_rules()

    def save(self, path: Optional[str] = None) -> None:
        self.manager.save(path)

    def load(self, path: str) -> None:
        self.manager.load(path) 