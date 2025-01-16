# silenttrinity/silenttrinity/teamserver/core/server.py

import asyncio
import logging
import aiohttp
from .websocket import SecureWebSocketServer
from .ipc import IPCServer

class TeamServer:
    def __init__(self, host='0.0.0.0', ws_port=8765):
        self.host = host
        self.ws_port = ws_port
        self.websocket_server = None
        self.ipc_server = None
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('TeamServer')
        
        # Health status
        self.healthy = False
        
    async def health_check(self):
        """Simple in-process health check."""
        while True:
            # We consider ourselves healthy if both servers are running
            # In a more robust system, we'd check actual connectivity or stats
            if self.websocket_server and self.ipc_server:
                self.healthy = True
            else:
                self.healthy = False
            await asyncio.sleep(5)
        
    async def start(self):
        """Start the team server gracefully"""
        try:
            self.logger.info("Initializing servers...")
            
            self.websocket_server = SecureWebSocketServer(self.host, self.ws_port)
            self.ipc_server = IPCServer()
            
            self.logger.info("Starting Team Server tasks...")
            
            # Register IPC handlers (example)
            self.ipc_server.register_handler(b'client_connected', self.handle_client_connected)
            self.ipc_server.register_handler(b'client_disconnected', self.handle_client_disconnected)
            
            # Create tasks
            tasks = [
                asyncio.create_task(self.websocket_server.start(), name="WebSocketServer"),
                asyncio.create_task(self.ipc_server.start(), name="IPCServer"),
                asyncio.create_task(self.health_check(), name="HealthCheck"),
            ]
            
            # Run tasks concurrently
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.error(f"Failed to start Team Server: {str(e)}")
            raise
        
    async def handle_client_connected(self, message):
        self.logger.info(f"IPC: new client connected -> {message}")
        
    async def handle_client_disconnected(self, message):
        self.logger.info(f"IPC: client disconnected -> {message}")

    async def stop(self):
        """Stop the team server gracefully"""
        self.logger.info("Stopping Team Server...")
        try:
            if self.websocket_server:
                await self.websocket_server.stop()
            if self.ipc_server:
                await self.ipc_server.stop()
            self.logger.info("Team Server stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping Team Server: {str(e)}")
            raise
