import pytest
import os
import sys
from pathlib import Path
import json
import threading
import time
import uuid
import logging
from typing import Dict, Any, Optional

# Add src to Python path
project_root = Path(__file__).parent.parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from ontology_framework.debug.state_inspector import StateInspector
from ontology_framework.debug.action_tracer import ActionTracer
from ontology_framework.debug.debug_logger import DebugLogger, LogLevel

# Configure test logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestContext:
    """Test context with debug tools."""
    
    def __init__(self):
        """Initialize test context."""
        self.test_id = str(uuid.uuid4())
        self.debug_dir = project_root / "logs" / "debug" / "tests" / self.test_id
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize debug tools
        self.state_inspector = StateInspector(enabled=True)
        self.action_tracer = ActionTracer(enabled=True)
        self.debug_logger = DebugLogger(
            enabled=True,
            min_level=LogLevel.TRACE,
            log_dir=self.debug_dir
        )
        
        # Store original environment
        self.original_env = dict(os.environ)
    
    def cleanup(self):
        """Clean up test context."""
        # Export debug data
        self.debug_logger.export_metrics(self.debug_dir / "metrics.json")
        self.state_inspector.export_state(self.debug_dir / "state.json")
        self.action_tracer.export_trace(self.debug_dir / "trace.json")
        
        # Restore environment
        os.environ.clear()
        os.environ.update(self.original_env)

@pytest.fixture
def test_context():
    """Fixture for test context."""
    ctx = TestContext()
    yield ctx
    ctx.cleanup()

class TestMCPServer:
    """Tests for MCP server initialization and client handling."""
    
    def test_server_initialization(self, test_context):
        """Test server initialization process."""
        with test_context.debug_logger.operation("test_server_initialization"):
            from bfg9k_mcp import FastMCP, PatchedServerSession
            
            # Track test state
            test_context.state_inspector.track_server(
                'test_server', {'phase': 'initialization'}
            )
            
            try:
                # Create MCP instance
                mcp = FastMCP(
                    "Test MCP",
                    session_class=PatchedServerSession
                )
                
                # Track MCP state
                test_context.state_inspector.track_server(
                    'mcp', {'status': 'initialized'}
                )
                
                assert mcp is not None, "MCP instance should be created"
                
                # Start server in background thread
                server_thread = threading.Thread(
                    target=mcp.run,
                    args=('localhost', 8001),
                    daemon=True
                )
                server_thread.start()
                
                # Allow server to start
                time.sleep(1)
                
                # Track server state
                test_context.state_inspector.track_server(
                    'mcp', {'status': 'running'}
                )
                
                assert server_thread.is_alive(), "Server thread should be running"
                
            except Exception as e:
                test_context.debug_logger.error(
                    "Server initialization failed",
                    {'error': str(e)}
                )
                raise
    
    def test_client_creation(self, test_context):
        """Test client creation and tracking."""
        with test_context.debug_logger.operation("test_client_creation"):
            from bfg9k_mcp import FastMCP, PatchedServerSession
            
            # Track test state
            test_context.state_inspector.track_server(
                'test_server', {'phase': 'client_creation'}
            )
            
            try:
                # Create MCP instance
                mcp = FastMCP(
                    "Test MCP",
                    session_class=PatchedServerSession
                )
                
                # Start server in background thread
                server_thread = threading.Thread(
                    target=mcp.run,
                    args=('localhost', 8002),
                    daemon=True
                )
                server_thread.start()
                time.sleep(1)
                
                # Create multiple clients
                client_ids = []
                for i in range(3):
                    with test_context.action_tracer.trace_action(
                        "create_client",
                        metadata={'client_index': i}
                    ) as action_id:
                        client_id = f"test_client_{i}"
                        client_ids.append(client_id)
                        
                        # Track client state
                        test_context.state_inspector.track_client(
                            client_id,
                            {
                                'status': 'creating',
                                'index': i
                            }
                        )
                        
                        # Simulate client creation
                        time.sleep(0.1)
                        
                        test_context.state_inspector.track_client(
                            client_id,
                            {
                                'status': 'created',
                                'index': i
                            }
                        )
                
                # Verify client states
                for client_id in client_ids:
                    client_state = test_context.state_inspector.get_client_state(client_id)
                    assert client_state is not None, f"Client {client_id} state should exist"
                    assert client_state['state']['status'] == 'created', \
                        f"Client {client_id} should be created"
                
            except Exception as e:
                test_context.debug_logger.error(
                    "Client creation test failed",
                    {'error': str(e)}
                )
                raise
    
    def test_server_info_persistence(self, test_context):
        """Test server information persistence."""
        with test_context.debug_logger.operation("test_server_info_persistence"):
            from bfg9k_mcp import FastMCP, PatchedServerSession
            
            # Track test state
            test_context.state_inspector.track_server(
                'test_server', {'phase': 'server_info_persistence'}
            )
            
            try:
                # Create MCP instance
                mcp = FastMCP(
                    "Test MCP",
                    session_class=PatchedServerSession
                )
                
                # Start server in background thread
                server_thread = threading.Thread(
                    target=mcp.run,
                    args=('localhost', 8003),
                    daemon=True
                )
                server_thread.start()
                time.sleep(1)
                
                # Test server info persistence
                with test_context.action_tracer.trace_action("check_server_info"):
                    # Track initial state
                    test_context.state_inspector.track_server(
                        'mcp', {'status': 'checking_info'}
                    )
                    
                    # TODO: Add actual server info persistence checks
                    # This will depend on how server info is stored and accessed
                    
                    test_context.state_inspector.track_server(
                        'mcp', {'status': 'info_checked'}
                    )
                
            except Exception as e:
                test_context.debug_logger.error(
                    "Server info persistence test failed",
                    {'error': str(e)}
                )
                raise
    
    def test_action_handling(self, test_context):
        """Test action handling and dependencies."""
        with test_context.debug_logger.operation("test_action_handling"):
            from bfg9k_mcp import FastMCP, PatchedServerSession
            
            # Track test state
            test_context.state_inspector.track_server(
                'test_server', {'phase': 'action_handling'}
            )
            
            try:
                # Create MCP instance
                mcp = FastMCP(
                    "Test MCP",
                    session_class=PatchedServerSession
                )
                
                # Start server in background thread
                server_thread = threading.Thread(
                    target=mcp.run,
                    args=('localhost', 8004),
                    daemon=True
                )
                server_thread.start()
                time.sleep(1)
                
                # Test action handling
                with test_context.action_tracer.trace_action("test_actions"):
                    # Create a chain of dependent actions
                    action1_id = test_context.action_tracer.start_action(
                        "action1",
                        metadata={'description': 'First action'}
                    )
                    
                    action2_id = test_context.action_tracer.start_action(
                        "action2",
                        dependencies={action1_id},
                        metadata={'description': 'Second action'}
                    )
                    
                    action3_id = test_context.action_tracer.start_action(
                        "action3",
                        dependencies={action2_id},
                        metadata={'description': 'Third action'}
                    )
                    
                    # Complete actions in order
                    test_context.action_tracer.complete_action(action1_id)
                    test_context.action_tracer.complete_action(action2_id)
                    test_context.action_tracer.complete_action(action3_id)
                    
                    # Verify action chain
                    chain = test_context.action_tracer.get_action_chain(action3_id)
                    assert len(chain) == 1, "Action chain should have correct length"
                    
                    # Check for blocked actions
                    blocked = test_context.action_tracer.get_blocked_actions()
                    assert len(blocked) == 0, "No actions should be blocked"
                
            except Exception as e:
                test_context.debug_logger.error(
                    "Action handling test failed",
                    {'error': str(e)}
                )
                raise 