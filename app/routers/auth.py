from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.user import SignupRequest, LoginRequest
from app.services.auth import signup_user, login_user
from app.db import get_db

router = APIRouter()

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = login_user(request, db)
    if user:
        return {
            "access_token": user["access_token"],
            "token_type": user["token_type"],
            "user_id": user["user_id"],
            "message": user["message"]
        }
    raise HTTPException(status_code=401, detail="Invalid username or password")

@router.post("/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    return signup_user(request, db)
