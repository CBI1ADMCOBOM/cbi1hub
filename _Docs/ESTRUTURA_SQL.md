# Estrutura do Banco de Dados (PostgreSQL / Supabase)

Este documento descreve o esquema do banco de dados utilizado pelo sistema CBI-1 Hub.

## Tabelas Principais

### `public.profiles`
Armazena dados estendidos dos usuários (além da tabela `auth.users` interna do Supabase/Gotrue).
- `id` (UUID, PK): Referência para `auth.users(id)`.
- `full_name`, `war_name` (Text): Identificação.
- `role` (Text): Papel do usuário (`USER`, `ADMIN`, `DISPATCHER`). Importante para controle de acesso.
- `corporation_id` (Text): Registro Estatístico (RE).
- `opm_id` (Text): Grupamento do usuário.

### `public.occurrences` (Módulo RAIA)
Ocorrências de Anomalias e Irregularidades.
- `id` (UUID, PK)
- `user_id` (UUID, FK): Autor.
- `opm_id` (BigInt): Unidade responsável.
- `concessionaire_id` (UUID): Concessionária envolvida.
- `nature_id` (Text): Classificação da anomalia.
- `photos` (Text[]): Array de URLs das fotos no MinIO.
- **RLS**: Usuários veem apenas as próprias. Admins veem todas.

### `public.vulto_occurrences` (Módulo Vulto)
Comunicados de destaque gerados.
- `id` (UUID, PK)
- `municipio_id` (UUID): ID do município. *Nota: Código foi adaptado para lookup de ID.*
- `generated_text` (Text): Texto final formatado.
- `oficiais_presenca` (Text): Lista de oficiais no local.
- **RLS**: Usuários veem apenas as próprias. Admins veem todas.

### `public.rain_occurrences` (Módulo Chuvas)
Ocorrências de Chuvas Intensas.
- `tipo_atendimento` (Text): 'BOMBEIROS' ou 'OUTROS'.
- `bombeiros_prontidao` (Text): Nível de prontidão.
- **RLS**: Usuários veem apenas as próprias. Admins veem todas.

### `public.inconsistencies` (Módulo Inconsistências)
Reportes de erros técnicos ou operacionais.
- `tipo` (Text): 'OPERACIONAL' ou 'TECNICA'.
- `motivo_tec_codigo` (Text): Código do erro técnico (ex: T4_APP).
- `t4_sistema_afetado` (Text): Sistema com falha.

## Tabelas de Referência (Auxiliares)

- **`public.opm`**: Lista de Organizações Policiais Militares (GB, SGB, EB).
- **`public.municipalities`**: Lista de municípios do Estado de SP (`id`, `name`).
- **`public.css`**: Lista de Concessionárias (`id`, `name`). Protected by default RLS (backend uses admin client to bypass).
- **`public.oco_raia`**: Naturezas de ocorrência RAIA. Protected by default RLS.

## Políticas de Segurança (Row Level Security - RLS)

Todas as tabelas principais possuem RLS habilitado:
1.  **Leitura/Escrita Padrão**: `auth.uid() = user_id`. (Usuário só acessa o que criou).
2.  **Leitura Admin**: Uma policy verifica se o usuário tem `role = 'ADMIN'` na tabela `profiles`. Se sim, permite `SELECT` irrestrito.

## Notas de Implementação

- **Migrações**: O esquema foi construído via arquivos `.sql` localizados em `_archive/sql_migrations`.
- **Correções Recentes**:
    - A tabela `vulto_occurrences` foi desenhada esperando `municipio_id` (UUID), mas o frontend enviava texto. O backend agora resolve o ID antes de salvar.
    - Tabelas auxiliares (`css`, `oco_raia`) possuem RLS restritivo. O backend Python utiliza `supabase_admin` para leitura pública dessas listas de referência.
