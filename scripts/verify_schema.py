"""
Quick verification - check if type column exists
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys_path_parent = str(Path(__file__).parent.parent)

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL")

async def verify():
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Check realtime agent table
        result = await conn.execute(text("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'voice-agent-realtime-agent'
            ORDER BY ordinal_position
        """))
        
        print("\n🔹 voice-agent-realtime-agent columns:")
        for col_name, data_type, default_val in result.fetchall():
            print(f"  - {col_name}: {data_type}" + (f" (default: {default_val})" if default_val else ""))
        
        # Check custom agent table
        result = await conn.execute(text("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'voice-agent-custom-agent'
            ORDER BY ordinal_position
        """))
        
        print("\n🔹 voice-agent-custom-agent columns:")
        for col_name, data_type, default_val in result.fetchall():
            print(f"  - {col_name}: {data_type}" + (f" (default: {default_val})" if default_val else ""))
    
    await engine.dispose()

asyncio.run(verify())
