-- Criação da tabela Profiles (Extensão do auth.users)
-- Ajustado para bater com 'profiles_rows.sql'
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    full_name TEXT,
    war_name TEXT, 
    role TEXT DEFAULT 'USER', -- ADMIN, USER, DISPATCHER
    corporation_id TEXT, -- RE/Matrícula
    rank TEXT, -- Posto/Graduação
    opm_id TEXT, -- Loose reference due to data mismatch (Seed uses UUID, OPM table uses Int)
    contact TEXT,
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Usuários veem e editam seu próprio perfil
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);
