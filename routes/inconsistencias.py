from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services import supabase, supabase_admin, login_required

inc_bp = Blueprint('inconsistencias', __name__)

@inc_bp.route('/gerar-inconsistencia')
@login_required
def gerar_inconsistencia():
    return render_template('inconsistencia/menu_inc.html', user=session['user'])

@inc_bp.route('/gerar-inconsistencia/novo')
@login_required
def gerar_inconsistencia_novo():
    return render_template('inconsistencia/gerar_inconsistencia.html', user=session['user'])

@inc_bp.route('/api/inconsistencias/save', methods=['POST'])
@login_required
def save_inconsistencia():
    try:
        data = request.json
        user_id = session['user']['id']
        
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
             
             if data.get('motivo_tec') == 'T4_193':
                 inc_data['t4_origem'] = data.get('t4_origem')
                 inc_data['t4_operadora'] = data.get('t4_operadora')
                 inc_data['t4_numero'] = data.get('t4_numero')
                 inc_data['t4_datahora'] = data.get('t4_datahora') if data.get('t4_datahora') else None
                 inc_data['t4_falha'] = data.get('t4_falha')
                 
             if data.get('motivo_tec') == 'T4_APP':
                 inc_data['t4_sistema_afetado'] = data.get('t4_sistema')

        supabase_admin.table('inconsistencies').insert(inc_data).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Erro Inconsistencia: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@inc_bp.route('/gerar-inconsistencia/listar')
@login_required
def gerar_inconsistencia_listar():
    try:
        user_id = session['user']['id']
        res = supabase_admin.table('inconsistencies').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        inconsistencies = res.data
        return render_template('inconsistencia/listar_inconsistencias.html', user=session['user'], items=inconsistencies)
    except Exception as e:
        print(f"Erro ao listar inconsistencias: {e}")
        return redirect(url_for('main.dashboard'))

@inc_bp.route('/api/inconsistencias/<id>', methods=['DELETE'])
@login_required
def delete_inconsistencia(id):
    try:
        user_id = session['user']['id']
        res = supabase_admin.table('inconsistencies').select('user_id').eq('id', id).single().execute()
        
        if not res.data:
            return jsonify({"success": False, "error": "Registro não encontrado."}), 404
            
        if res.data['user_id'] != user_id:
             return jsonify({"success": False, "error": "Permissão negada."}), 403

        supabase_admin.table('inconsistencies').delete().eq('id', id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
