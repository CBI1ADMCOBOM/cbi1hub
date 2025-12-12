-- Criação da tabela Municipalities
CREATE TABLE IF NOT EXISTS public.municipalities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL, -- Unique constraint para funcionar o ON CONFLICT
    state TEXT NOT NULL DEFAULT 'SP',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- RLS
ALTER TABLE public.municipalities ENABLE ROW LEVEL SECURITY;

-- Permitir leitura pública (autenticada)
CREATE POLICY "Allow public read of municipalities" ON public.municipalities
    FOR SELECT USING (auth.role() = 'authenticated');
