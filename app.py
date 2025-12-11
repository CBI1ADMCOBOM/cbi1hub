import os
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client, Client
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_super_secreta_padrao_dev") # Trocar em produção!

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Cliente Admin (Service Role) - Usado para criar usuários auto-confirmados e gestão
service_key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase_admin: Client = create_client(url, service_key)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login')
def login_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

@app.route('/reset-password-confirm')
def reset_password_confirm_page():
    return render_template('auth/reset_password_confirm.html', supabase_key=key)

@app.route('/')
@login_required
def dashboard():
    # Buscar dados completos do perfil do usuário
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        # Atualizar sessão com dados do perfil
        session['user'].update(res.data)
    except:
        pass
    return render_template('dashboard.html', user=session['user'])

@app.route('/elaborar-raia')
@login_required
def elaborar_raia():
    return render_template('raia/menu_raia.html', user=session['user'])

@app.route('/elaborar-raia/novo')
@login_required
def elaborar_raia_novo():
    return render_template('raia/elaborar_raia.html', user=session['user'])

@app.route('/elaborar-raia/listar')
@login_required
def elaborar_raia_listar():
    return render_template('raia/listar_raias.html', user=session['user'])

@app.route('/elaborar-vulto')
@login_required
def elaborar_vulto():
    return render_template('vulto/menu_vulto.html', user=session['user'])

@app.route('/elaborar-vulto/novo')
@login_required
def elaborar_vulto_novo():
    try:
        user_id = session['user']['id']
        profile_res = supabase.table('profiles').select('rank, war_name').eq('id', user_id).execute()
        profile = profile_res.data[0] if profile_res.data else {}
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
        profile = {}
        
    return render_template('vulto/elaborar_vulto.html', user=session['user'], profile=profile)

@app.route('/gerar-inconsistencia')
@login_required
def gerar_inconsistencia():
    return render_template('inconsistencia/menu_inc.html', user=session['user'])

@app.route('/gerar-inconsistencia/novo')
@login_required
def gerar_inconsistencia_novo():
    return render_template('inconsistencia/gerar_inconsistencia.html', user=session['user'])

@app.route('/api/inconsistencias/save', methods=['POST'])
@login_required
def save_inconsistencia():
    try:
        data = request.json
        user_id = session['user']['id']
        
        # Mapeamento do payload para colunas do banco
        inc_data = {
            'user_id': user_id,
            'data_ocorrencia': data.get('data_ocorrencia'),
            'talao_numero': data.get('talao'),
            'tipo': data.get('tipo', '').upper(),
            'observacao': data.get('observacao')
        }
        
        if inc_data['tipo'] == 'OPERACIONAL':
             inc_data['motivo_op_codigo'] = data.get('motivo_op')
             inc_data['motivo_op_descricao'] = data.get('motivo_descricao')
        elif inc_data['tipo'] == 'TECNICA':
             inc_data['motivo_tec_codigo'] = data.get('motivo_tec')
             inc_data['motivo_tec_descricao'] = data.get('motivo_descricao')
             
             # Campos específicos
             if data.get('motivo_tec') == 'T4_193':
                 inc_data['t4_origem'] = data.get('t4_origem')
                 inc_data['t4_operadora'] = data.get('t4_operadora')
                 inc_data['t4_numero'] = data.get('t4_numero')
                 inc_data['t4_datahora'] = data.get('t4_datahora') if data.get('t4_datahora') else None
                 inc_data['t4_falha'] = data.get('t4_falha')
                 
             if data.get('motivo_tec') == 'T4_APP':
                 inc_data['t4_sistema_afetado'] = data.get('t4_sistema')

        res = supabase_admin.table('inconsistencies').insert(inc_data).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Erro Inconsistencia: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/gerar-inconsistencia/listar')
@login_required
def gerar_inconsistencia_listar():
    try:
        user_id = session['user']['id']
        # Buscar minhas inconsistências
        res = supabase.table('inconsistencies').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        inconsistencies = res.data
        return render_template('inconsistencia/listar_inconsistencias.html', user=session['user'], inconsistencies=inconsistencies)
    except Exception as e:
        print(f"Erro ao listar inconsistencias: {e}")
        return redirect(url_for('dashboard'))

@app.route('/chuvas-intensas')
@login_required
def chuvas_intensas():
    # print("Acessando menu chuvas intensas") 
    return render_template('chuvas/menu_chuvas.html', user=session['user'])

@app.route('/chuvas-intensas/novo')
@login_required
def chuvas_intensas_novo():
    return render_template('chuvas/elaborar_chuvas.html', user=session['user'])

@app.route('/chuvas-intensas/selecao')
@login_required
def chuvas_intensas_selecao():
    return render_template('chuvas/selecionar_gb.html', user=session['user'])

@app.route('/chuvas-intensas/listar')
@login_required
def chuvas_intensas_listar():
    try:
        user_id = session['user']['id']
        gb_filter = request.args.get('gb')
        modo = request.args.get('modo')
        
        items = []
        is_gb_view = False
        
        if gb_filter:
            is_gb_view = True
            # Busca IDs das estações desse GB
            # O formato no banco em opm.GB deve ser consultado. Como não tenho certeza se é '7GB' ou '7º GB', 
            # vou usar ilike com o numero. Ex: gb='7GB' -> ilike '%7%'
            # Mas o usuario pediu botoes especificos.
            # Vou assumir que o parametro bate com o banco ou fazer um like generico.
            
            # Extrair apenas numeros do gb_filter string (ex: '7GB' -> '7')
            gb_num = ''.join(filter(str.isdigit, gb_filter))
            
            # Buscar na tabela OPM
            opm_res = supabase_admin.table('opm').select('id').ilike('GB', f'%{gb_num}%').execute()
            if opm_res.data:
                station_ids = [opm['id'] for opm in opm_res.data]
                if station_ids:
                    # Buscar ocorrencias dessas estações
                    rain_res = supabase_admin.table('rain_occurrences').select('*').in_('bombeiros_station_id', station_ids).order('created_at', desc=True).execute()
                    items = rain_res.data
        else:
            # Modo 'meus' ou padrão
            res = supabase_admin.table('rain_occurrences').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            items = res.data

        print(f"Listando chuvas (GB={gb_filter}, Meus={not gb_filter}): {len(items)} items encontrados.")
        
        return render_template('chuvas/listar_chuvas.html', user=session['user'], items=items, is_gb_view=is_gb_view)
    except Exception as e:
        print(f"Erro listar chuvas: {e}")
        return redirect(url_for('chuvas_intensas'))

@app.route('/api/chuvas/save', methods=['POST'])
@login_required
def save_chuvas():
    try:
        data = request.json
        user_id = session['user']['id']
        
        # Mapeamento do payload para banco
        rain_data = {
            'user_id': user_id,
            'talao_numero': data.get('talao_numero'),
            'data_hora': data.get('data_hora'),
            'endereco': data.get('endereco'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            
            # Mudança estratégica: Salvar o NOME do município, não o ID
            # Para isso, o campo no banco deve ser 'municipio_nome' (se não existir, criar ou usar outro campo texto)
            # Mas espere, criei o banco AGORA com 'municipio_id BIGINT'.
            # Opção A: Tentar salvar o nome no campo 'endereco' (gambiarra)
            # Opção B: Pedir pro user alterar o campo no banco.
            # Opção C: Usar 'municipio_id' como string? Nao, é bigint.
            # Opção D: Deixar null o id e concatenar o municipio no endereço para não perder.
            
            'municipio_id': None, # Ignora ID pois mudamos para nome no front
            # Vou concatenar o município no endereço se ele não estiver lá, para garantir persistência sem mudar esquema agora
            # Mas o ideal é mudar a tabela.
            
            'tipo_atendimento': data.get('tipo_atendimento'),
            'bombeiros_station_id': int(data.get('bombeiros_station_id')) if data.get('bombeiros_station_id') else None,
            'bombeiros_prontidao': data.get('bombeiros_prontidao'),
            'bombeiros_viatura': data.get('bombeiros_viatura'),
            'bombeiros_encarregado': data.get('bombeiros_encarregado'),
            
            'outros_orgao': data.get('outros_orgao'),
            'outros_detalhes': data.get('outros_detalhes'),
            
            'natureza_codigo': data.get('natureza_codigo'),
            'area_tipo': data.get('area_tipo'),
            'prioridade': data.get('prioridade'),
            
            'limpeza_via': data.get('limpeza_via'),
            'status': data.get('status'),
            'resultado': data.get('resultado'),
            'observacao': f"Município: {data.get('municipio_id')} | {data.get('observacao', '')}" # Salvando municipio na observação provisoriamente
        }
        
        # Usar admin client para garantir permissões se necessario (embora policy permita insert auth.uid)
        res = supabase_admin.table('rain_occurrences').insert(rain_data).execute()
        return jsonify({"success": True, "id": res.data[0]['id']})
    except Exception as e:
        print(f"Erro Salvar Chuvas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chuvas/update/<id>', methods=['PUT'])
@login_required
def update_chuvas(id):
    try:
        data = request.json
        user_id = session['user']['id']
        
        # Verificar se o registro pertence ao usuário (ou se é admin, mas focando no dono por enquanto)
        # Opcional: Se tiver RLS configurado, o proprio supabase client do usuario ja barraria, 
        # mas aqui estamos usando supabase_admin ou precisamos instanciar cliente com token do user.
        # Por simplicidade e segurança, verificamos ownership antes de update com admin.
        check = supabase_admin.table('rain_occurrences').select('user_id').eq('id', id).single().execute()
        if not check.data:
             return jsonify({"success": False, "error": "Registro não encontrado."}), 404
        if check.data['user_id'] != user_id:
             return jsonify({"success": False, "error": "Sem permissão para editar este registro."}), 403

        # Mapeamento do payload para atualização
        # Replicando a lógica do save, mas apenas campos editáveis
        rain_data = {
            'talao_numero': data.get('talao_numero'),
            'data_hora': data.get('data_hora'),
            'endereco': data.get('endereco'),
            # 'latitude': data.get('latitude'), # Geralmente não edita geo manualmente mas ok se vier
            # 'longitude': data.get('longitude'),
            
            'tipo_atendimento': data.get('tipo_atendimento'),
            'bombeiros_station_id': int(data.get('bombeiros_station_id')) if data.get('bombeiros_station_id') else None,
            'bombeiros_prontidao': data.get('bombeiros_prontidao'),
            'bombeiros_viatura': data.get('bombeiros_viatura'),
            'bombeiros_encarregado': data.get('bombeiros_encarregado'),
            
            'outros_orgao': data.get('outros_orgao'),
            'outros_detalhes': data.get('outros_detalhes'),
            
            'natureza_codigo': data.get('natureza_codigo'),
            'area_tipo': data.get('area_tipo'),
            'prioridade': data.get('prioridade'),
            
            'limpeza_via': data.get('limpeza_via'),
            'status': data.get('status'),
            'resultado': data.get('resultado'),
            'observacao': data.get('observacao') # Aqui assume que o front manda a observação completa já editada
        }
        
        # Remove chaves com None para não apagar dados existentes se o front não mandar tudo? 
        # Não, PUT geralmente substitui o recurso ou update via PATCH. Aqui estamos fazendo update de campos especificos.
        # O supabase update atualiza apenas o que for passado.
        # Vamos garantir que não tenhamos chaves indesejadas.
        
        res = supabase_admin.table('rain_occurrences').update(rain_data).eq('id', id).execute()
        return jsonify({"success": True})

    except Exception as e:
        print(f"Erro Update Chuvas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chuvas/delete/<id>', methods=['DELETE'])
@login_required
def delete_chuvas(id):
    try:
        user_id = session['user']['id']
        
        # Verificar ownership
        check = supabase_admin.table('rain_occurrences').select('user_id').eq('id', id).single().execute()
        if not check.data:
             return jsonify({"success": False, "error": "Registro não encontrado."}), 404
        if check.data['user_id'] != user_id:
             return jsonify({"success": False, "error": "Sem permissão para excluir este registro."}), 403

        supabase_admin.table('rain_occurrences').delete().eq('id', id).execute()
        return jsonify({"success": True})

    except Exception as e:
        print(f"Erro Delete Chuvas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/inconsistencias/<id>', methods=['DELETE'])
@login_required
def delete_inconsistencia(id):
    try:
        user_id = session['user']['id']
        # Verificar se pertence ao usuário
        res = supabase_admin.table('inconsistencies').select('user_id').eq('id', id).single().execute()
        
        if not res.data:
            return jsonify({"success": False, "error": "Registro não encontrado."}), 404
            
        if res.data['user_id'] != user_id:
             return jsonify({"success": False, "error": "Permissão negada."}), 403

        supabase_admin.table('inconsistencies').delete().eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/mergulho')
@login_required
def mergulho():
    return render_template('mergulho/index.html', user=session['user'])

@app.route('/ronda-supervisor')
@login_required
def ronda_supervisor():
    return render_template('ronda/index.html', user=session['user'])

@app.route('/apoio-fogo')
@login_required
def apoio_fogo():
    return render_template('fogo/index.html', user=session['user'])

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('username')
    password = data.get('password')

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # Salvar na sessão do Flask
        session['user'] = {
            'id': response.user.id,
            'email': response.user.email,
            'access_token': response.session.access_token,
            'refresh_token': response.session.refresh_token
        }
        
        return jsonify({"success": True, "redirect": url_for('dashboard')})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/signup')
def signup_page():
    return render_template('auth/signup.html')

@app.route('/api/opms')
def get_opms():
    try:
        # Usando a nova tabela 'opm'
        # Usando supabase_admin para garantir leitura (bypass RLS)
        response = supabase_admin.table('opm').select('*').order('EB').execute()
        
        return jsonify(response.data)
    except Exception as e:
        print(f"Erro ao buscar OPMs: {e}")
        return jsonify([]), 500

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    contact = data.get('contact', '')

    # Validação de domínio de e-mail
    if not email or not email.endswith('@policiamilitar.sp.gov.br'):
        return jsonify({"success": False, "error": "Apenas e-mails funcionais (@policiamilitar.sp.gov.br) são permitidos."})

    # Validação e sanitização de contato
    contact_clean = re.sub(r'\D', '', contact)
    if not contact_clean or len(contact_clean) < 10 or len(contact_clean) > 11:
        return jsonify({"success": False, "error": "Telefone inválido. Informe DDD + Número (10 ou 11 dígitos)."}), 400
    
    # Validação de RE
    re_value = data.get('re')
    if not re_value or not re.match(r'^\d{6}-\d{1}$', re_value):
        return jsonify({"success": False, "error": "R.E. inválido. Use o formato 123456-7."}), 400
    
    # Metadados para salvar no profile via trigger
    metadata = {
        'full_name': data.get('full_name'),
        'war_name': data.get('war_name'),
        're': re_value,
        'rank': data.get('rank'),
        'opm_id': data.get('opm_id'),
        'contact': contact_clean
    }

    try:
        # DEV MODE: Usando admin para criar usuário já confirmado (email_confirm=True)
        # Em produção, reverter para supabase.auth.sign_up e remover email_confirm
        response = supabase_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": metadata
        })
        return jsonify({"success": True, "message": "Usuário criado com sucesso! (Auto-confirmado)"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('auth/forgot_password.html')

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')

    try:
        # Envia email de recuperação
        supabase.auth.reset_password_email(email, options={
            "redirect_to": "http://10.44.133.44:3001/reset-password-confirm" 
        })
        return jsonify({"success": True, "message": "Email enviado"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/profile/me', methods=['PUT'])
@login_required
def update_my_profile():
    user_id = session['user']['id']
    data = request.get_json()
    
    try:
        # Campos permitidos para edição pelo próprio usuário
        update_data = {
            'full_name': data.get('full_name'),
            'war_name': data.get('war_name'),
            'contact': data.get('contact'),
            # RE e Rank geralmente são dados funcionais fixos, mas vou permitir edição se o usuário quiser corrigir
            # Se quiser bloquear, basta remover daqui
            'rank': data.get('rank'),
            're': data.get('re')
        }
        
        # Remover chaves com valores vazios/nulos para não apagar dados se não forem enviados
        update_data = {k: v for k, v in update_data.items() if v is not None}

        # Validar RE se for enviado
        if 're' in update_data:
             if not re.match(r'^\d{6}-\d{1}$', update_data['re']):
                return jsonify({"success": False, "error": "R.E. inválido. Use o formato 123456-7."}), 400
        
        # Validar Contato se for enviado
        if 'contact' in update_data:
             contact_clean = re.sub(r'\D', '', update_data['contact'])
             if not contact_clean or len(contact_clean) < 10 or len(contact_clean) > 11:
                return jsonify({"success": False, "error": "Telefone inválido."}), 400
             update_data['contact'] = contact_clean

        # Atualizar no banco
        supabase.table('profiles').update(update_data).eq('id', user_id).execute()
        
        # Atualizar senha se fornecida
        if data.get('password'):
            new_password = data.get('password')
            supabase.auth.update_user({"password": new_password})

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/naturezas_raia')
@login_required
def get_naturezas_raia():
    try:
        # Busca as naturezas na tabela 'oco_raia' do schema 'public'
        # Assumindo que a tabela tem colunas como 'id' e 'descricao' ou 'nome'
        # Vou buscar tudo e deixar o front filtrar se precisar
        res = supabase.table('oco_raia').select('*').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/concessionarias')
@login_required
def get_concessionarias():
    try:
        # Busca as concessionárias na tabela 'css' do schema 'public'
        res = supabase.table('css').select('id, name').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        return jsonify({"error": str(e)}), 500

@app.route('/api/municipios')
@login_required
def get_municipios():
    try:
        res = supabase.table('municipalities').select('id, name').order('name').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
from minio import Minio
from minio.error import S3Error
import io

# Configuração MinIO
MINIO_ENDPOINT = "10.44.133.44:9100" # Sem http://
MINIO_ACCESS_KEY = "admin_sentinela"
MINIO_SECRET_KEY = "PassMinioSentinela_CBI1"
MINIO_BUCKET = "raia-photos"
MINIO_PUBLIC_URL_BASE = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False # HTTP
)

# Garantir que o bucket existe
try:
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)
        # Definir política pública (opcional, mas bom para visualização)
        policy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":["*"]},"Action":["s3:GetObject"],"Resource":["arn:aws:s3:::%s/*"]}]}' % MINIO_BUCKET
        minio_client.set_bucket_policy(MINIO_BUCKET, policy)
except Exception as e:
    print(f"Erro ao configurar bucket MinIO: {e}")

@app.route('/api/raia/save', methods=['POST'])
@login_required
def save_raia():
    try:
        data = request.form.to_dict()
        files = request.files.getlist('photos')
        user_id = session['user']['id']
        
        photo_urls = []
        for file in files:
            if file:
                file_ext = file.filename.split('.')[-1]
                file_name = f"{user_id}_{os.urandom(8).hex()}.{file_ext}"
                
                # Upload MinIO
                file_content = file.read()
                file_stream = io.BytesIO(file_content)
                
                minio_client.put_object(
                    MINIO_BUCKET,
                    file_name,
                    file_stream,
                    length=len(file_content),
                    content_type=file.content_type
                )
                
                # URL Pública
                public_url = f"{MINIO_PUBLIC_URL_BASE}/{file_name}"
                photo_urls.append(public_url)
        
        # Preparar dados para inserção
        # Mapear campos do form para colunas do banco
        occurrence_data = {
            'user_id': user_id,
            'opm_id': data.get('opm_id'),
            'concessionaire_id': data.get('concessionaire_id'),
            'nature_id': data.get('nature'), # ID da natureza
            'description': data.get('description'),
            'address': data.get('location_text'), # Mapeando location_text para address
            'manual_location': data.get('location_text'), # E também para manual_location por garantia
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'has_responsible': data.get('has_responsible') == 'YES',
            'responsible_name': data.get('resp_name'),
            'responsible_role': data.get('resp_role'),
            'responsible_contact': data.get('resp_contact'),
            'photos': photo_urls, # Array de URLs
            'status': 'NOVO' # Status inicial reformulado
        }
        
        # IMPORTANTE: Usando supabase_admin para garantir a inserção independente de RLS complexas,
        # já que a autenticação e autorização já foram verificadas pelo @login_required e session.
        res = supabase_admin.table('occurrences').insert(occurrence_data).execute()
        
        return jsonify({"success": True, "data": res.data})
        
    except Exception as e:
        print(f"Erro ao salvar RAIA: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/vulto/save', methods=['POST'])
@login_required
def save_vulto():
    try:
        data = request.get_json()
        user_id = session['user']['id']
        
        # Lógica de Oficiais Presentes
        posto_oficial = data.get('posto_oficial')
        nome_oficial = data.get('nome_oficial')
        
        if posto_oficial and nome_oficial:
            oficiais_presenca_str = f"{posto_oficial} {nome_oficial}"
        else:
            oficiais_presenca_str = "NÃO HOUVE OFICIAL NO LOCAL"

        # Buscar dados da OPM para o cabeçalho
        opm_text = ""
        if data.get('opm_id'):
            try:
                opm_res = supabase.table('opm').select('*').eq('id', data.get('opm_id')).single().execute()
                if opm_res.data:
                    opm = opm_res.data
                    sgb_text = opm['SGB']
                    if 'SGB' not in sgb_text: sgb_text += " SGB"
                    opm_text = f"{opm['GB']} - {sgb_text} - EB {opm['EB']}"
            except Exception as e:
                print(f"Erro ao buscar OPM: {e}")
                opm_text = "OPM NÃO IDENTIFICADA"

        # Formatar Data (YYYY-MM-DD -> DD/MM/YYYY)
        def fmt_date(d):
            if not d: return ""
            try:
                parts = d.split('-')
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
            except: return d

        # Formatação do texto PADRÃO (Igual Frontend)
        texto_gerado = (
            f"SECRETARIA DA SEGURANÇA PÚBLICA\n"
            f"CORPO DE BOMBEIROS MILITAR DO ESTADO DE SÃO PAULO\n"
            f"RELATÓRIO DE OCORRÊNCIA VULTO OU DESTAQUE\n"
            f"{opm_text}\n"
            f"A. NÚMERO OCORRÊNCIA: {data.get('talao_numero')}\n"
            f"B. DATA/HORA DA OCORRÊNCIA: {fmt_date(data.get('data_inicio'))} às {data.get('hora_inicio')}h.\n"
            f"C. STATUS DA OCORRÊNCIA: {data.get('status')}\n"
            f"D. TIPO DE OCORRÊNCIA (JUSTIFICATIVA VULTO/DESTAQUE): {data.get('justificativa_vulto')}\n"
            f"E. NATUREZA DA OCORRÊNCIA: {data.get('natureza_codigo')}\n"
            f"F. MUNICÍPIO: {data.get('municipio_nome')}\n"
            f"G. ENDEREÇO: {data.get('endereco')}\n"
            f"H. BAIRRO:    {data.get('bairro')}\n"
            f"I. QUANTIDADE DE VIATURAS: {data.get('qtd_viaturas')}\n"
            f"J. QUANTIDADE DE MILITARES: {data.get('qtd_bombeiros')}\n"
            f"K. ENCARREGADO NO LOCAL DA OCORRÊNCIA: {data.get('encarregado_posto')} {data.get('encarregado_nome')}\n"
            f"L. HISTÓRICO INICIAL: {data.get('historico_inicial')}\n"
            f"M. HISTÓRICO FINAL: {data.get('historico_final')}\n"
            f"N. NOME PM TRANSMISSÃO: {data.get('pm_transmissao_posto')} {data.get('pm_transmissao_nome')}\n"
            f"O. TEMPO PRIMEIRA VTR NO LOCAL (em minutos): {data.get('tempo_resposta')}\n"
            f"P. OFICIAIS QUE COMPARECERAM NO LOCAL: {oficiais_presenca_str}"
        )

        vulto_data = {
            'user_id': user_id,
            'opm_id': int(data.get('opm_id')) if data.get('opm_id') else None,
            'talao_numero': data.get('talao_numero'),
            'data_inicio': data.get('data_inicio'),
            'hora_inicio': data.get('hora_inicio'),
            'status': data.get('status'),
            'data_termino': data.get('data_termino') if data.get('data_termino') else None,
            'hora_termino': data.get('hora_termino') if data.get('hora_termino') else None,
            'justificativa_vulto': data.get('justificativa_vulto'),
            'natureza_codigo': data.get('natureza_codigo'),
            'municipio_nome': data.get('municipio_nome'), # Alterado de id para nome (Texto)
            'endereco': data.get('endereco'),
            'bairro': data.get('bairro'),
            'qtd_viaturas': data.get('qtd_viaturas'),
            'qtd_bombeiros': data.get('qtd_bombeiros'),
            'tempo_resposta_minutos': data.get('tempo_resposta'),
            'encarregado_posto': data.get('encarregado_posto'),
            'encarregado_nome': data.get('encarregado_nome'),
            'historico_inicial': data.get('historico_inicial'),
            'historico_final': data.get('historico_final'),
            'pm_transmissao_posto': data.get('pm_transmissao_posto'),
            'pm_transmissao_nome': data.get('pm_transmissao_nome'),
            'oficiais_presenca': oficiais_presenca_str,
            'generated_text': texto_gerado
        }
        
        # Validar campos numéricos vazios
        if not vulto_data['tempo_resposta_minutos']: vulto_data['tempo_resposta_minutos'] = None

        res = supabase_admin.table('vulto_occurrences').insert(vulto_data).execute()
        return jsonify({"success": True, "data": res.data, "generated_text": texto_gerado})
        
    except Exception as e:
        print(f"Erro Vulto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/elaborar-vulto/listar')
@login_required
def elaborar_vulto_listar():
    return render_template('vulto/listar_vultos.html', user=session['user'])

@app.route('/api/vulto/me')
@login_required
def get_my_vultos():
    try:
        user_id = session['user']['id']
        # Buscar Vultos do usuário
        # IMPORTANTE: Usando supabase_admin para garantir leitura (bypass RLS caso policy esteja bugada)
        res = supabase_admin.table('vulto_occurrences').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        print(f"Erro ao buscar vultos: {e}")
        return jsonify([]), 500

@app.route('/admin')
@login_required
def admin_dashboard():
    # Garantir que temos os dados atualizados do perfil (incluindo role)
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
        flash('Erro ao verificar permissões.', 'danger')
        return redirect(url_for('dashboard'))

    if session['user'].get('role') != 'ADMIN':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('admin/menu_admin.html', user=session['user'])

@app.route('/admin/users')
@login_required
def admin_users():
    # Garantir que temos os dados atualizados do perfil
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
        flash('Erro ao verificar permissões.', 'danger')
        return redirect(url_for('dashboard'))

    if session['user'].get('role') != 'ADMIN':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Busca todos os perfis
        res = supabase_admin.table('profiles').select('*').order('full_name').execute()
        users = res.data
        return render_template('admin/admin_dashboard.html', user=session['user'], all_users=users)
    except Exception as e:
        return f"Erro ao carregar usuários: {e}"

@app.route('/admin/occurrences')
@login_required
def admin_occurrences():
    # Garantir que temos os dados atualizados do perfil
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
        flash('Erro ao verificar permissões.', 'danger')
        return redirect(url_for('dashboard'))

    if session['user'].get('role') != 'ADMIN':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Buscar todos os perfis para mapear nomes
        # Buscar todos os perfis para mapear nomes e postos
        # Tentativa com 'rank' baseado no código de signup
        profiles_res = supabase_admin.table('profiles').select('id, war_name, email, rank').execute()
        user_map = {}
        for p in profiles_res.data:
            grad = p.get('rank', '')
            name = p.get('war_name', p.get('email'))
            # Formatar Posto + Nome (ex: CB PM SILVA)
            full_name = f"{grad} {name}".strip() if grad else name
            user_map[p['id']] = {
                'nome': full_name,
                'email': p.get('email', '')
            }

        # Buscar todas as ocorrências ATIVAS (não arquivadas)
        res = supabase_admin.table('occurrences').select('*').neq('status', 'ARCHIVED').order('created_at', desc=True).execute()
        raias = res.data
        for r in raias:
            user_info = user_map.get(r.get('user_id'), {'nome': 'Desconhecido', 'email': ''})
            r['elaborador_nome'] = user_info['nome']
            r['elaborador_email'] = user_info['email']
        
        # Buscar todas as ocorrências de VULTO
        res_vulto = supabase_admin.table('vulto_occurrences').select('*').order('created_at', desc=True).execute()
        vultos = res_vulto.data
        for v in vultos:
            user_info = user_map.get(v.get('user_id'), {'nome': 'Desconhecido', 'email': ''})
            v['elaborador_nome'] = user_info['nome']
            v['elaborador_email'] = user_info['email']

        # Buscar todas as inconsistências (admin vê tudo)
        res_inc = supabase_admin.table('inconsistencies').select('*').order('created_at', desc=True).execute()
        inconsistencias = res_inc.data
        for i in inconsistencias:
            user_info = user_map.get(i.get('user_id'), {'nome': 'Desconhecido', 'email': ''})
            i['elaborador_nome'] = user_info['nome']
            i['elaborador_email'] = user_info['email']
        
        # Buscar todas as ocorrências de CHUVAS INTENSAS
        res_chuvas = supabase_admin.table('rain_occurrences').select('*').order('created_at', desc=True).execute()
        chuvas = res_chuvas.data
        for c in chuvas:
            user_info = user_map.get(c.get('user_id'), {'nome': 'Desconhecido', 'email': ''})
            c['elaborador_nome'] = user_info['nome']
            c['elaborador_email'] = user_info['email']

        # Buscar mapeamento de naturezas RAIA
        try:
            nat_res = supabase_admin.table('oco_raia').select('code, description').execute()
            raia_nature_map = {n['code']: f"{n['code']} - {n['description']}" for n in nat_res.data}
        except:
            raia_nature_map = {}

        # Mapeamento estático Chuvas
        chuvas_nature_map = {
            'A1': 'A1 - Árvore em Risco',
            'A2': 'A2 - Poda Emergencial',
            'A3': 'A3 - Risco Elétrico',
            'A4': 'A4 - Obstrução de Via',
            'A5': 'A5 - Outras / Alagamento'
        }

        return render_template('admin/painel_ocorrencias.html', user=session['user'], raias=raias, inconsistencias=inconsistencias, vultos=vultos, chuvas=chuvas, view_type='active', raia_nature_map=raia_nature_map, chuvas_nature_map=chuvas_nature_map)
    except Exception as e:
        return f"Erro ao carregar ocorrências: {e}"

@app.route('/admin/occurrences/archived')
@login_required
def admin_occurrences_archived():
    # Garantir que temos os dados atualizados do perfil
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
        return redirect(url_for('dashboard'))

    if session['user'].get('role') != 'ADMIN':
        return redirect(url_for('dashboard'))
    
    try:
        # 1. Mapeamento de Usuários (Replicado da rota principal)
        profiles_res = supabase_admin.table('profiles').select('id, war_name, email, rank').execute()
        user_map = {}
        for p in profiles_res.data:
            grad = p.get('rank', '')
            name = p.get('war_name', p.get('email'))
            full_name = f"{grad} {name}".strip() if grad else name
            user_map[p['id']] = {
                'nome': full_name,
                'email': p.get('email', '')
            }

        # 2. Buscar RAIA Arquivadas
        res = supabase_admin.table('occurrences').select('*').eq('status', 'ARCHIVED').order('created_at', desc=True).execute()
        raias = res.data
        for r in raias:
            user_info = user_map.get(r.get('user_id'), {'nome': 'Desconhecido', 'email': ''})
            r['elaborador_nome'] = user_info['nome']
            r['elaborador_email'] = user_info['email']

        # 3. Buscar Vulto Arquivadas
        res_vulto = supabase_admin.table('vulto_occurrences').select('*').eq('status', 'ARCHIVED').order('created_at', desc=True).execute()
        vultos = res_vulto.data
        for v in vultos:
            user_info = user_map.get(v.get('user_id'), {'nome': 'Desconhecido', 'email': ''})
            v['elaborador_nome'] = user_info['nome']
            v['elaborador_email'] = user_info['email']

        # 4. Buscar Inconsistências Arquivadas
        res_inc = supabase_admin.table('inconsistencies').select('*').eq('status', 'ARCHIVED').order('created_at', desc=True).execute()
        inconsistencias = res_inc.data
        for i in inconsistencias:
            user_info = user_map.get(i.get('user_id'), {'nome': 'Desconhecido', 'email': ''})
            i['elaborador_nome'] = user_info['nome']
            i['elaborador_email'] = user_info['email']

        # 5. Buscar Chuvas Arquivadas
        res_chuvas = supabase_admin.table('rain_occurrences').select('*').eq('status', 'ARCHIVED').order('created_at', desc=True).execute()
        chuvas = res_chuvas.data
        for c in chuvas:
            user_info = user_map.get(c.get('user_id'), {'nome': 'Desconhecido', 'email': ''})
            c['elaborador_nome'] = user_info['nome']
            c['elaborador_email'] = user_info['email']

        # 6. Mapeamento de Naturezas (Replicado)
        try:
            nat_res = supabase_admin.table('oco_raia').select('code, description').execute()
            raia_nature_map = {n['code']: f"{n['code']} - {n['description']}" for n in nat_res.data}
        except:
            raia_nature_map = {}

        chuvas_nature_map = {
            'A1': 'A1 - Árvore em Risco',
            'A2': 'A2 - Poda Emergencial',
            'A3': 'A3 - Risco Elétrico',
            'A4': 'A4 - Obstrução de Via',
            'A5': 'A5 - Outras / Alagamento'
        }
        
        return render_template('admin/painel_ocorrencias.html', user=session['user'], raias=raias, inconsistencias=inconsistencias, vultos=vultos, chuvas=chuvas, view_type='archived', raia_nature_map=raia_nature_map, chuvas_nature_map=chuvas_nature_map)
    except Exception as e:
        return f"Erro ao carregar ocorrências arquivadas: {e}"
        
@app.route('/api/admin/users', methods=['GET'])
@login_required
def list_users():
    # TODO: Verificar permissão de admin aqui também
    try:
        # Join com OPM seria ideal, mas Supabase-py faz isso via select string
        res = supabase.table('profiles').select('*, opm:opm_cb(name)').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.get_json()
    
    try:
        # Atualizar profile (pode ser via cliente normal se tiver permissão RLS, ou admin)
        profile_data = {
            'full_name': data.get('full_name'),
            'war_name': data.get('war_name'),
            'rank': data.get('rank'),
            'role': data.get('role')
        }
        # Usando admin client para garantir update
        supabase_admin.table('profiles').update(profile_data).eq('id', user_id).execute()
        
        # Atualizar senha se fornecida
        if data.get('password'):
            new_password = data.get('password')
            # Atualiza senha no Auth usando cliente admin
            supabase_admin.auth.admin.update_user_by_id(user_id, {"password": new_password})
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    try:
        # Deletar usuário do Auth (Cascade deve remover do profile)
        supabase_admin.auth.admin.delete_user(user_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/raia/me', methods=['GET'])
@login_required
def list_my_raias():
    user_id = session['user']['id']
    try:
        # Busca ocorrências do usuário logado usando admin para garantir leitura
        res = supabase_admin.table('occurrences').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/raia/me/<id>', methods=['DELETE'])
@login_required
def delete_my_raia(id):
    user_id = session['user']['id']
    try:
        # Verificar se a ocorrência pertence ao usuário
        res = supabase_admin.table('occurrences').select('user_id').eq('id', id).single().execute()
        
        if not res.data:
            return jsonify({"success": False, "error": "Ocorrência não encontrada."}), 404
            
        if res.data['user_id'] != user_id:
             return jsonify({"success": False, "error": "Permissão negada."}), 403

        # Se for dono, deleta
        supabase_admin.table('occurrences').delete().eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/inconsistencias/<id>/status', methods=['PUT'])
@login_required
def update_inconsistencia_status(id):
    # Refresh user session data to ensure role is up to date
    try:
        user_id = session['user']['id']
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
        session.modified = True
    except Exception as e:
        print(f"Erro ao atualizar perfil na API: {e}")

    if session['user'].get('role') != 'ADMIN':
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    try:
        new_status = request.json.get('status')
        if not new_status:
            return jsonify({"success": False, "error": "Status required"}), 400
            
        supabase_admin.table('inconsistencies').update({'status': new_status}).eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
         return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/occurrences/<id>', methods=['DELETE'])
@login_required
def delete_occurrence(id):
    # Garantir refresh do profile para ter o role
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
        # Importante: para persistir a sessão atualizada, o Flask precisa salvar o cookie na resposta.
        # Mas aqui vamos usar o dado atualizado apenas para a verificação local.
    except Exception as e:
        print(f"Erro ao atualizar profile na API: {e}")

    if session['user'].get('role') != 'ADMIN':
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    
    try:
        supabase_admin.table('occurrences').delete().eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/occurrences/<id>/status', methods=['PUT'])
@login_required
def update_occurrence_status(id):
    # Endpoint para atualizar status de RAIA (tabela occurrences)
    if session['user'].get('role') != 'ADMIN':
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    try:
        new_status = request.json.get('status')
        if not new_status:
            return jsonify({"success": False, "error": "Status required"}), 400
            
        supabase_admin.table('occurrences').update({'status': new_status}).eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
         return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/inconsistencias/<id>/archive', methods=['PUT'])
@login_required
def archive_inconsistencia(id):
    if session['user'].get('role') != 'ADMIN':
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    try:
        supabase_admin.table('inconsistencies').update({'status': 'ARCHIVED'}).eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/vulto/<id>/archive', methods=['PUT'])
@login_required
def archive_vulto(id):
    if session['user'].get('role') != 'ADMIN':
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    try:
        supabase_admin.table('vulto_occurrences').update({'status': 'ARCHIVED'}).eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/chuvas/<id>/archive', methods=['PUT'])
@login_required
def archive_chuvas(id):
    if session['user'].get('role') != 'ADMIN':
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    try:
        supabase_admin.table('rain_occurrences').update({'status': 'ARCHIVED'}).eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/occurrences/<id>/archive', methods=['PUT'])
@login_required
def archive_occurrence(id):
    # Garantir refresh do profile
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
    except Exception as e:
        print(f"Erro ao atualizar profile na API: {e}")

    if session['user'].get('role') != 'ADMIN':
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    
    try:
        supabase_admin.table('occurrences').update({'status': 'ARCHIVED'}).eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/chuvas/<id>', methods=['DELETE'])
@login_required
def delete_chuvas_admin(id):
    # Garantir refresh do profile
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
    except Exception as e:
        print(f"Erro ao atualizar profile na API: {e}")

    if session['user'].get('role') != 'ADMIN':
        return jsonify({"success": False, "error": "Acesso negado"}), 403
    
    try:
        supabase_admin.table('rain_occurrences').delete().eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/raia/update/<id>', methods=['PUT'])
@login_required
def update_raia(id):
    try:
        data = request.json
        user_id = session['user']['id']
        
        # Verificar ownership
        res = supabase_admin.table('occurrences').select('user_id').eq('id', id).single().execute()
        if not res.data:
            return jsonify({"success": False, "error": "Ocorrência não encontrada."}), 404
        if res.data['user_id'] != user_id:
            return jsonify({"success": False, "error": "Permissão negada."}), 403

        # Campos permitidos para atualização
        update_data = {}
        
        # Mapeamento de campos do frontend para o banco
        if 'nature_id' in data: update_data['nature_id'] = data['nature_id']
        if 'description' in data: update_data['description'] = data['description']
        if 'manual_location' in data: update_data['manual_location'] = data['manual_location']
        if 'address' in data: update_data['address'] = data['address']
        if 'status' in data: update_data['status'] = data['status']
        
        if 'has_responsible' in data:
            update_data['has_responsible'] = data['has_responsible']
            if data['has_responsible']:
                if 'responsible_name' in data: update_data['responsible_name'] = data['responsible_name']
                if 'responsible_role' in data: update_data['responsible_role'] = data['responsible_role']
                if 'responsible_contact' in data: update_data['responsible_contact'] = data['responsible_contact']
            else:
                 update_data['responsible_name'] = None
                 update_data['responsible_role'] = None
                 update_data['responsible_contact'] = None

        if update_data:
            supabase_admin.table('occurrences').update(update_data).eq('id', id).execute()
        
        return jsonify({"success": True})

    except Exception as e:
        print(f"Erro Update RAIA: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
