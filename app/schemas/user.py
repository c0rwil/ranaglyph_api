from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(None, description="New username")
    phone_number: Optional[str] = Field(None, description="Optional phone number")


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: Optional[bool] = True
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str



class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User
    message: str