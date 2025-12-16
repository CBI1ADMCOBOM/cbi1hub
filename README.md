# CBI-1 Hub - Sistema de Gestão de Ocorrências e Vulto

Este projeto é uma plataforma web para gestão de ocorrências (RAIA) e comunicados de destaque (Vulto) para o Corpo de Bombeiros (CBI-1).

## Módulos Principais

### 1. RAIA (Registro de Anomalias e Irregularidades Ambientais / Administrativas?)
- Cadastro de ocorrências com geolocalização.
- Upload de imagens para MinIO.
- Integração com mapas.
- Painel Administrativo para gestão.

### 2. Vulto (Comunicados de Destaque)
- Formulário para elaboração de textos padronizados para WhatsApp.
- Geração automática de texto formatado (Padrão e IA).
- Registro histórico de ocorrências de vulto.
- **Tabela**: `vulto_occurrences` (Supabase).
- **Campos**: Inclui lógica de Oficiais Presentes, Encarregados e Localização detalhada.

## Estrutura de Arquivos Importantes
- `app.py`: Backend Flask principal.
- `templates/`: Arquivos HTML (Jinja2).
    - `vulto/elaborar_vulto.html`: Formulário principal do Vulto.
    - `raia/`: Templates do módulo RAIA.
- `plano_banco_dados.md`: Documentação técnica do Schema do Banco de Dados.
- `_archive/`: Scripts antigos ou de migração única.

## Como Executar
1. Ativar ambiente virtual (`source venv/bin/activate`).
2. Configurar variáveis de ambiente (`.env`).
3. Rodar `python app.py` (ou `start.sh`).

## Notas de Desenvolvimento Recentes
- **Vulto**: Migrado de Google Apps Script para Flask.
- **Municipalidades**: O Backend agora realiza lookup de ID para nome, permitindo salvar corretamente.
- **Correções (Dez/2025)**:
    - **RAIA**: Corrigido carregamento de listas (Naturezas e Concessionárias) bypassando RLS via admin client.
    - **Vulto**: Adicionada opção de excluir ocorrência (próprio usuário).
    - **Vulto**: Corrigido erro de schema (municipio_nome vs id) no salvamento.

### Login admin
1.  admin@raia.app
2.  193193