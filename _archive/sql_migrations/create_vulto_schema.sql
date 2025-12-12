-- Tabela para Ocorrências de Vulto
CREATE TABLE IF NOT EXISTS public.vulto_occurrences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    opm_id BIGINT REFERENCES public.opm(id), -- Unidade de Atendimento (GB/SGB/EB via tabela unificada)
    
    -- Dados Básicos
    talao_numero TEXT,
    data_inicio DATE,
    hora_inicio TIME,
    status TEXT DEFAULT 'EM ATENDIMENTO', -- EM ATENDIMENTO, ENCERRADA
    data_termino DATE,
    hora_termino TIME,
    
    -- Classificação
    justificativa_vulto TEXT, -- "5 VÍTIMAS...", "INCÊNDIO FATAL..."
    natureza_codigo TEXT, -- Ex: "N01 - INCÊNDIO"
    
    -- Localização
    municipio_id UUID REFERENCES public.municipalities(id),
    endereco TEXT,
    bairro TEXT,
    
    -- Recursos
    qtd_viaturas INTEGER,
    qtd_bombeiros INTEGER,
    
    -- Pessoal
    encarregado_posto TEXT,
    encarregado_nome TEXT,
    
    -- Histórico
    historico_inicial TEXT,
    historico_final TEXT,
    
    -- Transmissão
    pm_transmissao_posto TEXT,
    pm_transmissao_nome TEXT,
    
    -- Extra
    tempo_resposta_minutos INTEGER,
    oficiais_presenca TEXT, -- JSON ou Texto livre com lista de oficiais
    
    -- Sistema
    generated_text TEXT, -- Texto final gerado pela IA/Sistema
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Políticas de Segurança (RLS)
ALTER TABLE public.vulto_occurrences ENABLE ROW LEVEL SECURITY;

-- Usuários veem suas próprias (ou Admin vê tudo - criar policy depois)
CREATE POLICY "Users can view own vulto" ON public.vulto_occurrences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own vulto" ON public.vulto_occurrences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Admins
CREATE POLICY "Admins can view all vulto" ON public.vulto_occurrences
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'ADMIN'
        )
    );
