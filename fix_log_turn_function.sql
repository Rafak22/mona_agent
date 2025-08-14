-- Fix for the log_turn RPC function in Supabase
-- This fixes the "column reference 'conversation_id' is ambiguous" error
-- AND the "primary_goals type mismatch" error

-- Drop the existing function if it exists
DROP FUNCTION IF EXISTS log_turn(
    p_user_id UUID,
    p_conversation_id UUID,
    p_profile JSONB,
    p_state_patch JSONB,
    p_current_step TEXT,
    p_role TEXT,
    p_content JSONB,
    p_meta JSONB
);

-- Create the fixed function
CREATE OR REPLACE FUNCTION log_turn(
    p_user_id UUID,
    p_conversation_id UUID,
    p_profile JSONB,
    p_state_patch JSONB,
    p_current_step TEXT,
    p_role TEXT,
    p_content JSONB,
    p_meta JSONB
) RETURNS VOID AS $$
BEGIN
    -- Insert into conversation_turns table with explicit column references
    INSERT INTO conversation_turns (
        conversation_id,
        step,
        role,
        content,
        meta,
        created_at
    ) VALUES (
        p_conversation_id,
        p_current_step,
        p_role,
        p_content,
        p_meta,
        NOW()
    );
    
    -- Update the conversation with current step
    UPDATE conversations 
    SET 
        current_step = p_current_step,
        state = state || p_state_patch,
        updated_at = NOW()
    WHERE id = p_conversation_id;
    
    -- Upsert profile data with proper type casting for primary_goals
    INSERT INTO profiles (
        user_id,
        user_role,
        industry,
        company_size,
        website_status,
        website_url,
        primary_goals,
        budget_range
    ) VALUES (
        p_user_id,
        p_profile->>'user_role',
        p_profile->>'industry',
        p_profile->>'company_size',
        p_profile->>'website_status',
        p_profile->>'website_url',
        CASE 
            WHEN p_profile->'primary_goals' IS NULL THEN '{}'::text[]
            WHEN jsonb_typeof(p_profile->'primary_goals') = 'array' THEN 
                ARRAY(SELECT jsonb_array_elements_text(p_profile->'primary_goals'))
            ELSE '{}'::text[]
        END,
        p_profile->>'budget_range'
    )
    ON CONFLICT (user_id) DO UPDATE SET
        user_role = EXCLUDED.user_role,
        industry = EXCLUDED.industry,
        company_size = EXCLUDED.company_size,
        website_status = EXCLUDED.website_status,
        website_url = EXCLUDED.website_url,
        primary_goals = EXCLUDED.primary_goals,
        budget_range = EXCLUDED.budget_range,
        updated_at = NOW();
        
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION log_turn(
    UUID, UUID, JSONB, JSONB, TEXT, TEXT, JSONB, JSONB
) TO authenticated;
