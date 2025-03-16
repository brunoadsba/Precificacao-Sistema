"""
Utilitários para geração e manipulação de orçamentos.
"""
import os
import random
import logging
import datetime
import string
from babel.numbers import format_currency
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from fpdf import FPDF

logger = logging.getLogger(__name__)

def gerar_numero_orcamento():
    """
    Gera um número de orçamento único baseado na data atual e um código aleatório.
    
    Returns:
        str: Número do orçamento no formato YYYYMMDD-XXXX
    """
    data_atual = datetime.datetime.now().strftime('%Y%m%d')
    codigo_aleatorio = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{data_atual}-{codigo_aleatorio}"

def calcular_custos_logisticos(regiao, distancia_km=None):
    """
    Calcula os custos logísticos com base na região e distância.
    
    Args:
        regiao (str): Região do serviço
        distancia_km (float, optional): Distância em quilômetros
        
    Returns:
        float: Custo logístico calculado
    """
    try:
        # Valores base por região
        custos_base = {
            "Central": 0.0,
            "Norte": 150.0,
            "Oeste": 200.0,
            "Sudoeste": 250.0,
            "Sul e Extremo Sul": 300.0,
            "Instituto": 0.0
        }
        
        # Obter custo base da região
        custo_base = custos_base.get(regiao, 0.0)
        
        # Adicionar custo por quilômetro se fornecido
        if distancia_km and distancia_km > 0:
            # Valor por km (R$ 2,00)
            valor_por_km = 2.0
            custo_adicional = distancia_km * valor_por_km
            return custo_base + custo_adicional
        
        return custo_base
    
    except Exception as e:
        logger.error(f"Erro ao calcular custos logísticos: {str(e)}")
        return 0.0

def calcular_custos_multiplos_dias(dias_coleta):
    """
    Calcula custos adicionais para coletas que duram múltiplos dias.
    
    Args:
        dias_coleta (int): Número de dias de coleta
        
    Returns:
        float: Custo adicional para múltiplos dias
    """
    try:
        if not dias_coleta or dias_coleta <= 1:
            return 0.0
        
        # Custo adicional por dia (diária)
        custo_diaria = 250.0
        
        # Calcular custo total (dias - 1, pois o primeiro dia já está incluído no preço base)
        return custo_diaria * (dias_coleta - 1)
    
    except Exception as e:
        logger.error(f"Erro ao calcular custos de múltiplos dias: {str(e)}")
        return 0.0

def calcular_custos_laboratoriais(tipo_amostrador, quantidade_amostras, tipo_analise, necessita_art, metodo_envio):
    """
    Calcula os custos laboratoriais para análises ambientais.
    
    Args:
        tipo_amostrador (str): Tipo de amostrador
        quantidade_amostras (int): Quantidade de amostras
        tipo_analise (str): Tipo de análise
        necessita_art (bool): Se necessita ART
        metodo_envio (str): Método de envio das amostras
        
    Returns:
        float: Custo laboratorial calculado
    """
    try:
        custo_total = 0.0
        
        # Custo base por tipo de amostrador
        custos_amostrador = {
            "Bomba de Amostragem": 150.0,
            "Dosímetro": 120.0,
            "Tubos Colorimétricos": 100.0,
            "Amostragem Passiva": 80.0
        }
        
        # Custo base por tipo de análise
        custos_analise = {
            "Química": 200.0,
            "Física": 150.0,
            "Biológica": 250.0
        }
        
        # Custo de ART
        custo_art = 88.78 if necessita_art else 0.0
        
        # Custo de envio
        custos_envio = {
            "Correios": 50.0,
            "Transportadora": 100.0,
            "Retirada no Local": 0.0
        }
        
        # Calcular custo total
        custo_amostrador = custos_amostrador.get(tipo_amostrador, 0.0)
        custo_analise = custos_analise.get(tipo_analise, 0.0)
        custo_envio = custos_envio.get(metodo_envio, 0.0)
        
        # Custo por amostra
        custo_por_amostra = custo_amostrador + custo_analise
        
        # Custo total
        custo_total = (custo_por_amostra * quantidade_amostras) + custo_art + custo_envio
        
        return custo_total
    
    except Exception as e:
        logger.error(f"Erro ao calcular custos laboratoriais: {str(e)}")
        return 0.0

def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira.
    
    Args:
        valor (float): Valor a ser formatado
        
    Returns:
        str: Valor formatado como moeda (R$ X.XXX,XX)
    """
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

class PDF(FPDF):
    def header(self):
        # Logo
        try:
            self.image('static/img/logo.png', 10, 8, 33)
        except:
            pass
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Orçamento', 0, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def gerar_pdf_orcamento(dados_orcamento):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    # Informações do cliente
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Informações do Cliente:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Empresa: {dados_orcamento['empresa']}", 0, 1)
    pdf.cell(0, 10, f"Email: {dados_orcamento['email']}", 0, 1)
    pdf.cell(0, 10, f"Telefone: {dados_orcamento['telefone']}", 0, 1)
    pdf.cell(0, 10, f"Contato: {dados_orcamento['contato']}", 0, 1)
    pdf.ln(10)
    
    # Número do orçamento e data
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Orçamento Nº: {dados_orcamento['numero']}", 0, 1)
    pdf.cell(0, 10, f"Data: {dados_orcamento['data']}", 0, 1)
    pdf.ln(10)
    
    # Serviços
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Serviços:', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    for servico in dados_orcamento['servicos']:
        pdf.multi_cell(0, 10, f"- {servico['nome']}")
        if 'detalhes' in servico:
            for detalhe in servico['detalhes']:
                pdf.multi_cell(0, 10, f"  • {detalhe}")
    pdf.ln(10)
    
    # Valores
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Valores:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Subtotal: R$ {dados_orcamento['subtotal']:.2f}", 0, 1)
    
    if 'desconto' in dados_orcamento and dados_orcamento['desconto'] > 0:
        pdf.cell(0, 10, f"Desconto: R$ {dados_orcamento['desconto']:.2f}", 0, 1)
    
    if 'percentual_sesi' in dados_orcamento and dados_orcamento['percentual_sesi'] > 0:
        pdf.cell(0, 10, f"Percentual SESI: {dados_orcamento['percentual_sesi']}%", 0, 1)
        pdf.cell(0, 10, f"Valor SESI: R$ {dados_orcamento['valor_sesi']:.2f}", 0, 1)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Total: R$ {dados_orcamento['total']:.2f}", 0, 1)
    
    # Condições
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Condições:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, "1. Validade do orçamento: 30 dias\n2. Forma de pagamento: A combinar\n3. Prazo de execução: A definir após aprovação")
    
    # Salvar o PDF
    caminho_pdf = os.path.join('orcamentos', f"orcamento_{dados_orcamento['numero']}.pdf")
    pdf.output(caminho_pdf)
    
    return caminho_pdf

def gerar_corpo_email_orcamento(dados_orcamento):
    """
    Gera o corpo do email para envio do orçamento.
    
    Args:
        dados_orcamento (dict): Dados do orçamento
        
    Returns:
        str: Corpo do email em formato HTML
    """
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #333366; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .total {{ font-weight: bold; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Orçamento de Serviços</h1>
            <p>Prezado(a) {dados_orcamento['contato']},</p>
            <p>Segue o orçamento solicitado para a empresa {dados_orcamento['empresa']}.</p>
            
            <h2>Detalhes do Orçamento</h2>
            <p><strong>Número:</strong> {dados_orcamento['numero_orcamento']}</p>
            <p><strong>Data:</strong> {datetime.datetime.now().strftime('%d/%m/%Y')}</p>
            
            <h2>Serviços</h2>
            <table>
                <tr>
                    <th>Serviço</th>
                    <th>Região</th>
                    <th>Detalhes</th>
                    <th>Valor</th>
                </tr>
                {''.join([f"<tr><td>{s['nome']}</td><td>{s['regiao']}</td><td>{s.get('detalhes', '')}</td><td>{formatar_moeda(s['valor'])}</td></tr>" for s in dados_orcamento['servicos']])}
            </table>
            
            <p><strong>Subtotal:</strong> {formatar_moeda(dados_orcamento['subtotal'])}</p>
            <p><strong>SESI ({dados_orcamento['percentual_sesi']}%):</strong> {formatar_moeda(dados_orcamento['valor_sesi'])}</p>
            <p class="total"><strong>TOTAL:</strong> {formatar_moeda(dados_orcamento['total'])}</p>
            
            <h2>Observações</h2>
            <ol>
                <li>Este orçamento tem validade de 30 dias.</li>
                <li>O prazo de execução será definido após a aprovação do orçamento.</li>
                <li>O pagamento deverá ser realizado conforme condições acordadas.</li>
            </ol>
            
            <p>Em anexo, você encontrará o orçamento em formato PDF.</p>
            <p>Caso tenha alguma dúvida ou precise de mais informações, não hesite em nos contatar.</p>
            
            <p>Atenciosamente,<br>
            Equipe de Serviços</p>
        </div>
    </body>
    </html>
    """ 