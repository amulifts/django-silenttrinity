from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import base64
import os

class CryptoManager:
    """Handles encryption/decryption for TeamServer communications"""
    
    def __init__(self):
        self._key = None
        self._fernet = None
        self._private_key = None
        self._public_key = None
        self.initialize()
    
    def initialize(self):
        """Initialize encryption keys"""
        # Generate RSA key pair for initial key exchange
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self._public_key = self._private_key.public_key()
        
        # Generate session key for Fernet (symmetric) encryption
        self._key = Fernet.generate_key()
        self._fernet = Fernet(self._key)
    
    def get_public_key(self):
        """Get public key in PEM format"""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def encrypt_session_key(self, public_key_pem):
        """Encrypt session key with client's public key"""
        public_key = serialization.load_pem_public_key(public_key_pem)
        encrypted_key = public_key.encrypt(
            self._key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_key)
    
    def decrypt_session_key(self, encrypted_key):
        """Decrypt session key using private key"""
        encrypted_key = base64.b64decode(encrypted_key)
        decrypted_key = self._private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_key
    
    def encrypt(self, data):
        """Encrypt data using Fernet symmetric encryption"""
        if isinstance(data, str):
            data = data.encode()
        return self._fernet.encrypt(data)
    
    def decrypt(self, encrypted_data):
        """Decrypt data using Fernet symmetric encryption"""
        return self._fernet.decrypt(encrypted_data)
    
    def generate_nonce(self):
        """Generate random nonce for message signing"""
        return base64.b64encode(os.urandom(16)).decode()