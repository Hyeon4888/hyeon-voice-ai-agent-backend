from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "voice-agent-user"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    refresh_token: Optional[str] = Field(default=None)
    refresh_token_expires: Optional[datetime] = Field(default=None)
