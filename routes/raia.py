from flask import Blueprint, render_template, request, jsonify, session
from services import supabase, supabase_admin, login_required, minio_client, MINIO_BUCKET, MINIO_PUBLIC_URL_BASE
import os
import io
import time

raia_bp = Blueprint('raia', __name__)

@raia_bp.context_processor
def inject_version():
    return dict(v=int(time.time()))



@raia_bp.route('/elaborar-raia')
@login_required
def elaborar_raia():
    return render_template('raia/menu_raia.html', user=session['user'])

@raia_bp.route('/elaborar-raia/novo')
@login_required
def elaborar_raia_novo():
    return render_template('raia/elaborar_raia.html', user=session['user'])

@raia_bp.route('/elaborar-raia/listar')
@login_required
def elaborar_raia_listar():
    return render_template('raia/listar_raias.html', user=session['user'])

@raia_bp.route('/api/raia/save', methods=['POST'])
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
                
                file_content = file.read()
                file_stream = io.BytesIO(file_content)
                
                minio_client.put_object(
                    MINIO_BUCKET,
                    file_name,
                    file_stream,
                    length=len(file_content),
                    content_type=file.content_type
                )
                
                public_url = f"{MINIO_PUBLIC_URL_BASE}/{file_name}"
                photo_urls.append(public_url)
        
        occurrence_data = {
            'user_id': user_id,
            'opm_id': data.get('opm_id'),
            'concessionaire_id': data.get('concessionaire_id'),
            'nature_id': data.get('nature'),
            'description': data.get('description'),
            'address': data.get('location_text'), 
            'manual_location': data.get('location_text'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'has_responsible': data.get('has_responsible') == 'YES',
            'responsible_name': data.get('resp_name'),
            'responsible_role': data.get('resp_role'),
            'responsible_contact': data.get('resp_contact'),
            'photos': photo_urls,
            'status': 'NOVO'
        }
        
        res = supabase_admin.table('occurrences').insert(occurrence_data).execute()
        
        return jsonify({"success": True, "data": res.data})
        
    except Exception as e:
        print(f"Erro ao salvar RAIA: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@raia_bp.route('/api/naturezas_raia')
@login_required
def get_naturezas_raia():
    try:
        res = supabase_admin.table('oco_raia').select('*').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@raia_bp.route('/api/concessionarias')
@login_required
def get_concessionarias():
    try:
        res = supabase_admin.table('css').select('id, name').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@raia_bp.route('/api/raia/me')
@login_required
def get_my_raias():
    try:
        user_id = session['user']['id']
        # Fetch occurrences for this user, ordered by creation date
        res = supabase_admin.table('occurrences').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        print(f"Erro ao buscar RAIAs: {e}")
        return jsonify({"error": str(e)}), 500

@raia_bp.route('/api/raia/me/<id>', methods=['DELETE'])
@login_required
def delete_my_raia(id):
    try:
        user_id = session['user']['id']
        # Verify ownership before deleting
        # Just creating a delete query with user_id matching is safer/easiest
        res = supabase_admin.table('occurrences').delete().eq('id', id).eq('user_id', user_id).execute()
        
        if len(res.data) > 0:
            return jsonify({"success": True, "message": "Ocorrência excluída"})
        else:
            return jsonify({"success": False, "error": "Ocorrência não encontrada ou sem permissão"}), 404
            
    except Exception as e:
        print(f"Erro ao excluir RAIA: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
