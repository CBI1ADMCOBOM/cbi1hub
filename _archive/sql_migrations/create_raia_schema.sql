-- Criação da tabela de ocorrências RAIA
CREATE TABLE IF NOT EXISTS public.occurrences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    opm_id BIGINT REFERENCES public.opm(id),
    concessionaire_id UUID REFERENCES public.css(id),
    nature_id TEXT, -- Armazena o código ou ID da natureza
    description TEXT,
    address TEXT,
    manual_location TEXT,
    latitude TEXT,
    longitude TEXT,
    has_responsible BOOLEAN DEFAULT FALSE,
    responsible_name TEXT,
    responsible_role TEXT,
    responsible_contact TEXT,
    photos TEXT[], -- Array de URLs das fotos
    status TEXT DEFAULT 'OPEN',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Políticas de Segurança (RLS)
ALTER TABLE public.occurrences ENABLE ROW LEVEL SECURITY;

-- Usuários podem ver apenas suas próprias ocorrências
CREATE POLICY "Users can view own occurrences" ON public.occurrences
    FOR SELECT USING (auth.uid() = user_id);

-- Usuários podem inserir suas próprias ocorrências
CREATE POLICY "Users can insert own occurrences" ON public.occurrences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Admins podem ver tudo (assumindo role na tabela profiles ou claim)
-- Exemplo simples baseado na role da tabela profiles
CREATE POLICY "Admins can view all occurrences" ON public.occurrences
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE profiles.id = auth.uid() AND profiles.role = 'ADMIN'
        )
    );

-- Criação do Bucket de Storage (se não existir, precisa ser feito via interface ou API, SQL não cria bucket diretamente no Supabase Storage padrão, mas podemos tentar criar a policy)
-- O bucket 'raia-photos' deve ser criado manualmente no painel do Supabase se este script não funcionar para buckets.
-- Mas podemos criar as policies para os objetos dentro do bucket 'raia-photos'.

-- Policy para Storage: Permitir upload autenticado
-- Nota: Isso deve ser rodado no editor SQL do Supabase, pois buckets são gerenciados via API/Interface geralmente.
-- CREATE POLICY "Allow authenticated uploads" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'raia-photos' AND auth.role() = 'authenticated');
-- CREATE POLICY "Allow public viewing" ON storage.objects FOR SELECT USING (bucket_id = 'raia-photos');
