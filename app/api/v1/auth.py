from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ...core.config import settings
from ...core.security import create_access_token, verify_password, get_password_hash
from pydantic import BaseModel

router = APIRouter()

# Fixed Admin Credentials (per user request)
ADMIN_USER = "pr7security"
# We'll hash this once and use it for comparison
# Alternatively, I could just compare strings, but it's better to show correct pattern
ADMIN_HASH = get_password_hash("Admin123") 

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != ADMIN_USER or not verify_password(form_data.password, ADMIN_HASH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=form_data.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
