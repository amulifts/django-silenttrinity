import asyncio
import websockets
import json
import logging
from django.conf import settings
from teamserver.models import TeamServerUser, Session
from teamserver.core.utils.crypto import CryptoManager
from django.utils import timezone
from teamserver.models import SessionLog

logger = logging.getLogger('teamserver.websocket')

class WebSocketServer:
    def __init__(self):
        self.clients = {}  # Store active client connections
        self.crypto = CryptoManager()
        
    async def authenticate_client(self, websocket, path):
        """Authenticate incoming WebSocket connection"""
        try:
            auth_message = await websocket.recv()
            auth_data = json.loads(auth_message)
            
            token = auth_data.get('token')
            if not token:
                await websocket.send(json.dumps({'error': 'No authentication token provided'}))
                return False
                
            try:
                user = TeamServerUser.objects.get(auth_tokens__token=token, auth_tokens__is_valid=True)
                return user
            except TeamServerUser.DoesNotExist:
                await websocket.send(json.dumps({'error': 'Invalid token'}))
                return False
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({'error': 'Invalid message format'}))
            return False
        except Exception as e:
            logger.error(f'Authentication error: {str(e)}')
            await websocket.send(json.dumps({'error': 'Authentication failed'}))
            return False
            
    async def handle_client_message(self, websocket, user, message):
        """Handle incoming messages from authenticated clients"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'checkin':
                session_id = data.get('session_id')
                try:
                    session = Session.objects.get(id=session_id)
                    session.last_checkin = timezone.now()
                    session.save()
                    await websocket.send(json.dumps({'type': 'checkin_ack'}))
                except Session.DoesNotExist:
                    await websocket.send(json.dumps({'error': 'Invalid session'}))
                    
            elif message_type == 'command_result':
                session_id = data.get('session_id')
                result = data.get('result')
                
                try:
                    session = Session.objects.get(id=session_id)
                    SessionLog.objects.create(
                        session=session,
                        type='command_result',
                        content=result
                    )
                    await websocket.send(json.dumps({'type': 'result_received'}))
                except Session.DoesNotExist:
                    await websocket.send(json.dumps({'error': 'Invalid session'}))
                    
            else:
                await websocket.send(json.dumps({'error': 'Unknown message type'}))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({'error': 'Invalid message format'}))
        except Exception as e:
            logger.error(f'Message handling error: {str(e)}')
            await websocket.send(json.dumps({'error': 'Message handling failed'}))
            
    async def handler(self, websocket, path):
        """Main WebSocket connection handler"""
        user = await self.authenticate_client(websocket, path)
        if not user:
            return
            
        self.clients[user.id] = websocket
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, user, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f'Client disconnected: {user.username}')
        finally:
            if user.id in self.clients:
                del self.clients[user.id]
                
    async def start(self, host='0.0.0.0', port=5000, ssl_context=None):
        """Start the WebSocket server"""
        server = await websockets.serve(
            self.handler,
            host,
            port,
            ssl=ssl_context
        )
        logger.info(f'WebSocket server started on {host}:{port}')
        await server.wait_closed()