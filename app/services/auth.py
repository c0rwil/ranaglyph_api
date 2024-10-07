from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, SignupRequest, LoginRequest
import logging
import bcrypt
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Function to create a new access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to get the current user based on the provided JWT token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        logger.debug(f"Decoding token: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.error("Token missing 'sub' field.")
            raise credentials_exception
        logger.debug(f"Token decoded successfully: {payload}")

    except JWTError as e:
        logger.error(f"JWT decoding failed: {e}")
        raise credentials_exception

    # Lookup user in the database
    logger.debug(f"Looking up user with ID: {user_id}")
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found.")
        raise credentials_exception

    logger.info(f"User {user.username} authenticated successfully.")
    return User(id=user.id, username=user.username, email=user.email, is_active=user.is_active)


# Function to sign up a new user
def signup_user(request: SignupRequest, db: Session) -> dict:
    if db.query(UserModel).filter(UserModel.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(UserModel).filter(UserModel.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already taken")

    hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = UserModel(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,
        timestamp=datetime.utcnow(),
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User {new_user.username} successfully registered.")
    return {"message": "Signup successful"}


# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# Function to handle user login
def login_user(request: LoginRequest, db: Session) -> dict:
    user = db.query(UserModel).filter(UserModel.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        logger.error(f"Invalid credentials for email: {request.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    logger.info(f"User {user.username} logged in successfully. Token generated.")
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id
    }
