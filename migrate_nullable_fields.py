"""
Migration script to make agent fields nullable.
This script updates the database schema to allow NULL values for configuration fields.
"""

import asyncio
from sqlalchemy import text
from app.config.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

async def migrate():
    engine = create_async_engine(settings.DATABASE_URL, future=True)
    
    async with engine.begin() as conn:
        print("Starting migration...")
        
        # Make RealtimeAgent fields nullable
        print("Updating voice-agent-realtime-agent table...")
        await conn.execute(text("""
            ALTER TABLE "voice-agent-realtime-agent" 
            ALTER COLUMN "model" DROP NOT NULL,
            ALTER COLUMN "voice" DROP NOT NULL;
        """))
        
        # Make CustomAgent fields nullable
        print("Updating voice-agent-custom-agent table...")
        await conn.execute(text("""
            ALTER TABLE "voice-agent-custom-agent" 
            ALTER COLUMN "llm_websocket_url" DROP NOT NULL;
        """))
        
        print("Migration completed successfully!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
