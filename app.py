"""
Aplicação principal do sistema de precificação.
"""
import os
import logging
from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv
from routes.orcamentos import orcamentos_bp
from models.precos import gerenciador_precos
from config import get_config
from services.email_sender import email_service

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Criar diretórios necessários se não existirem
os.makedirs('logs', exist_ok=True)
os.makedirs('orcamentos', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('csv', exist_ok=True)

# Inicializar aplicação Flask
app = Flask(__name__)

# Aplicar configurações
config = get_config()
app.config.from_object(config)
config.init_app(app)

# Inicializar serviços
email_service.init_app(app)

# Registrar blueprints
app.register_blueprint(orcamentos_bp, url_prefix='/orcamentos')

# Rota principal
@app.route('/')
def index():
    return render_template('index.html', percentual_sesi=app.config['PERCENTUAL_SESI_PADRAO'])

# Rota para arquivos estáticos
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Manipuladores de erro
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Erro interno do servidor: {str(e)}")
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# Inicialização do sistema
first_request_done = False

@app.before_request
def init_system():
    global first_request_done
    if not first_request_done:
        # Criar diretórios necessários
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('orcamentos', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Carregar preços
        try:
            gerenciador_precos.carregar_precos()
            app.logger.info("Preços carregados com sucesso")
        except Exception as e:
            app.logger.error(f"Erro ao carregar preços: {str(e)}")
        
        first_request_done = True

# Executar aplicação
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    logger.info(f"Iniciando aplicação no modo {'desenvolvimento' if debug else 'produção'} na porta {port}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.critical(f"Erro ao iniciar aplicação: {str(e)}")

