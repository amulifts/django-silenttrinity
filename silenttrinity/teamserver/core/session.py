# silenttrinity/silenttrinity/teamserver/core/session.py

from datetime import datetime, timedelta
import json
import threading

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(minutes=30)  # Default timeout
        self.lock = threading.Lock()  # For thread safety
    
    def create_session(self, session_id, websocket, crypto):
        with self.lock:
            self.sessions[session_id] = {
                'websocket': websocket,
                'crypto': crypto,
                'created_at': datetime.now(),
                'last_active': datetime.now(),
                'info': {},
                'tasks': []
            }
        # Example: write to a simple JSON file or a Redis store
        self._write_to_persistent_store(session_id)
        return self.sessions[session_id]
    
    def get_session(self, session_id):
        with self.lock:
            return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id):
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['last_active'] = datetime.now()
                self._write_to_persistent_store(session_id)
    
    def remove_session(self, session_id):
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        current_time = datetime.now()
        expired = []
        with self.lock:
            for session_id, session in list(self.sessions.items()):
                if current_time - session['last_active'] > self.session_timeout:
                    expired.append(session_id)
            for session_id in expired:
                del self.sessions[session_id]
        return expired
    
    def get_active_sessions(self):
        with self.lock:
            return {
                session_id: {
                    'created_at': session['created_at'],
                    'last_active': session['last_active'],
                    'info': session['info']
                }
                for session_id, session in self.sessions.items()
            }
    
    def _write_to_persistent_store(self, session_id):
        """Example method to store session data to a local file (sketch only)."""
        session_data = self.sessions[session_id]
        with open("sessions_store.json", "a") as f:
            f.write(json.dumps({
                'session_id': session_id,
                'info': session_data['info'],
                'last_active': str(session_data['last_active'])
            }) + "\n")
    
    async def broadcast(self, message):
        with self.lock:
            sessions_copy = list(self.sessions.items())
        
        for session_id, session in sessions_copy:
            try:
                encrypted = session['crypto'].encrypt(json.dumps(message).encode())
                await session['websocket'].send(encrypted)
            except Exception as e:
                print(f"Error broadcasting to {session_id}: {str(e)}")
