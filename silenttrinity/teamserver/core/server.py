# silenttrinity/silenttrinity/teamserver/core/server.py

import asyncio
import logging
from teamserver.core.websocket import SecureWebSocketServer
from teamserver.core.ipc import IPCServer
from teamserver.core.utils.ports import find_free_port
from teamserver.core.utils.logger import StructuredLogger

class TeamServer:
    """
    TeamServer orchestrates the WebSocket server and the IPC server.
    Each TeamServer instance can run on different ports/hosts, supporting multi-server setups.
    """
    def __init__(self, host='0.0.0.0', ws_port=8765, secure=False, zmq_public_key=None, zmq_secret_key=None):
        self.host = host
        self.ws_port = ws_port
        self.secure = secure
        self.zmq_public_key = zmq_public_key
        self.zmq_secret_key = zmq_secret_key
        
        self.websocket_server = None
        self.ipc_server = None
        self.logger = StructuredLogger('TeamServer').logger
        self.healthy = False

    async def health_check(self):
        """Simple health check routine."""
        while True:
            if self.websocket_server and self.ipc_server:
                self.healthy = True
            else:
                self.healthy = False
            await asyncio.sleep(5)
        
    async def start(self):
        try:
            self.logger.info("Initializing servers for multi-user/multi-server usage...")
            
            # Initialize the IPC server with ephemeral keys if secure
            self.ipc_server = IPCServer(
                secure=self.secure,
                server_public_key=self.zmq_public_key,
                server_secret_key=self.zmq_secret_key
            )
            
            # Initialize WebSocket (secure or insecure)
            self.websocket_server = SecureWebSocketServer(
                host=self.host,
                port=self.ws_port,
                ipc_server=self.ipc_server,
                secure=self.secure
            )
            
            self.logger.info(f"Starting Team Server on {self.host}:{self.ws_port} (secure={self.secure})...")

            # Register IPC event handlers
            self.ipc_server.register_handler(b'client_connected', self.handle_client_connected)
            self.ipc_server.register_handler(b'client_disconnected', self.handle_client_disconnected)
            
            tasks = [
                asyncio.create_task(self.ipc_server.start(), name="IPCServer"),
                asyncio.create_task(self.websocket_server.start(), name="WebSocketServer"),
                asyncio.create_task(self.health_check(), name="HealthCheck"),
            ]
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.error(f"Failed to start Team Server: {str(e)}")
            raise
        
    async def handle_client_connected(self, message):
        self.logger.info(f"IPC: new client connected -> {message}")
        
    async def handle_client_disconnected(self, message):
        self.logger.info(f"IPC: client disconnected -> {message}")
    
    async def stop(self):
        self.logger.info("Stopping Team Server gracefully...")
        try:
            if self.websocket_server:
                await self.websocket_server.stop()
            if self.ipc_server:
                await self.ipc_server.stop()
            self.logger.info("Team Server stopped successfully.")
        except Exception as e:
            self.logger.error(f"Error stopping Team Server: {str(e)}")
            raise
