from sqlalchemy import Column, BigInteger, String, Text, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    phone_number = Column(String, nullable=True)  # Optional phone number
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True)
