from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from datetime import datetime
from typing import List, Optional
from ...schemas.models import ServiceInDB, ServiceCreate, ServiceUpdate
from ...db.mongodb import get_database
from ...services.cloudinary_service import upload_image, delete_image
from ..deps import get_current_user
import tempfile
import os
import uuid

router = APIRouter()

@router.get("/", response_model=List[ServiceInDB])
async def list_services(db=Depends(get_database)):
    cursor = db.services.find().sort("created_at", -1)
    return await cursor.to_list(length=100)

@router.get("/{service_id}", response_model=ServiceInDB)
async def get_service(service_id: str, db=Depends(get_database)):
    service = await db.services.find_one({"_id": service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", response_model=ServiceInDB)
async def create_service(
    heading: str = Form(...),
    description: str = Form(...),
    long_description: Optional[str] = Form(None),
    guidelines: Optional[str] = Form(None), # Comma separated
    file: UploadFile = File(...),
    db=Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        upload_result = upload_image(tmp_path, folder="pr7security/services")
        
        # Prepare DB item
        guidelines_list = [g.strip() for g in guidelines.split(",")] if guidelines else []
        new_service = {
            "_id": str(uuid.uuid4()),
            "heading": heading,
            "description": description,
            "long_description": long_description,
            "guidelines": guidelines_list,
            "image_url": upload_result["url"],
            "public_id": upload_result["public_id"],
            "created_at": datetime.utcnow()
        }
        
        await db.services.insert_one(new_service)
        return new_service
    finally:
        os.unlink(tmp_path)

@router.delete("/{service_id}")
async def delete_service(service_id: str, db=Depends(get_database), current_user: str = Depends(get_current_user)):
    service = await db.services.find_one({"_id": service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    delete_image(service["public_id"])
    await db.services.delete_one({"_id": service_id})
    return {"message": "Service deleted successfully"}

@router.put("/{service_id}", response_model=ServiceInDB)
async def update_service(
    service_id: str,
    heading: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    long_description: Optional[str] = Form(None),
    guidelines: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db=Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    service = await db.services.find_one({"_id": service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    update_data = {}
    if heading:
        update_data["heading"] = heading
    if description:
        update_data["description"] = description
    if long_description:
        update_data["long_description"] = long_description
    if guidelines is not None:
        update_data["guidelines"] = [g.strip() for g in guidelines.split(",")] if guidelines else []
    
    if file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        try:
            delete_image(service["public_id"])
            upload_result = upload_image(tmp_path, folder="pr7security/services")
            update_data["image_url"] = upload_result["url"]
            update_data["public_id"] = upload_result["public_id"]
        finally:
            os.unlink(tmp_path)
    
    if update_data:
        await db.services.update_one({"_id": service_id}, {"$set": update_data})
        service.update(update_data)
        
    return service
