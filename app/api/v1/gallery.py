from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from datetime import datetime
from typing import List, Optional
from ...schemas.models import GalleryInDB, GalleryCreate, GalleryUpdate
from ...db.mongodb import get_database
from ...services.cloudinary_service import upload_image, delete_image
from ..deps import get_current_user
import tempfile
import os
import uuid

router = APIRouter()

@router.get("/", response_model=List[GalleryInDB])
async def list_gallery(db=Depends(get_database)):
    cursor = db.gallery.find().sort("created_at", -1)
    return await cursor.to_list(length=100)

@router.post("/", response_model=GalleryInDB)
async def create_gallery_item(
    title: str = Form(...),
    file: UploadFile = File(...),
    db=Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    # Temporary save for Cloudinary upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Upload to Cloudinary
        upload_result = upload_image(tmp_path, folder="pr7security/gallery")
        
        # Prepare DB item
        new_item = {
            "_id": str(uuid.uuid4()),
            "title": title,
            "image_url": upload_result["url"],
            "public_id": upload_result["public_id"],
            "created_at": datetime.utcnow()
        }
        
        await db.gallery.insert_one(new_item)
        return new_item
    finally:
        os.unlink(tmp_path)

@router.delete("/{item_id}")
async def delete_gallery_item(item_id: str, db=Depends(get_database), current_user: str = Depends(get_current_user)):
    item = await db.gallery.find_one({"_id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Delete from Cloudinary
    delete_image(item["public_id"])
    
    # Delete from DB
    await db.gallery.delete_one({"_id": item_id})
    return {"message": "Item deleted successfully"}

@router.put("/{item_id}", response_model=GalleryInDB)
async def update_gallery_item(
    item_id: str,
    title: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db=Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    item = await db.gallery.find_one({"_id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = {}
    if title:
        update_data["title"] = title
    
    if file:
        # Save and upload new image
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        try:
            # Delete old image and upload new one
            delete_image(item["public_id"])
            upload_result = upload_image(tmp_path, folder="pr7security/gallery")
            update_data["image_url"] = upload_result["url"]
            update_data["public_id"] = upload_result["public_id"]
        finally:
            os.unlink(tmp_path)
    
    if update_data:
        await db.gallery.update_one({"_id": item_id}, {"$set": update_data})
        item.update(update_data)
        
    return item
