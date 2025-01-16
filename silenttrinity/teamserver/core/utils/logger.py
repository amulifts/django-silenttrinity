# silenttrinity/silenttrinity/teamserver/core/utils/logger.py

# teamserver/core/utils/logger.py

# teamserver/core/utils/logger.py

# teamserver/core/utils/logger.py

import logging
import sys
from datetime import datetime
from pathlib import Path
import coloredlogs

class C2Logger:
    """Custom logger for C2 server operations"""
    
    LEVELS = {
        'DEBUG': {'color': 'white'},
        'INFO': {'color': 'green'},
        'WARNING': {'color': 'yellow'},
        'ERROR': {'color': 'red'},
        'CRITICAL': {'color': 'red', 'bold': True}
    }
    
    def __init__(self, name='C2Server'):
        self.logger = logging.getLogger(name)
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging format and outputs"""
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Generate log filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'c2_server_{timestamp}.log'
        
        # Set up file handler
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Set up console handler with colored output
        coloredlogs.install(
            level='DEBUG',
            logger=self.logger,
            fmt='%(asctime)s [%(levelname)s] %(message)s',
            level_styles=self.LEVELS
        )
        
        # Add file handler
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
    
    # Custom logging methods...
    def server_start(self, host, port):
        """Log server start information"""
        self.logger.info("="*50)
        self.logger.info("C2 Server Initialization")
        self.logger.info("="*50)
        self.logger.info(f"Starting server on ws://{host}:{port}")
        self.logger.debug("Server configuration loaded")
        
    def client_connect(self, client_id, address):
        """Log client connection"""
        self.logger.info(f"New client connection from {address} [ID: {client_id}]")
        
    def client_disconnect(self, client_id):
        """Log client disconnection"""
        self.logger.info(f"Client disconnected [ID: {client_id}]")
        
    def key_exchange(self, client_id):
        """Log key exchange events"""
        self.logger.debug(f"Key exchange initiated with client [ID: {client_id}]")
        
    def session_established(self, session_id):
        """Log session establishment"""
        self.logger.info(f"New session established [Session: {session_id}]")
        
    def command_executed(self, session_id, command):
        """Log command execution"""
        self.logger.debug(f"Command executed [Session: {session_id}] - {command}")
        
    def error(self, message, exc_info=None):
        """Log error messages"""
        self.logger.error(message, exc_info=exc_info)
        
    def warning(self, message):
        """Log warning messages"""
        self.logger.warning(message)
        
    def critical(self, message, exc_info=True):
        """Log critical messages"""
        self.logger.critical(message, exc_info=exc_info)
    
    # Proxy standard logging methods
    def debug(self, message, *args, **kwargs):
        """Proxy debug messages to the internal logger"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """Proxy info messages to the internal logger"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Proxy warning messages to the internal logger"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Proxy error messages to the internal logger"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Proxy critical messages to the internal logger"""
        self.logger.critical(message, *args, **kwargs)
