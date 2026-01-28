from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class CustomAgent(SQLModel, table=True):
    __tablename__ = "voice-agent-custom-agent"
    
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    user_id: int = Field(foreign_key="voice-agent-user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Custom specific fields
    llm_websocket_url: Optional[str] = Field(default=None)
    
    def __init__(self, **data):
        if "id" not in data and "name" in data:
            # Generate composite ID from name and timestamp
            created_at = data.get("created_at", datetime.utcnow())
            # Replace spaces and special chars with underscores, convert to lowercase
            safe_name = data["name"].replace(" ", "_").lower()
            data["id"] = f"{safe_name}_{int(created_at.timestamp())}"
        super().__init__(**data)
