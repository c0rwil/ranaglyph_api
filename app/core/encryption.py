from fastapi import HTTPException
from jose import JWTError, jwt
from Crypto.Cipher import AES
from typing import Tuple
from datetime import datetime, timedelta
import bcrypt
from app.core.config import settings

# Function to hash a password
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Generate JWT Token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=504)):
    to_encode = data.copy()
    # Ensure the "sub" is a string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)
    return encoded_jwt


# Encrypt a message using AES
def encrypt_message(plain_text: str) -> Tuple[bytes, bytes]:
    cipher = AES.new(settings.encryption_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode())
    return cipher.nonce, ciphertext

# Decrypt a message using AES
def decrypt_message(nonce: bytes, ciphertext: bytes) -> str:
    cipher = AES.new(settings.encryption_key, AES.MODE_EAX, nonce=nonce)
    plain_text = cipher.decrypt(ciphertext).decode()
    return plain_text

# Authenticate the JWT Token for WebSocket connections
async def authenticate_websocket(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Invalid authentication credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid authentication credentials")
