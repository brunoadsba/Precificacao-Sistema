import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import logging
from flask_mail import Mail, Message
from flask import current_app

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def enviar_email(nome_arquivo, cliente_email=None):
    # Implementação da função original
    pass

def enviar_email_orcamento(destinatario, empresa, servicos, total):
    """
    Envia um e-mail com o orçamento para o cliente
    """
    try:
        msg = Message(
            'Orçamento de Serviços',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[destinatario]
        )
        
        # Corpo do e-mail
        msg.body = f'''
Prezado(a) cliente,

Segue o orçamento solicitado para {empresa}.

Serviços:
{format_servicos_email(servicos)}

Total: {format_currency(total)}

Este orçamento é válido por 30 dias a partir da data de emissão.

Para mais informações, entre em contato via WhatsApp: (71) 9 8707-5563

Atenciosamente,
Equipe de Vendas
'''
        
        mail.send(msg)
        return True, "E-mail enviado com sucesso!"
    except Exception as e:
        return False, f"Erro ao enviar e-mail: {str(e)}"

def format_servicos_email(servicos):
    """Formata a lista de serviços para o e-mail"""
    return '\n'.join([
        f"- {s['nome']}: {format_currency(s['preco_unitario'])} x {s['quantidade']} = {format_currency(s['preco_unitario'] * s['quantidade'])}"
        for s in servicos
    ])

def format_currency(value):
    """Formata um valor para moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

# Função original mantida para compatibilidade
def enviar_email(nome_arquivo, cliente_email=None):
    # Implementação da função original
    pass 