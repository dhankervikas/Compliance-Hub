import json
from cryptography.fernet import Fernet
from app.config import settings

class SecurityManager:
    
    _cipher_suite = None

    @classmethod
    def _get_cipher(cls):
        if cls._cipher_suite is None:
            # Prefer APP_ENCRYPTION_KEY per user request
            key = getattr(settings, "APP_ENCRYPTION_KEY", None) or settings.FIELD_ENCRYPTION_KEY
            if not key:
                raise ValueError("APP_ENCRYPTION_KEY is not set.")
            cls._cipher_suite = Fernet(key)
        return cls._cipher_suite

    @classmethod
    def encrypt_metadata(cls, payload: dict) -> str:
        """
        Converts dict to JSON string, encrypts it, and returns a url-safe base64 string.
        """
        json_str = json.dumps(payload)
        encrypted_bytes = cls._get_cipher().encrypt(json_str.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    @classmethod
    def decrypt_metadata(cls, token: str) -> dict:
        """
        Decrypts a token and returns the original dictionary.
        """
        cipher = cls._get_cipher()
        decrypted_bytes = cipher.decrypt(token.encode('utf-8'))
        return json.loads(decrypted_bytes.decode('utf-8'))
