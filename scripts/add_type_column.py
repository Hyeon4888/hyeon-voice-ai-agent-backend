"""
Add type column to existing agent tables
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

async def add_type_column():
    """Add type column to agent tables"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        print("\n🔧 Adding type column to voice-agent-realtime-agent...")
        await conn.execute(text("""
            ALTER TABLE "voice-agent-realtime-agent"
            ADD COLUMN IF NOT EXISTS type VARCHAR NOT NULL DEFAULT 'realtime'
        """))
        
        print("\n🔧 Adding type column to voice-agent-custom-agent...")
        await conn.execute(text("""
            ALTER TABLE "voice-agent-custom-agent"
            ADD COLUMN IF NOT EXISTS type VARCHAR NOT NULL DEFAULT 'custom'
        """))
        
        print("\n✅ Type columns added successfully!")
        
        # Verify
        print("\n📊 Verifying changes...")
        result = await conn.execute(text("""
            SELECT 
                table_name,
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name IN ('voice-agent-realtime-agent', 'voice-agent-custom-agent')
            AND column_name = 'type'
            ORDER BY table_name
        """))
        
        rows = result.fetchall()
        for table_name, column_name, data_type, is_nullable, default_value in rows:
            print(f"✓ {table_name}.{column_name}: {data_type} (default: {default_value})")
    
    await engine.dispose()

if __name__ == "__main__":
    print("🔄 Adding type column to agent tables...")
    asyncio.run(add_type_column())
    print("\n✅ Migration completed!")
