import os
import pandas as pd
import logging
import sys
import pkg_resources
import traceback

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verificar se estamos no ambiente Vercel
is_vercel = os.getenv('VERCEL_DEPLOYMENT', '0') == '1'
logger.info(f"Ambiente Vercel: {is_vercel}")

def verificar_ambiente():
    """Verifica se o ambiente está configurado corretamente"""
    logger.info("Verificando ambiente...")
    
    # Verificar diretório de sessão
    session_dir = os.path.join(os.getcwd(), 'flask_session')
    if not os.path.exists(session_dir):
        logger.info(f"Criando diretório de sessão: {session_dir}")
        os.makedirs(session_dir, exist_ok=True)
    
    # Verificar arquivos CSV
    pgr_path = os.path.join(os.getcwd(), 'Precos_PGR.csv')
    ambientais_path = os.path.join(os.getcwd(), 'Precos_Ambientais.csv')
    
    logger.info(f"PGR Path: {pgr_path}, existe: {os.path.exists(pgr_path)}")
    logger.info(f"Ambientais Path: {ambientais_path}, existe: {os.path.exists(ambientais_path)}")
    
    # Criar arquivos CSV vazios se não existirem (apenas para evitar erros)
    if not os.path.exists(pgr_path):
        logger.warning(f"Arquivo PGR não encontrado, criando arquivo vazio: {pgr_path}")
        try:
            with open(pgr_path, 'w') as f:
                f.write("Serviço,Grau_Risco,Faixa_Trab,Região,Preço\n")
                f.write("\"Elaboração e acompanhamento do PGR\",\"1 e 2\",\"Até 19 Trab.\",\"Central\",700.00\n")
        except Exception as e:
            logger.error(f"Erro ao criar arquivo PGR: {str(e)}")
    
    if not os.path.exists(ambientais_path):
        logger.warning(f"Arquivo Ambientais não encontrado, criando arquivo vazio: {ambientais_path}")
        try:
            with open(ambientais_path, 'w') as f:
                f.write("Serviço,Tipo_Avaliacao,Adicional_GES_GHE,Região,Preço\n")
                f.write("\"Coleta para Avaliação Ambiental\",\"Pacote (1 a 4 avaliações)\",50.00,\"Central\",300.00\n")
        except Exception as e:
            logger.error(f"Erro ao criar arquivo Ambientais: {str(e)}")
    
    # Verificar dependências instaladas
    try:
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        logger.info(f"Flask versão: {installed_packages.get('flask', 'não instalado')}")
        logger.info(f"Flask-Session versão: {installed_packages.get('flask-session', 'não instalado')}")
        logger.info(f"Pandas versão: {installed_packages.get('pandas', 'não instalado')}")
    except Exception as e:
        logger.error(f"Erro ao verificar dependências: {str(e)}")
    
    # Verificar variáveis de ambiente
    logger.info(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'não definido')}")
    logger.info(f"VERCEL_DEPLOYMENT: {os.environ.get('VERCEL_DEPLOYMENT', 'não definido')}")
    
    return {
        'session_dir_exists': os.path.exists(session_dir),
        'pgr_exists': os.path.exists(pgr_path),
        'ambientais_exists': os.path.exists(ambientais_path),
        'python_version': sys.version,
        'platform': sys.platform,
        'cwd': os.getcwd(),
        'env': {
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'não definido'),
            'VERCEL_DEPLOYMENT': os.environ.get('VERCEL_DEPLOYMENT', 'não definido')
        }
    }

# Verificar ambiente antes de importar a aplicação
try:
    ambiente_info = verificar_ambiente()
    logger.info(f"Informações do ambiente: {ambiente_info}")
    
    # Tentar importar a aplicação simplificada primeiro
    try:
        from vercel_app import app
        logger.info("Aplicação simplificada importada com sucesso")
    except ImportError as e:
        logger.warning(f"Erro ao importar aplicação simplificada: {str(e)}")
        # Tentar importar a aplicação completa
        try:
            from app import app
            logger.info("Aplicação completa importada com sucesso")
        except ImportError as e:
            logger.error(f"Erro ao importar aplicação completa: {str(e)}")
            raise
    
except Exception as e:
    logger.error(f"Erro ao inicializar a aplicação: {str(e)}")
    traceback.print_exc()
    # Criar uma aplicação mínima para diagnóstico
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error_index():
        return jsonify({
            'error': f"Erro ao inicializar a aplicação: {str(e)}",
            'traceback': traceback.format_exc(),
            'environment': verificar_ambiente()
        })

# Ponto de entrada para o Vercel
app = app

if __name__ == "__main__":
    from waitress import serve
    
    # Obter porta do ambiente ou usar 3000 como padrão
    port = int(os.environ.get("PORT", 3000))
    
    print(f"Iniciando servidor na porta {port}")
    serve(app, host="0.0.0.0", port=port) 