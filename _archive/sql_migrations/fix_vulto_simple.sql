-- Script simplificado para correção da tabela Vulto
-- Rode estas linhas uma por uma ou o bloco todo se o editor permitir

-- 1. Remove a restrição de chave estrangeira (se existir)
DO $$ 
BEGIN 
  IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'vulto_occurrences_municipio_id_fkey') THEN 
    ALTER TABLE public.vulto_occurrences DROP CONSTRAINT vulto_occurrences_municipio_id_fkey; 
  END IF; 
END $$;

-- 2. Remove a coluna antiga (ID)
ALTER TABLE public.vulto_occurrences DROP COLUMN IF EXISTS municipio_id;

-- 3. Adiciona a nova coluna de texto
ALTER TABLE public.vulto_occurrences ADD COLUMN IF NOT EXISTS municipio_nome TEXT;
