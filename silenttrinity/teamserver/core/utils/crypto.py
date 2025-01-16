# silenttrinity/silenttrinity/teamserver/core/utils/crypto.py

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
import os
import base64
from cryptography.hazmat.primitives import serialization

class CryptoManager:
    """Implements SILENTTRINITY's cryptographic protocol with AES-GCM"""
    
    def __init__(self):
        self._curve = ec.SECP521R1()
        self._private_key = None
        self._public_key = None
        self._shared_key = None
        self._aesgcm = None
        self.initialize()
    
    def initialize(self):
        """Initialize ECDHE keys"""
        self._private_key = ec.generate_private_key(self._curve)
        self._public_key = self._private_key.public_key()
    
    def get_public_key(self):
        """Export public key for key exchange"""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def perform_key_exchange(self, peer_public_key_bytes):
        """Perform ECDHE key exchange and derive AES-GCM key"""
        peer_public_key = serialization.load_pem_public_key(peer_public_key_bytes)
        self._shared_key = self._private_key.exchange(ec.ECDH(), peer_public_key)
        
        # Derive a 32-byte key for AES-GCM using HKDF
        kdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"silenttrinity-v1"
        )
        key_material = kdf.derive(self._shared_key)
        
        self._aesgcm = AESGCM(key_material)
    
    def encrypt(self, data):
        """Encrypt data using AES-GCM"""
        if not isinstance(data, bytes):
            data = data.encode()
        nonce = os.urandom(12)  # Recommended size for GCM nonce
        ciphertext = self._aesgcm.encrypt(nonce, data, None)
        return base64.b64encode(nonce + ciphertext)
    
    def decrypt(self, encrypted_data):
        """Decrypt data using AES-GCM"""
        data = base64.b64decode(encrypted_data)
        nonce = data[:12]
        ciphertext = data[12:]
        
        try:
            plaintext = self._aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext
        except InvalidTag:
            raise ValueError("Message authentication failed")
    
    def generate_nonce(self):
        """Generate secure random nonce"""
        return base64.b64encode(os.urandom(32)).decode()