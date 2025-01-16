# silenttrinity/silenttrinity/teamserver/management/commands/start_c2server.py

from django.core.management.base import BaseCommand
import asyncio
from teamserver.core.websocket import C2Server
from teamserver.core.handlers import MessageHandlers
from teamserver.core.utils.logger import StructuredLogger
import platform
import psutil
import sys

class Command(BaseCommand):
    help = 'Start the C2 WebSocket server'
    
    def __init__(self):
        super().__init__()
        self.logger = StructuredLogger('C2Management')

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            default='0.0.0.0',
            help='Host to bind the server to'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=5000,
            help='Port to bind the server to'
        )

    def log_system_info(self):
        """Log system information at startup"""
        self.logger.info("="*50)
        self.logger.info("System Information")
        self.logger.info("="*50)
        self.logger.info(f"OS: {platform.system()} {platform.release()}")
        self.logger.info(f"Python Version: {sys.version.split()[0]}")
        self.logger.info(f"CPU Cores: {psutil.cpu_count(logical=True)}")
        memory = psutil.virtual_memory()
        self.logger.info(f"Memory: {memory.total // (1024*1024*1024)}GB Total, {memory.percent}% Used")
        self.logger.info("="*50)

    def handle(self, *args, **options):
        # Log system information
        self.log_system_info()
        
        # Create and configure server
        server = C2Server(
            host=options['host'],
            port=options['port']
        )
        
        # Initialize message handlers
        handlers = MessageHandlers(server)
        
        # Start server
        try:
            asyncio.run(server.start())
        except KeyboardInterrupt:
            self.logger.info("Server shutdown initiated by user")
            self.stdout.write(self.style.SUCCESS('Server stopped'))
        except Exception as e:
            self.logger.critical(f"Server crashed: {str(e)}", exc_info=True)
            self.stdout.write(self.style.ERROR(f'Server error: {str(e)}'))
