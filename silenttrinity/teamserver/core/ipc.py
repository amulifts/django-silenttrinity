# silenttrinity/silenttrinity/teamserver/core/ipc.py

import zmq
import zmq.asyncio
import json
import asyncio
import logging
import os

from teamserver.core.utils.ports import find_free_port
from teamserver.core.utils.logger import StructuredLogger

class IPCServer:
    def __init__(self, secure=False, pub_port=None, sub_port=None, server_public_key=None, server_secret_key=None):
        """
        :param secure: If True, use ZeroMQ Curve encryption
        :param pub_port: Force specific port for PUB, else find free
        :param sub_port: Force specific port for SUB, else find free
        :param server_public_key: ephemeral ZMQ public key if secure
        :param server_secret_key: ephemeral ZMQ secret key if secure
        """
        self.context = zmq.asyncio.Context()
        self.logger = StructuredLogger('IPC_Server').logger
        
        # If no port specified, pick free ones
        self.pub_port = pub_port if pub_port else find_free_port()
        self.sub_port = sub_port if sub_port else find_free_port()
        
        # Create PUB socket
        self.publisher = self.context.socket(zmq.PUB)
        
        # Create SUB socket
        self.subscriber = self.context.socket(zmq.SUB)
        
        # Handlers
        self.handlers = {}
        
        self.secure = secure
        self.server_pub_key = server_public_key
        self.server_secret_key = server_secret_key
        
    def register_handler(self, topic, handler):
        if not isinstance(topic, bytes):
            topic = topic.encode()
        self.handlers[topic] = handler
        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic)
        
    async def publish(self, topic, message):
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
        while True:
            try:
                topic, message = await self.subscriber.recv_multipart()
                self.logger.debug(f"Received message on topic {topic}")
                
                if topic in self.handlers:
                    try:
                        msg_str = message.decode()
                        msg_data = json.loads(msg_str)
                        await self.handlers[topic](msg_data)
                    except json.JSONDecodeError:
                        self.logger.error(f"Failed to parse JSON: {message}")
                    except Exception as e:
                        self.logger.error(f"Error handling message: {str(e)}")
                else:
                    self.logger.warning(f"No handler for topic: {topic}")
                    
            except asyncio.CancelledError:
                self.logger.info("IPC message loop cancelled.")
                break
            except Exception as e:
                self.logger.error(f"Error in message handling loop: {str(e)}")
                await asyncio.sleep(1)
                
    async def start(self):
        """Start the IPC server on random or user-specified ports, with optional security."""
        try:
            pub_addr = f"tcp://127.0.0.1:{self.pub_port}"
            sub_addr = f"tcp://127.0.0.1:{self.sub_port}"
            
            if self.secure and self.server_pub_key and self.server_secret_key:
                # Setup CURVE security
                self.publisher.curve_secretkey = self.server_secret_key
                self.publisher.curve_publickey = self.server_pub_key
                self.publisher.curve_server = True
                
                self.subscriber.curve_secretkey = self.server_secret_key
                self.subscriber.curve_publickey = self.server_pub_key
                self.subscriber.curve_server = True
                
                self.logger.info(f"Starting IPC server (Curve) on PUB={pub_addr}, SUB={sub_addr}")
            else:
                self.logger.info(f"Starting IPC server (no security) on PUB={pub_addr}, SUB={sub_addr}")
            
            self.publisher.bind(pub_addr)
            self.subscriber.bind(sub_addr)
            
            await self.handle_messages()
        except Exception as e:
            self.logger.error(f"Failed to start IPC server: {str(e)}")
            raise
            
    async def stop(self):
        self.logger.info("Stopping IPC server")
        self.publisher.close(linger=0)
        self.subscriber.close(linger=0)
        self.context.term()
