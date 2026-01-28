import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    engine = create_async_engine(os.getenv('DATABASE_URL'), echo=False)
    async with engine.begin() as conn:
        # Check realtime agent id type
        result = await conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'voice-agent-realtime-agent'
            AND column_name = 'id'
        """))
        row = result.fetchone()
        print(f"voice-agent-realtime-agent.id: {row[1] if row else 'NOT FOUND'}")
        
        # Check custom agent id type
        result = await conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'voice-agent-custom-agent'
            AND column_name = 'id'
        """))
        row = result.fetchone()
        print(f"voice-agent-custom-agent.id: {row[1] if row else 'NOT FOUND'}")
    await engine.dispose()

asyncio.run(main())
