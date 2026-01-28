"""
Fix agent table ID column types - drop and recreate with VARCHAR
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def fix_tables():
    engine = create_async_engine(os.getenv('DATABASE_URL'), echo=True)
    
    async with engine.begin() as conn:
        print("\n🗑️ Dropping existing agent tables...")
        
        # Drop tables (CASCADE to handle foreign keys)
        await conn.execute(text('DROP TABLE IF EXISTS "voice-agent-realtime-agent" CASCADE'))
        await conn.execute(text('DROP TABLE IF EXISTS "voice-agent-custom-agent" CASCADE'))
        
        print("\n✅ Tables dropped")
        print("\n🔨 Creating tables with correct schema...")
        
        # Create realtime agent table with VARCHAR id
        await conn.execute(text("""
            CREATE TABLE "voice-agent-realtime-agent" (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                user_id INTEGER NOT NULL REFERENCES "voice-agent-user"(id) ON DELETE CASCADE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                type VARCHAR NOT NULL DEFAULT 'realtime',
                model VARCHAR,
                voice VARCHAR,
                system_prompt TEXT,
                greeting_prompt TEXT
            )
        """))
        
        # Create custom agent table with VARCHAR id
        await conn.execute(text("""
            CREATE TABLE "voice-agent-custom-agent" (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                user_id INTEGER NOT NULL REFERENCES "voice-agent-user"(id) ON DELETE CASCADE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                type VARCHAR NOT NULL DEFAULT 'custom',
                llm_websocket_url VARCHAR
            )
        """))
        
        # Create indexes
        await conn.execute(text('CREATE INDEX idx_realtime_agent_name ON "voice-agent-realtime-agent"(name)'))
        await conn.execute(text('CREATE INDEX idx_realtime_agent_user_id ON "voice-agent-realtime-agent"(user_id)'))
        await conn.execute(text('CREATE INDEX idx_custom_agent_name ON "voice-agent-custom-agent"(name)'))
        await conn.execute(text('CREATE INDEX idx_custom_agent_user_id ON "voice-agent-custom-agent"(user_id)'))
        
        print("\n✅ Tables created successfully!")
        
        # Verify
        print("\n📊 Verifying schema...")
        result = await conn.execute(text("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name IN ('voice-agent-realtime-agent', 'voice-agent-custom-agent')
            AND column_name = 'id'
            ORDER BY table_name
        """))
        
        for table_name, column_name, data_type in result.fetchall():
            print(f"✓ {table_name}.{column_name}: {data_type}")
    
    await engine.dispose()

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete all agents!")
    print("⚠️  This script will drop and recreate agent tables with VARCHAR id type.")
    confirm = input("\n❓ Are you sure you want to proceed? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled")
    else:
        asyncio.run(fix_tables())
        print("\n✅ Migration completed! Agent tables now have VARCHAR id columns.")
