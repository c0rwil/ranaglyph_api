from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True
