from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import List
from ...schemas.models import JobApplicationInDB, JobApplicationCreate
from ...db.mongodb import get_database
from ..deps import get_current_user
import uuid

router = APIRouter()

@router.get("/", response_model=List[JobApplicationInDB])
async def list_applications(db=Depends(get_database), current_user: str = Depends(get_current_user)):
    cursor = db.applications.find().sort("created_at", -1)
    return await cursor.to_list(length=500)

@router.post("/", response_model=JobApplicationInDB, status_code=status.HTTP_201_CREATED)
async def submit_application(
    application: JobApplicationCreate,
    db=Depends(get_database)
):
    new_application = application.dict()
    new_application["_id"] = str(uuid.uuid4())
    new_application["created_at"] = datetime.utcnow()
    
    await db.applications.insert_one(new_application)
    return new_application

@router.delete("/{application_id}")
async def delete_application(application_id: str, db=Depends(get_database), current_user: str = Depends(get_current_user)):
    result = await db.applications.delete_one({"_id": application_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted successfully"}
