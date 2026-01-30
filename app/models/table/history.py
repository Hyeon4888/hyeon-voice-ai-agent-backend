from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, time

class History(SQLModel, table=True):
    __tablename__ = "voice-agent-history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="voice-agent-user.id")
    agent_id: str = Field(foreign_key="voice-agent-agent.id")
    date: date
    time: time
    duration: int
    summary: Optional[str] = Field(default=None)
    conversation: Optional[str] = Field(default=None)
