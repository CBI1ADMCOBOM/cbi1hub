-- Adiciona coluna de status na tabela de inconsistências
ALTER TABLE public.inconsistencies
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'NOVO';

-- Atualiza registros existentes para terem status 'NOVO'
UPDATE public.inconsistencies SET status = 'NOVO' WHERE status IS NULL;
