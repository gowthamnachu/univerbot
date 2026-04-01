-- Migration: Update vector dimensions from 1024 to 384 for Sentence Transformers (all-MiniLM-L6-v2)
-- Run this in your Supabase SQL Editor

-- Step 1: Drop the existing vector index (required before altering column type)
DROP INDEX IF EXISTS idx_document_chunks_embedding;

-- Step 2: Drop the match_documents function (it references old VECTOR dimensions)
DROP FUNCTION IF EXISTS match_documents(vector, integer, uuid);

-- Step 3: Clear all existing embeddings (they are incompatible with new dimensions)
UPDATE public.document_chunks SET embedding = NULL;

-- Step 4: Alter the embedding column to use 384 dimensions
ALTER TABLE public.document_chunks 
ALTER COLUMN embedding TYPE VECTOR(384);

-- Step 5: Recreate the vector similarity search index for 384 dimensions
CREATE INDEX idx_document_chunks_embedding ON public.document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Step 6: Recreate the match_documents function with 384 dimensions
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
        document_chunks.id,
        document_chunks.content,
        1 - (document_chunks.embedding <=> query_embedding) AS similarity
    FROM document_chunks
    WHERE document_chunks.bot_id = filter_bot_id
    AND document_chunks.embedding IS NOT NULL
    ORDER BY document_chunks.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Verify the changes
SELECT 
    column_name, 
    udt_name, 
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'document_chunks' 
AND column_name = 'embedding';
