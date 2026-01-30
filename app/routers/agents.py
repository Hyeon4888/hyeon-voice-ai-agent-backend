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
from ..routers.core.auth.router import get_current_user
from livekit.api import AccessToken, VideoGrants
from ..config.config import settings
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

class AgentCreate(BaseModel):
    name: str
    type: str = "realtime"
    api_key: str

class AgentUpdate(BaseModel):
    model: Optional[str] = None
    voice: Optional[str] = None
    system_prompt: Optional[str] = None
    greeting_prompt: Optional[str] = None
    api_key: Optional[str] = None

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
        api_key=agent_in.api_key
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
    
    # Update fields if provided
    if agent_update.model is not None:
        agent.model = agent_update.model
    if agent_update.voice is not None:
        agent.voice = agent_update.voice
    if agent_update.system_prompt is not None:
        agent.system_prompt = agent_update.system_prompt
    if agent_update.greeting_prompt is not None:
        agent.greeting_prompt = agent_update.greeting_prompt
    if agent_update.api_key is not None:
        agent.api_key = agent_update.api_key
    
    await session.commit()
    await session.refresh(agent)
    await session.refresh(agent)
    return agent

async def verify_api_key_or_user(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session)
) -> dict:
    # DEBUG LOGGING
    logger.info("DEBUG: verify_api_key_or_user called")
    
    if not authorization:
        logger.info("DEBUG: No authorization header")
        raise HTTPException(status_code=401, detail="Not authenticated")

    scheme, _, param = authorization.partition(" ")
    logger.info(f"DEBUG: scheme: '{scheme}', param: '{param}'")

    # 1. Check for API Key
    if scheme.lower() == "bearer" and param == settings.API_SECRET_KEY:
        logger.info("DEBUG: API Key matched")
        return {"type": "api_key", "user_id": None}
    
    # 2. Check for User (JWT)
    # We manually invoke the logic from get_current_user here to avoid strict dependency failures
    # Since get_current_user is complex to import and call manually with dependencies, 
    # we will attempt to decode the JWT here directly or use a helper if possible.
    # A cleaner way is to try-except the jwt decoding.
    
    from ..routers.core.auth.router import oauth2_scheme, ALGORITHM, SECRET_KEY, User
    import jwt

    logger.info("DEBUG: Checking for User JWT")
    try:
        # Verify JWT
        payload = jwt.decode(param, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.info("DEBUG: JWT missing email")
            raise HTTPException(status_code=401, detail="Invalid token")
            
        # Fetch user
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.scalars().first()
        
        if user:
            logger.info(f"DEBUG: User authenticated: {user.email}")
            return {"type": "user", "user": user}
        else:
             logger.info("DEBUG: User not found in DB")
    except jwt.PyJWTError as e:
        logger.info(f"DEBUG: JWT Error: {e}")
        # If it was an API key attempt, we already failed that check.
        # If it was a JWT attempt, it failed here.
        pass
    except Exception as e:
        logger.error(f"DEBUG: Unexpected auth error: {e}")

    logger.info("DEBUG: Authentication failed (neither API Key nor valid User Token)")
    raise HTTPException(status_code=401, detail="Not authenticated")

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
