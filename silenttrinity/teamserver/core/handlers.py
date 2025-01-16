import json
import asyncio
from datetime import datetime

class MessageHandlers:
    def __init__(self, server):
        self.server = server
        self.register_handlers()
    
    def register_handlers(self):
        """Register all message handlers with the server"""
        self.server.register_handler('checkin', self.handle_checkin)
        self.server.register_handler('task_result', self.handle_task_result)
        self.server.register_handler('error', self.handle_error)
    
    async def handle_checkin(self, data, session_id):
        """Handle initial client checkin"""
        # Update session info
        self.server.sessions[session_id]['info'].update({
            'hostname': data.get('hostname'),
            'username': data.get('username'),
            'os': data.get('os'),
            'last_checkin': datetime.now()
        })
        
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
        
        return {
            'type': 'task_result_response',
            'status': 'received',
            'task_id': task_id
        }
    
    async def handle_error(self, data, session_id):
        """Handle error messages from clients"""
        error_type = data.get('error_type')
        error_msg = data.get('message')
        
        print(f"Error from {session_id}: {error_type} - {error_msg}")
        
        return {
            'type': 'error_response',
            'status': 'received'
        }