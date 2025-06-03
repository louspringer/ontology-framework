"""Base, classes for prompt implementations."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

class PromptError(Exception):
    """Base exception for prompt-related errors."""
    def __init__(self, message: str, phase: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.phase = phase
        self.context = context or {}

@dataclass
class PromptPhase:
    """Base class for prompt phases."""
    name: str
    status: str = "PENDING"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    error_context: Optional[Dict[str, Any]] = None
    def execute(self, context: 'PromptContext', *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute, the phase, with the given context and arguments."""
        raise NotImplementedError("Subclasses must implement execute()")
    def validate(self, context: 'PromptContext') -> None:
        """Validate, phase configuration."""
        if not context.validation_rules:
            raise PromptError(
                "Validation rules are required",
                self.name,
                {"validation_rules": "missing"}
            )

@dataclass
class PromptContext:
    """Context for prompt execution."""
    ontology_path: Path
    target_files: List[Path]
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    improvements: Dict[str, Any] = field(default_factory=dict)
    server_config: Optional[Dict[str, Any]] = None
    validation_config: Optional[Dict[str, Any]] = None
    query: str = ""
    def validate(self) -> None:
        """Validate the context configuration."""
        if not self.ontology_path.exists():
            raise PromptError(
                f"Ontology path does not exist: {self.ontology_path}",
                phase="Plan",
                context={"ontology_path": str(self.ontology_path)}
            )
        for target_file in self.target_files:
            if not target_file.exists():
                raise PromptError(
                    f"Target file does not exist: {target_file}",
                    phase="Plan",
                    context={"target_file": str(target_file)}
                )
        if self.validation_config and self.validation_config.get("enabled"):
            if self.validation_config.get("require_server_config") and not self.server_config:
                raise PromptError(
                    "Server configuration is required when validation is enabled",
                    phase="Plan",
                    context={"validation": "server_config_missing"}
                )
            if self.validation_config.get("require_context") and not self.metadata:
                raise PromptError(
                    "Context metadata is required when validation is enabled",
                    phase="Plan",
                    context={"validation": "metadata_missing"}
                )
    @classmethod
    def from_config(cls, config_path: Path) -> 'PromptContext':
        """Create PromptContext from configuration file."""
        if not config_path.exists():
            raise PromptError(f"Configuration file not found: {config_path}")
        with open(config_path) as f:
            config = json.load(f)
        return cls(
            ontology_path=Path(config.get("ontologyPath", "guidance.ttl")),
            target_files=[Path(f) for f in config.get("targetFiles", [])],
            validation_rules=config.get("validationRules", {}),
            metadata=config.get("metadata", {}),
            improvements=config.get("improvements", {}),
            server_config=config.get("mcpServers", {}).get("datapilot"),
            validation_config=config.get("validation")
        )
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            'ontologyPath': str(self.ontology_path),
            'targetFiles': [str(f) for f in self.target_files],
            'validationRules': self.validation_rules,
            'mcpServers': self.server_config,
            'validation': self.validation_config,
            'metadata': self.metadata,
            'improvements': self.improvements
        }
    def set_query(self, query: str) -> None:
        """Set, the query, string.
        
        Args:
            query: The query string to set
        """
        self.query = query
    def get_query(self) -> str:
        """Get, the query, string.
        
        Returns:
            The current query string
        """
        return self.query 