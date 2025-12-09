import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
# Tenta usar a Service Key para verificação (tem mais permissões)
key: str = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("ERRO: Variáveis de ambiente não encontradas.")
    exit(1)

supabase: Client = create_client(url, key)

print("--- Verificando Supabase ---")

# 1. Verificar Tabela 'occurrences'
try:
    print("1. Verificando tabela 'occurrences'...")
    # Tenta selecionar 1 registro (mesmo que vazio, se não der erro a tabela existe)
    res = supabase.table('occurrences').select('id').limit(1).execute()
    print("   [OK] Tabela 'occurrences' encontrada.")
except Exception as e:
    print(f"   [ERRO] Falha ao acessar tabela 'occurrences': {e}")
    print("   -> Certifique-se de ter rodado o script SQL create_raia_schema.sql")

# 2. Verificar Bucket 'raia-photos'
try:
    print("\n2. Verificando bucket 'raia-photos'...")
    buckets = supabase.storage.list_buckets()
    found = False
    for b in buckets:
        if b.name == 'raia-photos':
            found = True
            print(f"   [OK] Bucket 'raia-photos' encontrado. (Public: {b.public})")
            break
    
    if not found:
        print("   [ERRO] Bucket 'raia-photos' NÃO encontrado.")
        print("   -> Crie um bucket PÚBLICO chamado 'raia-photos' no menu Storage do Supabase.")
        
except Exception as e:
    print(f"   [ERRO] Falha ao listar buckets: {e}")

print("\n--- Fim da Verificação ---")
