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
    type: str  # "realtime" or "custom"

class RealtimeAgentUpdate(BaseModel):
    model: str | None = None
    voice: str | None = None
    system_prompt: str | None = None
    greeting_prompt: str | None = None

class CustomAgentUpdate(BaseModel):
    llm_websocket_url: str | None = None

@router.post("/create", response_model=Union[RealtimeAgent, CustomAgent])
async def create_agent(agent_in: AgentCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Check for duplicate agent name under the same user
    if agent_in.type == "realtime":
        existing_statement = select(RealtimeAgent).where(
            RealtimeAgent.name == agent_in.name,
            RealtimeAgent.user_id == current_user.id
        )
        existing_result = await session.execute(existing_statement)
        if existing_result.scalars().first():
            raise HTTPException(status_code=400, detail="An agent with this name already exists")
        
        agent = RealtimeAgent(
            name=agent_in.name,
            user_id=current_user.id
        )
    elif agent_in.type == "custom":
        existing_statement = select(CustomAgent).where(
            CustomAgent.name == agent_in.name,
            CustomAgent.user_id == current_user.id
        )
        existing_result = await session.execute(existing_statement)
        if existing_result.scalars().first():
            raise HTTPException(status_code=400, detail="An agent with this name already exists")
        
        agent = CustomAgent(
            name=agent_in.name,
            user_id=current_user.id
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid agent type")

    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent

@router.put("/update/realtime/{agent_id}", response_model=RealtimeAgent)
async def update_realtime_agent(
    agent_id: str,
    agent_update: RealtimeAgentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement = select(RealtimeAgent).where(RealtimeAgent.id == agent_id, RealtimeAgent.user_id == current_user.id)
    result = await session.execute(statement)
    agent = result.scalars().first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update fields if provided
    if agent_update.model is not None:
        agent.model = agent_update.model
    if agent_update.voice is not None:
        agent.voice = agent_update.voice
    if agent_update.system_prompt is not None:
        agent.system_prompt = agent_update.system_prompt
    if agent_update.greeting_prompt is not None:
        agent.greeting_prompt = agent_update.greeting_prompt
    
    await session.commit()
    await session.refresh(agent)
    return agent

@router.put("/update/custom/{agent_id}", response_model=CustomAgent)
async def update_custom_agent(
    agent_id: str,
    agent_update: CustomAgentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement = select(CustomAgent).where(CustomAgent.id == agent_id, CustomAgent.user_id == current_user.id)
    result = await session.execute(statement)
    agent = result.scalars().first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update fields if provided
    if agent_update.llm_websocket_url is not None:
        agent.llm_websocket_url = agent_update.llm_websocket_url
    
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
        statement = select(RealtimeAgent).where(
            RealtimeAgent.id == agent_id,
            RealtimeAgent.user_id == current_user.id
        )
        result = await session.execute(statement)
        agent = result.scalars().first()
    elif type == "custom":
        statement = select(CustomAgent).where(
            CustomAgent.id == agent_id,
            CustomAgent.user_id == current_user.id
        )
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
