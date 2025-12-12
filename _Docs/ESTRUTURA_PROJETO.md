# Documentação Técnica do Projeto RAIA

## 1. Visão Geral
O **RAIA (Registro de Atendimento Integrado e Análise)** é um sistema web desenvolvido para o Corpo de Bombeiros (CBI-1) para gerenciar ocorrências, usuários e relatórios. O sistema foca em segurança, integridade de dados e facilidade de uso operacional.

## 2. Tecnologias Utilizadas
- **Backend**: Python com Flask.
- **Banco de Dados & Auth**: Supabase (PostgreSQL).
- **Armazenamento (Storage)**: MinIO (S3 Compatible).
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla).
- **Estilização**: CSS customizado com design responsivo e moderno.

## 3. Estrutura de Diretórios
```
/server_telco/cbi1hub
├── app.py                 # Núcleo da aplicação (Rotas, Lógica, Configuração)
├── .env                   # Variáveis de ambiente (Chaves de API, Segredos)
├── start.sh               # Script de inicialização do servidor
├── requirements.txt       # Dependências Python
├── venv/                  # Ambiente virtual Python
├── _Docs/                 # Documentação do projeto
├── _archive/              # Arquivos antigos e backups
├── static/                # Arquivos estáticos
│   ├── style.css          # Estilos globais
│   ├── img/               # Imagens e ícones
│   └── uploads/           # (Opcional) Uploads locais temporários
└── templates/             # Páginas HTML (Jinja2)
    ├── login.html         # Tela de Login
    ├── signup.html        # Tela de Cadastro
    ├── dashboard.html     # Painel Principal
    ├── admin/             # Área Administrativa
    │   ├── menu_admin.html
    │   ├── admin_dashboard.html
    │   └── painel_ocorrencias.html
    ├── raia/              # Módulo RAIA (Ocorrências)
    │   ├── menu_raia.html
    │   ├── elaborar_raia.html
    │   └── listar_raias.html
    ├── chuvas/            # Módulo Chuvas Intensas
    │   ├── menu_chuvas.html
    │   ├── elaborar_chuvas.html
    │   ├── listar_chuvas.html
    │   └── selecionar_gb.html # Filtro de visualização por GB
    ├── vulto/             # Módulo Vulto (Ocorrências de Grande Porte)
    │   ├── menu_vulto.html
    │   └── elaborar_vulto.html
    ├── inconsistencia/    # Módulo Inconsistências (Reporte de Erros)
    │   ├── menu_inc.html
    │   ├── gerar_inconsistencia.html
    │   └── listar_inconsistencias.html
    ├── auth/              # Autenticação
    │   ├── login.html
    │   ├── signup.html
    │   └── reset_password_confirm.html
    ├── mergulho/          # Módulo Mergulho (Placeholder)
    ├── ronda/             # Módulo Ronda Supervisor (Placeholder)
    └── fogo/              # Módulo Apoio Fogo (Placeholder)
```

## 4. Banco de Dados (Supabase)

### Schemas
- **`public`**: Dados mestres, perfis de usuários, ocorrências e chuvas.
- **`auth`**: Gerenciado internamente pelo Supabase para autenticação.

### Principais Tabelas (`public`)
1.  **`profiles`**: Extensão dos dados do usuário.
    - `id` (FK auth.users), `full_name`, `war_name`, `rank`, `re`, `opm_id`, `contact`, `role` (ELABORATOR, ADMIN).
2.  **`occurrences`**: Tabela principal de ocorrências RAIA.
    - `id`, `user_id`, `nature_id`, `description`, `address`, `status` (OPEN, ARCHIVED), `photos`, etc.
3.  **`rain_occurrences`**: Tabela de Chuvas Intensas.
    - `id`, `talao_numero`, `status` (ESPERA, ATENDIDO, etc.), `prioridade`, `resultado` (SUPRESSAO, CORTE, etc.).
4.  **`vulto_occurrences`**: Ocorrências de Vulto (Destaque).
    - `id`, `justificativa_vulto`, `generated_text` (Texto Zap), `qtd_viaturas`, `oficiais_presenca`, etc.
5.  **`inconsistencies`**: Registro de problemas operacionais/técnicos.
    - `id`, `tipo` (OPERACIONAL, TECNICA), `t4_sistema_afetado`, `observacao`.
6.  **`opm`**: Lista de OPMs (Estações).
    - `id`, `EB` (Nome), `GB`, `SGB`.
7.  **`municipalities`**: Lista de municípios.
8.  **`css`**: Lista de concessionárias.
9.  **`oco_raia`**: Naturezas de ocorrência.

## 5. Funcionalidades Chave

### 5.1. Autenticação e Cadastro
- **Login**: E-mail (`@policiamilitar.sp.gov.br`) e Senha.
- **Cadastro**: Validação de R.E., Contato e E-mail funcional.
- **RBAC**: Acesso diferenciado para `ADMIN`.

### 5.2. Módulo RAIA
- **Elaboração**: Formulário com geolocalização e fotos (MinIO).
- **Listagem**: Histórico pessoal.

### 5.3. Módulo Chuvas Intensas
- **Gestão**: Registro específico para eventos climáticos.
- **Fluxo**: Elaboração -> Listagem (Visualização e Edição em Sidebar).
- **Visualização**: Filtros por GB (7º, 15º, 16º, 19º) ou Minhas Ocorrências.
- **Edição**:
    - *Modo GB*: Apenas alteração de Status e Resultado.
    - *Modo Pessoal*: Edição total e Exclusão.

### 5.4. Módulo Vulto
- **Geração Automática**: Criação de texto padrão para divulgação em grupos (WhatsApp).
- **Registro**: Armazenamento detalhado de recursos, tempos e oficiais presentes.

### 5.5. Módulo Inconsistências
- **Reporte**: Usuários podem reportar falhas técnicas (T4) ou operacionais.
- **Gestão**: Admins visualizam todos os reportes.

### 5.6. Painel Administrativo
- **Gestão de Usuários**: Visualizar e editar perfis.
- **Auditoria**: Visualizar, arquivar e deletar ocorrências RAIA e Inconsistências.

## 6. Configuração e Deploy

### Variáveis de Ambiente (`.env`)
- `SUPABASE_URL`, `SUPABASE_KEY`: Acesso App.
- `SUPABASE_SERVICE_KEY`: Acesso Admin (Criação de usuários, bypass RLS).
- `SECRET_KEY`: Sessão Flask.
- `MINIO_...`: Configuração do Storage.

### Execução
1.  `./start.sh` para iniciar.
2.  Acessar porta `3001`.
