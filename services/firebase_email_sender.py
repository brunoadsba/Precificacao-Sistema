"""
Serviço para envio de e-mails com registro no Firebase.
"""
import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from config.firebase_config import firebase_config

# Configurar logger
logger = logging.getLogger(__name__)

class FirebaseEmailService:
    """
    Classe para envio de e-mails com registro no Firebase.
    """
    def __init__(self):
        """
        Inicializa o serviço de e-mail.
        """
        self.app = None
        self.remetente = None
        self.senha = None
        self.servidor_smtp = None
        self.porta_smtp = None
        self.usar_ssl = None
        self.initialized = False
        
    def init_app(self, app):
        """
        Inicializa o serviço de e-mail com a aplicação Flask.
        
        Args:
            app: Aplicação Flask
        """
        self.app = app
        
        # Obter configurações de e-mail
        self.remetente = app.config.get('EMAIL_REMETENTE')
        self.senha = app.config.get('EMAIL_SENHA')
        self.servidor_smtp = app.config.get('EMAIL_SERVIDOR_SMTP', 'smtp.gmail.com')
        self.porta_smtp = app.config.get('EMAIL_PORTA_SMTP', 587)
        self.usar_ssl = app.config.get('EMAIL_USAR_SSL', False)
        
        # Verificar se as configurações estão definidas
        if not self.remetente or not self.senha:
            logger.warning("Configurações de e-mail incompletas. Serviço de e-mail não inicializado.")
            return
            
        # Verificar se o Firebase está inicializado
        if not firebase_config.initialized:
            firebase_config.init_app(app)
            
        self.initialized = True
        logger.info("Serviço de e-mail inicializado")
        
    def enviar_email(self, destinatario, assunto, corpo, anexos=None):
        """
        Envia um e-mail.
        
        Args:
            destinatario (str): E-mail do destinatário
            assunto (str): Assunto do e-mail
            corpo (str): Corpo do e-mail (HTML)
            anexos (list, optional): Lista de caminhos para arquivos a serem anexados
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso, False caso contrário
        """
        if not self.initialized:
            logger.warning("Serviço de e-mail não inicializado. Não é possível enviar e-mail.")
            return False
            
        try:
            # Criar mensagem
            mensagem = MIMEMultipart()
            mensagem['From'] = self.remetente
            mensagem['To'] = destinatario
            mensagem['Subject'] = assunto
            
            # Adicionar corpo
            mensagem.attach(MIMEText(corpo, 'html'))
            
            # Adicionar anexos
            if anexos:
                for anexo in anexos:
                    with open(anexo, 'rb') as f:
                        parte = MIMEApplication(f.read(), Name=os.path.basename(anexo))
                        parte['Content-Disposition'] = f'attachment; filename="{os.path.basename(anexo)}"'
                        mensagem.attach(parte)
            
            # Conectar ao servidor SMTP
            if self.usar_ssl:
                servidor = smtplib.SMTP_SSL(self.servidor_smtp, self.porta_smtp)
            else:
                servidor = smtplib.SMTP(self.servidor_smtp, self.porta_smtp)
                servidor.starttls()
                
            # Login
            servidor.login(self.remetente, self.senha)
            
            # Enviar e-mail
            servidor.send_message(mensagem)
            
            # Fechar conexão
            servidor.quit()
            
            # Registrar envio no Firebase
            self._registrar_envio_firebase(destinatario, assunto, anexos)
            
            logger.info(f"E-mail enviado para {destinatario}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {destinatario}: {str(e)}")
            
            # Registrar erro no Firebase
            self._registrar_erro_firebase(destinatario, assunto, str(e))
            
            return False
    
    def _registrar_envio_firebase(self, destinatario, assunto, anexos=None):
        """
        Registra o envio de um e-mail no Firebase.
        
        Args:
            destinatario (str): E-mail do destinatário
            assunto (str): Assunto do e-mail
            anexos (list, optional): Lista de caminhos para arquivos anexados
        """
        try:
            if not firebase_config.initialized:
                return
                
            # Criar registro
            registro = {
                'destinatario': destinatario,
                'assunto': assunto,
                'data_envio': datetime.now().isoformat(),
                'status': 'enviado',
                'anexos': [os.path.basename(anexo) for anexo in (anexos or [])]
            }
            
            # Salvar no Firestore
            firebase_config.db.collection('emails').add(registro)
            
        except Exception as e:
            logger.error(f"Erro ao registrar envio de e-mail no Firebase: {str(e)}")
    
    def _registrar_erro_firebase(self, destinatario, assunto, erro):
        """
        Registra um erro de envio de e-mail no Firebase.
        
        Args:
            destinatario (str): E-mail do destinatário
            assunto (str): Assunto do e-mail
            erro (str): Mensagem de erro
        """
        try:
            if not firebase_config.initialized:
                return
                
            # Criar registro
            registro = {
                'destinatario': destinatario,
                'assunto': assunto,
                'data_tentativa': datetime.now().isoformat(),
                'status': 'erro',
                'mensagem_erro': erro
            }
            
            # Salvar no Firestore
            firebase_config.db.collection('emails').add(registro)
            
        except Exception as e:
            logger.error(f"Erro ao registrar erro de e-mail no Firebase: {str(e)}")

# Instância global do serviço de e-mail
firebase_email_service = FirebaseEmailService() 