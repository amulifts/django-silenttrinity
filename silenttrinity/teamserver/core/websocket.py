
# silenttrinity/silenttrinity/teamserver/core/websocket.py

# teamserver/core/websocket.py

import asyncio
import json
import websockets
from datetime import datetime
from teamserver.core.utils.crypto import CryptoManager
from teamserver.core.utils.logger import C2Logger

class C2Server:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.crypto = CryptoManager()
        self.sessions = {}
        self.handlers = {}
        self.logger = C2Logger()
        
    async def handle_client(self, websocket, path):
        session_id = None
        client_address = websocket.remote_address
        
        try:
            self.logger.client_connect(id(websocket), client_address)
            
            # Initial key exchange
            self.logger.key_exchange(id(websocket))
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
                'info': {
                    'address': client_address,
                    'connected_at': datetime.now().isoformat(),
                    'last_active': datetime.now().isoformat()
                }
            }
            
            self.logger.session_established(session_id)
            
            # Send session confirmation
            await websocket.send(json.dumps({
                'type': 'session_established',
                'session_id': session_id
            }))
            
            # Main message handling loop
            async for message in websocket:
                try:
                    # Update last active timestamp
                    self.sessions[session_id]['info']['last_active'] = datetime.now().isoformat()
                    
                    # Decrypt and parse message
                    decrypted = self.sessions[session_id]['crypto'].decrypt(message)
                    data = json.loads(decrypted)
                    
                    self.logger.debug(f"Received message type: {data.get('type')} [Session: {session_id}]")
                    
                    # Handle message based on type
                    if data['type'] in self.handlers:
                        response = await self.handlers[data['type']](data, session_id)
                        if response:
                            # Encrypt and send response
                            encrypted = self.sessions[session_id]['crypto'].encrypt(
                                json.dumps(response).encode()
                            )
                            await websocket.send(encrypted)
                            self.logger.command_executed(session_id, data['type'])
                            
                except Exception as e:
                    self.logger.error(f"Error handling message: {str(e)}", exc_info=True)
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.client_disconnect(id(websocket))
        except Exception as e:
            self.logger.critical(f"Critical error in client handler: {str(e)}", exc_info=True)
        finally:
            if session_id and session_id in self.sessions:
                del self.sessions[session_id]
                self.logger.debug(f"Session cleaned up [Session: {session_id}]")
    
    def register_handler(self, msg_type, handler):
        """Register message handlers"""
        self.logger.debug(f"Registered handler for message type: {msg_type}")
        self.handlers[msg_type] = handler
    
    async def start(self):
        """Start the WebSocket server"""
        self.logger.server_start(self.host, self.port)
        
        try:
            async with websockets.serve(self.handle_client, self.host, self.port):
                self.logger.info("Server is ready for connections")
                await asyncio.Future()  # run forever
        except Exception as e:
            self.logger.critical(f"Failed to start server: {str(e)}", exc_info=True)
            raise

    async def broadcast(self, message):
        """Broadcast message to all connected clients"""
        self.logger.debug(f"Broadcasting message to {len(self.sessions)} clients")
        
        for session_id, session in self.sessions.items():
            try:
                encrypted = session['crypto'].encrypt(json.dumps(message).encode())
                await session['websocket'].send(encrypted)
                self.logger.debug(f"Broadcast message sent to session {session_id}")
            except Exception as e:
                self.logger.error(f"Error broadcasting to session {session_id}: {str(e)}")
