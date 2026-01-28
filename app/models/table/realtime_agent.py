from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class RealtimeAgent(SQLModel, table=True):
    __tablename__ = "voice-agent-realtime-agent"
    
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    user_id: int = Field(foreign_key="voice-agent-user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    type: str = Field(default="realtime")  # Agent type identifier
    
    # Realtime specific fields
    model: Optional[str] = Field(default=None)
    voice: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)
    greeting_prompt: Optional[str] = Field(default=None)
    
    def __init__(self, **data):
        if "id" not in data and "name" in data:
            # Generate composite ID from name and timestamp
            created_at = data.get("created_at", datetime.utcnow())
            # Replace spaces and special chars with underscores, convert to lowercase
            safe_name = data["name"].replace(" ", "_").lower()
            data["id"] = f"{safe_name}_{int(created_at.timestamp())}"
        super().__init__(**data)
