import os
from datetime import timedelta
from pathlib import Path


class Config:
    # Base directory of the application
    BASEDIR = Path(__file__).parent.resolve()

    # Database directory and file path
    DATABASE_DIR = BASEDIR / 'database'
    DATABASE_PATH = DATABASE_DIR / 'app.db'

    # Ensure the database directory exists
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    # Flask configurations
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')  # Use an environment variable or fallback
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # Static AES key for encryption (32 bytes for AES-256)
    STATIC_AES_KEY = b"thisisaverysecurestatickey123456"
    if not isinstance(STATIC_AES_KEY, bytes) or len(STATIC_AES_KEY) != 32:
        raise ValueError("STATIC_AES_KEY must be a 32-byte value for AES-256.")

