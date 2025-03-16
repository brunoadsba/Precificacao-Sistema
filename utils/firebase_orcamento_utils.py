"""
Utilitários para gerenciamento de orçamentos usando Firebase.
"""
import os
import json
import logging
import uuid
from datetime import datetime
from fpdf import FPDF
from config.firebase_config import firebase_config
from utils.orcamento_utils import formatar_moeda

# Configurar logger
logger = logging.getLogger(__name__)

def gerar_numero_orcamento():
    """
    Gera um número único para o orçamento.
    
    Returns:
        str: Número do orçamento no formato YYYYMMDD-XXXX
    """
    data_atual = datetime.now().strftime("%Y%m%d")
    identificador = str(uuid.uuid4())[:8].upper()
    return f"{data_atual}-{identificador}"

def gerar_pdf_orcamento(dados_orcamento):
    """
    Gera um PDF para o orçamento e o armazena no Firebase Storage.
    
    Args:
        dados_orcamento (dict): Dados do orçamento
        
    Returns:
        str: URL do PDF no Firebase Storage, None em caso de erro
    """
    try:
        # Verificar se o Firebase está inicializado
        if not firebase_config.initialized:
            logger.warning("Firebase não inicializado. Não é possível gerar PDF.")
            return None
            
        # Criar PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Configurar fonte
        pdf.set_font("Arial", "B", 16)
        
        # Título
        pdf.cell(190, 10, "ORÇAMENTO", 0, 1, "C")
        pdf.cell(190, 10, f"Nº {dados_orcamento['numero_orcamento']}", 0, 1, "C")
        
        # Linha separadora
        pdf.line(10, 30, 200, 30)
        
        # Dados do cliente
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "DADOS DO CLIENTE", 0, 1, "L")
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(190, 8, f"Empresa: {dados_orcamento['empresa']}", 0, 1, "L")
        pdf.cell(190, 8, f"E-mail: {dados_orcamento['email']}", 0, 1, "L")
        
        if dados_orcamento.get('telefone'):
            pdf.cell(190, 8, f"Telefone: {dados_orcamento['telefone']}", 0, 1, "L")
            
        if dados_orcamento.get('contato'):
            pdf.cell(190, 8, f"Contato: {dados_orcamento['contato']}", 0, 1, "L")
        
        # Linha separadora
        pdf.line(10, pdf.get_y() + 5, 200, pdf.get_y() + 5)
        pdf.ln(10)
        
        # Serviços
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "SERVIÇOS", 0, 1, "L")
        
        # Cabeçalho da tabela
        pdf.set_font("Arial", "B", 10)
        pdf.cell(80, 8, "Serviço", 1, 0, "C")
        pdf.cell(40, 8, "Região", 1, 0, "C")
        pdf.cell(30, 8, "Valor", 1, 1, "C")
        
        # Dados da tabela
        pdf.set_font("Arial", "", 10)
        for servico in dados_orcamento['servicos']:
            # Verificar se o nome do serviço é muito longo
            nome_servico = servico['nome']
            if len(nome_servico) > 35:
                nome_servico = nome_servico[:32] + "..."
                
            pdf.cell(80, 8, nome_servico, 1, 0, "L")
            pdf.cell(40, 8, servico['regiao'], 1, 0, "C")
            pdf.cell(30, 8, formatar_moeda(servico['valor']), 1, 1, "R")
        
        # Resumo
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, "RESUMO", 0, 1, "L")
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(150, 8, "Subtotal:", 0, 0, "R")
        pdf.cell(40, 8, formatar_moeda(dados_orcamento['subtotal']), 0, 1, "R")
        
        pdf.cell(150, 8, f"SESI ({dados_orcamento['percentual_sesi']}%):", 0, 0, "R")
        pdf.cell(40, 8, formatar_moeda(dados_orcamento['valor_sesi']), 0, 1, "R")
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(150, 8, "TOTAL:", 0, 0, "R")
        pdf.cell(40, 8, formatar_moeda(dados_orcamento['total']), 0, 1, "R")
        
        # Rodapé
        pdf.ln(10)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 8, f"Data: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, "L")
        pdf.cell(190, 8, "Validade: 30 dias", 0, 1, "L")
        
        # Gerar PDF como string
        pdf_output = pdf.output(dest="S").encode("latin1")
        
        # Fazer upload para o Firebase Storage
        caminho_destino = f"orcamentos/orcamento_{dados_orcamento['numero_orcamento']}.pdf"
        url_pdf = firebase_config.upload_arquivo(
            caminho_destino=caminho_destino,
            conteudo=pdf_output,
            tipo_conteudo="application/pdf"
        )
        
        # Salvar dados do orçamento no Firestore
        doc_ref = firebase_config.db.collection('orcamentos').document(dados_orcamento['numero_orcamento'])
        dados_para_salvar = dados_orcamento.copy()
        dados_para_salvar['data_criacao'] = datetime.now().isoformat()
        dados_para_salvar['url_pdf'] = url_pdf
        doc_ref.set(dados_para_salvar)
        
        return url_pdf
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF do orçamento: {str(e)}")
        return None

def obter_orcamento(numero_orcamento):
    """
    Obtém os dados de um orçamento do Firestore.
    
    Args:
        numero_orcamento (str): Número do orçamento
        
    Returns:
        dict: Dados do orçamento, None em caso de erro
    """
    try:
        # Verificar se o Firebase está inicializado
        if not firebase_config.initialized:
            logger.warning("Firebase não inicializado. Não é possível obter orçamento.")
            return None
            
        # Buscar orçamento no Firestore
        doc_ref = firebase_config.db.collection('orcamentos').document(numero_orcamento)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        else:
            logger.warning(f"Orçamento {numero_orcamento} não encontrado")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao obter orçamento {numero_orcamento}: {str(e)}")
        return None

def download_orcamento_pdf(numero_orcamento):
    """
    Faz download do PDF de um orçamento do Firebase Storage.
    
    Args:
        numero_orcamento (str): Número do orçamento
        
    Returns:
        bytes: Conteúdo do PDF, None em caso de erro
    """
    try:
        # Verificar se o Firebase está inicializado
        if not firebase_config.initialized:
            logger.warning("Firebase não inicializado. Não é possível fazer download do orçamento.")
            return None
            
        # Buscar orçamento no Firestore para obter o caminho do PDF
        orcamento = obter_orcamento(numero_orcamento)
        
        if not orcamento or 'url_pdf' not in orcamento:
            logger.warning(f"URL do PDF do orçamento {numero_orcamento} não encontrada")
            return None
            
        # Extrair o caminho do Storage da URL
        url_pdf = orcamento['url_pdf']
        caminho_storage = url_pdf.split('/')[-1]
        
        # Fazer download do PDF
        return firebase_config.download_arquivo(f"orcamentos/{caminho_storage}")
            
    except Exception as e:
        logger.error(f"Erro ao fazer download do PDF do orçamento {numero_orcamento}: {str(e)}")
        return None

def gerar_corpo_email_orcamento(dados_orcamento):
    """
    Gera o corpo do e-mail para envio do orçamento.
    
    Args:
        dados_orcamento (dict): Dados do orçamento
        
    Returns:
        str: Corpo do e-mail em formato HTML
    """
    try:
        # Criar corpo do e-mail em HTML
        corpo_email = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                h1, h2 {{ color: #333366; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .total {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Orçamento Nº {dados_orcamento['numero_orcamento']}</h1>
                
                <p>Prezado(a) cliente,</p>
                
                <p>Segue o orçamento solicitado para sua empresa <strong>{dados_orcamento['empresa']}</strong>.</p>
                
                <h2>Serviços</h2>
                <table>
                    <tr>
                        <th>Serviço</th>
                        <th>Região</th>
                        <th>Valor</th>
                    </tr>
        """
        
        # Adicionar serviços
        for servico in dados_orcamento['servicos']:
            corpo_email += f"""
                    <tr>
                        <td>{servico['nome']}</td>
                        <td>{servico['regiao']}</td>
                        <td>{formatar_moeda(servico['valor'])}</td>
                    </tr>
            """
        
        # Adicionar resumo
        corpo_email += f"""
                </table>
                
                <h2>Resumo</h2>
                <table>
                    <tr>
                        <td>Subtotal</td>
                        <td>{formatar_moeda(dados_orcamento['subtotal'])}</td>
                    </tr>
                    <tr>
                        <td>SESI ({dados_orcamento['percentual_sesi']}%)</td>
                        <td>{formatar_moeda(dados_orcamento['valor_sesi'])}</td>
                    </tr>
                    <tr class="total">
                        <td>TOTAL</td>
                        <td>{formatar_moeda(dados_orcamento['total'])}</td>
                    </tr>
                </table>
                
                <p>Este orçamento tem validade de 30 dias a partir da data de envio.</p>
                
                <p>Em caso de dúvidas, entre em contato conosco.</p>
                
                <p>Atenciosamente,<br>
                Equipe de Vendas</p>
            </div>
        </body>
        </html>
        """
        
        return corpo_email
        
    except Exception as e:
        logger.error(f"Erro ao gerar corpo do e-mail: {str(e)}")
        return f"Segue em anexo o orçamento Nº {dados_orcamento['numero_orcamento']} para a empresa {dados_orcamento['empresa']}." 