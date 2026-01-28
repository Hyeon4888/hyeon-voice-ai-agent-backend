from typing import Optional
from sqlmodel import Field
from datetime import datetime
from .schemas import AgentBase

class CustomAgent(AgentBase, table=True):
    __tablename__ = "voice-agent-custom-agent"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="voice-agent-user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Custom specific fields
    llm_websocket_url: str
