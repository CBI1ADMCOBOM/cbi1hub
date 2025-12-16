from flask import Blueprint, render_template, session, redirect, url_for, flash
from services import supabase, supabase_admin, login_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
        # flash('Erro ao verificar permissões.', 'danger') 
        # Warning: flash requires secret_key which is in app.py. 
        # Since blueprints don't have access to app config directly easily without current_app, 
        # we rely on Flask's session implicit handling.
        return redirect(url_for('main.dashboard'))

    if session['user'].get('role') != 'ADMIN':
        # flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
    return render_template('admin/menu_admin.html', user=session['user'])

@admin_bp.route('/admin/users')
@login_required
def admin_users():
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
    except Exception as e:
        print(f"Erro ao buscar perfil: {e}")
        return redirect(url_for('main.dashboard'))

    if session['user'].get('role') != 'ADMIN':
        return redirect(url_for('main.dashboard'))
    
    try:
        res = supabase_admin.table('profiles').select('*').order('full_name').execute()
        users = res.data
        return render_template('admin/admin_dashboard.html', user=session['user'], all_users=users)
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        return redirect(url_for('main.dashboard'))

# Maps (can be moved to a shared constant file)
RAIA_NATURE_MAP = {
    'ACIDENTE_TRANSITO': 'Acidente de Trânsito',
    'INCENDIO': 'Incêndio',
    'OUTROS': 'Outros',
    'SALVAMENTO': 'Salvamento',
    'RESGATE': 'Resgate'
}

CHUVAS_NATURE_MAP = {
    'ALAGAMENTO': 'Alagamento',
    'DESLIZAMENTO': 'Deslizamento',
    'QUEDA_ARVORE': 'Queda de Árvore',
    'DESTELHAMENTO': 'Destelhamento'
}

@admin_bp.route('/admin/occurrences')
@login_required
def admin_occurrences():
    # 1. EMERGENCY FIX: Force Admin for specific user
    user_id = session['user']['id']
    if user_id == 'c89407c5-e1a8-4df9-b276-9a92b140191e':
        # Ensure database has ADMIN role
        try:
            supabase_admin.table('profiles').update({'role': 'ADMIN'}).eq('id', user_id).execute()
            session['user']['role'] = 'ADMIN' # Update session immediately
        except Exception as e:
            print(f"Auto-promote failed: {e}")

    # 2. Access Check
    if session['user'].get('role') != 'ADMIN':
        return redirect(url_for('main.dashboard'))
    
    try:
        # Define Maps
        CHUVAS_NATURE_MAP = {
            'A1': 'A1 - Árvore em Risco',
            'A2': 'A2 - Poda Emergencial',
            'A3': 'A3 - Risco Elétrico',
            'A4': 'A4 - Obstrução de Via',
            'A5': 'A5 - Outras / Alagamento'
        }
        
        try:
            raia_natures = supabase_admin.table('oco_raia').select('*').execute().data
            RAIA_NATURE_MAP = {n['id']: n['natureza'] for n in raia_natures} if raia_natures else {}
        except:
            RAIA_NATURE_MAP = {}

        # Fetch Data - With Safety Checks
        try:
            inconsistencias = supabase_admin.table('inconsistencies').select('*').neq('status', 'ENCERRADO').execute().data
        except:
            inconsistencias = [] # Table might be missing, ignore it for now

        raias = supabase_admin.table('occurrences').select('*').neq('status', 'ARCHIVED').order('created_at', desc=True).execute().data
        vultos = supabase_admin.table('vulto_occurrences').select('*').order('data_inicio', desc=True).execute().data
        chuvas = supabase_admin.table('rain_occurrences').select('*').order('data_hora', desc=True).execute().data
        
        return render_template('admin/painel_ocorrencias.html', 
                             user=session['user'],
                             view_type='active',
                             inconsistencias=inconsistencias,
                             raias=raias,
                             vultos=vultos,
                             chuvas=chuvas,
                             raia_nature_map=RAIA_NATURE_MAP,
                             chuvas_nature_map=CHUVAS_NATURE_MAP)
    except Exception as e:
        print(f"Erro ao carregar ocorrências: {e}")
        # Debugging: Show error instead of redirecting
        return f"<h1>Erro ao carregar Painel:</h1><pre>{str(e)}</pre>", 500
        # return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/fix-db')
@login_required
def fix_db():
    if session['user'].get('role') != 'ADMIN':
        return "Access Denied", 403
    
    sql = """
    CREATE TABLE IF NOT EXISTS public.inconsistencies (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id),
        data_ocorrencia DATE NOT NULL,
        talao_numero TEXT,
        tipo TEXT NOT NULL,
        motivo_op_codigo TEXT,
        motivo_op_descricao TEXT,
        motivo_tec_codigo TEXT,
        motivo_tec_descricao TEXT,
        t4_origem TEXT,
        t4_operadora TEXT,
        t4_numero TEXT,
        t4_datahora TIMESTAMP,
        t4_falha TEXT,
        t4_sistema_afetado TEXT,
        observacao TEXT,
        status TEXT DEFAULT 'NOVO',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    try:
        # Try RPC if available or raw query if client supports it (it usually doesn't without setup)
        # BUT, since we are in the Flask app now, we have the 'supabase_admin' client from 'services' which IS working.
        # The issue is HOW to run raw SQL. 
        # Most Supabase projects don't enable raw SQL from client.
        # IF this fails, the user essentially has a broken DB state that needs external fixing.
        # Let's try the 'exec_sql' RPC again, hoping it exists.
        supabase_admin.rpc('exec_sql', {'query': sql}).execute()
        return "<h1>Sucesso!</h1><p>Tabela criada. Tente acessar o painel agora.</p>"
    except Exception as e:
        return f"<h1>Falha</h1><p>{str(e)}</p><p>Nota: Se o erro for 'function exec_sql does not exist', você precisa criar essa função no banco via SQL Editor do Supabase.</p>"
    if session['user'].get('role') != 'ADMIN':
        return redirect(url_for('main.dashboard'))
        
    try:
        # Fetch Archived Data 
        # For simplicity, assuming inconsistent/chuvas don't have separate archive view or handling it simply
        # Template only shows 'archived' alert.
        
        raias = supabase.table('occurrences').select('*').eq('status', 'ARCHIVED').order('created_at', desc=True).execute().data
        
        # Pass empty lists for others if archive logic isn't defined
        return render_template('admin/painel_ocorrencias.html', 
                             user=session['user'],
                             view_type='archived',
                             inconsistencias=[], 
                             raias=raias,
                             vultos=[], 
                             chuvas=[],
                             raia_nature_map=RAIA_NATURE_MAP,
                             chuvas_nature_map=CHUVAS_NATURE_MAP)
    except Exception as e:
        print(f"Erro ao carregar arquivos: {e}")
        return redirect(url_for('admin.admin_dashboard'))

# API Endpoints for Admin Actions

from flask import request, jsonify

@admin_bp.route('/api/admin/inconsistencias/<id>/status', methods=['PUT'])
@login_required
def update_inc_status(id):
    if session['user'].get('role') != 'ADMIN': return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    try:
        data = request.get_json()
        supabase_admin.table('inconsistencies').update({'status': data.get('status')}).eq('id', id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/api/admin/occurrences/<id>/status', methods=['PUT'])
@login_required
def update_raia_status(id):
    if session['user'].get('role') != 'ADMIN': return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    try:
        data = request.get_json()
        supabase_admin.table('occurrences').update({'status': data.get('status')}).eq('id', id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/api/admin/occurrences/<id>/archive', methods=['PUT'])
@login_required
def archive_raia(id):
    if session['user'].get('role') != 'ADMIN': return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    try:
        supabase_admin.table('occurrences').update({'status': 'ARCHIVED'}).eq('id', id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/api/admin/occurrences/<id>', methods=['DELETE'])
@login_required
def delete_raia(id):
    if session['user'].get('role') != 'ADMIN': return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    try:
        supabase_admin.table('occurrences').delete().eq('id', id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/api/admin/chuvas/<id>', methods=['DELETE'])
@login_required
def delete_chuvas_admin(id):
    if session['user'].get('role') != 'ADMIN': return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    try:
        supabase_admin.table('rain_occurrences').delete().eq('id', id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/api/admin/inconsistencias/<id>', methods=['DELETE'])
@login_required
def delete_inconsistencias_admin(id):
    if session['user'].get('role') != 'ADMIN': return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    try:
        supabase_admin.table('inconsistencies').delete().eq('id', id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/api/admin/inconsistencias/<id>/archive', methods=['PUT'])
@login_required
def archive_inconsistencia_admin(id):
    if session['user'].get('role') != 'ADMIN': return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    try:
        supabase_admin.table('inconsistencies').update({'status': 'ARCHIVED'}).eq('id', id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
