from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from services import supabase, supabase_admin
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_page():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('username')
    password = data.get('password')

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        session['user'] = {
            'id': response.user.id,
            'email': response.user.email,
            'access_token': response.session.access_token,
            'refresh_token': response.session.refresh_token
        }
        
        return jsonify({"success": True, "redirect": url_for('main.dashboard')})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/signup')
def signup_page():
    return render_template('auth/signup.html')

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    contact = data.get('contact', '')

    if not email or not email.endswith('@policiamilitar.sp.gov.br'):
        return jsonify({"success": False, "error": "Apenas e-mails funcionais (@policiamilitar.sp.gov.br) são permitidos."})

    contact_clean = re.sub(r'\D', '', contact)
    if not contact_clean or len(contact_clean) < 10 or len(contact_clean) > 11:
        return jsonify({"success": False, "error": "Telefone inválido. Informe DDD + Número (10 ou 11 dígitos)."}), 400
    
    re_value = data.get('re')
    if not re_value or not re.match(r'^\d{6}-\d{1}$', re_value):
        return jsonify({"success": False, "error": "R.E. inválido. Use o formato 123456-7."}), 400
    
    metadata = {
        'full_name': data.get('full_name'),
        'war_name': data.get('war_name'),
        're': re_value,
        'rank': data.get('rank'),
        'opm_id': data.get('opm_id'),
        'contact': contact_clean
    }

    try:
        response = supabase_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": metadata
        })
        return jsonify({"success": True, "message": "Usuário criado com sucesso! (Auto-confirmado)"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@auth_bp.route('/forgot-password')
def forgot_password_page():
    return render_template('auth/forgot_password.html')

@auth_bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')

    try:
        supabase.auth.reset_password_email(email, options={
            "redirect_to": "http://10.44.133.44:3001/reset-password-confirm" 
        })
        return jsonify({"success": True, "message": "Email enviado"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@auth_bp.route('/reset-password-confirm')
def reset_password_confirm_page():
    # Note: 'key' was used here in original code but it refers to public key.
    # Ideally should process token from query params or just render template.
    # The original passed 'supabase_key=key' to template. 'key' is available in services.
    from services import key
    return render_template('auth/reset_password_confirm.html', supabase_key=key)
