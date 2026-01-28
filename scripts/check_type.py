import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    engine = create_async_engine(os.getenv('DATABASE_URL'), echo=False)
    async with engine.begin() as conn:
        r1 = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='voice-agent-realtime-agent' AND column_name='type'"
        ))
        r2 = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='voice-agent-custom-agent' AND column_name='type'"
        ))
        print('Type column in realtime-agent:', 'EXISTS ✅' if r1.fetchone() else 'MISSING ❌')
        print('Type column in custom-agent:', 'EXISTS ✅' if r2.fetchone() else 'MISSING ❌')
    await engine.dispose()

asyncio.run(main())
