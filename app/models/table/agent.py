from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Agent(SQLModel, table=True):
    __tablename__ = "voice-agent-agent"
    
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    user_id: int = Field(foreign_key="voice-agent-user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    type: str = Field(default="realtime")
    api_key: str = Field()
    
    # Realtime configuration fields
    model: Optional[str] = Field(default="gpt-4o-realtime-preview-2024-10-01")
    voice: Optional[str] = Field(default="alloy")
    system_prompt: Optional[str] = Field(default="You are a helpful AI assistant.")
    greeting_prompt: Optional[str] = Field(default="Hello, how can I help you today?")
    
    def __init__(self, **data):
        if "id" not in data and "name" in data and "user_id" in data:
            # Generate composite ID from name, timestamp, and user_id
            created_at = data.get("created_at", datetime.utcnow())
            # Replace spaces and special chars with underscores, convert to lowercase
            safe_name = data["name"].replace(" ", "_").lower()
            user_id = data["user_id"]
            data["id"] = f"{safe_name}_{int(created_at.timestamp())}_{user_id}"
        super().__init__(**data)
