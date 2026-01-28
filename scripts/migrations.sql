-- ============================================
-- Database Migration Script for Supabase
-- Generated based on SQLModel definitions
-- ============================================

-- This script creates all tables from scratch
-- For updates to existing tables, modify the ALTER TABLE sections below

-- ============================================
-- DROP EXISTING TABLES (if recreating)
-- ============================================
-- Uncomment the following lines if you want to drop and recreate tables
-- WARNING: This will delete all data!

-- DROP TABLE IF EXISTS "voice-agent-realtime-agent" CASCADE;
-- DROP TABLE IF EXISTS "voice-agent-custom-agent" CASCADE;
-- DROP TABLE IF EXISTS "voice-agent-user" CASCADE;

-- ============================================
-- CREATE TABLES
-- ============================================

-- User Table
CREATE TABLE IF NOT EXISTS "voice-agent-user" (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    refresh_token VARCHAR,
    refresh_token_expires TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_email ON "voice-agent-user"(email);

-- Realtime Agent Table
CREATE TABLE IF NOT EXISTS "voice-agent-realtime-agent" (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    user_id INTEGER NOT NULL REFERENCES "voice-agent-user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model VARCHAR,
    voice VARCHAR,
    system_prompt TEXT,
    greeting_prompt TEXT
);

-- Create index on name and user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_realtime_agent_name ON "voice-agent-realtime-agent"(name);
CREATE INDEX IF NOT EXISTS idx_realtime_agent_user_id ON "voice-agent-realtime-agent"(user_id);

-- Custom Agent Table
CREATE TABLE IF NOT EXISTS "voice-agent-custom-agent" (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    user_id INTEGER NOT NULL REFERENCES "voice-agent-user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    llm_websocket_url VARCHAR
);

-- Create index on name and user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_custom_agent_name ON "voice-agent-custom-agent"(name);
CREATE INDEX IF NOT EXISTS idx_custom_agent_user_id ON "voice-agent-custom-agent"(user_id);

-- ============================================
-- ALTER EXISTING TABLES (for updates)
-- ============================================
-- Use these if you're updating existing tables instead of creating from scratch

-- Example: Add a new column to user table
-- ALTER TABLE "voice-agent-user" 
--     ADD COLUMN IF NOT EXISTS refresh_token VARCHAR,
--     ADD COLUMN IF NOT EXISTS refresh_token_expires TIMESTAMP;

-- Example: Add new columns to realtime agent table
-- ALTER TABLE "voice-agent-realtime-agent"
--     ADD COLUMN IF NOT EXISTS model VARCHAR,
--     ADD COLUMN IF NOT EXISTS voice VARCHAR,
--     ADD COLUMN IF NOT EXISTS system_prompt TEXT,
--     ADD COLUMN IF NOT EXISTS greeting_prompt TEXT;

-- Example: Modify column type
-- ALTER TABLE "voice-agent-realtime-agent" 
--     ALTER COLUMN system_prompt TYPE TEXT;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================
-- Run these to verify the migration

-- Show all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'voice-agent-%'
ORDER BY table_name;

-- Show columns for each table
SELECT 
    table_name,
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name LIKE 'voice-agent-%'
ORDER BY table_name, ordinal_position;

-- Show foreign key constraints
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND tc.table_name LIKE 'voice-agent-%';
