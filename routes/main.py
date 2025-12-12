from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services import supabase, supabase_admin, login_required
import re

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    user_id = session['user']['id']
    try:
        res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        session['user'].update(res.data)
    except:
        pass
    return render_template('dashboard.html', user=session['user'])

@main_bp.route('/mergulho')
@login_required
def mergulho():
    return render_template('mergulho/index.html', user=session['user'])

@main_bp.route('/ronda-supervisor')
@login_required
def ronda_supervisor():
    return render_template('ronda/index.html', user=session['user'])

@main_bp.route('/apoio-fogo')
@login_required
def apoio_fogo():
    return render_template('fogo/index.html', user=session['user'])

@main_bp.route('/api/opms')
def get_opms():
    try:
        response = supabase_admin.table('opm').select('*').order('EB').execute()
        return jsonify(response.data)
    except Exception as e:
        print(f"Erro ao buscar OPMs: {e}")
        return jsonify([]), 500

@main_bp.route('/api/municipios')
@login_required
def get_municipios():
    try:
        res = supabase.table('municipalities').select('id, name').order('name').execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/api/profile/me', methods=['PUT'])
@login_required
def update_my_profile():
    user_id = session['user']['id']
    data = request.get_json()
    
    try:
        update_data = {
            'full_name': data.get('full_name'),
            'war_name': data.get('war_name'),
            'contact': data.get('contact'),
            'rank': data.get('rank'),
            'corporation_id': data.get('re')
        }
        
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if 'corporation_id' in update_data:
             if not re.match(r'^\d{6}-\d{1}$', update_data['corporation_id']):
                return jsonify({"success": False, "error": "R.E. inválido. Use o formato 123456-7."}), 400
        
        if 'contact' in update_data:
             contact_clean = re.sub(r'\D', '', update_data['contact'])
             if not contact_clean or len(contact_clean) < 10 or len(contact_clean) > 11:
                return jsonify({"success": False, "error": "Telefone inválido."}), 400
             update_data['contact'] = contact_clean

        supabase.table('profiles').update(update_data).eq('id', user_id).execute()
        
        if data.get('password'):
            new_password = data.get('password')
            supabase.auth.update_user({"password": new_password})

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
