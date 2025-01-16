# silenttrinity/silenttrinity/teamserver/core/websocket.py

import asyncio
import websockets
import json
import base64
import os
import uuid
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecureWebSocketServer:
    def __init__(self, host='0.0.0.0', port=8765, ipc_server=None):
        """Initialize the WebSocket server with AES-GCM encryption"""
        self.host = host
        self.port = port
        self.clients = {}
        self.ipc_server = ipc_server  # Could be None if not using IPC
        
    async def handle_client(self, websocket, path):
        client_id = str(uuid.uuid4())
        encryption_key = None
        
        try:
            # ECDH key exchange
            server_private_key = ec.generate_private_key(ec.SECP384R1())
            server_public_key = server_private_key.public_key()
            
            # Send server's public key
            server_public_bytes = server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            await websocket.send(json.dumps({
                'type': 'key_exchange',
                'public_key': base64.b64encode(server_public_bytes).decode()
            }))
            
            # Receive client's public key
            client_data = await websocket.recv()
            client_msg = json.loads(client_data)
            if client_msg.get('type') != 'key_exchange':
                raise ValueError("Expected key_exchange message")
            
            client_public_bytes = base64.b64decode(client_msg['public_key'])
            client_public_key = serialization.load_pem_public_key(client_public_bytes)
            
            shared_key = server_private_key.exchange(ec.ECDH(), client_public_key)
            kdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake data')
            encryption_key = kdf.derive(shared_key)
            
            self.clients[client_id] = {
                'websocket': websocket,
                'key': encryption_key,
                'connected_at': datetime.now().isoformat()
            }
            
            # Notify IPC if available
            if self.ipc_server:
                await self.ipc_server.publish(b'client_connected', {
                    'client_id': client_id,
                    'timestamp': datetime.now().isoformat()
                })
            
            while True:
                message = await websocket.recv()
                decrypted = self.decrypt_message(message, encryption_key)
                
                # Attempt to parse JSON
                try:
                    msg_data = json.loads(decrypted)
                except json.JSONDecodeError:
                    await websocket.send(self.encrypt_message(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }), encryption_key))
                    continue
                
                # Process message
                response = await self.process_message(msg_data, client_id)
                encrypted = self.encrypt_message(response, encryption_key)
                await websocket.send(encrypted)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            # Enhanced error handling
            error_msg = f"Error with client {client_id}: {str(e)}"
            print(error_msg)
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
                if self.ipc_server:
                    await self.ipc_server.publish(b'client_disconnected', {
                        'client_id': client_id,
                        'timestamp': datetime.now().isoformat()
                    })
    
    def encrypt_message(self, plaintext, key):
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return base64.b64encode(nonce + ciphertext).decode()
    
    def decrypt_message(self, encrypted_data, key):
        aesgcm = AESGCM(key)
        data = base64.b64decode(encrypted_data)
        nonce = data[:12]
        ciphertext = data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None)
    
    async def process_message(self, msg_data, client_id):
        # Basic message router for demonstration
        if msg_data.get('type') == 'command_result':
            return json.dumps({
                'type': 'ack',
                'status': 'success',
                'message': 'Result received'
            })
        else:
            return json.dumps({
                'type': 'error',
                'message': f"Unknown message type: {msg_data.get('type')}"
            })
    
    async def start(self):
        print(f"WebSocket server starting on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # run forever
    
    async def stop(self):
        # For a graceful shutdown, if needed
        print("Stopping SecureWebSocketServer...")
        # websockets.serve doesn't expose a direct shutdown, so we rely on tasks cancellation
        await asyncio.sleep(0.5)

