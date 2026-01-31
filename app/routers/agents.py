from fastapi import APIRouter, Depends, HTTPException, Header, Security
import logging

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..models.table.agent import Agent
from ..models.table.user import User
from ..models import get_session
from ..routers.core.auth.router import get_current_user, verify_api_key_or_user
from livekit.api import AccessToken, VideoGrants
from ..config.config import settings
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

class AgentCreate(BaseModel):
    name: str
    type: str = "realtime"

class AgentUpdate(BaseModel):
    model: Optional[str] = None
    voice: Optional[str] = None
    system_prompt: Optional[str] = None
    greeting_prompt: Optional[str] = None
    api_key: Optional[str] = None
    tool_id: Optional[str] = None
    inbound_id: Optional[UUID] = None

@router.post("/create", response_model=Agent)
async def create_agent(agent_in: AgentCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Check for duplicate agent name under the same user
    existing_statement = select(Agent).where(
        Agent.name == agent_in.name,
        Agent.user_id == current_user.id
    )
    existing_result = await session.execute(existing_statement)
    if existing_result.scalars().first():
        raise HTTPException(status_code=400, detail="An agent with this name already exists")
    
    agent = Agent(
        name=agent_in.name,
        type=agent_in.type,
        user_id=current_user.id,
    )

    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent

@router.put("/update/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement = select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id)
    result = await session.execute(statement)
    agent = result.scalars().first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Debug logging
    logger.info(f"DEBUG: Updating agent {agent_id}. Received: {agent_update.model_dump(exclude_unset=True)}")
    
    # Update fields if provided in matching schema
    update_data = agent_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(agent, key):
            setattr(agent, key, value)
    
    await session.commit()
    await session.refresh(agent)
    await session.refresh(agent)
    return agent


@router.get("/get/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str, 
    session: AsyncSession = Depends(get_session), 
    auth_info: dict = Depends(verify_api_key_or_user)
):
    if auth_info["type"] == "api_key":
        # API Key access: Fetch agent by ID only
        statement = select(Agent).where(Agent.id == agent_id)
    else:
        # User access: Fetch agent by ID and User ID
        current_user = auth_info["user"]
        statement = select(Agent).where(
            Agent.id == agent_id,
            Agent.user_id == current_user.id
        )
    
    result = await session.execute(statement)
    agent = result.scalars().first()
    
    if agent:
        return agent

    raise HTTPException(status_code=404, detail="Agent not found")

@router.get("/get", response_model=List[Agent])
async def read_agents(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Agent).where(Agent.user_id == current_user.id)
    result = await session.execute(statement)
    agents = result.scalars().all()
    
    return agents

class TokenResponse(BaseModel):
    token: str
    url: str

@router.get("/token", response_model=TokenResponse)
async def get_token(agent_id: str,current_user: User = Depends(get_current_user)):
    grant = VideoGrants(room_join=True, room="voice-assistant-room", can_publish=True, can_subscribe=True)
    access_token = (
        AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
        .with_identity(str(current_user.id))
        .with_grants(grant)
        .with_attributes({"agent_id": agent_id})
    )
    
    return TokenResponse(
        token=access_token.to_jwt(),
        url=settings.LIVEKIT_URL
    )
