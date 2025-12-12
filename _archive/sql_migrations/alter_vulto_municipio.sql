-- Alterar tabela vulto_occurrences para armazenar nome do município (TEXT) em vez de ID (UUID)
-- Isso alinha com a decisão de "hardcodar" a lista de municípios no frontend
-- e remove a dependência de uma tabela externa para este módulo específico.

DO $$
BEGIN
    -- 1. Se existir a coluna municipio_id como UUID, vamos alterá-la.
    --    Primeiro removemos a FK se existir.
    IF EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_name = 'vulto_occurrences_municipio_id_fkey' 
        AND table_name = 'vulto_occurrences'
    ) THEN
        ALTER TABLE public.vulto_occurrences DROP CONSTRAINT vulto_occurrences_municipio_id_fkey;
    END IF;

    -- 2. Alterar o nome da coluna e o tipo
    --    Se a coluna se chama municipio_id e é UUID, vamos mudar.
    --    Se já tiver dados, convertemos para texto (vai ficar o UUID em texto, o que não é ideal se quisermos o nome, 
    --    mas como a tabela é nova, assumimos que está vazia ou o reset é aceitável.
    --    Na verdade, melhor dropar e recriar a coluna como texto 'municipio_nome' para evitar confusão.
    
    ALTER TABLE public.vulto_occurrences DROP COLUMN IF EXISTS municipio_id;
    ALTER TABLE public.vulto_occurrences ADD COLUMN IF NOT EXISTS municipio_nome TEXT;

END $$;
