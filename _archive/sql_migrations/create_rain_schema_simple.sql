-- Criação da tabela de ocorrências de CHUVAS INTENSAS (Versão Simplificada sem FKs estritas para evitar erros)
DROP TABLE IF EXISTS public.rain_occurrences;

CREATE TABLE public.rain_occurrences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- FK lógica para auth.users(id)
    
    -- Dados Básicos
    talao_numero TEXT,
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    endereco TEXT,
    latitude TEXT,
    longitude TEXT,
    municipio_id BIGINT, -- FK lógica para municipalities(id)
    
    -- Tipo de Atendimento
    tipo_atendimento TEXT, 
    
    -- Se Bombeiros
    bombeiros_station_id BIGINT, -- FK lógica para opm(id) (Verificar se é INT ou BIGINT no banco original)
    bombeiros_prontidao TEXT, 
    bombeiros_viatura TEXT,
    bombeiros_encarregado TEXT,
    
    -- Se Outros
    outros_orgao TEXT, 
    outros_detalhes TEXT,
    
    -- Classificação
    natureza_codigo TEXT, 
    area_tipo TEXT, 
    prioridade TEXT,
    
    -- Andamento
    limpeza_via TEXT, 
    status TEXT DEFAULT 'ESPERA', 
    resultado TEXT, 
    
    observacao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Habilitar RLS
ALTER TABLE public.rain_occurrences ENABLE ROW LEVEL SECURITY;

-- Criar Policies
CREATE POLICY "Users can select own" ON public.rain_occurrences FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own" ON public.rain_occurrences FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Admins view all" ON public.rain_occurrences FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.profiles WHERE profiles.id = auth.uid() AND profiles.role = 'ADMIN')
);
