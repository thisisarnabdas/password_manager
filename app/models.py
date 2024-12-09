from app import db, ph  # Make sure ph is imported from app
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.LargeBinary(16), nullable=False)  # Salt for AES key derivation

    stored_passwords = db.relationship('StoredPassword', backref='user', lazy=True)

    def set_password(self, password):
        """Hashes the password using Argon2 and generates a salt for AES key derivation."""
        self.password_hash = ph.hash(password)  # PasswordHasher instance
        self.salt = os.urandom(16)  # Generate a random salt for AES key derivation

    def check_password(self, password):
        """Verifies the provided password matches the stored password hash."""
        try:
            return ph.verify(self.password_hash, password)
        except Exception:
            return False

    def get_aes_key(self, plain_password):
        """Derives an AES key using the plain password and stored salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(plain_password.encode())


class StoredPassword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    encrypted_password = db.Column(db.LargeBinary, nullable=False)
    iv = db.Column(db.LargeBinary(16), nullable=False)  # AES initialization vector
    url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def encrypt_password(self, raw_password, key):
        """Encrypts the password using AES-256 and stores it with IV."""
        iv = os.urandom(16)  # Generate a new IV for each encryption
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        self.encrypted_password = encryptor.update(raw_password.encode()) + encryptor.finalize()
        self.iv = iv

    def decrypt_password(self, key):
        """Decrypts the stored password using AES-256 and the stored IV."""
        try:
            cipher = Cipher(algorithms.AES(key), modes.CFB(self.iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(self.encrypted_password) + decryptor.finalize()
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption failed: {e}")  # Consider logging this for troubleshooting
            return None
