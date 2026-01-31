from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class PhoneNumber(SQLModel, table=True):
    __tablename__ = "phone_number"
    
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    label: str
    number: str
    provider: str
    user_id: int = Field(foreign_key="voice-agent-user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
