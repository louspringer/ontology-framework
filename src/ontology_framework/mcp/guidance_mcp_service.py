"""
Guidance MCP service implementation.
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional, TextIO
from .core import MCPServer

class GuidanceMCPService:
    """Service for handling MCP server lifecycle."""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

    async def _read_request(self) -> Optional[Dict[str, Any]]:
        """Read request from stdin."""
        try:
            line = await self.reader.readline()
            if not line:
                return None
            return json.loads(line.decode())
        except json.JSONDecodeError:
            return None

    async def _write_response(self, response: Dict[str, Any]) -> None:
        """Write response to stdout."""
        try:
            line = json.dumps(response) + "\n"
            self.writer.write(line.encode())
            await self.writer.drain()
        except Exception as e:
            print(f"Error writing response: {e}", file=sys.stderr)

    async def _handle_connection(self) -> None:
        """Handle connection lifecycle."""
        while True:
            request = await self._read_request()
            if request is None:
                break

            try:
                response = await self.server.handle_request(request)
                await self._write_response(response)
            except Exception as e:
                error_response = {
                    "error": str(e),
                    "request": request
                }
                await self._write_response(error_response)

    async def run(self) -> None:
        """Run the service."""
        # Use stdin/stdout for communication
        loop = asyncio.get_event_loop()
        self.reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(self.reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        
        transport, protocol = await loop.connect_write_pipe(
            asyncio.streams.FlowControlMixin, 
            sys.stdout
        )
        self.writer = asyncio.StreamWriter(transport, protocol, self.reader, loop)

        try:
            if self.server.lifespan:
                async with self.server.lifespan(self.server) as context:
                    self.server.request_context = context
                    await self._handle_connection()
            else:
                await self._handle_connection()
        finally:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed() 