import os
from dotenv import load_dotenv

load_dotenv()

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
    # Em ambiente de produção (Vercel) usamos sessão baseada em cookies
    # Em desenvolvimento mantemos o filesystem
    if os.environ.get("VERCEL_ENV") == "production":
        SESSION_TYPE = 'cookie'  # Usar cookies gerenciados pelo Flask
    else:
        SESSION_TYPE = 'filesystem'  # Armazenar sessões em arquivos
        SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_session')  # Diretório para armazenar arquivos de sessão
        SESSION_FILE_THRESHOLD = 500  # Número máximo de arquivos de sessão
    
    SESSION_PERMANENT = True     # Tornar a sessão permanente
    PERMANENT_SESSION_LIFETIME = 3600  # Duração da sessão em segundos (1 hora)
    SESSION_USE_SIGNER = True    # Assinar cookies de sessão
    SESSION_KEY_PREFIX = 'precificacao_'  # Prefixo para chaves de sessão
    # Adicione outras configurações conforme necessário
