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
    # Adicione outras configurações conforme necessário
