
# silenttrinity/silenttrinity/teamserver/core/websocket.py

import asyncio
import json
import websockets
from django.conf import settings
from teamserver.core.utils.crypto import CryptoManager

class C2Server:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.crypto = CryptoManager()
        self.sessions = {}  # Store active sessions
        self.handlers = {}  # Message handlers
        
    async def handle_client(self, websocket, path):
        """Handle individual client connections"""
        session_id = None
        try:
            # Initial key exchange
            client_hello = await websocket.recv()
            client_hello = json.loads(client_hello)
            
            # Generate and send server public key
            server_public_key = self.crypto.get_public_key()
            await websocket.send(json.dumps({
                'type': 'key_exchange',
                'public_key': server_public_key.decode()
            }))
            
            # Receive encrypted session key
            encrypted_key = await websocket.recv()
            encrypted_key = json.loads(encrypted_key)
            session_key = self.crypto.decrypt_session_key(encrypted_key['session_key'])
            
            # Create session
            session_id = self.crypto.generate_nonce()
            self.sessions[session_id] = {
                'websocket': websocket,
                'crypto': CryptoManager(),
                'info': {}
            }
            
            # Send session confirmation
            await websocket.send(json.dumps({
                'type': 'session_established',
                'session_id': session_id
            }))
            
            # Main message handling loop
            async for message in websocket:
                try:
                    # Decrypt and parse message
                    decrypted = self.sessions[session_id]['crypto'].decrypt(message)
                    data = json.loads(decrypted)
                    
                    # Handle message based on type
                    if data['type'] in self.handlers:
                        response = await self.handlers[data['type']](data, session_id)
                        if response:
                            # Encrypt and send response
                            encrypted = self.sessions[session_id]['crypto'].encrypt(
                                json.dumps(response).encode()
                            )
                            await websocket.send(encrypted)
                            
                except Exception as e:
                    print(f"Error handling message: {str(e)}")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected")
        finally:
            if session_id and session_id in self.sessions:
                del self.sessions[session_id]
    
    def register_handler(self, msg_type, handler):
        """Register message handlers"""
        self.handlers[msg_type] = handler
    
    async def start(self):
        """Start the WebSocket server"""
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"C2 Server listening on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever

    async def broadcast(self, message):
        """Broadcast message to all connected clients"""
        for session_id, session in self.sessions.items():
            try:
                encrypted = session['crypto'].encrypt(json.dumps(message).encode())
                await session['websocket'].send(encrypted)
            except Exception as e:
                print(f"Error broadcasting to {session_id}: {str(e)}")