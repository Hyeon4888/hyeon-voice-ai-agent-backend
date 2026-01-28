from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from ..models.table.realtime_agent import RealtimeAgent
from ..models.table.custom_agent import CustomAgent
from ..models.table.user import User
from ..models import get_session
from ..routers.core.auth.router import get_current_user
from livekit.api import AccessToken, VideoGrants
from ..config.config import settings
from pydantic import BaseModel

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)
class AgentCreate(BaseModel):
    name: str
    type: str

@router.post("/create", response_model=Union[RealtimeAgent, CustomAgent])
async def create_agent(agent_in: AgentCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    if agent_in.type == "realtime":
        config = agent_in.config or {}
        
        agent = RealtimeAgent(
            name=agent_in.name,
            user_id=current_user.id,
            model=config.get("model"),
            voice=config.get("voice"),
            system_prompt=config.get("system_prompt"),
            greeting_prompt=config.get("greeting_prompt")
        )
    elif agent_in.type == "custom":
        config = agent_in.config or {}
        
        agent = CustomAgent(
            name=agent_in.name,
            user_id=current_user.id,
            llm_websocket_url=config.get("llm_websocket_url")
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid agent type")

    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent

@router.get("/get/{agent_id}", response_model=Union[RealtimeAgent, CustomAgent])
async def get_agent(
    agent_id: str, 
    type: str, 
    session: AsyncSession = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    if type == "realtime":
        statement = select(RealtimeAgent).where(RealtimeAgent.id == agent_id, RealtimeAgent.user_id == current_user.id)
        result = await session.execute(statement)
        agent = result.scalars().first()
    elif type == "custom":
        statement = select(CustomAgent).where(CustomAgent.id == agent_id, CustomAgent.user_id == current_user.id)
        result = await session.execute(statement)
        agent = result.scalars().first()
    else:
        raise HTTPException(status_code=400, detail="Invalid agent type")

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent

@router.get("/get", response_model=List[Union[RealtimeAgent, CustomAgent]])
async def read_agents(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement_realtime = select(RealtimeAgent).where(RealtimeAgent.user_id == current_user.id)
    result_realtime = await session.execute(statement_realtime)
    realtime_agents = result_realtime.scalars().all()

    statement_custom = select(CustomAgent).where(CustomAgent.user_id == current_user.id)
    result_custom = await session.execute(statement_custom)
    custom_agents = result_custom.scalars().all()
    
    return [*realtime_agents, *custom_agents]

class TokenResponse(BaseModel):
    token: str
    url: str

@router.get("/token", response_model=TokenResponse)
async def get_token(current_user: User = Depends(get_current_user)):
    grant = VideoGrants(room_join=True, room="voice-assistant-room", can_publish=True, can_subscribe=True)
    access_token = AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET, identity=f"user-{current_user.id}", name=current_user.name, grants=grant)
    
    return TokenResponse(
        token=access_token.to_jwt(),
        url=settings.LIVEKIT_URL
    )
