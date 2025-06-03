# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class StateInspector:
    """Debug tool for inspecting client and server state."""
    
    def __init__(self, enabled: bool = False):
        """Initialize the state inspector.
        
        Args:
            enabled: Whether the inspector is enabled
        """
        self.enabled = enabled
        self.state_history: List[Dict[str, Any]] = []
        self.current_state: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup debug logging."""
        if not self.enabled:
            return
            
        self.log_dir = Path("logs/debug/state")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.log_dir / f"state_inspector_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)
    
    def track_client(self, client_id: str, state: Dict[str, Any]):
        """Track client state changes.
        
        Args:
            client_id: Client identifier
            state: Current client state
        """
        if not self.enabled:
            return
            
        with self._lock:
            timestamp = datetime.now().isoformat()
            
            # Update current state
            if 'clients' not in self.current_state:
                self.current_state['clients'] = {}
            self.current_state['clients'][client_id] = {
                'state': state,
                'last_updated': timestamp
            }
            
            # Add to history
            self.state_history.append({
                'timestamp': timestamp,
                'type': 'client_state',
                'client_id': client_id,
                'state': state
            })
            
            logger.debug(f"Client state update - ID: {client_id}, State: {json.dumps(state)}")
    
    def track_server(self, server_id: str, state: Dict[str, Any]):
        """Track server state changes.
        
        Args:
            server_id: Server identifier
            state: Current server state
        """
        if not self.enabled:
            return
            
        with self._lock:
            timestamp = datetime.now().isoformat()
            
            # Update current state
            if 'servers' not in self.current_state:
                self.current_state['servers'] = {}
            self.current_state['servers'][server_id] = {
                'state': state,
                'last_updated': timestamp
            }
            
            # Add to history
            self.state_history.append({
                'timestamp': timestamp,
                'type': 'server_state',
                'server_id': server_id,
                'state': state
            })
            
            logger.debug(f"Server state update - ID: {server_id}, State: {json.dumps(state)}")
    
    def track_action(self, action_id: str, action_type: str, state: Dict[str, Any]):
        """Track action state changes.
        
        Args:
            action_id: Action identifier
            action_type: Type of action
            state: Current action state
        """
        if not self.enabled:
            return
            
        with self._lock:
            timestamp = datetime.now().isoformat()
            
            # Update current state
            if 'actions' not in self.current_state:
                self.current_state['actions'] = {}
            self.current_state['actions'][action_id] = {
                'type': action_type,
                'state': state,
                'last_updated': timestamp
            }
            
            # Add to history
            self.state_history.append({
                'timestamp': timestamp,
                'type': 'action_state',
                'action_id': action_id,
                'action_type': action_type,
                'state': state
            })
            
            logger.debug(f"Action state update - ID: {action_id}, Type: {action_type}, State: {json.dumps(state)}")
    
    def get_client_state(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of a client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Optional[Dict[str, Any]]: Client state if found
        """
        if not self.enabled:
            return None
            
        with self._lock:
            return self.current_state.get('clients', {}).get(client_id)
    
    def get_server_state(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of a server.
        
        Args:
            server_id: Server identifier
            
        Returns:
            Optional[Dict[str, Any]]: Server state if found
        """
        if not self.enabled:
            return None
            
        with self._lock:
            return self.current_state.get('servers', {}).get(server_id)
    
    def get_action_state(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of an action.
        
        Args:
            action_id: Action identifier
            
        Returns:
            Optional[Dict[str, Any]]: Action state if found
        """
        if not self.enabled:
            return None
            
        with self._lock:
            return self.current_state.get('actions', {}).get(action_id)
    
    def get_history(self, entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get state history, optionally filtered by entity ID.
        
        Args:
            entity_id: Optional entity identifier to filter by
            
        Returns:
            List[Dict[str, Any]]: State history
        """
        if not self.enabled:
            return []
            
        with self._lock:
            if entity_id:
                return [
                    entry for entry in self.state_history
                    if entry.get('client_id') == entity_id
                    or entry.get('server_id') == entity_id
                    or entry.get('action_id') == entity_id
                ]
            return self.state_history.copy()
    
    def export_state(self, export_path: Optional[Path] = None) -> None:
        """Export current state and history to file.
        
        Args:
            export_path: Optional path to export to
        """
        if not self.enabled:
            return
            
        with self._lock:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_path is None:
                export_path = self.log_dir / f"state_export_{timestamp}.json"
            
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'current_state': self.current_state,
                'history': self.state_history
            }
            
            export_path.write_text(json.dumps(export_data, indent=2))
            logger.info(f"State exported to {export_path}")
    
    @contextmanager
    def track_operation(self, operation_id: str, operation_type: str):
        """Context manager for tracking operation state.
        
        Args:
            operation_id: Operation identifier
            operation_type: Type of operation
        """
        if not self.enabled:
            yield
            return
            
        try:
            self.track_action(
                operation_id,
                operation_type,
                {'status': 'started', 'timestamp': datetime.now().isoformat()}
            )
            yield
            self.track_action(
                operation_id,
                operation_type,
                {'status': 'completed', 'timestamp': datetime.now().isoformat()}
            )
        except Exception as e:
            self.track_action(
                operation_id,
                operation_type,
                {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            )
            raise 