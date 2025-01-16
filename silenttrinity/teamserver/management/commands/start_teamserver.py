from django.core.management.base import BaseCommand
from django.conf import settings
import asyncio
import logging
import ssl
import argparse
import sys
import os

from teamserver.core.utils.crypto import CryptoManager
from teamserver.models import TeamServerUser

logger = logging.getLogger('teamserver')

class Command(BaseCommand):
    help = 'Start the SILENTTRINITY TeamServer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            default='0.0.0.0',
            help='Host to bind the TeamServer to'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=5000,
            help='Port to bind the TeamServer to'
        )
        parser.add_argument(
            '--ssl',
            action='store_true',
            help='Enable SSL/TLS'
        )
        parser.add_argument(
            '--cert',
            help='Path to SSL certificate'
        )
        parser.add_argument(
            '--key',
            help='Path to SSL private key'
        )

    def setup_logging(self):
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(log_dir, 'teamserver.log')
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    def handle(self, *args, **options):
        self.setup_logging()
        
        host = options['host']
        port = options['port']
        use_ssl = options['ssl']
        cert_path = options['cert']
        key_path = options['key']

        # Initialize crypto
        crypto = CryptoManager()
        
        # Setup SSL if enabled
        ssl_context = None
        if use_ssl:
            if not cert_path or not key_path:
                self.stderr.write(
                    'Error: --cert and --key are required when using SSL'
                )
                return
            
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_path, key_path)

        # Start TeamServer
        logger.info(f'Starting TeamServer on {host}:{port}')
        logger.info('SSL: ' + ('Enabled' if use_ssl else 'Disabled'))
        
        try:
            # Start WebSocket server
            from teamserver.core.websocket import WebSocketServer
            server = WebSocketServer()
            
            # Run the server
            asyncio.run(server.start(
                host=host,
                port=port,
                ssl_context=ssl_context
            ))
            
        except KeyboardInterrupt:
            logger.info('TeamServer shutdown requested')
        except Exception as e:
            logger.error(f'TeamServer error: {str(e)}')
            raise