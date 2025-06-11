from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import User, Item
import db
from auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Item])
async def get_items(current_user: User = Depends(get_current_active_user)):
    user_items = [item for item in db.fake_items_db if item["owner_id"] == current_user.id]
    return user_items

@router.post("/", response_model=Item)
async def create_item(item: Item, current_user: User = Depends(get_current_active_user)):
    item_dict = item.dict()
    item_dict["id"] = len(db.fake_items_db) + 1
    item_dict["owner_id"] = current_user.id
    db.fake_items_db.append(item_dict)
    return Item(**item_dict)

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int, current_user: User = Depends(get_current_active_user)):
    item = next((item for item in db.fake_items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this item")
    
    return Item(**item)

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: Item, current_user: User = Depends(get_current_active_user)):
    item_index = next((i for i, item in enumerate(db.fake_items_db) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if db.fake_items_db[item_index]["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this item")
    
    db.fake_items_db[item_index].update(item_update.dict(exclude={"id", "owner_id"}))
    return Item(**db.fake_items_db[item_index])

@router.delete("/{item_id}")
async def delete_item(item_id: int, current_user: User = Depends(get_current_active_user)):
    item_index = next((i for i, item in enumerate(db.fake_items_db) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if db.fake_items_db[item_index]["owner_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this item")
    
    del db.fake_items_db[item_index]
    return {"message": "Item deleted successfully"}