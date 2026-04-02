from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from datetime import datetime
from typing import List, Optional
from ...schemas.models import BlogInDB, BlogCreate, BlogUpdate
from ...db.mongodb import get_database
from ...services.cloudinary_service import upload_image, delete_image
from ..deps import get_current_user
import tempfile
import os
import uuid

router = APIRouter()

@router.get("/", response_model=List[BlogInDB])
async def list_blogs(db=Depends(get_database)):
    cursor = db.blogs.find().sort("created_at", -1)
    return await cursor.to_list(length=100)

@router.get("/{blog_id}", response_model=BlogInDB)
async def get_blog(blog_id: str, db=Depends(get_database)):
    blog = await db.blogs.find_one({"_id": blog_id})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

@router.post("/", response_model=BlogInDB)
async def create_blog(
    title: str = Form(...),
    excerpt: str = Form(...),
    content: str = Form(...),
    category: str = Form(...),
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
        upload_result = upload_image(tmp_path, folder="pr7security/blogs")
        
        # Prepare DB item
        new_item = {
            "_id": str(uuid.uuid4()),
            "title": title,
            "excerpt": excerpt,
            "content": content,
            "category": category,
            "image_url": upload_result["url"],
            "public_id": upload_result["public_id"],
            "created_at": datetime.utcnow()
        }
        
        await db.blogs.insert_one(new_item)
        return new_item
    finally:
        os.unlink(tmp_path)

@router.delete("/{blog_id}")
async def delete_blog(blog_id: str, db=Depends(get_database), current_user: str = Depends(get_current_user)):
    blog = await db.blogs.find_one({"_id": blog_id})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    # Delete from Cloudinary
    delete_image(blog["public_id"])
    
    # Delete from DB
    await db.blogs.delete_one({"_id": blog_id})
    return {"message": "Blog deleted successfully"}

@router.put("/{blog_id}", response_model=BlogInDB)
async def update_blog(
    blog_id: str,
    title: Optional[str] = Form(None),
    excerpt: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db=Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    blog = await db.blogs.find_one({"_id": blog_id})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    update_data = {}
    if title: update_data["title"] = title
    if excerpt: update_data["excerpt"] = excerpt
    if content: update_data["content"] = content
    if category: update_data["category"] = category
    
    if file:
        # Save and upload new image
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        try:
            # Delete old image and upload new one
            delete_image(blog["public_id"])
            upload_result = upload_image(tmp_path, folder="pr7security/blogs")
            update_data["image_url"] = upload_result["url"]
            update_data["public_id"] = upload_result["public_id"]
        finally:
            os.unlink(tmp_path)
    
    if update_data:
        await db.blogs.update_one({"_id": blog_id}, {"$set": update_data})
        blog.update(update_data)
        
    return blog
