# silenttrinity/silenttrinity/teamserver/management/commands/start_c2server.py

from django.core.management.base import BaseCommand
import asyncio
from teamserver.core.websocket import C2Server
from teamserver.core.handlers import MessageHandlers

class Command(BaseCommand):
    help = 'Start the C2 WebSocket server'

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

    def handle(self, *args, **options):
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
            self.stdout.write(self.style.SUCCESS('Server stopped'))