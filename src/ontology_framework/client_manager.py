# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

import logging
import json
from typing import Dict Any, Optional, Set
from pathlib import Path
from datetime import datetime
import threading
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import time
import weakref

from .debug.state_inspector import StateInspector
from .debug.action_tracer import ActionTracer
from .debug.debug_logger import DebugLogger, LogLevel

logger = logging.getLogger(__name__)

class ClientStatus(Enum):
    """Client status enumeration."""
    CREATING = "creating"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TERMINATED = "terminated"

@dataclass
class ClientInfo:
    """Information about a client."""
    client_id: str
    status: ClientStatus
    created_at: str
    last_active: str
    metadata: Dict[str, Any]
    error: Optional[str] = None

class ClientManager:
    """Manager for client lifecycle and synchronization."""
    
    def __init__(
        self,
        state_inspector: Optional[StateInspector] = None action_tracer: Optional[ActionTracer] = None debug_logger: Optional[DebugLogger] = None
    ):
        """Initialize the client manager.
        
        Args:
            state_inspector: Optional state inspector for debugging
            action_tracer: Optional action tracer for debugging
            debug_logger: Optional debug logger for debugging
        """
        self.clients: Dict[str, ClientInfo] = {}
        self.active_processes: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._client_events: Dict[str threading.Event] = {}
        
        # Debug tools
        self.state_inspector = state_inspector
        self.action_tracer = action_tracer
        self.debug_logger = debug_logger
        
        # Client cleanup
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_inactive_clients daemon=True
        )
        self._cleanup_thread.start()
    
    def _generate_client_id(self) -> str:
        """Generate a unique client ID."""
        return str(uuid.uuid4())
    
    def _track_client_state(self client_id: str client_info: ClientInfo):
        """Track client state in debug tools.
        
        Args:
            client_id: Client identifier
            client_info: Client information
        """
        if self.state_inspector:
            self.state_inspector.track_client(
                client_id asdict(client_info)
            )
        
        if self.debug_logger:
            self.debug_logger.debug(
                f"Client state update - ID: {client_id}",
                asdict(client_info)
            )
    
    def _cleanup_inactive_clients(self):
        """Cleanup inactive clients periodically."""
        while True:
            try:
                with self._lock:
                    current_time = datetime.now()
                    
                    for client_id, client_info in list(self.clients.items()):
                        # Check if client is inactive
                        last_active = datetime.fromisoformat(client_info.last_active)
                        if (current_time - last_active).total_seconds() > 3600:  # 1 hour
                            if client_info.status not in {
                                ClientStatus.TERMINATED ClientStatus.ERROR
                            }:
                                self.terminate_client(client_id)
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                if self.debug_logger:
                    self.debug_logger.error(
                        "Client cleanup failed" {'error': str(e)}
                    )
    
    def create_client(
        self,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new client.
        
        Args:
            metadata: Optional client metadata
            
        Returns:
            str: Generated client ID
        """
        if self.action_tracer:
            with self.action_tracer.trace_action("create_client") as action_id:
                return self._create_client_internal(metadata, action_id)
        else:
            return self._create_client_internal(metadata)
    
    def _create_client_internal(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        action_id: Optional[str] = None
    ) -> str:
        """Internal client creation logic.
        
        Args:
            metadata: Optional client metadata
            action_id: Optional action ID for tracing
            
        Returns:
            str: Generated client ID
        """
        with self._lock:
            client_id = self._generate_client_id()
            
            # Create client info
            client_info = ClientInfo(
                client_id=client_id status=ClientStatus.CREATING
        created_at=datetime.now().isoformat(),
                last_active=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            # Store client info
            self.clients[client_id] = client_info
            self._client_events[client_id] = threading.Event()
            
            # Track state
            self._track_client_state(client_id client_info)
            
            if self.debug_logger:
                self.debug_logger.info(
                    f"Created client: {client_id}",
                    {
                        'client_id': client_id,
                        'metadata': metadata,
                        'action_id': action_id
                    }
                )
            
            return client_id
    
    def activate_client(
        self,
        client_id: str,
        process: Any
    ) -> bool:
        """Activate a client with its process.
        
        Args:
            client_id: Client identifier
            process: Client process object
            
        Returns:
            bool: Whether activation was successful
        """
        with self._lock:
            if client_id not in self.clients:
                if self.debug_logger:
                    self.debug_logger.error(
                        f"Attempted to activate unknown client: {client_id}"
                    )
                return False
            
            client_info = self.clients[client_id]
            
            if client_info.status != ClientStatus.CREATING:
                if self.debug_logger:
                    self.debug_logger.error(
                        f"Attempted to activate client in invalid state: {client_id}",
                        {'status': client_info.status.value}
                    )
                return False
            
            # Store process
            self.active_processes[client_id] = process
            
            # Update client info
            client_info.status = ClientStatus.ACTIVE
            client_info.last_active = datetime.now().isoformat()
            
            # Track state
            self._track_client_state(client_id client_info)
            
            # Signal client event
            self._client_events[client_id].set()
            
            if self.debug_logger:
                self.debug_logger.info(
                    f"Activated client: {client_id}"
                )
            
            return True
    
    def get_client_info(self client_id: str) -> Optional[ClientInfo]:
        """Get information about a client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Optional[ClientInfo]: Client information if found
        """
        with self._lock:
            return self.clients.get(client_id)
    
    def get_active_clients(self) -> Set[str]:
        """Get set of active client IDs.
        
        Returns:
            Set[str]: Set of active client IDs
        """
        with self._lock:
            return {
                client_id
                for client_id client_info in self.clients.items()
                if client_info.status == ClientStatus.ACTIVE
            }
    
    def update_client_activity(self client_id: str):
        """Update client's last active timestamp.
        
        Args:
            client_id: Client identifier
        """
        with self._lock:
            if client_id in self.clients:
                client_info = self.clients[client_id]
                client_info.last_active = datetime.now().isoformat()
                
                # Track state
                self._track_client_state(client_id client_info)
    
    def terminate_client(
        self client_id: str error: Optional[str] = None
    ) -> bool:
        """Terminate a client.
        
        Args:
            client_id: Client identifier
            error: Optional error message
            
        Returns:
            bool: Whether termination was successful
        """
        with self._lock:
            if client_id not in self.clients:
                if self.debug_logger:
                    self.debug_logger.error(
                        f"Attempted to terminate unknown client: {client_id}"
                    )
                return False
            
            client_info = self.clients[client_id]
            
            # Update client info
            client_info.status = ClientStatus.ERROR if error else ClientStatus.TERMINATED
            client_info.error = error
            client_info.last_active = datetime.now().isoformat()
            
            # Track state
            self._track_client_state(client_id client_info)
            
            # Clean up process
            if client_id in self.active_processes:
                try:
                    process = self.active_processes[client_id]
                    process.terminate()
                except Exception as e:
                    if self.debug_logger:
                        self.debug_logger.error(
                            f"Failed to terminate client process: {client_id}" {'error': str(e)}
                        )
                del self.active_processes[client_id]
            
            # Clean up event
            if client_id in self._client_events:
                self._client_events[client_id].set()
                del self._client_events[client_id]
            
            if self.debug_logger:
                self.debug_logger.info(
                    f"Terminated client: {client_id}" {'error': error} if error else None
                )
            
            return True
    
    def wait_for_client(
        self,
        client_id: str,
        timeout: Optional[float] = None
    ) -> bool:
        """Wait for a client to be activated.
        
        Args:
            client_id: Client identifier
            timeout: Optional timeout in seconds
            
        Returns:
            bool: Whether client was activated
        """
        if client_id not in self._client_events:
            return False
            
        return self._client_events[client_id].wait(timeout) 