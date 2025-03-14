import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Verificar se estamos no ambiente Vercel
is_vercel = os.getenv('VERCEL_DEPLOYMENT', '0') == '1'

# Verificar se Flask-Session está disponível
try:
    import flask_session
    has_flask_session = True
except ImportError:
    has_flask_session = False
    logging.warning("Flask-Session não está instalado. Algumas funcionalidades podem não estar disponíveis.")

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
    if has_flask_session:
        # Configurações para Flask-Session (sessão baseada em arquivo)
        SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
        SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'False') == 'True'
        SESSION_LIFETIME = 3600
        SESSION_USE_SIGNER = True
        SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR', os.path.join(os.getcwd(), 'flask_session'))
        SESSION_FILE_THRESHOLD = 500
        SESSION_KEY_PREFIX = 'precificacao_'
    else:
        # Configurações para sessão padrão do Flask (baseada em cookie)
        PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Configurações do CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = False  # Desabilita a verificação automática para permitir isenções específicas
    WTF_CSRF_TIME_LIMIT = 3600  # Tempo de validade do token em segundos (1 hora)
    
    # Adicione outras configurações conforme necessário
