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
import os
from pythonjsonlogger import jsonlogger
import coloredlogs

SENSITIVE_FIELDS = ["SECRET_KEY", "PASSWORD", "PRIVATE_KEY", "TOKEN"]

def redact_sensitive_data(record):
    """Mask sensitive data in log messages."""
    message = record.getMessage()
    for field in SENSITIVE_FIELDS:
        if field in message:
            message = message.replace(field, "[REDACTED]")
    record.msg = message
    return True

class JSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def __init__(self):
        super().__init__('%(asctime)s %(levelname)s %(name)s %(message)s')
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()
    
    def add_fields(self, log_record, record, message_dict):
        super(JSONFormatter, self).add_fields(log_record, record, message_dict)
        log_record['hostname'] = self.hostname
        log_record['username'] = self.username

class StructuredLogger:
    """Advanced structured logger with JSON output for files and colored console logs."""
    
    def __init__(self, name='C2Server'):
        self.logger = logging.getLogger(name)
        
        # Read log directory from environment or use default
        self.log_directory = os.getenv('C2_LOG_DIR', 'logs')
        
        self.setup_logging()
        self.session_id = str(uuid.uuid4())
    
    def setup_logging(self):
        self.logger.propagate = False
        
        # Avoid adding multiple handlers
        if not self.logger.handlers:
            # Create logs directory from config
            log_dir = Path(self.log_directory)
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f'c2_server_{timestamp}.json'
            
            file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
            file_handler.setFormatter(JSONFormatter())
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
            
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
            
            # Add a filter to redact sensitive info
            file_handler.addFilter(redact_sensitive_data)
            console_handler.addFilter(redact_sensitive_data)
            
            self.logger.addHandler(file_handler)
            
            # coloredlogs.install already attaches console_handler internally
            self.logger.setLevel(logging.DEBUG)
    
    def _log(self, level, message, **kwargs):
        extra = {
            "extra_fields": {
                "session_id": self.session_id,
                "timestamp_unix": datetime.utcnow().timestamp(),
                **kwargs
            }
        }
        self.logger.log(level, message, extra=extra)
    
    # Remainder of the StructuredLogger class stays the same, no changes needed
    # except that the logger is now utilizing the filter for sensitive data.
    
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
