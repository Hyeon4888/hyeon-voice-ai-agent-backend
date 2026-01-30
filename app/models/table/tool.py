from sqlmodel import SQLModel, Field
from typing import Optional

class Tool(SQLModel, table=True):
    __tablename__ = "voice-agent-tool"
    
    id: str = Field(primary_key=True)
    name: str
    appointment_tool: bool = Field(default=False)
    user_id: int = Field(foreign_key="voice-agent-user.id")
