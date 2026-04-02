from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import List, Optional
from ...schemas.models import VacancyInDB, VacancyCreate, VacancyUpdate
from ...db.mongodb import get_database
from ..deps import get_current_user
import uuid

router = APIRouter()

@router.get("/", response_model=List[VacancyInDB])
async def list_vacancies(db=Depends(get_database)):
    cursor = db.vacancies.find().sort("created_at", -1)
    return await cursor.to_list(length=100)

@router.post("/", response_model=VacancyInDB, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy: VacancyCreate,
    db=Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    new_vacancy = vacancy.dict()
    new_vacancy["_id"] = str(uuid.uuid4())
    new_vacancy["created_at"] = datetime.utcnow()
    
    await db.vacancies.insert_one(new_vacancy)
    return new_vacancy

@router.delete("/{vacancy_id}")
async def delete_vacancy(vacancy_id: str, db=Depends(get_database), current_user: str = Depends(get_current_user)):
    result = await db.vacancies.delete_one({"_id": vacancy_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return {"message": "Vacancy deleted successfully"}

@router.put("/{vacancy_id}", response_model=VacancyInDB)
async def update_vacancy(
    vacancy_id: str,
    vacancy_update: VacancyUpdate,
    db=Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    existing_vacancy = await db.vacancies.find_one({"_id": vacancy_id})
    if not existing_vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    update_data = {k: v for k, v in vacancy_update.dict().items() if v is not None}
    
    if update_data:
        await db.vacancies.update_one({"_id": vacancy_id}, {"$set": update_data})
        existing_vacancy.update(update_data)
        
    return existing_vacancy
