"""
Configurações da aplicação.
"""
import os
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """Configuração base."""
    # Configurações gerais
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao'
    DEBUG = False
    TESTING = False
    
    # Configurações de diretórios
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ORCAMENTOS_FOLDER = os.path.join(BASE_DIR, 'orcamentos')
    CSV_FOLDER = os.path.join(BASE_DIR, 'csv')
    
    # Configurações de e-mail
    EMAIL_SERVER = os.environ.get('EMAIL_SERVER') or 'smtp.gmail.com'
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT') or 587)
    EMAIL_USERNAME = os.environ.get('EMAIL_REMETENTE')
    EMAIL_PASSWORD = os.environ.get('EMAIL_SENHA')
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    
    # Configurações de logging
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')
    
    # Configurações de preços
    PRECO_PGR_CSV = os.path.join(CSV_FOLDER, 'Precos_PGR.csv')
    PRECO_AMBIENTAIS_CSV = os.path.join(CSV_FOLDER, 'Precos_Ambientais.csv')
    
    # Configurações de percentuais
    PERCENTUAL_SESI_PADRAO = 30
    
    @staticmethod
    def init_app(app):
        """Inicializa a aplicação com as configurações."""
        # Criar diretórios necessários
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.ORCAMENTOS_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(Config.BASE_DIR, 'logs'), exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=Config.LOG_LEVEL,
            format=Config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento."""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class TestingConfig(Config):
    """Configuração para ambiente de testes."""
    TESTING = True
    DEBUG = True
    
    # Usar banco de dados de teste
    # Desativar envio de e-mails reais
    EMAIL_BACKEND = 'dummy'


class ProductionConfig(Config):
    """Configuração para ambiente de produção."""
    # Usar variáveis de ambiente para configurações sensíveis
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Configurações de segurança adicionais
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


# Dicionário de configurações disponíveis
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Obter configuração atual
def get_config():
    """Retorna a configuração com base no ambiente."""
    env = os.environ.get('FLASK_ENV') or 'default'
    return config.get(env, config['default'])
