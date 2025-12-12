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
    if session['user'].get('role') != 'ADMIN':
        return redirect(url_for('main.dashboard'))
    
    try:
        # Fetch Data
        inconsistencias = supabase.table('inconsistencies').select('*').neq('status', 'ENCERRADO').execute().data
        raias = supabase.table('occurrences').select('*').neq('status', 'ARCHIVED').order('created_at', desc=True).execute().data
        vultos = supabase.table('vultos').select('*').order('data_inicio', desc=True).execute().data # Assuming vultos don't have archive status yet or treating all as active for now?
        chuvas = supabase.table('chuvas').select('*').order('data_hora', desc=True).execute().data
        
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
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/occurrences/archived')
@login_required
def admin_occurrences_archived():
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
