from flask import Flask, jsonify, request, render_template
import os
import sys
import logging
import traceback
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verificar se estamos no ambiente Vercel
is_vercel = os.getenv('VERCEL_DEPLOYMENT', '0') == '1'
logger.info(f"Inicializando vercel-app.py no ambiente Vercel: {is_vercel}")

# Inicialização do aplicativo Flask
try:
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'chave_secreta_padrao')
    
    # Configurar sessão
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    # Tentar inicializar Flask-Session
    try:
        from flask_session import Session
        Session(app)
        logger.info("Flask-Session inicializado com sucesso")
    except ImportError:
        logger.warning("Flask-Session não está disponível, usando sessão padrão do Flask")
    
    logger.info("Aplicativo Flask inicializado com sucesso")
    
except Exception as e:
    logger.error(f"Erro ao inicializar o aplicativo Flask: {str(e)}")
    traceback.print_exc()
    raise

@app.route('/')
def index():
    """Rota principal para verificar se a aplicação está funcionando"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Erro ao renderizar template: {str(e)}")
        return jsonify({
            'status': 'ok',
            'message': 'Aplicação simplificada para o Vercel funcionando corretamente',
            'environment': os.environ.get('FLASK_ENV', 'não definido'),
            'vercel_deployment': os.environ.get('VERCEL_DEPLOYMENT', 'não definido')
        })

@app.route('/diagnostico')
def diagnostico():
    """Rota de diagnóstico para verificar o ambiente"""
    try:
        import pkg_resources
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        
        # Verificar diretório de sessão
        session_dir = os.path.join(os.getcwd(), 'flask_session')
        session_dir_exists = os.path.exists(session_dir)
        
        # Verificar arquivos CSV
        pgr_path = os.path.join(os.getcwd(), 'Precos_PGR.csv')
        ambientais_path = os.path.join(os.getcwd(), 'Precos_Ambientais.csv')
        
        # Verificar se os templates existem
        templates_dir = os.path.join(os.getcwd(), 'templates')
        templates_dir_exists = os.path.exists(templates_dir)
        
        # Verificar se os arquivos estáticos existem
        static_dir = os.path.join(os.getcwd(), 'static')
        static_dir_exists = os.path.exists(static_dir)
        
        return jsonify({
            'status': 'ok',
            'python_version': sys.version,
            'platform': sys.platform,
            'cwd': os.getcwd(),
            'environment': os.environ.get('FLASK_ENV', 'não definido'),
            'vercel_deployment': os.environ.get('VERCEL_DEPLOYMENT', 'não definido'),
            'session_dir_exists': session_dir_exists,
            'pgr_exists': os.path.exists(pgr_path),
            'ambientais_exists': os.path.exists(ambientais_path),
            'templates_dir_exists': templates_dir_exists,
            'static_dir_exists': static_dir_exists,
            'installed_packages': installed_packages
        })
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/teste')
def teste():
    """Rota de teste para verificar se a aplicação está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Rota de teste funcionando corretamente'
    })

@app.route('/dependencias')
def dependencias():
    """Rota para listar as dependências instaladas"""
    try:
        import pkg_resources
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        return jsonify(installed_packages)
    except Exception as e:
        logger.error(f"Erro ao listar dependências: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == "__main__":
    from waitress import serve
    
    # Obter porta do ambiente ou usar 3000 como padrão
    port = int(os.environ.get("PORT", 3000))
    
    print(f"Iniciando servidor na porta {port}")
    serve(app, host="0.0.0.0", port=port) 