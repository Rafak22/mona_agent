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