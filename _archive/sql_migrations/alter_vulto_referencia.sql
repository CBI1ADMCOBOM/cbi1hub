-- Adicionar coluna 'referencia' na tabela vulto_occurrences
ALTER TABLE public.vulto_occurrences ADD COLUMN IF NOT EXISTS referencia TEXT;
