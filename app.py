from flask import Flask, render_template, request, redirect, url_for, flash, session, json
import pandas as pd
import os
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import pathlib
import re
from dotenv import load_dotenv
from config import Config
from services.email_sender import init_mail, enviar_email_orcamento
from babel.numbers import format_currency

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Função para verificar a estrutura da planilha
def verificar_planilha():
    """
    Verifica a estrutura da planilha Excel e imprime informações úteis para debug
    """
    try:
        df = pd.read_excel(EXCEL_PATH)
        print(f"Caminho da planilha: {EXCEL_PATH}")
        print(f"Colunas na planilha: {df.columns.tolist()}")
        print(f"Número de linhas: {len(df)}")
        print("Primeiras linhas da planilha:")
        print(df.head())
        duplicados = df['Serviço'].duplicated().sum()
        print(f"Número de serviços duplicados: {duplicados}")
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
        
        if nome_servico == "Coleta para Avaliação Ambiental":
            if quantidade <= 4:
                return 300.00
            else:
                return 300.00 + (quantidade - 4) * 75.00
        
        elif nome_servico == "Ruído Limítrofe (NBR 10151)":
            if quantidade <= 4:
                return 200.00
            else:
                return 200.00 + (quantidade - 4) * 50.00
        
        elif nome_servico == "Relatório Técnico por Agente Ambiental":
            return 800.00 * quantidade
        
        elif nome_servico == "Revisão de Relatório Técnico (após 90 dias)":
            return 160.00 * quantidade
        
        elif nome_servico == "Laudo de Insalubridade":
            return 800.00 * quantidade
        
        elif nome_servico == "Revisão de Laudo de Insalubridade (após 90 dias)":
            return 160.00 * quantidade
        
        elif nome_servico == "LTCAT - Condições Ambientais de Trabalho":
            return 800.00 * quantidade
        
        elif nome_servico == "Revisão de LTCAT (após 90 dias)":
            return 160.00 * quantidade
        
        elif nome_servico == "Laudo de Periculosidade":
            return 1000.00 * quantidade
        
        elif nome_servico == "Revisão de Laudo de Periculosidade (após 90 dias)":
            return 200.00 * quantidade
        
        elif nome_servico == "Elaboração e acompanhamento do PGR":
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

verificar_planilha()

# Inicializar Flask-Mail (mantido para compatibilidade)
init_mail(app)

def carregar_dados_excel():
    """Carrega os dados das tabelas de precificação do arquivo Excel"""
    try:
        df_pgr = pd.read_excel(EXCEL_PATH, sheet_name='tabela_1')
        df_outros = pd.read_excel(EXCEL_PATH, sheet_name='tabela_5')
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
            print("Formulário recebido:")
            print(f"Dados do formulário: {request.form}")
            
            session.pop('servicos', None)
            session.pop('total_orcamento', None)
            session.pop('data_orcamento', None)
            
            cliente_email = request.form.get('cliente_email', '')
            empresa_cliente = request.form.get('empresa', '')
            
            servicos = []
            nomes = request.form.getlist('nome')
            detalhes = request.form.getlist('detalhes')
            quantidades = request.form.getlist('quantidade')
            unidades = request.form.getlist('unidade')
            empresas = request.form.getlist('servicos[][empresa]')
            regioes = request.form.getlist('regiao')
            
            print(f"Cliente email: {cliente_email}")
            print(f"Empresa do cliente: {empresa_cliente}")
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
                empresa = empresas[i] if i < len(empresas) and empresas[i] else empresa_cliente
                regiao = regioes[i] if i < len(regioes) else "Central"
                
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
            
            session['cliente_email'] = cliente_email
            session['empresa_cliente'] = empresa_cliente
            session['servicos'] = servicos
            session['total_orcamento'] = total_orcamento
            session['data_orcamento'] = datetime.now().strftime('%d/%m/%Y')
            
            return redirect(url_for('resumo'))
            
        except Exception as e:
            print(f"Erro ao processar o formulário: {e}")
            flash(f"Erro ao processar o formulário: {e}")
            return redirect(url_for('formulario'))
    
    servicos = obter_servicos()
    return render_template('formulario.html', servicos=servicos)

@app.route('/resumo')
def resumo():
    """Renderiza o resumo dos serviços antes de gerar o orçamento"""
    if 'servicos' not in session or 'cliente_email' not in session:
        flash("Dados de orçamento não encontrados. Por favor, preencha o formulário novamente.")
        return redirect(url_for('formulario'))
    
    cliente_email = session.get('cliente_email', '')
    empresa_cliente = session.get('empresa_cliente', '')
    servicos = session.get('servicos', [])
    
    return render_template('resumo.html', email=cliente_email, empresa_cliente=empresa_cliente, servicos=servicos)

@app.route('/gerar_orcamento', methods=['POST'])
def gerar_orcamento():
    """Gera o orçamento e envia por e-mail com base nos dados do resumo"""
    if 'servicos' not in session or 'cliente_email' not in session:
        flash("Dados de orçamento não encontrados. Por favor, preencha o formulário novamente.")
        return redirect(url_for('formulario'))
    
    cliente_email = session.get('cliente_email', '')
    empresa_cliente = session.get('empresa_cliente', '')
    servicos = session.get('servicos', [])
    total_orcamento = session.get('total_orcamento', 0)
    data_orcamento = session.get('data_orcamento', datetime.now().strftime('%d/%m/%Y'))
    
    # Formata os serviços para o e-mail
    servicos_formatados = []
    for servico in servicos:
        servico_formatado = servico.copy()
        servico_formatado['preco_unitario_formatado'] = format_currency(servico['preco_unitario'], 'BRL', locale='pt_BR')
        servico_formatado['preco_total_formatado'] = format_currency(servico['preco_total'], 'BRL', locale='pt_BR')
        servicos_formatados.append(servico_formatado)
    
    total_formatado = format_currency(total_orcamento, 'BRL', locale='pt_BR')
    
    # Envia o e-mail usando a função de email_sender.py
    sucesso, mensagem = enviar_email_orcamento(cliente_email, empresa_cliente, servicos_formatados, total_orcamento)
    
    if sucesso:
        flash("Orçamento enviado com sucesso para o seu e-mail!")
        return redirect(url_for('confirmacao'))
    else:
        flash(f"Erro ao enviar o orçamento: {mensagem}")
        return redirect(url_for('resumo'))

@app.route('/confirmacao')
def confirmacao():
    """Renderiza a página de confirmação após o envio do orçamento"""
    return render_template('confirmacao.html')

def explorar_planilha():
    """
    Explora a estrutura da planilha Excel e imprime informações detalhadas
    """
    try:
        excel_file = pd.ExcelFile(EXCEL_PATH)
        sheet_names = excel_file.sheet_names
        print(f"Planilhas disponíveis: {sheet_names}")
        
        for sheet_name in sheet_names:
            print(f"\n--- Planilha: {sheet_name} ---")
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)
            print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            print(f"Colunas: {df.columns.tolist()}")
            print("Primeiras 5 linhas:")
            print(df.head())
            if sheet_name == 'Tabela5' or 'tabela5' in sheet_name.lower():
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

explorar_planilha()

@app.route('/')
def index():
    """Página inicial do sistema"""
    return redirect(url_for('formulario'))

@app.route('/processar_formulario', methods=['POST'])
def processar_formulario():
    """Processa o formulário de orçamento"""
    if request.method == 'POST':
        cliente_email = request.form.get('cliente_email', '')
        empresa_cliente = request.form.get('empresa', '')
        
        servicos_form = []
        total_orcamento = 0
        
        servicos_keys = [k for k in request.form.keys() if k.startswith('servicos[')]
        if not servicos_keys:
            flash("Nenhum serviço foi adicionado ao orçamento.")
            return redirect(url_for('formulario'))
        
        indices = set()
        for key in servicos_keys:
            match = re.search(r'servicos\[(\d+)\]', key)
            if match:
                indices.add(int(match.group(1)))
        
        for i in sorted(indices):
            nome = request.form.get(f'servicos[{i}][nome]', '')
            if not nome:
                continue
                
            regiao = request.form.get(f'servicos[{i}][regiao]', '')
            quantidade = int(request.form.get(f'servicos[{i}][quantidade]', 1))
            preco_unitario = float(request.form.get(f'servicos[{i}][preco_unitario]', 0))
            preco_total = float(request.form.get(f'servicos[{i}][preco_total]', 0))
            
            grau_risco = None
            num_trabalhadores = None
            if nome == 'Elaboração e acompanhamento do PGR':
                grau_risco = request.form.get(f'servicos[{i}][grau_risco]', '')
                num_trabalhadores = request.form.get(f'servicos[{i}][num_trabalhadores]', '')
            
            servico = {
                'nome': nome,
                'empresa': empresa_cliente,
                'regiao': regiao,
                'quantidade': quantidade,
                'unidade': 'contrato',
                'preco_unitario': preco_unitario,
                'preco_total': preco_total
            }
            
            if grau_risco:
                servico['grau_risco'] = grau_risco
            if num_trabalhadores:
                servico['num_trabalhadores'] = num_trabalhadores
                
            servicos_form.append(servico)
            total_orcamento += preco_total
        
        if not servicos_form:
            flash("Nenhum serviço válido foi adicionado ao orçamento.")
            return redirect(url_for('formulario'))
        
        session['cliente_email'] = cliente_email
        session['empresa_cliente'] = empresa_cliente
        session['servicos'] = servicos_form
        session['total_orcamento'] = total_orcamento
        session['data_orcamento'] = datetime.now().strftime('%d/%m/%Y')
        
        return redirect(url_for('resumo'))
    
    return redirect(url_for('formulario'))

@app.route('/enviar_email/<int:orcamento_id>')
def enviar_email(orcamento_id):
    dados_orcamento = session.get('orcamento_data')
    if not dados_orcamento:
        flash('Dados do orçamento não encontrados.', 'danger')
        return redirect(url_for('formulario'))
    
    total = sum(s['preco_unitario'] * s['quantidade'] for s in dados_orcamento['servicos'])
    
    sucesso, mensagem = enviar_email_orcamento(
        destinatario=dados_orcamento['email'],
        empresa=dados_orcamento['empresa'],
        servicos=dados_orcamento['servicos'],
        total=total
    )
    
    categoria = 'success' if sucesso else 'danger'
    flash(mensagem, categoria)
    
    return redirect(url_for('orcamento', orcamento_id=orcamento_id))

# Configuração para Vercel
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)