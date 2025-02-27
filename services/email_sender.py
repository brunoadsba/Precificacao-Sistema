import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import logging
from babel.numbers import format_currency  # Importa para formatação de moeda
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def init_mail(app):
    """Inicializa o Flask-Mail, mas mantido para compatibilidade (não usado aqui)"""
    pass

def enviar_email(nome_arquivo, cliente_email=None):
    # Implementação da função original (mantida para compatibilidade, mas não usada)
    pass

def enviar_email_orcamento(destinatario, empresa, servicos, total):
    """
    Envia um e-mail com o orçamento para o cliente usando smtplib
    """
    try:
        # Configurações do servidor SMTP
        smtp_server = "smtp.gmail.com"
        port = 587  # Porta para TLS
        sender_email = os.environ.get('EMAIL_REMETENTE')
        password = os.environ.get('EMAIL_SENHA')
        
        # Depuração: Verifique se as credenciais estão disponíveis
        logger.info("Tentando enviar e-mail para %s com remetente %s", destinatario, sender_email)
        if not sender_email or not password:
            raise ValueError("Credenciais de e-mail (EMAIL_REMETENTE ou EMAIL_SENHA) não estão configuradas no .env")
        
        # Cria a mensagem
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinatario
        msg['Subject'] = 'Orçamento de Serviços'
        
        # Corpo do e-mail em HTML
        corpo_email = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Orçamento de Serviços</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f9f9f9;">
            <div style="max-width: 800px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; padding: 20px 0; background-color: #0d6efd; color: white; border-radius: 8px 8px 0 0; margin-bottom: 20px;">
                    <h1>Orçamento de Serviços</h1>
                </div>
                
                <div style="margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px;">
                    <p><strong>Cliente:</strong> {destinatario}</p>
                    <p><strong>Empresa:</strong> {empresa}</p>
                </div>
                
                <div>
                    <h2>Serviços Orçados</h2>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        <thead>
                            <tr>
                                <th style="background-color: #0d6efd; color: white; text-align: left; padding: 12px;">Serviço</th>
                                <th style="background-color: #0d6efd; color: white; text-align: right; padding: 12px;">Valor Total</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Adiciona cada serviço à tabela
        for servico in servicos:
            corpo_email += f"""
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: left;">{servico['nome']} (Quantidade: {servico['quantidade']} {servico['unidade']})</td>
                                <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">{format_currency(servico['preco_total'], 'BRL', locale='pt_BR')}</td>
                            </tr>
            """
        
        # Finaliza a tabela e adiciona o total
        corpo_email += f"""
                        </tbody>
                    </table>
                    
                    <div style="margin-top: 20px; text-align: right; font-size: 18px; font-weight: bold; padding: 10px; background-color: #e9ecef; border-radius: 4px;">
                        <p>Total do Orçamento: {format_currency(total, 'BRL', locale='pt_BR')}</p>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 15px; background-color: #f8d7da; border-radius: 4px; color: #721c24;">
                        <p>Este orçamento é válido por 30 dias a partir da data de emissão.</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; font-size: 14px; color: #6c757d;">
                        <p>Para mais informações ou para aceitar este orçamento, entre em contato conosco:</p>
                        <p>WhatsApp: <a href="https://wa.me/5571987075563" style="color: #28a745; text-decoration: none;">(71) 9 8707-5563</a></p>
                        <a href="https://wa.me/5571987075563" style="display: inline-block; margin: 15px 0; padding: 10px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">Falar com um consultor</a>
                        <p>© {datetime.now().year} {empresa or 'BR Produções'}. Todos os direitos reservados.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Adiciona o corpo HTML à mensagem
        msg.attach(MIMEText(corpo_email, 'html', 'utf-8'))
        
        # Inicia a conexão com o servidor SMTP
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        
        # Envia o e-mail
        server.send_message(msg)
        server.quit()
        
        logger.info("E-mail enviado com sucesso para %s", destinatario)
        return True, "E-mail enviado com sucesso!"
    except Exception as e:
        logger.error("Erro ao enviar e-mail: %s", str(e))
        import traceback
        traceback.print_exc()
        return False, f"Erro ao enviar e-mail: {str(e)}"

def format_servicos_email(servicos):
    """Formata a lista de serviços para o e-mail (não usada diretamente, mas mantida para compatibilidade)"""
    return '\n'.join([
        f"- {s['nome']}: {format_currency(s['preco_unitario'], 'BRL', locale='pt_BR')} x {s['quantidade']} = {format_currency(s['preco_unitario'] * s['quantidade'], 'BRL', locale='pt_BR')}"
        for s in servicos
    ])

# Função original mantida para compatibilidade
def enviar_email(nome_arquivo, cliente_email=None):
    # Implementação da função original
    pass