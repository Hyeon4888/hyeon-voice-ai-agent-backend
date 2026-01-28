"""
Database Migration Script for Supabase
This script syncs Supabase database tables with the SQLModel definitions in app/models/table/
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import SQLModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Import table models directly - these have minimal dependencies
from typing import Optional
from sqlmodel import Field
from datetime import datetime

# Define models inline to avoid import issues
class User(SQLModel, table=True):
    __tablename__ = "voice-agent-user"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    refresh_token: Optional[str] = Field(default=None)
    refresh_token_expires: Optional[datetime] = Field(default=None)

class RealtimeAgent(SQLModel, table=True):
    __tablename__ = "voice-agent-realtime-agent"
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    user_id: int = Field(foreign_key="voice-agent-user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    type: str = Field(default="realtime")
    model: Optional[str] = Field(default=None)
    voice: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)
    greeting_prompt: Optional[str] = Field(default=None)

class CustomAgent(SQLModel, table=True):
    __tablename__ = "voice-agent-custom-agent"
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    user_id: int = Field(foreign_key="voice-agent-user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    type: str = Field(default="custom")
    llm_websocket_url: Optional[str] = Field(default=None)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

print(f"🔄 Starting database migration...")
print(f"📊 Database: {DATABASE_URL.split('@')[1].split('/')[0]}")

async def drop_all_tables():
    """Drop all existing tables (use with caution!)"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Drop tables in reverse order of dependencies
        await conn.execute(text('DROP TABLE IF EXISTS "voice-agent-realtime-agent" CASCADE'))
        await conn.execute(text('DROP TABLE IF EXISTS "voice-agent-custom-agent" CASCADE'))
        await conn.execute(text('DROP TABLE IF EXISTS "voice-agent-user" CASCADE'))
    
    await engine.dispose()
    print("✅ All tables dropped successfully")

async def create_all_tables():
    """Create all tables based on SQLModel definitions"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Create tables using SQLModel metadata
        await conn.run_sync(SQLModel.metadata.create_all)
    
    await engine.dispose()
    print("✅ All tables created successfully")

async def migrate_fresh():
    """Drop all tables and recreate them (WARNING: This will delete all data!)"""
    print("⚠️  WARNING: This will delete ALL data in the database!")
    print("⚠️  Tables to be dropped and recreated:")
    print("   - voice-agent-user")
    print("   - voice-agent-realtime-agent")
    print("   - voice-agent-custom-agent")
    
    confirm = input("\n❓ Are you sure you want to proceed? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Migration cancelled")
        return
    
    print("\n🗑️  Dropping tables...")
    await drop_all_tables()
    
    print("\n🔨 Creating tables...")
    await create_all_tables()
    
    print("\n✅ Migration completed successfully!")

async def migrate_safe():
    """Create tables if they don't exist (safe migration)"""
    print("🔒 Safe migration mode - only creating missing tables")
    await create_all_tables()
    print("\n✅ Safe migration completed!")

async def show_schema():
    """Display the current database schema"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Get all tables
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'voice-agent-%'
            ORDER BY table_name
        """))
        
        tables = result.fetchall()
        
        if not tables:
            print("📋 No voice-agent tables found in database")
        else:
            print(f"\n📋 Found {len(tables)} tables:")
            
            for (table_name,) in tables:
                print(f"\n🔹 Table: {table_name}")
                
                # Get columns
                columns_result = await conn.execute(text(f"""
                    SELECT 
                        column_name, 
                        data_type, 
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """))
                
                columns = columns_result.fetchall()
                
                for col_name, data_type, is_nullable, default in columns:
                    nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                    default_str = f" DEFAULT {default}" if default else ""
                    print(f"   - {col_name}: {data_type} {nullable}{default_str}")
    
    await engine.dispose()

def print_help():
    """Print usage instructions"""
    print("""
📚 Database Migration Script Usage:

Commands:
  python scripts/migrate_db.py fresh   - Drop all tables and recreate (⚠️  DELETES DATA!)
  python scripts/migrate_db.py safe    - Create tables if they don't exist (safe)
  python scripts/migrate_db.py schema  - Show current database schema
  python scripts/migrate_db.py help    - Show this help message

Examples:
  # View current schema
  python scripts/migrate_db.py schema
  
  # Safe migration (recommended for updates)
  python scripts/migrate_db.py safe
  
  # Fresh migration (use only for development/testing)
  python scripts/migrate_db.py fresh

Tables managed by this script:
  - voice-agent-user
  - voice-agent-realtime-agent
  - voice-agent-custom-agent
    """)

async def main():
    if len(sys.argv) < 2:
        print("❌ Error: Missing command argument")
        print_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "fresh":
        await migrate_fresh()
    elif command == "safe":
        await migrate_safe()
    elif command == "schema":
        await show_schema()
    elif command == "help":
        print_help()
    else:
        print(f"❌ Error: Unknown command '{command}'")
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
