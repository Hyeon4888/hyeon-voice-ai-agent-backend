import asyncio
from sqlalchemy import text
from app.models import engine
from app.models.table.agent import Agent
from sqlmodel import SQLModel

async def recreate_tables():
    async with engine.begin() as conn:
        print("Dropping old tables...")
        await conn.execute(text("DROP TABLE IF EXISTS \"voice-agent-realtime-agent\" CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS \"voice-agent-custom-agent\" CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS \"voice-agent-agent\" CASCADE"))
        
        print("Creating new tables...")
        # Create all tables defined in SQLModel metadata
        # We only want to create the new agent table, but create_all is safe if other tables exist
        await conn.run_sync(SQLModel.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(recreate_tables())
