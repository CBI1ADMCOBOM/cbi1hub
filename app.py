import os
from flask import Flask, redirect, url_for
from services import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_super_secreta_padrao_dev")

# -------------------------------------------------------------------------
# Registro de Blueprints
# -------------------------------------------------------------------------
from routes.auth import auth_bp
from routes.raia import raia_bp
from routes.vulto import vulto_bp
from routes.chuvas import chuvas_bp
from routes.inconsistencias import inc_bp
from routes.admin import admin_bp
from routes.main import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(raia_bp)
app.register_blueprint(vulto_bp)
app.register_blueprint(chuvas_bp)
app.register_blueprint(inc_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)

# Redirecionamento de raiz para login se não logado é tratado no main.dashboard
# Mas se precisar de algo global, pode ser aqui.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
