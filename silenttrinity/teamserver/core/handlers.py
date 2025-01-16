# silenttrinity/silenttrinity/teamserver/core/handlers.py

import json
import asyncio
from datetime import datetime
from teamserver.core.utils.logger import StructuredLogger

logger = StructuredLogger('MessageHandlers')

# A simple in-memory dictionary to store task results (for demonstration).
TASK_RESULTS = {}

class MessageHandlers:
    def __init__(self, server):
        self.server = server
        self.register_handlers()
        logger.debug("MessageHandlers initialized and handlers registered")
    
    def register_handlers(self):
        self.server.register_handler('checkin', self.handle_checkin)
        self.server.register_handler('task_result', self.handle_task_result)
        self.server.register_handler('error', self.handle_error)
        logger.debug("All message handlers registered")
    
    async def handle_checkin(self, data, session_id):
        """Handle initial client checkin"""
        if not isinstance(data, dict):
            logger.error("Checkin data must be a dictionary")
            return {'type': 'error', 'message': 'Invalid data format'}
        
        hostname = data.get('hostname')
        username = data.get('username')
        os_info = data.get('os')
        
        # Validate inputs
        if not hostname or not username or not os_info:
            return {'type': 'error', 'message': 'Missing hostname, username, or os info'}
    
        session = self.server.sessions.get(session_id)
        if session:
            session['info'].update({
                'hostname': hostname,
                'username': username,
                'os': os_info,
                'last_checkin': datetime.now().isoformat()
            })
            logger.info(f"Session {session_id} checkin updated: hostname={hostname}, username={username}, os={os_info}")
        else:
            logger.error(f"Session {session_id} not found during checkin")
            return {'type': 'error', 'message': 'Session not found'}
    
        return {
            'type': 'checkin_response',
            'status': 'success',
            'session_id': session_id
        }
    
    async def handle_task_result(self, data, session_id):
        """Handle task execution results"""
        if not isinstance(data, dict):
            logger.error("Task result data must be a dictionary")
            return {'type': 'error', 'message': 'Invalid data format'}

        task_id = data.get('task_id')
        result = data.get('result')
        
        if not task_id or result is None:
            logger.error("Task result missing 'task_id' or 'result'")
            return {'type': 'error', 'message': 'Missing task_id or result'}
        
        # Store the result
        TASK_RESULTS[task_id] = {
            'session_id': session_id,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        logger.info(f"Received task_result from session {session_id}: task_id={task_id}, result={result}")
    
        return {
            'type': 'task_result_response',
            'status': 'received',
            'task_id': task_id
        }
    
    async def handle_error(self, data, session_id):
        """Handle error messages from clients"""
        error_type = data.get('error_type')
        error_msg = data.get('message')
        
        if not error_type or not error_msg:
            logger.error("Error message missing 'error_type' or 'message'")
            return {'type': 'error', 'message': 'Invalid error data'}
        
        logger.error(f"Error from session {session_id}: {error_type} - {error_msg}")
    
        return {
            'type': 'error_response',
            'status': 'received'
        }
