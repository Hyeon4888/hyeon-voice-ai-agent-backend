from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON

class AgentBase(SQLModel):
    name: str = Field(index=True)
    config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

class AgentCreate(SQLModel):
    name: str
    type: str # "realtime" or "custom"
    config: Optional[Dict[str, Any]] = None # To hold specific fields during creation
