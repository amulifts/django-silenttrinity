# silenttrinity/silenttrinity/teamserver/core/utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
import socket
import getpass
import platform
import uuid
import traceback
import json
from pythonjsonlogger import jsonlogger
import coloredlogs

class JSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def __init__(self):
        # Define the JSON format with desired fields
        super().__init__('%(asctime)s %(levelname)s %(name)s %(message)s')
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()
    
    def add_fields(self, log_record, record, message_dict):
        """Add additional fields to the log record."""
        super(JSONFormatter, self).add_fields(log_record, record, message_dict)
        log_record['hostname'] = self.hostname
        log_record['username'] = self.username
        # Add more fields as needed

class StructuredLogger:
    """Advanced structured logger with JSON output for files and colored output for console."""
    
    def __init__(self, name='C2Server'):
        self.logger = logging.getLogger(name)
        self.setup_logging()
        self.session_id = str(uuid.uuid4())
    
    def setup_logging(self):
        """Configure JSON structured logging for file and colored logging for console."""
        # Prevent log messages from being propagated to the root logger
        self.logger.propagate = False
        
        # Avoid adding multiple handlers if the logger is instantiated multiple times
        if not self.logger.handlers:
            # Create logs directory if it doesn't exist
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            # Generate log filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f'c2_server_{timestamp}.json'
            
            # Set up rotating JSON file handler
            file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)  # 5 MB per file
            file_handler.setFormatter(JSONFormatter())
            file_handler.setLevel(logging.DEBUG)
            
            # Set up console handler with coloredlogs
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            # Define a simple format for console
            console_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
            
            # Install coloredlogs for the console handler
            coloredlogs.install(
                level='DEBUG',
                logger=self.logger,
                fmt=console_format,
                datefmt='%Y-%m-%d %H:%M:%S',
                level_styles={
                    'debug': {'color': 'white'},
                    'info': {'color': 'green'},
                    'warning': {'color': 'yellow'},
                    'error': {'color': 'red'},
                    'critical': {'color': 'red', 'bold': True},
                }
            )
            
            # Add file handler to the logger
            self.logger.addHandler(file_handler)
            
            # No need to add console_handler explicitly as coloredlogs.install already configures it
        
            # Set the overall logging level
            self.logger.setLevel(logging.DEBUG)
    
    def _log(self, level, message, **kwargs):
        """Generic logging method with extra fields."""
        extra = {
            "extra_fields": {
                "session_id": self.session_id,
                "timestamp_unix": datetime.utcnow().timestamp(),
                **kwargs
            }
        }
        self.logger.log(level, message, extra=extra)
    
    # Logging methods for specific events
    def server_start(self, host, port, **kwargs):
        """Log server startup."""
        self._log(logging.INFO, "Server starting", 
             event="server_start",
             server={"host": host, "port": port},
             **kwargs)
    
    def client_connect(self, client_id, address, **kwargs):
        """Log client connection."""
        self._log(logging.INFO, "Client connected",
             event="client_connect",
             client={"id": client_id, "address": address},
             **kwargs)
    
    def client_disconnect(self, client_id, **kwargs):
        """Log client disconnection."""
        self._log(logging.INFO, "Client disconnected",
             event="client_disconnect",
             client={"id": client_id},
             **kwargs)
    
    def key_exchange(self, client_id, **kwargs):
        """Log key exchange."""
        self._log(logging.DEBUG, "Key exchange initiated",
             event="key_exchange",
             client={"id": client_id},
             **kwargs)
    
    def session_established(self, session_id, **kwargs):
        """Log session establishment."""
        self._log(logging.INFO, "Session established",
             event="session_established",
             session={"id": session_id},
             **kwargs)
    
    def command_executed(self, session_id, command, **kwargs):
        """Log command execution."""
        self._log(logging.DEBUG, "Command executed",
             event="command_executed",
             session={"id": session_id},
             command={"type": command},
             **kwargs)
    
    def crypto_operation(self, operation, status, **kwargs):
        """Log cryptographic operations."""
        self._log(logging.DEBUG, f"Crypto operation: {operation}",
             event="crypto_operation",
             crypto={"operation": operation, "status": status},
             **kwargs)
    
    def error(self, message, exc_info=None, **kwargs):
        """Log error with stack trace."""
        self._log(logging.ERROR, message,
             event="error",
             error={"exc_info": exc_info},
             **kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning."""
        self._log(logging.WARNING, message,
             event="warning",
             **kwargs)
    
    def critical(self, message, exc_info=True, **kwargs):
        """Log critical error."""
        self._log(logging.CRITICAL, message,
             event="critical",
             error={"exc_info": exc_info},
             **kwargs)
    
    # Proxy standard logging methods for flexibility
    def debug(self, message, *args, **kwargs):
        """Proxy debug messages to the internal logger."""
        self._log(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """Proxy info messages to the internal logger."""
        self._log(logging.INFO, message, *args, **kwargs)
