-- Add type column to existing agent tables

-- Add type column to realtime agent table
ALTER TABLE "voice-agent-realtime-agent"
    ADD COLUMN IF NOT EXISTS type VARCHAR NOT NULL DEFAULT 'realtime';

-- Add type column to custom agent table
ALTER TABLE "voice-agent-custom-agent"
    ADD COLUMN IF NOT EXISTS type VARCHAR NOT NULL DEFAULT 'custom';

-- Verify the changes
SELECT 
    table_name,
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name IN ('voice-agent-realtime-agent', 'voice-agent-custom-agent')
AND column_name = 'type'
ORDER BY table_name;
