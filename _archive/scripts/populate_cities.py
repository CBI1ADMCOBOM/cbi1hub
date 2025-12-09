import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

cities = [
    'Aguaí', 'Águas da Prata', 'Águas de Lindóia', 'Águas de Santa Bárbara', 'Águas de São Pedro', 'Alambari', 
    'Alumínio', 'Americana', 'Amparo', 'Analândia', 'Angatuba', 'Anhembi', 'Apiaí', 'Araçariguama', 
    'Araçoiaba da Serra', 'Arandu', 'Araras', 'Areiópolis', 'Artur Nogueira', 'Atibaia', 'Avaré', 
    'Barão de Antonina', 'Barra do Chapéu', 'Bofete', 'Boituva', 'Bom Jesus dos Perdões', 'Bom Sucesso de Itararé', 
    'Botucatu', 'Bragança Paulista', 'Brotas', 'Buri', 'Cabreúva', 'Caconde', 'Campina do Monte Alegre', 
    'Campinas', 'Campo Limpo Paulista', 'Capão Bonito', 'Capela do Alto', 'Capivari', 'Casa Branca', 
    'Cerqueira César', 'Cerquilho', 'Cesário Lange', 'Charqueada', 'Conchal', 'Conchas', 'Cordeirópolis', 
    'Coronel Macedo', 'Corumbataí', 'Cosmópolis', 'Divinolândia', 'Elias Fausto', 'Engenheiro Coelho', 
    'Espírito Santo do Pinhal', 'Estiva Gerbi', 'Fartura', 'Guapiara', 'Guareí', 'Holambra', 'Hortolândia', 
    'Iaras', 'Ibiúna', 'Indaiatuba', 'Iperó', 'Ipeúna', 'Iracemápolis', 'Itaberá', 'Itaí', 'Itaoca', 
    'Itapetininga', 'Itapeva', 'Itapira', 'Itapirapuã Paulista', 'Itaporanga', 'Itararé', 'Itatiba', 
    'Itatinga', 'Itirapina', 'Itobi', 'Itu', 'Itupeva', 'Jaguariúna', 'Jarinu', 'Joanópolis', 'Jumirim', 
    'Jundiaí', 'Laranjal Paulista', 'Leme', 'Limeira', 'Lindóia', 'Louveira', 'Mairinque', 'Manduri', 
    'Mococa', 'Mogi Guaçu', 'Mogi Mirim', 'Mombuca', 'Monte Alegre do Sul', 'Monte Mor', 'Morungaba', 
    'Nazaré Paulista', 'Nova Campina', 'Nova Odessa', 'Paranapanema', 'Pardinho', 'Paulínia', 'Pedra Bela', 
    'Pedreira', 'Pereiras', 'Piedade', 'Pilar do Sul', 'Pinhalzinho', 'Piracaia', 'Piracicaba', 'Piraju', 
    'Pirassununga', 'Porangaba', 'Porto Feliz', 'Pratânia', 'Quadra', 'Rafard', 'Ribeira', 'Ribeirão Branco', 
    'Ribeirão Grande', 'Rio Claro', 'Rio das Pedras', 'Riversul', 'Saltinho', 'Salto', 'Salto de Pirapora', 
    'Santa Bárbara d\'Oeste', 'Santa Cruz da Conceição', 'Santa Cruz das Palmeiras', 'Santa Gertrudes', 
    'Santa Maria da Serra', 'Santo Antônio de Posse', 'Santo Antônio do Jardim', 'São João da Boa Vista', 
    'São José do Rio Pardo', 'São Manuel', 'São Miguel Arcanjo', 'São Pedro', 'São Roque', 
    'São Sebastião da Grama', 'Sarapuí', 'Sarutaiá', 'Serra Negra', 'Socorro', 'Sorocaba', 'Sumaré', 
    'Taguaí', 'Tambaú', 'Tapiraí', 'Tapiratiba', 'Taquarituba', 'Taquarivaí', 'Tatuí', 'Tejupá', 'Tietê', 
    'Torre de Pedra', 'Torrinha', 'Tuiuti', 'Valinhos', 'Vargem', 'Vargem Grande do Sul', 'Várzea Paulista', 
    'Vinhedo', 'Votorantim'
]

data = [{'name': city, 'state': 'SP'} for city in cities]

# Upsert (insert or update on conflict)
# Note: 'municipalities' must have a unique constraint on 'name' for minimal duplication, 
# or we just rely on ID. Assuming we want to populate these specific names.
# Better to select existing first to avoid duplicates if no unique constraint.

print(f"Inserindo {len(cities)} municípios...")

existing = supabase.table('municipalities').select('name').execute()
existing_names = {row['name'] for row in existing.data}

to_insert = [d for d in data if d['name'] not in existing_names]

if to_insert:
    res = supabase.table('municipalities').insert(to_insert).execute()
    print(f"Inseridos: {len(res.data)}")
else:
    print("Todos os municípios já existem.")
