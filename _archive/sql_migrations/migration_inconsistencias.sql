-- Tabela para registro de inconsistências
CREATE TABLE IF NOT EXISTS public.inconsistencies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    
    -- Dados Básicos
    data_ocorrencia DATE NOT NULL,
    talao_numero TEXT,
    
    -- Tipo
    tipo TEXT NOT NULL, -- 'OPERACIONAL' ou 'TECNICA'
    
    -- Detalhes Operacionais
    motivo_op_codigo TEXT, -- Ex: 'SC1', 'SC5'
    motivo_op_descricao TEXT, -- Texto completo da opção selecionada
    
    -- Detalhes Técnicos
    motivo_tec_codigo TEXT, -- Ex: 'T1', 'T4_193'
    motivo_tec_descricao TEXT,
    
    -- Campos Específicos T4-193
    t4_origem TEXT, -- FIXO, MOVEL
    t4_operadora TEXT, -- VIVO, CLARO...
    t4_numero TEXT,
    t4_datahora TIMESTAMP,
    t4_falha TEXT, -- NAO_CHAMA, MUDO...
    
    -- Campos Específicos T4-APP
    t4_sistema_afetado TEXT, -- VULTO, RAIA...
    
    -- Observações
    observacao TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
