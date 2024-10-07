from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.user import SignupRequest, LoginRequest, LoginResponse, UpdateUserRequest, User
from app.services.auth import signup_user, login_user, get_current_user, update_user
from app.db import get_db

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user_data = login_user(request, db)
    if user_data:
        user = User(
            id=user_data["user_id"],
            username=user_data["username"],
            email=user_data["email"],
            is_active=user_data["is_active"]
        )
        return {
            "access_token": user_data["access_token"],
            "token_type": user_data["token_type"],
            "user": user,
            "message": user_data["message"]
        }
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.post("/signup", response_model=dict)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    return signup_user(request, db)


@router.put("/user/update", response_model=User, summary="Update user profile")
async def update_user_profile(request: UpdateUserRequest, db: Session = Depends(get_db), current_user: User= Depends(get_current_user)):
    updated_user = update_user(current_user.id, request, db)
    return updated_user