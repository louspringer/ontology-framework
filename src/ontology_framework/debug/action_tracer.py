# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

import logging
import json
from typing import Dict, Any, Optional, List, Set
from pathlib import Path
from datetime import datetime
import threading
from contextlib import contextmanager
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ActionStatus(Enum):
    """Action status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class ActionContext:
    """Context for an action."""
    action_id: str
    action_type: str
    parent_id: Optional[str]
    timestamp: str
    status: ActionStatus
    metadata: Dict[str, Any]
    dependencies: Set[str]
    dependents: Set[str]
    error: Optional[str] = None

class ActionTracer:
    """Debug tool for tracing action flow and dependencies."""
    
    def __init__(self, enabled: bool = False):
        """Initialize the action tracer.
        
        Args:
            enabled: Whether the tracer is enabled
        """
        self.enabled = enabled
        self.actions: Dict[str, ActionContext] = {}
        self.action_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup debug logging."""
        if not self.enabled:
            return
            
        self.log_dir = Path("logs/debug/actions")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.log_dir / f"action_tracer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
    
    def _generate_action_id(self) -> str:
        """Generate a unique action ID."""
        return str(uuid.uuid4())
    
    def _log_action_update(self, action: ActionContext):
        """Log an action update.
        
        Args:
            action: Action context to log
        """
        if not self.enabled:
            return
            
        logger.debug(
            f"Action update - ID: {action.action_id}, "
            f"Type: {action.action_type}, "
            f"Status: {action.status.value}"
        )
        
        # Add to history
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_id': action.action_id,
            'action_type': action.action_type,
            'status': action.status.value,
            'parent_id': action.parent_id,
            'metadata': action.metadata,
            'dependencies': list(action.dependencies),
            'dependents': list(action.dependents),
            'error': action.error
        }
        self.action_history.append(history_entry)
    
    def start_action(
        self,
        action_type: str,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        dependencies: Optional[Set[str]] = None
    ) -> str:
        """Start tracking a new action.
        
        Args:
            action_type: Type of action
            parent_id: Optional parent action ID
            metadata: Optional action metadata
            dependencies: Optional set of dependency action IDs
            
        Returns:
            str: Generated action ID
        """
        if not self.enabled:
            return self._generate_action_id()
            
        with self._lock:
            action_id = self._generate_action_id()
            
            # Create action context
            action = ActionContext(
                action_id=action_id,
                action_type=action_type,
                parent_id=parent_id,
                timestamp=datetime.now().isoformat(),
                status=ActionStatus.PENDING,
                metadata=metadata or {},
                dependencies=dependencies or set(),
                dependents=set()
            )
            
            # Update dependency relationships
            if dependencies:
                for dep_id in dependencies:
                    if dep_id in self.actions:
                        self.actions[dep_id].dependents.add(action_id)
                        # Check if dependency is blocking
                        if self.actions[dep_id].status not in {
                            ActionStatus.COMPLETED, ActionStatus.FAILED
                        }:
                            action.status = ActionStatus.BLOCKED
            
            self.actions[action_id] = action
            self._log_action_update(action)
            
            return action_id
    
    def update_action(
        self,
        action_id: str,
        status: Optional[ActionStatus] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Update an action's state.
        
        Args:
            action_id: Action identifier
            status: Optional new status
            metadata: Optional metadata updates
            error: Optional error message
        """
        if not self.enabled:
            return
            
        with self._lock:
            if action_id not in self.actions:
                logger.warning(f"Attempted to update unknown action: {action_id}")
                return
                
            action = self.actions[action_id]
            
            # Update status
            if status:
                action.status = status
                
                # Update dependent actions
                if status == ActionStatus.COMPLETED:
                    for dep_id in action.dependents:
                        if dep_id in self.actions:
                            dep = self.actions[dep_id]
                            if dep.status == ActionStatus.BLOCKED:
                                # Check if all dependencies are complete
                                if all(
                                    self.actions[d].status == ActionStatus.COMPLETED
                                    for d in dep.dependencies
                                ):
                                    dep.status = ActionStatus.PENDING
                                    self._log_action_update(dep)
            
            # Update metadata
            if metadata:
                action.metadata.update(metadata)
            
            # Update error
            if error:
                action.error = error
            
            self._log_action_update(action)
    
    def complete_action(
        self,
        action_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Mark an action as completed or failed.
        
        Args:
            action_id: Action identifier
            metadata: Optional final metadata
            error: Optional error message (marks action as failed)
        """
        if not self.enabled:
            return
            
        status = ActionStatus.FAILED if error else ActionStatus.COMPLETED
        self.update_action(action_id, status, metadata, error)
    
    def get_action_state(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of an action.
        
        Args:
            action_id: Action identifier
            
        Returns:
            Optional[Dict[str, Any]]: Action state if found
        """
        if not self.enabled or action_id not in self.actions:
            return None
            
        with self._lock:
            return asdict(self.actions[action_id])
    
    def get_blocked_actions(self) -> List[str]:
        """Get list of blocked action IDs.
        
        Returns:
            List[str]: List of blocked action IDs
        """
        if not self.enabled:
            return []
            
        with self._lock:
            return [
                action_id
                for action_id, action in self.actions.items()
                if action.status == ActionStatus.BLOCKED
            ]
    
    def get_action_chain(self, action_id: str) -> List[Dict[str, Any]]:
        """Get the chain of actions leading to this action.
        
        Args:
            action_id: Action identifier
            
        Returns:
            List[Dict[str, Any]]: Chain of action states
        """
        if not self.enabled or action_id not in self.actions:
            return []
            
        with self._lock:
            chain = []
            current_id = action_id
            
            while current_id:
                action = self.actions[current_id]
                chain.append(asdict(action))
                current_id = action.parent_id
                
            return list(reversed(chain))
    
    def export_trace(self, export_path: Optional[Path] = None) -> None:
        """Export action trace to file.
        
        Args:
            export_path: Optional path to export to
        """
        if not self.enabled:
            return
            
        with self._lock:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_path is None:
                export_path = self.log_dir / f"action_trace_{timestamp}.json"
            
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'actions': {
                    action_id: asdict(action)
                    for action_id, action in self.actions.items()
                },
                'history': self.action_history
            }
            
            export_path.write_text(json.dumps(export_data, indent=2))
            logger.info(f"Action trace exported to {export_path}")
    
    @contextmanager
    def trace_action(
        self,
        action_type: str,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        dependencies: Optional[Set[str]] = None
    ):
        """Context manager for tracing an action.
        
        Args:
            action_type: Type of action
            parent_id: Optional parent action ID
            metadata: Optional action metadata
            dependencies: Optional set of dependency action IDs
        """
        if not self.enabled:
            yield None
            return
            
        action_id = self.start_action(action_type, parent_id, metadata, dependencies)
        self.update_action(action_id, ActionStatus.RUNNING)
        
        try:
            yield action_id
            self.complete_action(action_id)
        except Exception as e:
            self.complete_action(action_id, error=str(e))
            raise 