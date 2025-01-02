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

    stored_passwords = db.relationship("StoredPassword", backref="user", lazy=True)

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
    iv = db.Column(db.LargeBinary(16), nullable=False)  # AES initialization vector
    url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def encrypt_password(self, raw_password):
        try:
            key = Config.STATIC_AES_KEY
            iv = os.urandom(16)  # Generate a new IV for encryption
            print(f"Debug: Static Key Used for Encryption: {key}")
            print(f"Debug: IV for Encryption: {iv}")
            
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            self.encrypted_password = encryptor.update(raw_password.encode()) + encryptor.finalize()
            self.iv = iv
            
            # Debugging: Log encrypted password and IV
            print(f"Debug: Successfully Encrypted Password: {self.encrypted_password}")
        except Exception as e:
            print(f"Encryption failed: {e}")
            raise

    def decrypt_password(self):
        try:
            key = Config.STATIC_AES_KEY
            print(f"Debug: Static Key Used for Decryption: {key}")
            print(f"Debug: IV for Decryption: {self.iv}")
            print(f"Debug: Encrypted Password for Decryption: {self.encrypted_password}")
            
            cipher = Cipher(algorithms.AES(key), modes.CFB(self.iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(self.encrypted_password) + decryptor.finalize()
            
            # Debugging: Log decrypted password
            print(f"Debug: Successfully Decrypted Password: {decrypted.decode()}")
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None
