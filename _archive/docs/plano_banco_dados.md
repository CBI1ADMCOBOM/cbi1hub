# Plano de Construção do Banco de Dados - RAIA (Final)

## Estratégia de Schemas
- **`public`**: Dados compartilhados (Municípios, Perfis, Concessionárias).
- **`raia_sistema`**: Dados específicos do aplicativo (Ocorrências, Comentários).

## 1. Schema `public` (Dados Mestres)

### 1.1. Municípios (`municipalities`)
Lista oficial do IBGE para SP.
```sql
CREATE TABLE IF NOT EXISTS public.municipalities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    ibge_code TEXT UNIQUE,
    state CHAR(2) DEFAULT 'SP',
    active BOOLEAN DEFAULT TRUE
);
-- (Insert de 645 municípios será carregado via seeds_municipios.sql)
```

### 1.2. Concessionárias (`concessionaires`)
```sql
CREATE TABLE IF NOT EXISTS public.concessionaires (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    active BOOLEAN DEFAULT TRUE
);
```

### 1.3. Perfis (`profiles`)
```sql
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    role TEXT NOT NULL DEFAULT 'ELABORATOR', -- ELABORATOR, AUDITOR, ADMIN
    corporation_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 1.4. Naturezas de Incidente (`incident_natures`)
```sql
CREATE TABLE IF NOT EXISTS public.incident_natures (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    code TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT,
    active BOOLEAN DEFAULT TRUE
);
```

## 2. Schema `raia_sistema` (Dados do App)

### 2.1. Ocorrências (`occurrences`)
```sql
CREATE TABLE raia_sistema.occurrences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'ABERTO' NOT NULL, -- ABERTO, APROVADO, REPROVADO...
    
    -- Classificação
    nature_id UUID REFERENCES public.incident_natures(id),
    
    -- Localização
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    address_manual TEXT,
    municipality_id UUID REFERENCES public.municipalities(id),
    
    -- Detalhes
    description TEXT,
    
    -- Responsabilidade
    entity_type TEXT, -- CONCESSIONARIA, PREFEITURA
    concessionaire_id UUID REFERENCES public.concessionaires(id),
    entity_detail TEXT,
    
    -- Mídia
    media_urls TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 3. Scripts de Carga (Seeds)
- `seeds_municipios.sql`: Carrega os 645 municípios de SP.
- `seeds_naturezas.sql`: Carrega os códigos Z01/Z04 filtrados.

## 4. Módulo Vulto (Novo)

### 4.1. Ocorrências de Vulto (`public.vulto_occurrences`)
Tabela para registro de ocorrências de destaque/vulto.
```sql
CREATE TABLE IF NOT EXISTS public.vulto_occurrences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    opm_id BIGINT REFERENCES public.opm_cb(id), -- Estação/GB
    
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
    municipio_nome TEXT, -- Armazena nome direto (ex: 'Sorocaba')
    endereco TEXT,
    bairro TEXT,
    referencia TEXT,
    
    -- Recursos
    qtd_viaturas INTEGER,
    qtd_bombeiros INTEGER,
    tempo_resposta_minutos INTEGER,
    
    -- Pessoal
    encarregado_posto TEXT,
    encarregado_nome TEXT,
    oficiais_presenca TEXT, -- Ex: 'Cap Fulano' ou 'NÃO HOUVE...'
    
    -- Histórico
    historico_inicial TEXT,
    historico_final TEXT,
    
    -- Transmissão
    pm_transmissao_posto TEXT,
    pm_transmissao_nome TEXT,
    
    -- Meta
    generated_text TEXT, -- Cópia do texto gerado para WhatsApp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```
