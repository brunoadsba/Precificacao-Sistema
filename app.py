"""
Aplicação principal do sistema de precificação.
"""
import os
import logging
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging básico (será sobrescrito pelo config.py)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """
    Cria e configura a aplicação Flask.
    
    Returns:
        Flask: Aplicação Flask configurada
    """
    # Criar aplicação
    app = Flask(__name__)
    
    # Configurar CORS
    CORS(app)
    
    # Carregar configurações
    from config.config import get_config
    config = get_config()
    app.config.from_object(config)
    config.init_app(app)
    
    # Verificar se estamos em ambiente de produção
    is_production = os.getenv('FLASK_ENV') == 'production'
    
    # Verificar se estamos no Vercel
    is_vercel = os.getenv('VERCEL') == '1'
    
    # Verificar se estamos no Render
    is_render = os.getenv('RENDER') == '1'
    
    # Criar diretórios necessários (já criado no config.py, mas mantido para compatibilidade)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ORCAMENTOS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CSV_FOLDER'], exist_ok=True)
    
    # Configurar serviços
    if is_production or is_vercel or is_render:
        # Em produção, usar Firebase
        try:
            from config.firebase_config import firebase_config
            firebase_config.init_app(app)
            
            from models.firestore_precos import gerenciador_precos_firestore
            app.config['GERENCIADOR_PRECOS'] = gerenciador_precos_firestore
            gerenciador_precos_firestore.init_app(app)
            
            from services.firebase_email_sender import firebase_email_service
            app.config['EMAIL_SERVICE'] = firebase_email_service
            firebase_email_service.init_app(app)
            
            # Configurar utilitários
            app.config['USAR_FIREBASE_STORAGE'] = True
            logger.info("Serviços Firebase inicializados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar serviços Firebase: {str(e)}")
            # Fallback para serviços locais
            from models.precos import gerenciador_precos
            app.config['GERENCIADOR_PRECOS'] = gerenciador_precos
            gerenciador_precos.init_app(app)
            
            from services.email_sender import email_service
            app.config['EMAIL_SERVICE'] = email_service
            email_service.init_app(app)
            
            app.config['USAR_FIREBASE_STORAGE'] = False
    else:
        # Em desenvolvimento, usar arquivos locais
        from models.precos import gerenciador_precos
        app.config['GERENCIADOR_PRECOS'] = gerenciador_precos
        gerenciador_precos.init_app(app)
        
        from services.email_sender import email_service
        app.config['EMAIL_SERVICE'] = email_service
        email_service.init_app(app)
        
        # Configurar utilitários
        app.config['USAR_FIREBASE_STORAGE'] = False
        logger.info("Serviços locais inicializados com sucesso")
    
    # Registrar blueprints
    from routes.orcamentos import orcamentos_bp, init_app as init_orcamentos
    app.register_blueprint(orcamentos_bp, url_prefix='/orcamentos')
    init_orcamentos(app)
    
    # Rotas básicas
    @app.route('/')
    def index():
        """Página inicial."""
        return render_template('index.html', percentual_sesi=app.config['PERCENTUAL_SESI_PADRAO'])
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Arquivos estáticos."""
        return send_from_directory('static', filename)
    
    @app.route('/favicon.ico')
    def favicon():
        """Favicon."""
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
    # Páginas de erro
    @app.errorhandler(404)
    def page_not_found(e):
        """Página não encontrada."""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """Erro interno do servidor."""
        logger.error(f"Erro interno do servidor: {str(e)}")
        return render_template('500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        """Acesso proibido."""
        return render_template('403.html'), 403
    
    return app

# Criar aplicação
app = create_app()

# Executar aplicação
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_ENV', 'production') != 'production'
    
    logger.info(f"Iniciando servidor em {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)