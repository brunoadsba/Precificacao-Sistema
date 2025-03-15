import os
from dotenv import load_dotenv
import logging
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Verificar se estamos no ambiente Vercel
is_vercel = os.getenv('VERCEL_DEPLOYMENT', '0') == '1'
logger.info(f"Ambiente Vercel: {is_vercel}")

# Verificar se Flask-Session está disponível
try:
    import flask_session
    has_flask_session = True
    logger.info("Flask-Session está disponível")
except ImportError:
    has_flask_session = False
    logger.warning("Flask-Session não está instalado. Algumas funcionalidades podem não estar disponíveis.")

class Config:
    # Configurações do Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave_secreta_padrao')
    
    # Configurações do Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_REMETENTE')
    MAIL_PASSWORD = os.getenv('EMAIL_SENHA')
    MAIL_DEFAULT_SENDER = os.getenv('EMAIL_REMETENTE')
    
    # Configurações da sessão
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
    SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'False') == 'True'
    SESSION_LIFETIME = 3600
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR', os.path.join(os.getcwd(), 'flask_session'))
    SESSION_FILE_THRESHOLD = 500
    SESSION_KEY_PREFIX = 'precificacao_'
    
    # Configurações do CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = False  # Desabilita a verificação automática para permitir isenções específicas
    WTF_CSRF_TIME_LIMIT = 3600  # Tempo de validade do token em segundos (1 hora)
    
    # Configurações específicas para o Vercel
    if is_vercel:
        # Configurações para o ambiente Vercel
        DEBUG = False
        TESTING = False
        PREFERRED_URL_SCHEME = 'https'
        
    # Configurações de logging
    LOG_LEVEL = logging.INFO
    
    # Informações do ambiente
    @staticmethod
    def get_environment_info():
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'cwd': os.getcwd(),
            'env': {
                'FLASK_ENV': os.environ.get('FLASK_ENV', 'não definido'),
                'VERCEL_DEPLOYMENT': os.environ.get('VERCEL_DEPLOYMENT', 'não definido')
            }
        }
