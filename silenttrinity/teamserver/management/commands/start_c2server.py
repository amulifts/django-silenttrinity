# silenttrinity/silenttrinity/teamserver/management/commands/start_c2server.py

from django.core.management.base import BaseCommand
import asyncio
import platform
import psutil
import sys
import os
import hashlib
import zmq
from teamserver.core.server import TeamServer
from teamserver.core.utils.logger import StructuredLogger

class Command(BaseCommand):
    help = 'Start the TeamServer. Supports multi-server by picking random ports for the IPC server, and secure mode with ephemeral keys.'

    def __init__(self):
        super().__init__()
        self.logger = StructuredLogger('C2Management')

    def add_arguments(self, parser):
        parser.add_argument('--host', default='0.0.0.0', help='Host/IP for the WebSocket server.')
        parser.add_argument('--port', type=int, default=8765, help='Port for the WebSocket server.')
        parser.add_argument('--secure', action='store_true', help='Enable secure mode (wss for WebSocket, curve encryption for IPC).')
        parser.add_argument('--insecure', action='store_true', help='Run in insecure mode (ws for WebSocket, no curve encryption).')

    def log_system_info(self):
        self.logger.info("=" * 50)
        self.logger.info("System Information")
        self.logger.info("=" * 50)
        self.logger.info(f"OS: {platform.system()} {platform.release()}")
        self.logger.info(f"Python Version: {sys.version.split()[0]}")
        self.logger.info(f"CPU Cores: {psutil.cpu_count(logical=True)}")
        memory = psutil.virtual_memory()
        self.logger.info(f"Memory: {memory.total // (1024*1024*1024)}GB Total, {memory.percent}% Used")
        self.logger.info("=" * 50)

    def handle(self, *args, **options):
        self.log_system_info()
        
        secure_mode = options.get('secure', False)
        insecure_mode = options.get('insecure', False)

        if secure_mode and insecure_mode:
            self.stdout.write(self.style.ERROR("Cannot specify both --secure and --insecure. Pick one."))
            return
        if not secure_mode and not insecure_mode:
            # Default to insecure if neither is specified
            insecure_mode = True

        protocol = 'wss' if secure_mode else 'ws'
        host = options['host']
        port = options['port']
        
        # If user chooses secure, generate ephemeral curve keypair for ZeroMQ
        zmq_server_public = None
        zmq_server_secret = None
        if secure_mode:
            # Generate ephemeral curve key pair
            zmq_server_public, zmq_server_secret = zmq.curve_keypair()
            # Compute a "fingerprint" (SHA-256 hex) of the public key for user
            fingerprint = hashlib.sha256(zmq_server_public).hexdigest()
            self.stdout.write(self.style.WARNING(f"Teamserver certificate fingerprint: {fingerprint}"))
            self.stdout.write(self.style.WARNING("Ephemeral ZeroMQ curve keys generated."))
        else:
            self.stdout.write(self.style.WARNING("Running in insecure mode. ZeroMQ traffic & WebSocket will NOT be encrypted."))

        self.stdout.write(self.style.NOTICE(f"Initializing TeamServer on {protocol}://{host}:{port}..."))
        
        # Prepare environment or pass directly to constructor
        # We'll pass them directly in constructor for demonstration:
        server = TeamServer(
            host=host,
            ws_port=port,
            secure=secure_mode,
            zmq_public_key=zmq_server_public,
            zmq_secret_key=zmq_server_secret
        )
        
        try:
            asyncio.run(server.start())
        except KeyboardInterrupt:
            self.logger.info("Server shutdown initiated by user (Ctrl+C).")
            self.stdout.write(self.style.SUCCESS("Server stopped by user."))
        except Exception as e:
            self.logger.critical(f"Server crashed: {str(e)}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Server error: {str(e)}"))
        finally:
            try:
                asyncio.run(server.stop())
            except Exception as e:
                self.logger.error(f"Error stopping server: {str(e)}")
                self.stdout.write(self.style.ERROR(f"Error on shutdown: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("TeamServer has fully stopped."))
