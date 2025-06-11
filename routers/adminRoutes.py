from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import User
import db
from auth import get_current_active_user

router = APIRouter()

# Admin route (example of role-based access)
@router.get("/users", response_model=List[User])
async def get_all_users(current_user: User = Depends(get_current_active_user)):
    # In a real app, you'd check for admin role here
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return [User(**user) for user in db.fake_users_db.values()]