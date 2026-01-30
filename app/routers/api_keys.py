from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..models.table.api_key import ApiKey
from ..models.table.user import User
from ..models import get_session
from ..routers.core.auth.router import get_current_user
from pydantic import BaseModel

router = APIRouter(
    prefix="/api-keys",
    tags=["api-keys"],
    responses={404: {"description": "Not found"}},
)

class ApiKeyCreate(BaseModel):
    id: str
    name: str
    model: str

@router.post("/create", response_model=ApiKey)
async def create_api_key(api_key_in: ApiKeyCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Check if ID already exists
    existing_statement = select(ApiKey).where(ApiKey.id == api_key_in.id)
    existing_result = await session.execute(existing_statement)
    if existing_result.scalars().first():
        raise HTTPException(status_code=400, detail="API Key ID already exists")

    api_key = ApiKey(
        id=api_key_in.id,
        name=api_key_in.name,
        model=api_key_in.model,
        user_id=current_user.id
    )

    session.add(api_key)
    await session.commit()
    await session.refresh(api_key)
    return api_key

@router.get("/list", response_model=List[ApiKey])
async def list_api_keys(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(ApiKey).where(ApiKey.user_id == current_user.id)
    result = await session.execute(statement)
    api_keys = result.scalars().all()
    return api_keys

@router.get("/{name}", response_model=ApiKey)
async def get_api_key(name: str, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(ApiKey).where(ApiKey.name == name, ApiKey.user_id == current_user.id)
    result = await session.execute(statement)
    api_key = result.scalars().first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")
    
    return api_key

@router.delete("/{name}")
async def delete_api_key(name: str, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(ApiKey).where(ApiKey.name == name, ApiKey.user_id == current_user.id)
    result = await session.execute(statement)
    api_key = result.scalars().first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")
    
    await session.delete(api_key)
    await session.commit()
    return {"message": "API Key deleted"}
