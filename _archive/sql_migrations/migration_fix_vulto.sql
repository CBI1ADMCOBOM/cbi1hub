-- Arquivo para correção da tabela Vulto que não existe
-- Salve este conteúdo no Editor SQL do Supabase e execute.

CREATE TABLE IF NOT EXISTS public.vulto_occurrences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    -- Ajuste para a nova tabela 'opm' em vez de 'opm_cb' se tiver sido renomeada
    opm_id BIGINT REFERENCES public.opm(id), 
    
    -- Dados Básicos
    talao_numero TEXT,
    data_inicio DATE,
    hora_inicio TIME,
    status TEXT, -- EM ATENDIMENTO, ENCERRADA
    data_termino DATE,
    hora_termino TIME,
    
    -- Classificação
    justificativa_vulto TEXT,
    natureza_codigo TEXT,
    
    -- Localização
    municipio_nome TEXT,
    endereco TEXT,
    bairro TEXT,
    -- campo referencia removido intencionalmente
    
    -- Recursos
    qtd_viaturas INTEGER,
    qtd_bombeiros INTEGER,
    tempo_resposta_minutos INTEGER,
    
    -- Pessoal
    encarregado_posto TEXT,
    encarregado_nome TEXT,
    oficiais_presenca TEXT,
    
    -- Histórico
    historico_inicial TEXT,
    historico_final TEXT,
    
    -- Transmissão
    pm_transmissao_posto TEXT,
    pm_transmissao_nome TEXT,
    
    -- Meta
    generated_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar RLS (Segurança)
ALTER TABLE public.vulto_occurrences ENABLE ROW LEVEL SECURITY;

-- Permitir leitura para todos autenticados (ou ajustar conforme necessidade)
CREATE POLICY "Enable read/write for authenticated users only" ON public.vulto_occurrences
AS PERMISSIVE FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);
