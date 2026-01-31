from fastapi import APIRouter, Depends, HTTPException, Header, Security
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from ..models.table.phone_number import PhoneNumber
from ..models.table.user import User
from ..models import get_session
from ..routers.core.auth.router import get_current_user, verify_api_key_or_user

router = APIRouter(
    prefix="/phone_numbers",
    tags=["phone_numbers"],
    responses={404: {"description": "Not found"}},
)

class PhoneNumberCreate(BaseModel):
    label: str
    number: str
    provider: str

@router.post("/create", response_model=PhoneNumber)
async def create_phone_number(
    phone_in: PhoneNumberCreate, 
    session: AsyncSession = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    phone_number = PhoneNumber(
        label=phone_in.label,
        number=phone_in.number,
        provider=phone_in.provider,
        user_id=current_user.id
    )
    
    session.add(phone_number)
    await session.commit()
    await session.refresh(phone_number)
    return phone_number

@router.get("/get", response_model=List[PhoneNumber])
async def read_phone_numbers(
    session: AsyncSession = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    statement = select(PhoneNumber).where(PhoneNumber.user_id == current_user.id)
    result = await session.execute(statement)
    phone_numbers = result.scalars().all()
    return phone_numbers

@router.get("/get/{id}", response_model=PhoneNumber)
async def get_phone_number(
    id: UUID, 
    session: AsyncSession = Depends(get_session), 
    auth_info: dict = Depends(verify_api_key_or_user)
):
    if auth_info["type"] == "api_key":
        # API Key access: Fetch by ID only
        statement = select(PhoneNumber).where(PhoneNumber.id == id)
    else:
        # User access: Fetch by ID and User ID
        current_user = auth_info["user"]
        statement = select(PhoneNumber).where(
            PhoneNumber.id == id,
            PhoneNumber.user_id == current_user.id
        )
    
    result = await session.execute(statement)
    phone_number = result.scalars().first()
    
    if not phone_number:
        raise HTTPException(status_code=404, detail="Phone number not found")
    return phone_number

@router.delete("/delete/{phone_id}")
async def delete_phone_number(
    phone_id: UUID, 
    session: AsyncSession = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    statement = select(PhoneNumber).where(
        PhoneNumber.id == phone_id,
        PhoneNumber.user_id == current_user.id
    )
    result = await session.execute(statement)
    phone_number = result.scalars().first()
    
    if not phone_number:
        raise HTTPException(status_code=404, detail="Phone number not found")
        
    await session.delete(phone_number)
    await session.commit()
    
    return {"ok": True}
