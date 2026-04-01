-- UniverBot Database Schema
-- Run this in your Supabase SQL Editor

-- Enable pgvector extension for vector embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Profiles table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bots table
CREATE TABLE IF NOT EXISTS public.bots (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    system_prompt TEXT DEFAULT 'You are a helpful assistant.',
    api_key TEXT NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT true,
    flow_data JSONB,
    appearance JSONB DEFAULT '{
        "primary_color": "#00E5FF",
        "secondary_color": "#00B8CC",
        "header_color": "#0a0f1a",
        "background_color": "#030617",
        "user_bubble_color": "#00E5FF",
        "bot_bubble_color": "#0a0f1a",
        "user_text_color": "#030617",
        "bot_text_color": "#ffffff",
        "avatar_type": "default",
        "avatar_url": null,
        "avatar_initials": null,
        "chat_title": "Chat Assistant",
        "chat_subtitle": null,
        "welcome_message": "Hello! How can I help you today?",
        "placeholder_text": "Type your message...",
        "loading_style": "skeleton",
        "button_style": "round",
        "position": "bottom-right"
    }'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Migration: Add appearance column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'bots' AND column_name = 'appearance') THEN
        ALTER TABLE public.bots ADD COLUMN appearance JSONB DEFAULT '{
            "primary_color": "#00E5FF",
            "secondary_color": "#00B8CC",
            "header_color": "#0a0f1a",
            "background_color": "#030617",
            "user_bubble_color": "#00E5FF",
            "bot_bubble_color": "#0a0f1a",
            "user_text_color": "#030617",
            "bot_text_color": "#ffffff",
            "avatar_type": "default",
            "avatar_url": null,
            "avatar_initials": null,
            "chat_title": "Chat Assistant",
            "chat_subtitle": null,
            "welcome_message": "Hello! How can I help you today?",
            "placeholder_text": "Type your message...",
            "loading_style": "skeleton",
            "button_style": "round",
            "position": "bottom-right"
        }'::jsonb;
    END IF;
END $$;

-- Documents table
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    bot_id UUID REFERENCES public.bots(id) ON DELETE CASCADE NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document chunks with vector embeddings
CREATE TABLE IF NOT EXISTS public.document_chunks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    bot_id UUID REFERENCES public.bots(id) ON DELETE CASCADE NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384), -- all-MiniLM-L6-v2 dimension
    chunk_index INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    bot_id UUID REFERENCES public.bots(id) ON DELETE CASCADE NOT NULL,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat sessions table (for flow state management)
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT NOT NULL,
    bot_id UUID REFERENCES public.bots(id) ON DELETE CASCADE NOT NULL,
    state JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(session_id, bot_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_bots_user_id ON public.bots(user_id);
CREATE INDEX IF NOT EXISTS idx_bots_api_key ON public.bots(api_key);
CREATE INDEX IF NOT EXISTS idx_documents_bot_id ON public.documents(bot_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_bot_id ON public.document_chunks(bot_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON public.document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_bot_id ON public.chat_messages(bot_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_bot ON public.chat_sessions(session_id, bot_id);

-- Vector similarity search index (IVFFlat for faster queries)
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON public.document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Function to match documents using vector similarity
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(384),
    match_count INT,
    filter_bot_id UUID
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.content,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM public.document_chunks dc
    WHERE dc.bot_id = filter_bot_id
        AND dc.embedding IS NOT NULL
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Row Level Security (RLS) Policies

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Bots policies
CREATE POLICY "Users can view their own bots"
    ON public.bots FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own bots"
    ON public.bots FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own bots"
    ON public.bots FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own bots"
    ON public.bots FOR DELETE
    USING (auth.uid() = user_id);

-- Documents policies
CREATE POLICY "Users can view documents of their bots"
    ON public.documents FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.bots
            WHERE bots.id = documents.bot_id
            AND bots.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create documents for their bots"
    ON public.documents FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.bots
            WHERE bots.id = documents.bot_id
            AND bots.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete documents of their bots"
    ON public.documents FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.bots
            WHERE bots.id = documents.bot_id
            AND bots.user_id = auth.uid()
        )
    );

-- Document chunks policies
CREATE POLICY "Users can view chunks of their bots"
    ON public.document_chunks FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.bots
            WHERE bots.id = document_chunks.bot_id
            AND bots.user_id = auth.uid()
        )
    );

-- Chat messages policies (allow API access)
CREATE POLICY "Allow all chat messages operations"
    ON public.chat_messages FOR ALL
    USING (true)
    WITH CHECK (true);

-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create profile
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add update triggers
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bots_updated_at
    BEFORE UPDATE ON public.bots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
