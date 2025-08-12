# Messages Table Setup for Conversation History

This document explains how to set up the `messages` table in Supabase to enable conversation history for the MORVO chatbot.

## Table Structure

The `messages` table stores conversation history between users and the MORVO assistant with the following columns:

- `id` (uuid): Primary key, auto-generated
- `user_id` (text): The user identifier
- `role` (text): Either "user" or "assistant"
- `content` (text): The message content
- `created_at` (timestamp): When the message was created (auto-generated)

## Setup Instructions

### 1. Create the Table

Run the following SQL in your Supabase SQL Editor:

```sql
-- Create messages table for storing conversation history
CREATE TABLE IF NOT EXISTS public.messages (
    id uuid NOT NULL DEFAULT extensions.uuid_generate_v4(),
    user_id text NOT NULL,
    role text NOT NULL CHECK (role IN ('user', 'assistant')),
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT messages_pkey PRIMARY KEY (id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON public.messages USING btree (user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON public.messages USING btree (created_at);
CREATE INDEX IF NOT EXISTS idx_messages_role ON public.messages USING btree (role);

-- Add comments for documentation
COMMENT ON TABLE public.messages IS 'Stores conversation history between users and the MORVO assistant';
COMMENT ON COLUMN public.messages.user_id IS 'The user identifier';
COMMENT ON COLUMN public.messages.role IS 'Role of the message sender: user or assistant';
COMMENT ON COLUMN public.messages.content IS 'The message content';
COMMENT ON COLUMN public.messages.created_at IS 'Timestamp when the message was created';
```

### 2. Verify Environment Variables

Ensure these environment variables are set in Railway:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key

### 3. How It Works

1. **Message Storage**: Every user message and assistant reply is automatically saved to the `messages` table
2. **History Retrieval**: Before processing a new message, the system retrieves all previous messages for that user
3. **Context Enhancement**: The conversation history is passed to OpenAI to provide context for better responses
4. **Automatic Cleanup**: When a user types "start over", their conversation history is automatically cleared

### 4. Performance Considerations

- The table includes indexes on `user_id` and `created_at` for efficient queries
- Messages are ordered by creation time to maintain conversation flow
- The system gracefully handles cases where Supabase is not configured

### 5. Testing

After setup, test the conversation history by:

1. Sending a message to the `/chat` endpoint
2. Checking the `messages` table in Supabase
3. Sending another message and verifying the assistant uses context from the first message

## Troubleshooting

- **Table not found**: Ensure the SQL script was executed successfully
- **Permission denied**: Check that your Supabase key has the necessary permissions
- **No history**: Verify that `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set correctly 