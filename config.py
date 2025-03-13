import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configurações do Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave_secreta_padrao')
    
    # Comentar ou remover as configurações do Flask-Mail
    # MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.getenv('EMAIL_REMETENTE')
    # MAIL_PASSWORD = os.getenv('EMAIL_SENHA')
    # MAIL_DEFAULT_SENDER = os.getenv('EMAIL_REMETENTE')
    
    # Comentar ou remover as configurações da sessão baseada em arquivo
    # SESSION_TYPE = 'filesystem'
    # SESSION_PERMANENT = True
    # SESSION_LIFETIME = 3600
    # SESSION_USE_SIGNER = True
    # SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_session')
    # SESSION_FILE_THRESHOLD = 500
    # SESSION_KEY_PREFIX = 'precificacao_'
    # Adicione outras configurações conforme necessário
