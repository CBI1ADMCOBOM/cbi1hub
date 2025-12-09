-- Criação da tabela de ocorrências de CHUVAS INTENSAS
CREATE TABLE IF NOT EXISTS public.rain_occurrences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    
    -- Dados Básicos
    talao_numero TEXT,
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    endereco TEXT,
    latitude TEXT,
    longitude TEXT,
    municipio_id BIGINT REFERENCES public.municipalities(id),
    
    -- Tipo de Atendimento
    tipo_atendimento TEXT NOT NULL, -- 'BOMBEIROS' ou 'OUTROS'
    
    -- Se Bombeiros
    bombeiros_station_id BIGINT REFERENCES public.opm(id),
    bombeiros_prontidao TEXT, -- 'VERDE', 'AMARELA', 'AZUL'
    bombeiros_viatura TEXT,
    bombeiros_encarregado TEXT,
    
    -- Se Outros
    outros_orgao TEXT, -- 'DEFESA_CIVIL', 'PREFEITURA', 'ENERGIA', 'SANEAMENTO', 'PARCELA', etc
    outros_detalhes TEXT,
    
    -- Classificação
    natureza_codigo TEXT, -- 'A1', 'A2', 'A3', 'A4', 'A5'
    area_tipo TEXT, -- 'PARTICULAR', 'PUBLICA'
    prioridade TEXT, -- 'ALTA', 'MEDIA', 'BAIXA'
    
    -- Andamento
    limpeza_via TEXT, -- 'REALIZADA', 'AGUARDANDO', 'NAO_SE_APLICA'
    status TEXT DEFAULT 'ESPERA', -- 'ESPERA', 'AGENDADA', 'EM_ATENDIMENTO', 'ATENDIDO'
    resultado TEXT, -- 'SUPRESSAO', 'PODA', 'NAO_SE_APLICA'
    
    observacao TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Políticas de Segurança (RLS)
ALTER TABLE public.rain_occurrences ENABLE ROW LEVEL SECURITY;

-- Usuários podem ver apenas suas próprias ocorrências
DROP POLICY IF EXISTS "Users can view own rain occurrences" ON public.rain_occurrences;
CREATE POLICY "Users can view own rain occurrences" ON public.rain_occurrences
    FOR SELECT USING (auth.uid() = user_id);

-- Usuários podem inserir suas próprias ocorrências
DROP POLICY IF EXISTS "Users can insert own rain occurrences" ON public.rain_occurrences;
CREATE POLICY "Users can insert own rain occurrences" ON public.rain_occurrences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Admins podem ver tudo
DROP POLICY IF EXISTS "Admins can view all rain occurrences" ON public.rain_occurrences;
CREATE POLICY "Admins can view all rain occurrences" ON public.rain_occurrences
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'ADMIN'
        )
    );
