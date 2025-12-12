from flask import Blueprint, render_template, request, jsonify, session
from services import supabase, supabase_admin, login_required

vulto_bp = Blueprint('vulto', __name__)

@vulto_bp.route('/elaborar-vulto')
@login_required
def elaborar_vulto():
    return render_template('vulto/menu_vulto.html', user=session['user'])

@vulto_bp.route('/elaborar-vulto/novo')
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

@vulto_bp.route('/api/vulto/save', methods=['POST'])
@login_required
def save_vulto():
    try:
        data = request.get_json()
        user_id = session['user']['id']
        
        posto_oficial = data.get('posto_oficial')
        nome_oficial = data.get('nome_oficial')
        
        if posto_oficial and nome_oficial:
            oficiais_presenca_str = f"{posto_oficial} {nome_oficial}"
        else:
            oficiais_presenca_str = "NÃO HOUVE OFICIAL NO LOCAL"

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

        def fmt_date(d):
            if not d: return ""
            try:
                parts = d.split('-')
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
            except: return d

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
            'municipio_nome': data.get('municipio_nome'),
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
        
        if not vulto_data['tempo_resposta_minutos']: vulto_data['tempo_resposta_minutos'] = None

        res = supabase_admin.table('vulto_occurrences').insert(vulto_data).execute()
        return jsonify({"success": True, "data": res.data, "generated_text": texto_gerado})
        
    except Exception as e:
        print(f"Erro Vulto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@vulto_bp.route('/elaborar-vulto/listar')
@login_required
def elaborar_vulto_listar():
    return render_template('vulto/listar_vultos.html', user=session['user'])

@vulto_bp.route('/api/vulto/me')
@login_required
def get_my_vultos():
    try:
        user_id = session['user']['id']
        res = supabase_admin.table('vulto_occurrences').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        print(f"Erro ao buscar vultos: {e}")
        return jsonify([]), 500
