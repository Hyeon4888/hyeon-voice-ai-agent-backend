from sqlmodel import SQLModel, Field

class ApiKey(SQLModel, table=True):
    __tablename__ = "api-key"
    
    id: str = Field(primary_key=True)
    name: str
    model: str
    user_id: int = Field(foreign_key="voice-agent-user.id")
