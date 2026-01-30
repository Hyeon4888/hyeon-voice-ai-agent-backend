from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..models.table.tool import Tool
from ..models.table.user import User
from ..models import get_session
from ..routers.core.auth.router import get_current_user
from pydantic import BaseModel

router = APIRouter(
    prefix="/tools",
    tags=["tools"],
)

class ToolCreate(BaseModel):
    id: str
    name: str
    appointment_tool: bool = False

@router.post("/create", response_model=Tool)
async def create_tool(tool_in: ToolCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    existing_statement = select(Tool).where(Tool.id == tool_in.id)
    existing_result = await session.execute(existing_statement)
    if existing_result.scalars().first():
        raise HTTPException(status_code=400, detail="Tool ID already exists")

    tool = Tool(
        id=tool_in.id,
        name=tool_in.name,
        appointment_tool=tool_in.appointment_tool,
        user_id=current_user.id
    )

    session.add(tool)
    await session.commit()
    await session.refresh(tool)
    return tool

@router.get("/list", response_model=List[Tool])
async def list_tools(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Tool).where(Tool.user_id == current_user.id)
    result = await session.execute(statement)
    return result.scalars().all()

@router.get("/get/{id}", response_model=Tool)
async def get_tool(id: str, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Tool).where(Tool.id == id, Tool.user_id == current_user.id)
    result = await session.execute(statement)
    tool = result.scalars().first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@router.delete("/delete/{id}")
async def delete_tool(id: str, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Tool).where(Tool.id == id, Tool.user_id == current_user.id)
    result = await session.execute(statement)
    tool = result.scalars().first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    await session.delete(tool)
    await session.commit()
    return {"message": "Tool deleted"}
