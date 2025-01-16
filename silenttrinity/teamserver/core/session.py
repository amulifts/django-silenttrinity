from datetime import datetime, timedelta
import json

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(minutes=30)  # Default timeout
    
    def create_session(self, session_id, websocket, crypto):
        """Create a new session"""
        self.sessions[session_id] = {
            'websocket': websocket,
            'crypto': crypto,
            'created_at': datetime.now(),
            'last_active': datetime.now(),
            'info': {},
            'tasks': []
        }
        return self.sessions[session_id]
    
    def get_session(self, session_id):
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id):
        """Update session last activity time"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_active'] = datetime.now()
    
    def remove_session(self, session_id):
        """Remove a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired = []
        
        for session_id, session in self.sessions.items():
            if current_time - session['last_active'] > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            self.remove_session(session_id)
        
        return expired
    
    def get_active_sessions(self):
        """Get all active sessions"""
        return {
            session_id: {
                'created_at': session['created_at'],
                'last_active': session['last_active'],
                'info': session['info']
            }
            for session_id, session in self.sessions.items()
        }
    
    async def broadcast(self, message):
        """Broadcast message to all active sessions"""
        for session_id, session in self.sessions.items():
            try:
                encrypted = session['crypto'].encrypt(json.dumps(message).encode())
                await session['websocket'].send(encrypted)
            except Exception as e:
                print(f"Error broadcasting to {session_id}: {str(e)}")