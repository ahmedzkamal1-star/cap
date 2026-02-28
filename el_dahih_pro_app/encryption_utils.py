"""
Encryption utilities for protecting sensitive data and files
"""
import os
import json
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Manages encryption and decryption of sensitive data"""
    
    # Master key - should be stored securely in production
    MASTER_KEY = b'ElDahih_Secure_2024_Platform_Key'
    
    @staticmethod
    def _derive_key(password: str, salt: bytes = None) -> tuple:
        """Derive encryption key from password using PBKDF2"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    @staticmethod
    def encrypt_data(data: str, password: str = None) -> str:
        """Encrypt sensitive data"""
        try:
            if password is None:
                key = base64.urlsafe_b64encode(EncryptionManager.MASTER_KEY)
            else:
                key, _ = EncryptionManager._derive_key(password)
            
            cipher = Fernet(key)
            encrypted = cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return data
    
    @staticmethod
    def decrypt_data(encrypted_data: str, password: str = None) -> str:
        """Decrypt sensitive data"""
        try:
            if password is None:
                key = base64.urlsafe_b64encode(EncryptionManager.MASTER_KEY)
            else:
                key, _ = EncryptionManager._derive_key(password)
            
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return encrypted_data
    
    @staticmethod
    def encrypt_file(file_path: str, output_path: str = None, password: str = None) -> bool:
        """Encrypt a file"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            if output_path is None:
                output_path = file_path + '.encrypted'
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            if password is None:
                key = base64.urlsafe_b64encode(EncryptionManager.MASTER_KEY)
            else:
                key, salt = EncryptionManager._derive_key(password)
                # Prepend salt to encrypted data
                file_data = salt + file_data
            
            cipher = Fernet(key)
            encrypted_data = cipher.encrypt(file_data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"File encrypted: {output_path}")
            return True
        except Exception as e:
            logger.error(f"File encryption error: {str(e)}")
            return False
    
    @staticmethod
    def decrypt_file(encrypted_file_path: str, output_path: str = None, password: str = None) -> bool:
        """Decrypt a file"""
        try:
            if not os.path.exists(encrypted_file_path):
                logger.error(f"Encrypted file not found: {encrypted_file_path}")
                return False
            
            if output_path is None:
                output_path = encrypted_file_path.replace('.encrypted', '')
            
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            if password is None:
                key = base64.urlsafe_b64encode(EncryptionManager.MASTER_KEY)
                cipher = Fernet(key)
                file_data = cipher.decrypt(encrypted_data)
            else:
                # Extract salt from encrypted data
                salt = encrypted_data[:16]
                key, _ = EncryptionManager._derive_key(password, salt)
                cipher = Fernet(key)
                file_data = cipher.decrypt(encrypted_data)
                file_data = file_data[16:]  # Remove salt
            
            with open(output_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"File decrypted: {output_path}")
            return True
        except Exception as e:
            logger.error(f"File decryption error: {str(e)}")
            return False
    
    @staticmethod
    def encrypt_json(data: dict, file_path: str, password: str = None) -> bool:
        """Encrypt JSON data to file"""
        try:
            json_str = json.dumps(data)
            encrypted = EncryptionManager.encrypt_data(json_str, password)
            
            with open(file_path, 'w') as f:
                f.write(encrypted)
            
            logger.info(f"JSON encrypted to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"JSON encryption error: {str(e)}")
            return False
    
    @staticmethod
    def decrypt_json(file_path: str, password: str = None) -> dict:
        """Decrypt JSON data from file"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return {}
            
            with open(file_path, 'r') as f:
                encrypted = f.read()
            
            decrypted = EncryptionManager.decrypt_data(encrypted, password)
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"JSON decryption error: {str(e)}")
            return {}


class SecureStorage:
    """Secure storage for sensitive application data"""
    
    STORAGE_DIR = os.path.join(os.path.expanduser('~'), '.eldahih_secure')
    
    @staticmethod
    def _ensure_storage_dir():
        """Ensure storage directory exists"""
        if not os.path.exists(SecureStorage.STORAGE_DIR):
            os.makedirs(SecureStorage.STORAGE_DIR, mode=0o700)
    
    @staticmethod
    def save_secure(key: str, value: str) -> bool:
        """Save encrypted data"""
        try:
            SecureStorage._ensure_storage_dir()
            file_path = os.path.join(SecureStorage.STORAGE_DIR, f"{key}.secure")
            encrypted = EncryptionManager.encrypt_data(value)
            
            with open(file_path, 'w') as f:
                f.write(encrypted)
            
            os.chmod(file_path, 0o600)
            return True
        except Exception as e:
            logger.error(f"Secure save error: {str(e)}")
            return False
    
    @staticmethod
    def load_secure(key: str) -> str:
        """Load encrypted data"""
        try:
            file_path = os.path.join(SecureStorage.STORAGE_DIR, f"{key}.secure")
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                encrypted = f.read()
            
            return EncryptionManager.decrypt_data(encrypted)
        except Exception as e:
            logger.error(f"Secure load error: {str(e)}")
            return None
    
    @staticmethod
    def delete_secure(key: str) -> bool:
        """Delete encrypted data"""
        try:
            file_path = os.path.join(SecureStorage.STORAGE_DIR, f"{key}.secure")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Secure delete error: {str(e)}")
            return False
    
    @staticmethod
    def clear_all() -> bool:
        """Clear all secure storage"""
        try:
            if os.path.exists(SecureStorage.STORAGE_DIR):
                import shutil
                shutil.rmtree(SecureStorage.STORAGE_DIR)
            return True
        except Exception as e:
            logger.error(f"Clear storage error: {str(e)}")
            return False
