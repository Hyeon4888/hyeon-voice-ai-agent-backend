from typing import Optional
from sqlmodel import Field
from datetime import datetime
from .schemas import AgentBase

class RealtimeAgent(AgentBase, table=True):
    __tablename__ = "voice-agent-realtime-agent"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="voice-agent-user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Realtime specific fields
    model: str
    voice: str
    system_prompt: Optional[str] = Field(default=None)
    greeting_prompt: Optional[str] = Field(default=None)
