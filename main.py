from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import User, UserCreate, UserLogin, Token, Item  # models.py contains the Pydantic models
from routers import adminRoutes, itemRoutes  # Import your routers

import os
import datetime

import db
from auth import verify_password, get_password_hash, create_access_token, get_current_active_user

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI app
app = FastAPI(
    title="My FastAPI Boilerplate Service",
    description="A FastAPI backend service with authentication",
    version="0.0.3"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "error": "NOT_FOUND"}
    )

@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": "INTERNAL_ERROR"}
    )

# Authentication routes
@app.post("/auth/register", response_model=dict)
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

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    db_user = db.fake_users_db.get(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
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

# Public routes
@app.get("/")
async def root():
    return {"message": "Welcome to the API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow()}

# Protected routes
@app.get("/profile", response_model=User)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

app.include_router(adminRoutes.router, prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_active_user)])
app.include_router(itemRoutes.router, prefix="/items", tags=["items"], dependencies=[Depends(get_current_active_user)])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) #reload=True)