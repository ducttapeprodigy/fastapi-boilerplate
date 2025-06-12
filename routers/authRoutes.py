from fastapi import APIRouter, Depends, HTTPException, status
import datetime
from models import UserCreate, UserLogin, Token
import db
from auth import verify_password, get_password_hash, create_access_token
import logging
import os

logger = logging.getLogger("FastAPI_Boilerplate")
router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Authentication routes
@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    if user.username in db.fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db.fake_users_db[user.username] = {
        "id": len(db.fake_users_db) + 1,
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_active": True
    }
    
    return {"message": "User created successfully"}

@router.post("/login", response_model=Token,)
async def login(user: UserLogin):
    db_user = db.fake_users_db.get(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        logger.warning(f"Failed login attempt for user: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}