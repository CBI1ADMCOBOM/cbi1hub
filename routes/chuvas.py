from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services import supabase_admin, login_required

chuvas_bp = Blueprint('chuvas', __name__)

@chuvas_bp.route('/chuvas-intensas')
@login_required
def chuvas_intensas():
    return render_template('chuvas/menu_chuvas.html', user=session['user'])

@chuvas_bp.route('/chuvas-intensas/novo')
@login_required
def chuvas_intensas_novo():
    return render_template('chuvas/elaborar_chuvas.html', user=session['user'])

@chuvas_bp.route('/chuvas-intensas/selecao')
@login_required
def chuvas_intensas_selecao():
    return render_template('chuvas/selecionar_gb.html', user=session['user'])

@chuvas_bp.route('/chuvas-intensas/listar')
@login_required
def chuvas_intensas_listar():
    try:
        user_id = session['user']['id']
        gb_filter = request.args.get('gb')
        
        items = []
        is_gb_view = False
        
        if gb_filter:
            is_gb_view = True
            gb_num = ''.join(filter(str.isdigit, gb_filter))
            
            opm_res = supabase_admin.table('opm').select('id').ilike('GB', f'%{gb_num}%').execute()
            if opm_res.data:
                station_ids = [opm['id'] for opm in opm_res.data]
                if station_ids:
                    rain_res = supabase_admin.table('rain_occurrences').select('*').in_('bombeiros_station_id', station_ids).order('created_at', desc=True).execute()
                    items = rain_res.data
        else:
            res = supabase_admin.table('rain_occurrences').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            items = res.data

        return render_template('chuvas/listar_chuvas.html', user=session['user'], items=items, is_gb_view=is_gb_view)
    except Exception as e:
        print(f"Erro listar chuvas: {e}")
        return redirect(url_for('chuvas.chuvas_intensas'))

@chuvas_bp.route('/api/chuvas/save', methods=['POST'])
@login_required
def save_chuvas():
    try:
        data = request.json
        user_id = session['user']['id']
        
        rain_data = {
            'user_id': user_id,
            'talao_numero': data.get('talao_numero'),
            'data_hora': data.get('data_hora'),
            'endereco': data.get('endereco'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'municipio_id': None, 
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
            'observacao': f"Município: {data.get('municipio_id')} | {data.get('observacao', '')}"
        }
        
        res = supabase_admin.table('rain_occurrences').insert(rain_data).execute()
        return jsonify({"success": True, "id": res.data[0]['id']})
    except Exception as e:
        print(f"Erro Salvar Chuvas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@chuvas_bp.route('/api/chuvas/update/<id>', methods=['PUT'])
@login_required
def update_chuvas(id):
    try:
        data = request.json
        user_id = session['user']['id']
        
        check = supabase_admin.table('rain_occurrences').select('user_id').eq('id', id).single().execute()
        if not check.data:
             return jsonify({"success": False, "error": "Registro não encontrado."}), 404
        if check.data['user_id'] != user_id:
             return jsonify({"success": False, "error": "Sem permissão para editar este registro."}), 403

        rain_data = {
            'talao_numero': data.get('talao_numero'),
            'data_hora': data.get('data_hora'),
            'endereco': data.get('endereco'),
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
            'observacao': data.get('observacao')
        }
        
        supabase_admin.table('rain_occurrences').update(rain_data).eq('id', id).execute()
        return jsonify({"success": True})

    except Exception as e:
        print(f"Erro Update Chuvas: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@chuvas_bp.route('/api/chuvas/delete/<id>', methods=['DELETE'])
@login_required
def delete_chuvas(id):
    try:
        user_id = session['user']['id']
        
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
