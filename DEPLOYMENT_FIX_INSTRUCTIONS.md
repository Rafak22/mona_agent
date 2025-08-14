# 🚨 IMPORTANT: Fix Deployment Issues

## Step 1: Fix Supabase Database (CRITICAL)

You need to run this SQL in your Supabase dashboard to fix the database errors:

1. **Go to your Supabase Dashboard**
2. **Click on "SQL Editor"**
3. **Copy and paste this SQL:**

```sql
-- Fix for the log_turn RPC function in Supabase
-- This fixes the "column reference 'conversation_id' is ambiguous" error

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
    
    -- Upsert profile data
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
        COALESCE(p_profile->'primary_goals', '[]'::jsonb),
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
```

4. **Click "Run" to execute the SQL**

## Step 2: Wait for Render Deployment

After running the SQL:
1. **Wait 2-3 minutes** for Render to fully deploy the changes
2. **Clear your browser cache** (Ctrl+F5 or Cmd+Shift+R)
3. **Try accessing your app again**

## Step 3: Test the Correct URL

Make sure you're accessing the correct URL:
- **Your Render URL**: `https://mona-agent.onrender.com`
- **Frontend entry point**: `https://mona-agent.onrender.com/frontend/start.html`

## Step 4: Verify It's Working

After completing the above steps, the onboarding should work properly:
1. You should see the new onboarding interface with 4 progress dots
2. The database errors should be gone
3. User data should be saved to the database

## If Still Not Working

If you still see issues after following these steps:
1. Check the browser console for errors (F12 → Console)
2. Check the Render logs for any deployment errors
3. Run the test script: `python test_deployment.py`
