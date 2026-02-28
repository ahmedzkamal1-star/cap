import io
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from kivy.core.image import Image as CoreImage

class SecureViewer:
    @staticmethod
    def decrypt_in_memory(encrypted_data, key_hex):
        """Decrypts AES-256-CBC content and returns raw bytes WITHOUT saving to disk."""
        try:
            key = bytes.fromhex(key_hex)
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return data
        except Exception as e:
            print(f"Decryption Error: {e}")
            return None

    @staticmethod
    def get_kivy_image(image_bytes, ext='png'):
        """Converts raw bytes into a Kivy CoreImage for display."""
        data = io.BytesIO(image_bytes)
        try:
            return CoreImage(data, ext=ext).texture
        except Exception as e:
            print(f"Image Loading Error: {e}")
            return None

    @staticmethod
    def save_temp_pdf_context(pdf_bytes):
        """
        Since most PDF viewers need a file path, we would ideally use 
        a memory-mapped file or a temporary file that is instantly deleted.
        In Phase 2, we will focus on Images first as they are easier to handle in-memory.
        """
        pass
