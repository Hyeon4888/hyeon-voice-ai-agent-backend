from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..models.table.tool import Tool
from ..models.table.user import User
from ..models import get_session
from ..routers.core.auth.router import get_current_user, verify_api_key_or_user
from pydantic import BaseModel

router = APIRouter(
    prefix="/tools",
    tags=["tools"],
)

class ToolCreate(BaseModel):
    name: str

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    appointment_tool: Optional[bool] = None

@router.post("/create", response_model=Tool)
async def create_tool(tool_in: ToolCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    tool_id = f"{current_user.id}_{tool_in.name}"
    
    existing_statement = select(Tool).where(Tool.id == tool_id)
    existing_result = await session.execute(existing_statement)
    if existing_result.scalars().first():
        raise HTTPException(status_code=400, detail="Tool with this name already exists for this user")

    tool = Tool(
        id=tool_id,
        name=tool_in.name,
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
async def get_tool(
    id: str, 
    session: AsyncSession = Depends(get_session), 
    auth_info: dict = Depends(verify_api_key_or_user)
):
    if auth_info["type"] == "api_key":
        # API Key access: Fetch tool by ID only
        statement = select(Tool).where(Tool.id == id)
    else:
        # User access: Fetch tool by ID and User ID
        current_user = auth_info["user"]
        statement = select(Tool).where(
            Tool.id == id, 
            Tool.user_id == current_user.id
        )
    
    result = await session.execute(statement)
    tool = result.scalars().first()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool

@router.patch("/update/{id}", response_model=Tool)
async def update_tool(id: str, tool_in: ToolUpdate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Tool).where(Tool.id == id, Tool.user_id == current_user.id)
    result = await session.execute(statement)
    tool = result.scalars().first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    update_data = tool_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tool, key, value)
    
    session.add(tool)
    await session.commit()
    await session.refresh(tool)
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
