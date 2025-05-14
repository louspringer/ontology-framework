import asyncio
import logging
from mcp.server.session import ServerSession

logger = logging.getLogger("mcp.server.sse")

class PatchedServerSession(ServerSession):
    async def _received_request(self, responder):
        retries = 5
        delay = 0.5

        # Wait for full initialization
        while not self.initialized and retries > 0:
            logger.debug("Waiting for session to initialize...")
            await asyncio.sleep(delay)
            retries -= 1

        if not self.initialized:
            logger.warning(f"Session {self.session_id} not initialized after {5 * delay:.1f}s")
            return  # Drop request silently or raise RuntimeError here if you prefer

        await super()._received_request(responder)

    async def _handle_request(self, request_id, responder):
        # Log every incoming request + session ID
        logger.debug(f"Handling request {request_id} in session {self.session_id}")
        await super()._handle_request(request_id, responder)
