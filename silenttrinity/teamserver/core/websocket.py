# silenttrinity/silenttrinity/teamserver/core/websocket.py

import asyncio
import websockets
import ssl
import json
import base64
import os
import uuid
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings  # Import Django settings

class SecureWebSocketServer:
    def __init__(self, host='0.0.0.0', port=8765, ipc_server=None, secure=False):
        """
        :param secure: If True, use TLS (wss); else plain ws.
        """
        self.host = host
        self.port = port
        self.ipc_server = ipc_server
        self.secure = secure
        self.ssl_context = None
        self.clients = {}
        
        if self.secure:
            cert_path = getattr(settings, 'WEBSOCKET_CERT_PATH', None)
            key_path = getattr(settings, 'WEBSOCKET_KEY_PATH', None)
            if cert_path and key_path and os.path.exists(cert_path) and os.path.exists(key_path):
                self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                self.ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)
            else:
                print("[WARNING] --secure specified, but cert/key not found. Reverting to insecure.")
                self.secure = False
                self.ssl_context = None

    async def handle_client(self, websocket, path):
        client_id = str(uuid.uuid4())
        encryption_key = None
        
        try:
            # ECDH key exchange (AES-GCM)
            server_private_key = ec.generate_private_key(ec.SECP384R1())
            server_public_key = server_private_key.public_key()
            server_public_bytes = server_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            await websocket.send(json.dumps({
                'type': 'key_exchange',
                'public_key': base64.b64encode(server_public_bytes).decode()
            }))
            
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
            
            if self.ipc_server:
                await self.ipc_server.publish(b'client_connected', {
                    'client_id': client_id,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Main recv loop
            while True:
                message = await websocket.recv()
                decrypted_bytes = self.decrypt_message(message, encryption_key)
                
                try:
                    msg_data = json.loads(decrypted_bytes)
                except json.JSONDecodeError:
                    resp = json.dumps({'type': 'error', 'message': 'Invalid JSON'})
                    await websocket.send(self.encrypt_message(resp, encryption_key))
                    continue
                
                response = await self.process_message(msg_data, client_id)
                encrypted_resp = self.encrypt_message(response, encryption_key)
                await websocket.send(encrypted_resp)
                
        except asyncio.CancelledError:
            # Graceful shutdown
            pass
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
        data = base64.b64decode(encrypted_data)
        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    
    async def process_message(self, msg_data, client_id):
        # Basic router for demonstration
        msg_type = msg_data.get('type')
        if msg_type == 'command_result':
            return json.dumps({
                'type': 'ack',
                'status': 'success',
                'message': 'Result received'
            })
        else:
            return json.dumps({
                'type': 'error',
                'message': f"Unknown message type: {msg_type}"
            })
    
    async def start(self):
        proto = "wss" if self.secure else "ws"
        print(f"WebSocket server starting on {proto}://{self.host}:{self.port}")
        if self.secure and self.ssl_context:
            async with websockets.serve(self.handle_client, self.host, self.port, ssl=self.ssl_context):
                await asyncio.Future()
        else:
            # insecure
            async with websockets.serve(self.handle_client, self.host, self.port):
                await asyncio.Future()
    
    async def stop(self):
        print("Stopping SecureWebSocketServer...")
        await asyncio.sleep(0.5)