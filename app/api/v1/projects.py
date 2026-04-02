from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from datetime import datetime
from typing import List, Optional
from ...schemas.models import ProjectInDB, ProjectCreate, ProjectUpdate
from ...db.mongodb import get_database
from ...services.cloudinary_service import upload_image, delete_image
from ..deps import get_current_user
import tempfile
import os
import uuid

router = APIRouter()

@router.get("/", response_model=List[ProjectInDB])
async def list_projects(db=Depends(get_database)):
    cursor = db.projects.find().sort("created_at", -1)
    return await cursor.to_list(length=100)

@router.get("/{project_id}", response_model=ProjectInDB)
async def get_project(project_id: str, db=Depends(get_database)):
    project = await db.projects.find_one({"_id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectInDB)
async def create_project(
    title: str = Form(...),
    sector: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
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
        upload_result = upload_image(tmp_path, folder="pr7security/projects")
        
        # Prepare DB item
        new_item = {
            "_id": str(uuid.uuid4()),
            "title": title,
            "sector": sector,
            "location": location,
            "description": description,
            "image_url": upload_result["url"],
            "public_id": upload_result["public_id"],
            "created_at": datetime.utcnow()
        }
        
        await db.projects.insert_one(new_item)
        return new_item
    finally:
        os.unlink(tmp_path)

@router.delete("/{project_id}")
async def delete_project(project_id: str, db=Depends(get_database), current_user: str = Depends(get_current_user)):
    project = await db.projects.find_one({"_id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete from Cloudinary
    delete_image(project["public_id"])
    
    # Delete from DB
    await db.projects.delete_one({"_id": project_id})
    return {"message": "Project deleted successfully"}

@router.put("/{project_id}", response_model=ProjectInDB)
async def update_project(
    project_id: str,
    title: Optional[str] = Form(None),
    sector: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db=Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    project = await db.projects.find_one({"_id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = {}
    if title: update_data["title"] = title
    if sector: update_data["sector"] = sector
    if location: update_data["location"] = location
    if description: update_data["description"] = description
    
    if file:
        # Save and upload new image
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        try:
            # Delete old image and upload new one
            delete_image(project["public_id"])
            upload_result = upload_image(tmp_path, folder="pr7security/projects")
            update_data["image_url"] = upload_result["url"]
            update_data["public_id"] = upload_result["public_id"]
        finally:
            os.unlink(tmp_path)
    
    if update_data:
        await db.projects.update_one({"_id": project_id}, {"$set": update_data})
        project.update(update_data)
        
    return project
