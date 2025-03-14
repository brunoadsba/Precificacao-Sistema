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
    try:
        # Verificar se as credenciais de e-mail estão configuradas
        email_remetente = os.environ.get('EMAIL_REMETENTE')
        email_senha = os.environ.get('EMAIL_SENHA')
        
        if not email_remetente or not email_senha:
            logger.warning("Credenciais de e-mail (EMAIL_REMETENTE ou EMAIL_SENHA) não estão configuradas no .env")
        else:
            logger.info(f"E-mail configurado para: {email_remetente}")
            
        # Configurar o Flask-Mail (mesmo que não seja usado diretamente)
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = email_remetente
        app.config['MAIL_PASSWORD'] = email_senha
        app.config['MAIL_DEFAULT_SENDER'] = email_remetente
        
        return True
    except Exception as e:
        logger.error(f"Erro ao inicializar Flask-Mail: {str(e)}")
        return False

def enviar_email(nome_arquivo, cliente_email=None):
    # Implementação da função original (mantida para compatibilidade, mas não usada)
    pass

def enviar_email_orcamento_pdf(email_destino, pdf_path, numero_orcamento, empresa_cliente, servicos=None, subtotal=0, valor_sesi=0, total=0, percentual_sesi=30):
    """
    Envia um e-mail com o orçamento em PDF anexo e o resumo no corpo do e-mail.
    
    Args:
        email_destino: E-mail do destinatário
        pdf_path: Caminho para o arquivo PDF do orçamento
        numero_orcamento: Número do orçamento
        empresa_cliente: Nome da empresa cliente
        servicos: Lista de serviços do orçamento (opcional)
        subtotal: Valor subtotal do orçamento (opcional)
        valor_sesi: Valor do SESI (opcional)
        total: Valor total do orçamento (opcional)
        percentual_sesi: Percentual do SESI (opcional)
        
    Returns:
        tuple: (sucesso, mensagem)
    """
    try:
        # Configurações do servidor SMTP
        smtp_server = "smtp.gmail.com"
        port = 587  # Porta para TLS
        sender_email = os.environ.get('EMAIL_REMETENTE')
        password = os.environ.get('EMAIL_SENHA')
        
        # Depuração: Verifique se as credenciais estão disponíveis
        logger.info("Tentando enviar e-mail com PDF para %s com remetente %s", email_destino, sender_email)
        if not sender_email or not password:
            raise ValueError("Credenciais de e-mail (EMAIL_REMETENTE ou EMAIL_SENHA) não estão configuradas no .env")
        
        # Verificar se o arquivo PDF existe
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email_destino
        msg['Subject'] = f"Orçamento {numero_orcamento} - {empresa_cliente}"
        
        # Preparar a tabela de serviços se houver serviços
        servicos_html = ""
        if servicos:
            servicos_html = """
            <h2 style="margin-top: 30px; color: #0d6efd;">Resumo dos Serviços</h2>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <thead>
                    <tr>
                        <th style="background-color: #0d6efd; color: white; text-align: left; padding: 12px;">Serviço</th>
                        <th style="background-color: #0d6efd; color: white; text-align: center; padding: 12px;">Quantidade</th>
                        <th style="background-color: #0d6efd; color: white; text-align: right; padding: 12px;">Preço Unitário</th>
                        <th style="background-color: #0d6efd; color: white; text-align: right; padding: 12px;">Preço Total</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for servico in servicos:
                servicos_html += f"""
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: left;">{servico['nome']}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{servico['quantidade']}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">{servico.get('preco_unitario_formatado', f"R$ {servico['preco_unitario']:.2f}".replace('.', ','))}</td>
                        <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: right;">{servico.get('preco_total_formatado', f"R$ {servico['preco_total']:.2f}".replace('.', ','))}</td>
                    </tr>
                """
            
            # Adicionar resumo financeiro
            subtotal_formatado = f"R$ {subtotal:.2f}".replace('.', ',') if isinstance(subtotal, (int, float)) else subtotal
            valor_sesi_formatado = f"R$ {valor_sesi:.2f}".replace('.', ',') if isinstance(valor_sesi, (int, float)) else valor_sesi
            total_formatado = f"R$ {total:.2f}".replace('.', ',') if isinstance(total, (int, float)) else total
            
            servicos_html += """
                </tbody>
            </table>
            
            <div style="margin-top: 20px; text-align: right; font-size: 16px; padding: 10px; background-color: #e9ecef; border-radius: 4px;">
            """
            
            if subtotal:
                servicos_html += f"""
                <p><strong>Subtotal:</strong> {subtotal_formatado}</p>
                """
            
            if valor_sesi:
                servicos_html += f"""
                <p><strong>Percentual Indireto SESI ({percentual_sesi}%):</strong> {valor_sesi_formatado}</p>
                """
            
            if total:
                servicos_html += f"""
                <p style="font-size: 18px; color: #0d6efd;"><strong>Total do Orçamento:</strong> {total_formatado}</p>
                """
            
            servicos_html += """
            </div>
            """
        
        # Corpo do e-mail
        corpo_email = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f9f9f9;">
            <div style="max-width: 800px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; padding: 20px 0; background-color: #0d6efd; color: white; border-radius: 8px 8px 0 0; margin-bottom: 20px;">
                    <h1>Orçamento {numero_orcamento}</h1>
                </div>
                
                <p>Prezado(a) cliente,</p>
                <p>Segue em anexo o orçamento solicitado para a empresa <b>{empresa_cliente}</b>.</p>
                <p>Número do orçamento: <b>{numero_orcamento}</b></p>
                
                {servicos_html}
                
                <p>Para confirmar o orçamento ou em caso de dúvidas, por favor responda a este e-mail ou entre em contato conosco.</p>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #f8d7da; border-radius: 4px; color: #721c24;">
                    <p>Este orçamento é válido por 30 dias a partir da data de emissão.</p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; font-size: 14px; color: #6c757d;">
                    <p>Para mais informações ou para aceitar este orçamento, entre em contato conosco:</p>
                    <p>WhatsApp: <a href="https://wa.me/5571987075563" style="color: #28a745; text-decoration: none;">(71) 9 8707-5563</a></p>
                    <a href="https://wa.me/5571987075563" style="display: inline-block; margin: 15px 0; padding: 10px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">Falar com um consultor</a>
                    <p>© {datetime.now().year} {empresa_cliente}. Todos os direitos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo_email, 'html'))
        
        # Anexar PDF
        with open(pdf_path, 'rb') as f:
            anexo = MIMEApplication(f.read(), _subtype='pdf')
            anexo.add_header('Content-Disposition', 'attachment', filename=f"Orcamento_{numero_orcamento}.pdf")
            msg.attach(anexo)
        
        # Enviar e-mail
        with smtplib.SMTP(smtp_server, port) as servidor:
            servidor.starttls()
            servidor.login(sender_email, password)
            servidor.send_message(msg)
        
        logger.info(f"E-mail com PDF enviado com sucesso para {email_destino}")
        return True, "E-mail enviado com sucesso!"
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail com PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Erro ao enviar e-mail: {str(e)}"

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

def enviar_email_orcamento_pdf_buffer(email_destino, pdf_buffer, filename, numero_orcamento, empresa_cliente, servicos=None, subtotal=0, valor_sesi=0, total=0, percentual_sesi=30):
    """
    Envia um e-mail com o orçamento em PDF anexo e o resumo no corpo do e-mail.
    Esta versão aceita um buffer BytesIO em vez de um caminho de arquivo.
    
    Args:
        email_destino: E-mail do destinatário
        pdf_buffer: Buffer BytesIO contendo o PDF
        filename: Nome do arquivo para o anexo
        numero_orcamento: Número do orçamento
        empresa_cliente: Nome da empresa cliente
        servicos: Lista de serviços do orçamento (opcional)
        subtotal: Valor subtotal do orçamento (opcional)
        valor_sesi: Valor do SESI (opcional)
        total: Valor total do orçamento (opcional)
        percentual_sesi: Percentual do SESI (opcional)
        
    Returns:
        tuple: (sucesso, mensagem)
    """
    try:
        # Configurações do servidor SMTP
        smtp_server = "smtp.gmail.com"
        port = 587  # Porta para TLS
        sender_email = os.environ.get('EMAIL_REMETENTE')
        password = os.environ.get('EMAIL_SENHA')
        
        # Depuração: Verifique se as credenciais estão disponíveis
        logger.info("Tentando enviar e-mail com PDF para %s com remetente %s", email_destino, sender_email)
        if not sender_email or not password:
            logger.error("Credenciais de e-mail (EMAIL_REMETENTE ou EMAIL_SENHA) não estão configuradas no .env")
            return False, "Credenciais de e-mail não configuradas. Verifique o arquivo .env."
        
        # Verificar se o e-mail de destino é válido
        if not email_destino or '@' not in email_destino:
            logger.error("E-mail de destino inválido: %s", email_destino)
            return False, f"E-mail de destino inválido: {email_destino}"
        
        # Verificar se o buffer do PDF é válido
        if not pdf_buffer:
            logger.error("Buffer do PDF é nulo ou vazio")
            return False, "Buffer do PDF é nulo ou vazio"
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email_destino
        msg['Subject'] = f"Orçamento {numero_orcamento} - {empresa_cliente}"
        
        # Corpo do e-mail
        corpo_email = f"""
        <html>
        <body>
            <p>Prezado(a) cliente,</p>
            <p>Segue em anexo o orçamento solicitado para a empresa <b>{empresa_cliente}</b>.</p>
            <p>Número do orçamento: <b>{numero_orcamento}</b></p>
            <p>Para confirmar o orçamento ou em caso de dúvidas, por favor responda a este e-mail ou entre em contato conosco.</p>
            <p>Atenciosamente,<br>Equipe de Atendimento</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo_email, 'html'))
        
        # Anexar PDF do buffer
        try:
            pdf_data = pdf_buffer.getvalue()
            anexo = MIMEApplication(pdf_data, _subtype='pdf')
            anexo.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(anexo)
        except Exception as e:
            logger.error(f"Erro ao anexar PDF: {str(e)}")
            return False, f"Erro ao anexar PDF: {str(e)}"
        
        # Enviar e-mail
        try:
            with smtplib.SMTP(smtp_server, port) as servidor:
                servidor.starttls()
                servidor.login(sender_email, password)
                servidor.send_message(msg)
            
            logger.info(f"E-mail enviado com sucesso para {email_destino}")
            return True, "E-mail enviado com sucesso"
        except smtplib.SMTPAuthenticationError:
            logger.error("Erro de autenticação SMTP. Verifique suas credenciais de e-mail.")
            return False, "Erro de autenticação SMTP. Verifique suas credenciais de e-mail."
        except smtplib.SMTPException as e:
            logger.error(f"Erro SMTP ao enviar e-mail: {str(e)}")
            return False, f"Erro SMTP ao enviar e-mail: {str(e)}"
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, f"Erro ao enviar e-mail: {str(e)}"