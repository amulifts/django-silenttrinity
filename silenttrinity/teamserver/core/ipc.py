# silenttrinity/silenttrinity/teamserver/core/ipc.py

import zmq
import zmq.asyncio
import json
import asyncio
from datetime import datetime
import logging
import os

class IPCServer:
    def __init__(self, pub_port=5555, sub_port=5556):
        """Initialize IPC server with ZeroMQ PUB/SUB pattern and Curve security."""
        self.context = zmq.asyncio.Context()
        
        # If using CURVE, generate or load server keys:
        # For demonstration, we assume we have curve keys in environment or local files
        self.server_public_key = os.getenv('ZMQ_SERVER_PUBLIC_KEY')
        self.server_secret_key = os.getenv('ZMQ_SERVER_SECRET_KEY')
        
        self.publisher = self.context.socket(zmq.PUB)
        self.subscriber = self.context.socket(zmq.SUB)
        
        # Apply Curve security if keys exist
        if self.server_public_key and self.server_secret_key:
            self.publisher.curve_secretkey = self.server_secret_key.encode()
            self.publisher.curve_publickey = self.server_public_key.encode()
            self.publisher.curve_server = True
            
            self.subscriber.curve_secretkey = self.server_secret_key.encode()
            self.subscriber.curve_publickey = self.server_public_key.encode()
            self.subscriber.curve_server = True
        
        self.publisher.bind(f"tcp://127.0.0.1:{pub_port}")
        self.subscriber.bind(f"tcp://127.0.0.1:{sub_port}")
        
        self.handlers = {}
        self.logger = logging.getLogger('IPC_Server')
        
    def register_handler(self, topic, handler):
        """Register a handler for a specific message topic"""
        if not isinstance(topic, bytes):
            topic = topic.encode()
        self.handlers[topic] = handler
        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic)
        
    async def publish(self, topic, message):
        """Publish a message to a specific topic"""
        if not isinstance(topic, bytes):
            topic = topic.encode()
        
        if isinstance(message, dict):
            message = json.dumps(message)
        if isinstance(message, str):
            message = message.encode()
            
        try:
            await self.publisher.send_multipart([topic, message])
        except Exception as e:
            self.logger.error(f"Failed to publish message: {str(e)}")
        
    async def handle_messages(self):
        """Main loop for handling incoming messages"""
        while True:
            try:
                topic, message = await self.subscriber.recv_multipart()
                
                self.logger.debug(f"Received message on topic {topic}")
                
                if topic in self.handlers:
                    try:
                        if isinstance(message, bytes):
                            message = message.decode()
                        msg_data = json.loads(message)
                        
                        await self.handlers[topic](msg_data)
                    except json.JSONDecodeError:
                        self.logger.error(f"Failed to parse message: {message}")
                    except Exception as e:
                        self.logger.error(f"Error handling message: {str(e)}")
                else:
                    self.logger.warning(f"No handler for topic: {topic}")
                    
            except asyncio.CancelledError:
                # Graceful exit
                self.logger.info("IPC message loop cancelled.")
                break
            except Exception as e:
                self.logger.error(f"Error in message handling loop: {str(e)}")
                await asyncio.sleep(1)
                
    async def start(self):
        """Start the IPC server"""
        self.logger.info("Starting IPC server with ZeroMQ security" if self.server_public_key else "Starting IPC server (no security)")
        await self.handle_messages()
        
    async def stop(self):
        """Stop the IPC server gracefully"""
        self.logger.info("Stopping IPC server")
        self.publisher.close(linger=0)
        self.subscriber.close(linger=0)
        self.context.term()

# Example handlers
async def handle_client_connected(message):
    """Handle new client connections in detail"""
    # e.g., store into DB, log activity
    print(f"[IPC] Client connected: {message}")

async def handle_client_disconnected(message):
    """Handle client disconnections thoroughly"""
    print(f"[IPC] Client disconnected: {message}")

async def handle_command_result(message):
    """Handle command execution results properly"""
    # e.g., store results, trigger further actions
    print(f"[IPC] Received command result: {message}")
