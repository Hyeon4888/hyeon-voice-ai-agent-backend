"""
Migration script to update database schema for composite agent IDs and refresh tokens.
This script will:
1. Drop and recreate agent tables with new ID structure
2. Add refresh token fields to user table
"""

import asyncio
from sqlalchemy import text
from app.config.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

async def migrate():
    engine = create_async_engine(settings.DATABASE_URL, future=True)
    
    async with engine.begin() as conn:
        print("Starting migration...")
        
        # Drop existing agent tables
        print("Dropping existing agent tables...")
        await conn.execute(text('DROP TABLE IF EXISTS "voice-agent-realtime-agent" CASCADE;'))
        await conn.execute(text('DROP TABLE IF EXISTS "voice-agent-custom-agent" CASCADE;'))
        
        # Add refresh token columns to user table
        print("Adding refresh token fields to user table...")
        try:
            await conn.execute(text("""
                ALTER TABLE "voice-agent-user" 
                ADD COLUMN IF NOT EXISTS "refresh_token" VARCHAR,
                ADD COLUMN IF NOT EXISTS "refresh_token_expires" TIMESTAMP WITHOUT TIME ZONE;
            """))
        except Exception as e:
            print(f"Note: {e} (columns may already exist)")
        
        # Recreate agent tables with new schema
        print("Creating new agent tables with composite IDs...")
        await conn.execute(text("""
            CREATE TABLE "voice-agent-realtime-agent" (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                user_id INTEGER NOT NULL REFERENCES "voice-agent-user"(id),
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                model VARCHAR,
                voice VARCHAR,
                system_prompt VARCHAR,
                greeting_prompt VARCHAR
            );
        """))
        
        await conn.execute(text("""
            CREATE TABLE "voice-agent-custom-agent" (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                user_id INTEGER NOT NULL REFERENCES "voice-agent-user"(id),
                created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                llm_websocket_url VARCHAR
            );
        """))
        
        # Create indices
        print("Creating indices...")
        await conn.execute(text('CREATE INDEX ix_voice_agent_realtime_agent_name ON "voice-agent-realtime-agent" (name);'))
        await conn.execute(text('CREATE INDEX ix_voice_agent_custom_agent_name ON "voice-agent-custom-agent" (name);'))
        
        print("Migration completed successfully!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
