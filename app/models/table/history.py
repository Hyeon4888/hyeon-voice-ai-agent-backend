from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict
from datetime import date, time
from sqlalchemy import Column, JSON

class History(SQLModel, table=True):
    __tablename__ = "voice-agent-history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="voice-agent-user.id")
    agent_id: str = Field(foreign_key="voice-agent-agent.id")
    date: date
    time: time
    duration: int
    summary: Optional[str] = Field(default=None)
    conversation: List[dict] = Field(default=[], sa_column=Column(JSON))
