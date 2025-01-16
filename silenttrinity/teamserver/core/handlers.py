# silenttrinity/silenttrinity/teamserver/core/handlers.py

import json
import asyncio
from datetime import datetime
from teamserver.core.utils.logger import StructuredLogger

logger = StructuredLogger('MessageHandlers')

class MessageHandlers:
    def __init__(self, server):
        self.server = server
        self.register_handlers()
        logger.debug("MessageHandlers initialized and handlers registered")
    
    def register_handlers(self):
        """Register all message handlers with the server"""
        self.server.register_handler('checkin', self.handle_checkin)
        self.server.register_handler('task_result', self.handle_task_result)
        self.server.register_handler('error', self.handle_error)
        logger.debug("All message handlers registered")
    
    async def handle_checkin(self, data, session_id):
        """Handle initial client checkin"""
        hostname = data.get('hostname')
        username = data.get('username')
        os_info = data.get('os')
    
        # Update session info
        session = self.server.sessions.get(session_id)
        if session:
            session['info'].update({
                'hostname': hostname,
                'username': username,
                'os': os_info,
                'last_checkin': datetime.now().isoformat()
            })
            logger.info(f"Session {session_id} checkin updated: hostname={hostname}, username={username}, os={os_info}")
    
        return {
            'type': 'checkin_response',
            'status': 'success',
            'session_id': session_id
        }
    
    async def handle_task_result(self, data, session_id):
        """Handle task execution results"""
        task_id = data.get('task_id')
        result = data.get('result')
    
        # Process and store task result
        # TODO: Implement result storage
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
    
        logger.error(f"Error from session {session_id}: {error_type} - {error_msg}")
    
        return {
            'type': 'error_response',
            'status': 'received'
        }
