# silenttrinity/silenttrinity/teamserver/core/utils/crypto.py

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.exceptions import InvalidKey
import os
import base64
from cryptography.hazmat.primitives import serialization

class CryptoManager:
    """Implements SILENTTRINITY's cryptographic protocol"""
    
    def __init__(self):
        self._curve = ec.SECP521R1()
        self._private_key = None
        self._public_key = None
        self._shared_key = None
        self._session_key = None
        self._hmac_key = None
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
        """Perform ECDHE key exchange"""
        peer_public_key = serialization.load_pem_public_key(peer_public_key_bytes)
        self._shared_key = self._private_key.exchange(ec.ECDH(), peer_public_key)
        
        # Derive session keys using HKDF
        kdf = HKDF(
            algorithm=hashes.SHA256(),
            length=64,  # 32 bytes for AES + 32 bytes for HMAC
            salt=None,
            info=b"silenttrinity-v1"
        )
        key_material = kdf.derive(self._shared_key)
        
        self._session_key = key_material[:32]
        self._hmac_key = key_material[32:]
    
    def encrypt(self, data):
        """Encrypt data using AES-256-CBC with HMAC-SHA256"""
        if not isinstance(data, bytes):
            data = data.encode()
            
        # Add PKCS7 padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Generate IV
        iv = os.urandom(16)
        
        # Encrypt with AES-256-CBC
        cipher = Cipher(algorithms.AES(self._session_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine IV and ciphertext
        encrypted_data = iv + ciphertext
        
        # Calculate HMAC
        h = hmac.HMAC(self._hmac_key, hashes.SHA256())
        h.update(encrypted_data)
        mac = h.finalize()
        
        # Combine everything and encode
        return base64.b64encode(encrypted_data + mac)
    
    def decrypt(self, encrypted_data):
        """Decrypt data and verify HMAC"""
        # Decode from base64
        data = base64.b64decode(encrypted_data)
        
        # Split components
        mac = data[-32:]  # HMAC-SHA256 is 32 bytes
        encrypted_data = data[:-32]
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Verify HMAC
        h = hmac.HMAC(self._hmac_key, hashes.SHA256())
        h.update(encrypted_data)
        try:
            h.verify(mac)
        except InvalidKey:
            raise ValueError("Message authentication failed")
        
        # Decrypt
        cipher = Cipher(algorithms.AES(self._session_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_plaintext) + unpadder.finalize()
    
    def generate_nonce(self):
        """Generate secure random nonce"""
        return base64.b64encode(os.urandom(32)).decode()
    
