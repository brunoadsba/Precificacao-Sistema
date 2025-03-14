from flask import Flask, jsonify, request
import os
import sys
import logging
import traceback

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
    logger.info("Aplicativo Flask inicializado com sucesso")
    
except Exception as e:
    logger.error(f"Erro ao inicializar o aplicativo Flask: {str(e)}")
    traceback.print_exc()
    raise

@app.route('/')
def index():
    """Rota principal para verificar se a aplicação está funcionando"""
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
        
        return jsonify({
            'status': 'ok',
            'python_version': sys.version,
            'platform': sys.platform,
            'cwd': os.getcwd(),
            'session_dir_exists': session_dir_exists,
            'pgr_exists': os.path.exists(pgr_path),
            'ambientais_exists': os.path.exists(ambientais_path),
            'env': {
                'FLASK_ENV': os.environ.get('FLASK_ENV', 'não definido'),
                'VERCEL_DEPLOYMENT': os.environ.get('VERCEL_DEPLOYMENT', 'não definido'),
                'SESSION_TYPE': os.environ.get('SESSION_TYPE', 'não definido')
            },
            'dependencies': {
                'flask': installed_packages.get('flask', 'não instalado'),
                'flask-session': installed_packages.get('flask-session', 'não instalado'),
                'werkzeug': installed_packages.get('werkzeug', 'não instalado')
            },
            'request_info': {
                'path': request.path,
                'method': request.method,
                'headers': dict(request.headers)
            }
        })
    except Exception as e:
        logger.error(f"Erro na rota de diagnóstico: {str(e)}")
        return jsonify({'erro': str(e)}), 500

@app.route('/teste')
def teste():
    """Rota de teste para verificar se a aplicação está funcionando corretamente"""
    try:
        from datetime import datetime
        return jsonify({
            'status': 'ok',
            'message': 'Aplicação funcionando corretamente',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'environment': os.environ.get('FLASK_ENV', 'não definido')
        })
    except Exception as e:
        logger.error(f"Erro na rota de teste: {str(e)}")
        return jsonify({'erro': str(e)}), 500

@app.route('/dependencias')
def dependencias():
    """Rota para verificar as dependências instaladas"""
    try:
        import pkg_resources
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        
        # Verificar dependências específicas
        dependencies = {
            'flask': installed_packages.get('flask', 'não instalado'),
            'flask-session': installed_packages.get('flask-session', 'não instalado'),
            'flask-wtf': installed_packages.get('flask-wtf', 'não instalado'),
            'pandas': installed_packages.get('pandas', 'não instalado'),
            'python-dotenv': installed_packages.get('python-dotenv', 'não instalado'),
            'babel': installed_packages.get('babel', 'não instalado'),
            'waitress': installed_packages.get('waitress', 'não instalado')
        }
        
        # Verificar se Flask-Session está disponível
        try:
            import flask_session
            flask_session_available = 'sim'
        except ImportError:
            flask_session_available = 'não'
        
        return jsonify({
            'python_version': sys.version,
            'dependencies': dependencies,
            'flask_session_available': flask_session_available,
            'all_packages': installed_packages
        })
    except Exception as e:
        logger.error(f"Erro na rota de dependências: {str(e)}")
        return jsonify({'erro': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True) 