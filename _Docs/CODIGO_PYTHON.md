# Documentação da Base de Código Python (CBI-1 Hub)

Este documento detalha a estrutura, funcionamento e propósito de cada arquivo Python no projeto.

## Visão Geral da Arquitetura

O projeto é uma aplicação web **Flask** (Python) que atua como backend e frontend (Server-Side Rendering com Jinja2).
- **Banco de Dados**: Supabase (PostgreSQL).
- **Armazenamento de Arquivos**: MinIO (Compatível com S3) para fotos.
- **Autenticação**: Gerenciada pelo Supabase Auth, integrada via sessão do Flask.

---

## 1. Arquivos Principais (Core)

### `app.py`
**Ponto de entrada da aplicação.**
- Inicializa o app Flask.
- Carrega variáveis de ambiente.
- Registra os **Blueprints** (módulos de rotas) para organizar o código.
- Define a chave secreta da aplicação.

### `services.py`
**Camada de Serviços e Infraestrutura.**
- Conecta ao **Supabase**:
    - `supabase`: Cliente público (respeita Row Level Security - RLS).
    - `supabase_admin`: Cliente com `service_role` (bypass RLS) para operações administrativas.
- Conecta ao **MinIO**: Cliente para upload de imagens.
- **Decorators**: Define `@login_required` para proteger rotas.

---

## 2. Módulos de Rotas (Blueprints)

### `routes/auth.py` (Autenticação)
Gerencia o acesso dos usuários.
- **/login**: Interface e API de login via Supabase.
- **/signup**: Registro de novos usuários (apenas emails `@policiamilitar.sp.gov.br`). Cria perfil automaticamente.
- **/logout**: Limpa a sessão.
- **/reset-password**: Fluxo de recuperação de senha.

### `routes/main.py` (Dashboard e Utilitários)
Funcionalidades gerais do sistema.
- **/ (Dashboard)**: Painel principal, carrega dados do perfil do usuário.
- **/api/profile/me**: Atualiza dados do perfil (RE, Patente, Nome de Guerra).
- **/api/opms**: Lista as Estações de Bombeiros (GB/SGB/EB).
- **/api/municipios**: Lista municípios disponíveis.

### `routes/raia.py` (Módulo RAIA)
Registro de Anomalias e Irregularidades Ambientais.
- **/elaborar-raia/**: Telas de menu, criação e listagem.
- **/api/raia/save**: Recebe o formulário (multipart), faz upload das fotos para o MinIO, gera URLs públicas e salva os metadados no Supabase.
- **/api/naturezas_raia** & **/api/concessionarias**: Listas de referência (Bypass RLS via admin client).

### `routes/vulto.py` (Módulo Vulto)
Geração de textos padronizados para comunicados de destaque.
- **/elaborar-vulto/**: Formulário de criação e listagem.
- **Lógica de Texto**: Gera automaticamente o texto formatado do comunicado baseado nos inputs.
- **/api/vulto/save**: Salva a ocorrência. *Nota: Realiza lookup de ID do município pelo nome antes de salvar.*
- **/api/vulto/me**: Lista ocorrências do usuário (junta com tabela de municípios para exibir nomes).
- **DELETE**: Permite exclusão pelo próprio autor.

### `routes/chuvas.py` (Módulo Chuvas Intensas)
Monitoramento de ocorrências relacionadas a chuvas.
- **/chuvas-intensas/**: Telas de gestão e inputs.
- **Filtros por GB**: Permite filtrar ocorrências por Grupamento de Bombeiros.
- **CRUD Completo**: Create, Read, Update, Delete para ocorrências de chuva.

### `routes/inconsistencias.py` (Reporte de Erros)
Permite aos usuários reportarem erros operacionais ou técnicos.
- Tipos: `OPERACIONAL` ou `TECNICA` (ex: Falha no T4, App fora do ar).
- Painel para listar reportes do próprio usuário.

### `routes/admin.py` (Painel Administrativo)
Gestão centralizada para oficiais/admins.
- **/admin/occurrences**: Painel unificado vendo RAIA, Vulto, Chuvas e Inconsistências.
- **Ações**: Alterar status, arquivar e excluir registros de qualquer usuário.
- **/admin/fix-db**: Rota de emergência para tentar recriar tabelas faltantes via RPC (se configurado).
- **Auto-promoção**: Contém lógica hardcoded para promover um usuário específico a ADMIN em caso de emergência.

---

## 3. Scripts Utilitários

Estes scripts ficam na raiz e servem para manutenção manual executada via terminal.

- `promote_user.py`: Conecta no banco e promove um UUID específico para a role `ADMIN`.
- `fix_admin.py`: Variação do script acima, cria o perfil se não existir.
- `create_table.py`: Tenta criar a tabela de inconsistências via comando SQL direto (útil se as migrações automáticas falharem).

---

## Fluxo de Dados Típico

1.  **Requisição**: O usuário acessa uma rota (ex: `/elaborar-raia`).
2.  **Auth**: O decorator `@login_required` verifica a sessão.
3.  **Frontend**: O Flask renderiza o template HTML correspondente.
4.  **Interação**: O Javascript na página chama as APIs (ex: `/api/opms`).
5.  **Backend**: A rota chama o `supabase_admin` para buscar dados no PostgreSQL.
6.  **Retorno**: Dados retornam como JSON e a tela é atualizada.
