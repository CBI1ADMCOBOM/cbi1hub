-- Criação da tabela CSS (Concessionárias de Rodovias)
CREATE TABLE IF NOT EXISTS public.css (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- RLS
ALTER TABLE public.css ENABLE ROW LEVEL SECURITY;

-- Leitura pública autenticada
CREATE POLICY "Allow public read of css" ON public.css
    FOR SELECT USING (auth.role() = 'authenticated');
