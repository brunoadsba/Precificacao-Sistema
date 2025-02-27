from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import pathlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import re
from dotenv import load_dotenv
from config import Config
from services.email_sender import init_mail, enviar_email_orcamento
from babel.numbers import format_currency  # Nova importação para formatação de moeda

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Implementação direta da função de envio de e-mail
def enviar_email_orcamento(destinatario, assunto, corpo):
    """Envia um e-mail com o orçamento para o cliente usando smtplib diretamente"""
    try:
        # Configurações do servidor
        smtp_server = "smtp.gmail.com"
        port = 587  # Porta para TLS
        sender_email = os.environ.get('EMAIL_REMETENTE')
        password = os.environ.get('EMAIL_SENHA')
        
        print(f"Tentando enviar e-mail para {destinatario}")
        print(f"Usando credenciais: {sender_email}")
        
        # Cria a mensagem
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = destinatario
        msg['Subject'] = assunto
        
        # Adiciona o corpo HTML
        msg.attach(MIMEText(corpo, 'html', 'utf-8'))
        
        # Inicia a conexão com o servidor
        server = smtplib.SMTP(smtp_server, port)
        
        # Inicia o TLS
        server.starttls()
        
        # Login
        server.login(sender_email, password)
        
        # Envia o e-mail
        server.send_message(msg)
        
        # Encerra a conexão
        server.quit()
        
        print("E-mail enviado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Função para verificar a estrutura da planilha
def verificar_planilha():
    """
    Verifica a estrutura da planilha Excel e imprime informações úteis para debug
    """
    try:
        # Carrega a planilha
        df = pd.read_excel(EXCEL_PATH)
        
        # Imprime informações sobre a planilha
        print(f"Caminho da planilha: {EXCEL_PATH}")
        print(f"Colunas na planilha: {df.columns.tolist()}")
        print(f"Número de linhas: {len(df)}")
        
        # Imprime as primeiras linhas para verificar os dados
        print("Primeiras linhas da planilha:")
        print(df.head())
        
        # Verifica se há valores duplicados na coluna 'Serviço'
        duplicados = df['Serviço'].duplicated().sum()
        print(f"Número de serviços duplicados: {duplicados}")
        
        # Lista os serviços únicos
        servicos_unicos = df['Serviço'].unique().tolist()
        print(f"Serviços únicos ({len(servicos_unicos)}): {servicos_unicos}")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar planilha: {e}")
        return False

def obter_servicos():
    """
    Obtém a lista de serviços disponíveis
    
    Returns:
        list: Lista de nomes de serviços
    """
    # Lista de serviços definida manualmente
    servicos = [
        "Elaboração e acompanhamento do PGR",
        "Coleta para Avaliação Ambiental",
        "Ruído Limítrofe (NBR 10151)",
        "Relatório Técnico por Agente Ambiental",
        "Revisão de Relatório Técnico (após 90 dias)",
        "Laudo de Insalubridade",
        "Revisão de Laudo de Insalubridade (após 90 dias)",
        "LTCAT - Condições Ambientais de Trabalho",
        "Revisão de LTCAT (após 90 dias)",
        "Laudo de Periculosidade",
        "Revisão de Laudo de Periculosidade (após 90 dias)"
    ]
    
    print(f"Serviços disponíveis: {servicos}")
    return servicos

def obter_preco_servico(nome_servico, quantidade=1, regiao="Central"):
    """
    Obtém o preço de um serviço com base nas tabelas de preços
    
    Args:
        nome_servico: Nome do serviço
        quantidade: Quantidade do serviço
        regiao: Região onde o serviço será prestado
    
    Returns:
        float: Preço unitário do serviço
    """
    try:
        print(f"Buscando preço para: {nome_servico}, quantidade: {quantidade}, região: {regiao}")
        
        # Preços para serviços da Tabela 5
        if nome_servico == "Coleta para Avaliação Ambiental":
            if quantidade <= 4:
                return 300.00  # Preço para pacote de 1 a 4 avaliações na região Central
            else:
                return 300.00 + (quantidade - 4) * 75.00  # Preço base + avaliações adicionais
        
        elif nome_servico == "Ruído Limítrofe (NBR 10151)":
            if quantidade <= 4:
                return 200.00  # Preço para pacote de 1 a 4 avaliações na região Central
            else:
                return 200.00 + (quantidade - 4) * 50.00  # Preço base + avaliações adicionais
        
        elif nome_servico == "Relatório Técnico por Agente Ambiental":
            return 800.00 * quantidade  # Preço por relatório unitário
        
        elif nome_servico == "Revisão de Relatório Técnico (após 90 dias)":
            return 160.00 * quantidade  # Preço por relatório unitário
        
        elif nome_servico == "Laudo de Insalubridade":
            return 800.00 * quantidade  # Preço base
        
        elif nome_servico == "Revisão de Laudo de Insalubridade (após 90 dias)":
            return 160.00 * quantidade  # Preço base
        
        elif nome_servico == "LTCAT - Condições Ambientais de Trabalho":
            return 800.00 * quantidade  # Preço base
        
        elif nome_servico == "Revisão de LTCAT (após 90 dias)":
            return 160.00 * quantidade  # Preço base
        
        elif nome_servico == "Laudo de Periculosidade":
            return 1000.00 * quantidade  # Preço por laudo técnico
        
        elif nome_servico == "Revisão de Laudo de Periculosidade (após 90 dias)":
            return 200.00 * quantidade  # Preço por laudo técnico
        
        # Preços para Elaboração e acompanhamento do PGR
        elif nome_servico == "Elaboração e acompanhamento do PGR":
            # Preços para região Central baseados no número de trabalhadores
            if quantidade <= 19:
                return 700.00
            elif quantidade <= 50:
                return 850.00
            elif quantidade <= 100:
                return 1100.00
            elif quantidade <= 160:
                return 1900.00
            elif quantidade <= 250:
                return 2100.00
            elif quantidade <= 300:
                return 2300.00
            elif quantidade <= 350:
                return 2500.00
            elif quantidade <= 400:
                return 2550.00
            elif quantidade <= 450:
                return 2550.00
            elif quantidade <= 500:
                return 2675.00
            elif quantidade <= 550:
                return 3000.00
            elif quantidade <= 600:
                return 3225.00
            elif quantidade <= 650:
                return 3350.00
            elif quantidade <= 700:
                return 3425.00
            elif quantidade <= 750:
                return 3500.00
            else:
                return 3575.00
        
        # Se o serviço não for encontrado
        print(f"Serviço não encontrado nas tabelas de preços: {nome_servico}")
        return 0.0
        
    except Exception as e:
        print(f"Erro ao obter preço do serviço: {e}")
        return 0.0

# Inicialização do aplicativo Flask
app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)

# Caminho para o arquivo Excel usando caminhos relativos
BASE_DIR = pathlib.Path(__file__).parent
EXCEL_PATH = BASE_DIR / 'dados_precificacao_teste.xlsx'

# Agora podemos chamar verificar_planilha() após definir EXCEL_PATH
verificar_planilha()

# Inicializar Flask-Mail
init_mail(app)

def carregar_dados_excel():
    """Carrega os dados das tabelas de precificação do arquivo Excel"""
    try:
        # Carrega as duas abas da planilha
        df_pgr = pd.read_excel(EXCEL_PATH, sheet_name='tabela_1')
        df_outros = pd.read_excel(EXCEL_PATH, sheet_name='tabela_5')
        
        # Limpa os dados (remove NaN e linhas vazias)
        df_pgr = df_pgr.dropna(how='all')
        df_outros = df_outros.dropna(how='all')
        
        return df_pgr, df_outros
    except Exception as e:
        print(f"Erro ao carregar o arquivo Excel: {e}")
        return None, None

@app.route('/', methods=['GET', 'POST'])
def formulario():
    """Renderiza o formulário de orçamento e processa os dados enviados"""
    if request.method == 'POST':
        try:
            # Adicione logs para debug
            print("Formulário recebido:")
            print(f"Dados do formulário: {request.form}")
            
            # Limpa a sessão anterior
            session.pop('servicos', None)
            session.pop('total_orcamento', None)
            session.pop('data_orcamento', None)
            
            cliente_email = request.form.get('cliente_email', '')
            
            # Extrair os serviços do formulário
            servicos = []
            
            # Os campos vêm como listas no formulário
            nomes = request.form.getlist('nome')
            detalhes = request.form.getlist('detalhes')
            quantidades = request.form.getlist('quantidade')
            unidades = request.form.getlist('unidade')
            empresas = request.form.getlist('nome_empresa')
            regioes = request.form.getlist('regiao')  # Adicionado para capturar as regiões
            
            # Debug: imprima os dados recebidos
            print(f"Nomes: {nomes}")
            print(f"Detalhes: {detalhes}")
            print(f"Quantidades: {quantidades}")
            print(f"Unidades: {unidades}")
            print(f"Empresas: {empresas}")
            print(f"Regiões: {regioes}")
            
            if not nomes:
                flash("Nenhum serviço foi selecionado. Por favor, selecione pelo menos um serviço.")
                return redirect(url_for('formulario'))
            
            total_orcamento = 0
            
            for i in range(len(nomes)):
                nome = nomes[i]
                detalhe = detalhes[i] if i < len(detalhes) else ""
                quantidade = int(quantidades[i]) if i < len(quantidades) and quantidades[i].isdigit() else 1
                unidade = unidades[i] if i < len(unidades) else ""
                empresa = empresas[i] if i < len(empresas) else ""
                regiao = regioes[i] if i < len(regioes) else "Central"  # Usa a região selecionada ou Central como padrão
                
                # Calcula o preço usando a função que busca na planilha
                preco_unitario = obter_preco_servico(nome, quantidade, regiao)
                preco_total = preco_unitario * quantidade
                
                print(f"Serviço {i+1}: {nome}, Preço unitário: {preco_unitario}, Preço total: {preco_total}")
                
                total_orcamento += preco_total
                
                servicos.append({
                    'nome': nome,
                    'detalhes': detalhe,
                    'quantidade': quantidade,
                    'unidade': unidade,
                    'preco_unitario': preco_unitario,
                    'preco_total': preco_total,
                    'empresa': empresa,
                    'regiao': regiao
                })
            
            print(f"Total do orçamento: {total_orcamento}")
            print(f"Serviços processados: {servicos}")
            
            # Armazena na sessão para uso na página de orçamento
            session['cliente_email'] = cliente_email
            session['servicos'] = servicos
            session['total_orcamento'] = total_orcamento
            session['data_orcamento'] = datetime.now().strftime('%d/%m/%Y')
            
            # Redireciona para a página de orçamento
            return redirect(url_for('orcamento'))
            
        except Exception as e:
            print(f"Erro ao processar o formulário: {e}")
            flash(f"Erro ao processar o formulário: {e}")
            return redirect(url_for('formulario'))
    
    # Para GET, renderiza o formulário com a lista de serviços
    servicos = obter_servicos()
    return render_template('formulario.html', servicos=servicos)

@app.route('/orcamento')
def orcamento():
    """Renderiza a página de orçamento com base nos dados da sessão"""
    if 'servicos' not in session:
        flash("Dados de orçamento não encontrados. Por favor, preencha o formulário novamente.")
        return redirect(url_for('formulario'))
    
    # Recupera os dados da sessão
    cliente_email = session.get('cliente_email', '')
    servicos = session.get('servicos', [])
    total_orcamento = session.get('total_orcamento', 0)
    data_orcamento = session.get('data_orcamento', datetime.now().strftime('%d/%m/%Y'))
    
    print(f"Dados recuperados da sessão:")
    print(f"Cliente email: {cliente_email}")
    print(f"Serviços: {servicos}")
    print(f"Total: {total_orcamento}")
    
    # Formata os valores monetários com babel
    for servico in servicos:
        servico['preco_unitario_formatado'] = format_currency(servico['preco_unitario'], 'BRL', locale='pt_BR')
        servico['preco_total_formatado'] = format_currency(servico['preco_total'], 'BRL', locale='pt_BR')
    
    total_formatado = format_currency(total_orcamento, 'BRL', locale='pt_BR')
    
    return render_template(
        'orcamento.html', 
        cliente_email=cliente_email,
        servicos=servicos, 
        total_orcamento=total_formatado,
        data_orcamento=data_orcamento
    )

@app.route('/enviar_orcamento', methods=['POST'])
def enviar_orcamento():
    """Envia o orçamento por e-mail para o cliente"""
    if 'servicos' not in session:
        flash("Dados de orçamento não encontrados. Por favor, preencha o formulário novamente.")
        return redirect(url_for('formulario'))
    
    cliente_email = session.get('cliente_email', '')
    if not cliente_email:
        flash("E-mail do cliente não fornecido. Não é possível enviar o orçamento.")
        return redirect(url_for('orcamento'))
    
    # Recupera os dados da sessão
    servicos = session.get('servicos', [])
    total_orcamento = session.get('total_orcamento', 0)
    data_orcamento = session.get('data_orcamento', datetime.now().strftime('%d/%m/%Y'))
    
    # Imprime os dados para debug
    print("Dados recuperados da sessão:")
    print(f"Cliente email: {cliente_email}")
    print(f"Serviços: {servicos}")
    print(f"Total: {total_orcamento}")
    
    # Formata os valores monetários para o e-mail
    servicos_formatados = []
    for servico in servicos:
        servico_formatado = servico.copy()  # Cria uma cópia para não modificar o original na sessão
        servico_formatado['preco_unitario_formatado'] = format_currency(servico['preco_unitario'], 'BRL', locale='pt_BR')
        servico_formatado['preco_total_formatado'] = format_currency(servico['preco_total'], 'BRL', locale='pt_BR')
        servicos_formatados.append(servico_formatado)
    
    total_formatado = format_currency(total_orcamento, 'BRL', locale='pt_BR')
    
    # Cria o corpo do e-mail com design profissional
    corpo_email = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Orçamento de Serviços</title>
        <style>
            /* Estilos gerais */
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
            }}
            
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            
            /* Cabeçalho */
            .header {{
                text-align: center;
                padding: 20px 0;
                background-color: #0d6efd;
                color: white;
                border-radius: 8px 8px 0 0;
                margin-bottom: 20px;
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            
            .header p {{
                margin: 5px 0 0;
                font-size: 16px;
            }}
            
            /* Informações do cliente */
            .client-info {{
                margin-bottom: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }}
            
            /* Tabela de serviços */
            .services-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            
            .services-table th {{
                background-color: #0d6efd;
                color: white;
                text-align: left;
                padding: 12px;
            }}
            
            .services-table td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
            }}
            
            .services-table tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            
            .services-table tr:last-child td {{
                border-bottom: none;
            }}
            
            /* Alinhamento de texto */
            .text-left {{
                text-align: left;
            }}
            
            .text-center {{
                text-align: center;
            }}
            
            .text-right {{
                text-align: right;
            }}
            
            /* Total */
            .total {{
                margin-top: 20px;
                text-align: right;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: #e9ecef;
                border-radius: 4px;
            }}
            
            /* Validade */
            .validity {{
                margin-top: 20px;
                padding: 15px;
                background-color: #f8d7da;
                border-radius: 4px;
                color: #721c24;
            }}
            
            /* Rodapé */
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                text-align: center;
                font-size: 14px;
                color: #6c757d;
            }}
            
            .contact-button {{
                display: inline-block;
                margin: 15px 0;
                padding: 10px 20px;
                background-color: #28a745;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            
            /* Responsividade */
            @media (max-width: 600px) {{
                .container {{
                    padding: 10px;
                }}
                
                .header {{
                    padding: 15px 0;
                }}
                
                .services-table th,
                .services-table td {{
                    padding: 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Orçamento de Serviços</h1>
                <p>Data: {data_orcamento}</p>
            </div>
            
            <div class="client-info">
                <p><strong>Cliente:</strong> {cliente_email}</p>
            </div>
            
            <div class="services">
                <h2>Serviços Orçados</h2>
                
                <table class="services-table">
                    <thead>
                        <tr>
                            <th class="text-left">Serviço</th>
                            <th class="text-left">Empresa</th>
                            <th class="text-center">Quantidade</th>
                            <th class="text-right">Preço Unitário</th>
                            <th class="text-right">Preço Total</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    # Adiciona cada serviço à tabela
    for servico in servicos_formatados:
        corpo_email += f"""
                        <tr>
                            <td class="text-left">{servico['nome']}</td>
                            <td class="text-left">{servico['empresa']}</td>
                            <td class="text-center">{servico['quantidade']} {servico['unidade']}</td>
                            <td class="text-right">{servico['preco_unitario_formatado']}</td>
                            <td class="text-right">{servico['preco_total_formatado']}</td>
                        </tr>
        """
    
    # Finaliza a tabela e adiciona o total
    corpo_email += f"""
                    </tbody>
                </table>
                
                <div class="total">
                    <p>Total do Orçamento: {total_formatado}</p>
                </div>
                
                <div class="validity">
                    <p>Este orçamento é válido por 30 dias a partir da data de emissão.</p>
                </div>
            </div>
            
            <div class="footer">
                <p>Para mais informações ou para aceitar este orçamento, entre em contato conosco:</p>
                <p>WhatsApp: <a href="https://wa.me/5571987075563">(71) 9 8707-5563</a></p>
                <a href="https://wa.me/5571987075563" class="contact-button">Falar com um consultor</a>
                <p>© {datetime.now().year} BR Produções. Todos os direitos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Envia o e-mail
    assunto = f"Orçamento de Serviços - {data_orcamento}"
    enviado = enviar_email_orcamento(cliente_email, assunto, corpo_email)
    
    if enviado:
        flash("Orçamento enviado com sucesso para o seu e-mail!")
        return redirect(url_for('confirmacao'))
    else:
        flash("Erro ao enviar o orçamento por e-mail. Por favor, tente novamente.")
        return redirect(url_for('orcamento'))

@app.route('/confirmacao')
def confirmacao():
    """Renderiza a página de confirmação após o envio do orçamento"""
    return render_template('confirmacao.html')

def explorar_planilha():
    """
    Explora a estrutura da planilha Excel e imprime informações detalhadas
    """
    try:
        # Abre o arquivo Excel
        excel_file = pd.ExcelFile(EXCEL_PATH)
        
        # Lista todas as planilhas disponíveis
        sheet_names = excel_file.sheet_names
        print(f"Planilhas disponíveis: {sheet_names}")
        
        # Explora cada planilha
        for sheet_name in sheet_names:
            print(f"\n--- Planilha: {sheet_name} ---")
            
            # Lê a planilha
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)
            
            # Imprime informações básicas
            print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            print(f"Colunas: {df.columns.tolist()}")
            
            # Imprime as primeiras linhas
            print("Primeiras 5 linhas:")
            print(df.head())
            
            # Se for a Tabela5, extrai os serviços
            if sheet_name == 'Tabela5' or 'tabela5' in sheet_name.lower():
                # Tenta identificar a coluna que contém os serviços
                for col in df.columns:
                    valores = df[col].dropna().unique().tolist()
                    if len(valores) > 0:
                        print(f"Possíveis serviços na coluna '{col}':")
                        for valor in valores:
                            print(f"  - {valor}")
        
        return True
    except Exception as e:
        print(f"Erro ao explorar planilha: {e}")
        return False

# Chame esta função no início do aplicativo
explorar_planilha()

@app.route('/')
def index():
    """Página inicial do sistema"""
    return redirect(url_for('formulario'))

@app.route('/processar_formulario', methods=['POST'])
def processar_formulario():
    """Processa o formulário de orçamento"""
    if request.method == 'POST':
        # Obtém os dados do formulário
        cliente_email = request.form.get('cliente_email', '')
        empresa = request.form.get('empresa', 'BR Produções')
        
        # Processa os serviços
        servicos_form = []
        total_orcamento = 0
        
        # Verifica se há serviços no formulário
        servicos_keys = [k for k in request.form.keys() if k.startswith('servicos[')]
        if not servicos_keys:
            flash("Nenhum serviço foi adicionado ao orçamento.")
            return redirect(url_for('formulario'))
        
        # Determina o número de serviços
        indices = set()
        for key in servicos_keys:
            match = re.search(r'servicos\[(\d+)\]', key)
            if match:
                indices.add(int(match.group(1)))
        
        # Processa cada serviço
        for i in sorted(indices):
            nome = request.form.get(f'servicos[{i}][nome]', '')
            if not nome:
                continue
                
            regiao = request.form.get(f'servicos[{i}][regiao]', '')
            quantidade = int(request.form.get(f'servicos[{i}][quantidade]', 1))
            preco_unitario = float(request.form.get(f'servicos[{i}][preco_unitario]', 0))
            preco_total = float(request.form.get(f'servicos[{i}][preco_total]', 0))
            
            # Para o PGR, obtém os parâmetros adicionais
            grau_risco = None
            num_trabalhadores = None
            if nome == 'Elaboração e acompanhamento do PGR':
                grau_risco = request.form.get(f'servicos[{i}][grau_risco]', '')
                num_trabalhadores = request.form.get(f'servicos[{i}][num_trabalhadores]', '')
            
            servico = {
                'nome': nome,
                'empresa': empresa,
                'regiao': regiao,
                'quantidade': quantidade,
                'unidade': 'contrato',
                'preco_unitario': preco_unitario,
                'preco_total': preco_total
            }
            
            # Adiciona os parâmetros específicos do PGR, se aplicável
            if grau_risco:
                servico['grau_risco'] = grau_risco
            if num_trabalhadores:
                servico['num_trabalhadores'] = num_trabalhadores
                
            servicos_form.append(servico)
            total_orcamento += preco_total
        
        # Verifica se há serviços válidos
        if not servicos_form:
            flash("Nenhum serviço válido foi adicionado ao orçamento.")
            return redirect(url_for('formulario'))
        
        # Armazena os dados na sessão
        session['cliente_email'] = cliente_email
        session['empresa'] = empresa
        session['servicos'] = servicos_form
        session['total_orcamento'] = total_orcamento
        session['data_orcamento'] = datetime.now().strftime('%d/%m/%Y')
        
        return redirect(url_for('orcamento'))
    
    return redirect(url_for('formulario'))

@app.route('/enviar_email/<int:orcamento_id>')
def enviar_email(orcamento_id):
    # Recuperar dados do orçamento da sessão
    dados_orcamento = session.get('orcamento_data')
    if not dados_orcamento:
        flash('Dados do orçamento não encontrados.', 'danger')
        return redirect(url_for('formulario'))
    
    # Calcular total
    total = sum(s['preco_unitario'] * s['quantidade'] for s in dados_orcamento['servicos'])
    
    # Enviar e-mail
    sucesso, mensagem = enviar_email_orcamento(
        destinatario=dados_orcamento['email'],
        empresa=dados_orcamento['empresa'],
        servicos=dados_orcamento['servicos'],
        total=total
    )
    
    # Mostrar mensagem de sucesso ou erro
    categoria = 'success' if sucesso else 'danger'
    flash(mensagem, categoria)
    
    return redirect(url_for('orcamento', orcamento_id=orcamento_id))

# Configuração para Vercel (rodar na porta 3000 com waitress)
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)