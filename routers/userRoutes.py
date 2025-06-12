from fastapi import APIRouter, Depends
from models import User
from auth import get_current_active_user

router = APIRouter()

# Admin route (example of role-based access)
@router.get("/profile", response_model=User)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user