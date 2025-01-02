from app import db, ph 
from datetime import datetime
from app.config import Config 
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    stored_passwords = db.relationship('StoredPassword', backref='user',
                                       cascade='all, delete-orphan')
    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            return ph.verify(self.password_hash, password)
        except Exception:
            return False


class StoredPassword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    encrypted_password = db.Column(db.LargeBinary, nullable=False)
    url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def encrypt_password(self, raw_password):
        """Encrypts the password using AES-256"""
        try:
            key = Config.STATIC_AES_KEY
            print(f"Debug: Static Key Used for Encryption: {key}")
            cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())  # ECB mode
            encryptor = cipher.encryptor()
            padded_password = raw_password.ljust(16, " ")
            self.encrypted_password = encryptor.update(padded_password.encode()) + encryptor.finalize()
            print(f"Debug: Successfully Encrypted Password: {self.encrypted_password}")
        except Exception as e:
            print(f"Encryption failed: {e}")
            raise

    def decrypt_password(self):
        try:
            key = Config.STATIC_AES_KEY
            print(f"Debug: Static Key Used for Decryption: {key}")
            print(f"Debug: Encrypted Password for Decryption: {self.encrypted_password}")
            
            cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())  # ECB mode
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(self.encrypted_password) + decryptor.finalize()
            decrypted_password = decrypted.decode().rstrip(" ")
            print(f"Debug: Successfully Decrypted Password: {decrypted_password}")
            return decrypted_password
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

