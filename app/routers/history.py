from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, time
from ..models.table.history import History
from ..models.table.user import User
from ..models import get_session
from ..routers.core.auth.router import get_current_user, verify_api_key_or_user
from ..models.table.agent import Agent

router = APIRouter(
    prefix="/history",
    tags=["history"],
    responses={404: {"description": "Not found"}},
)

class HistoryCreate(SQLModel):
    agent_id: str
    date: date
    time: time
    duration: int
    summary: Optional[str] = None
    conversation: List[dict] = []

@router.post("/create", response_model=History)
async def create_history(
    history_in: HistoryCreate, 
    session: AsyncSession = Depends(get_session), 
    auth_info: dict = Depends(verify_api_key_or_user)
):
    if auth_info["type"] == "api_key":
        # API Key access: We need to find the user_id from the agent
        statement = select(Agent).where(Agent.id == history_in.agent_id)
        result = await session.execute(statement)
        agent = result.scalars().first()
        
        if not agent:
             raise HTTPException(status_code=404, detail="Agent not found")
        
        user_id = agent.user_id
    else:
        # User access
        user_id = auth_info["user"].id

    history = History(
        user_id=user_id,
        **history_in.model_dump()
    )
    
    session.add(history)
    await session.commit()
    await session.refresh(history)
    return history

@router.get("/get/{agent_id}", response_model=List[History])
async def read_history(agent_id: str, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(History).where(History.user_id == current_user.id, History.agent_id == agent_id).order_by(History.date.desc(), History.time.desc())

    result = await session.execute(statement)
    histories = result.scalars().all()
    return histories
