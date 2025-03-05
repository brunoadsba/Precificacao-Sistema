from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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
        df_pgr, df_outros = carregar_dados_excel()
        print(f"Caminho da planilha: {EXCEL_PATH}")
        print("Aba PGR (tabela_1) - Colunas:", df_pgr.columns.tolist())
        print("Aba Outros Serviços (tabela_5) - Colunas:", df_outros.columns.tolist())
        print("Aba PGR (tabela_1) - Número de linhas:", len(df_pgr))
        print("Aba Outros Serviços (tabela_5) - Número de linhas:", len(df_outros))
        print("Primeiras linhas da Aba PGR (tabela_1):")
        print(df_pgr.head())
        print("Primeiras linhas da Aba Outros Serviços (tabela_5):")
        print(df_outros.head())
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

def carregar_dados_excel():
    """Carrega os dados das tabelas de precificação do arquivo Excel"""
    try:
        # Carrega as duas abas corretas do Excel: 'tabela_1' para PGR e 'tabela_5' para outros serviços
        df_pgr = pd.read_excel(EXCEL_PATH, sheet_name='tabela_1')
        df_outros = pd.read_excel(EXCEL_PATH, sheet_name='tabela_5')
        # Remove linhas completamente vazias
        df_pgr = df_pgr.dropna(how='all')
        df_outros = df_outros.dropna(how='all')
        return df_pgr, df_outros
    except Exception as e:
        print(f"Erro ao carregar o arquivo Excel: {e}")
        return None, None

def obter_preco_servico(nome_servico, quantidade=1, regiao="Central", variavel=None, grau_risco=None, num_trabalhadores=None):
    """
    Obtém o preço de um serviço com base nas tabelas de preços, incluindo Variável, Região/Instituto, Grau de Risco e Número de Trabalhadores
    
    Args:
        nome_servico: Nome do serviço
        quantidade: Quantidade do serviço (não usado aqui para PGR, retornamos o preço unitário)
        regiao: Região ou "Instituto" onde o serviço será prestado
        variavel: Tipo de variável (ex.: "Pacote (1 a 4 avaliações)", "Por Avaliação Adicional")
        grau_risco: Grau de risco (1 e 2 ou 3 e 4) para PGR
        num_trabalhadores: Faixa de trabalhadores para PGR (ex.: "ate19", "20a50", etc.)
    
    Returns:
        float: Preço unitário do serviço
    """
    try:
        print(f"Buscando preço para: {nome_servico}, quantidade: {quantidade}, região: {regiao}, variável: {variavel}, grau_risco: {grau_risco}, num_trabalhadores: {num_trabalhadores}")
        
        # Carrega os dados das duas abas
        df_pgr, df_outros = carregar_dados_excel()
        if df_pgr is None or df_outros is None:
            return 0.0
        
        # Define o mapeamento de regiões, incluindo "Instituto" como uma opção especial
        regioes = {
            "Central": "Central",
            "Norte": "Norte",
            "Oeste": "Oeste",
            "Sudeste": "Sudeste",
            "Sul": "Sul",
            "Extremo Sul": "Extremo Sul",
            "Instituto": "Instituto"  # Nova opção para usar o valor da coluna C
        }
        
        if nome_servico == "Elaboração e acompanhamento do PGR":
            # Filtra os dados para PGR com base em Grau de Risco e Número de Trabalhadores
            if not grau_risco or not num_trabalhadores:
                print(f"Parâmetros ausentes para PGR: grau_risco={grau_risco}, num_trabalhadores={num_trabalhadores}")
                return 0.0
            
            # Converte num_trabalhadores para o formato correto (ex.: "ate19" -> "Até 19 Trab.")
            num_trab_map = {
                "ate19": "Até 19 Trab.",
                "20a50": "20 a 50 Trab.",
                "51a100": "51 a 100 Trab.",
                "101a160": "101 a 160 Trab.",
                "161a250": "161 a 250 Trab.",
                "251a300": "251 a 300 Trab.",
                "301a350": "301 a 350 Trab.",
                "351a400": "351 a 400 Trab.",
                "401a450": "401 a 450 Trab.",
                "451a500": "451 a 500 Trab.",
                "501a550": "501 a 550 Trab.",
                "551a600": "551 a 600 Trab.",
                "601a650": "601 a 650 Trab.",
                "651a700": "651 a 700 Trab.",
                "701a750": "701 a 750 Trab.",
                "751a800": "751 a 800 Trab."
            }
            
            # Filtra os dados da aba tabela_1 (PGR), ignorando a variável (não usada para PGR)
            servico_data = df_pgr[(df_pgr['Grau de Risco'] == grau_risco) & (df_pgr['Variável'] == num_trab_map[num_trabalhadores])]
            if servico_data.empty:
                print(f"Dados não encontrados para PGR com Grau de Risco {grau_risco} e {num_trab_map[num_trabalhadores]}")
                return 0.0
            
            row = servico_data.iloc[0]
            
            if regiao == "Instituto":
                preco_base = float(str(row['Instituto']).replace('R$', '').replace('.', '').replace(',', '.')) if pd.notna(row['Instituto']) else 0.0
            else:
                # Ajuste para lidar com a coluna "Sul" na aba tabela_1 (PGR usa "Sul" para Sul e Extremo Sul)
                if regiao in ["Sul", "Extremo Sul"]:
                    preco_regiao = float(str(row['Sul']).replace('R$', '').replace('.', '').replace(',', '.')) if pd.notna(row['Sul']) else 0.0
                else:
                    preco_regiao = float(str(row[regioes[regiao]]).replace('R$', '').replace('.', '').replace(',', '.')) if pd.notna(row[regioes[regiao]]) else 0.0
                preco_base = preco_regiao
            
            # Para PGR, ignoramos a variável, pois ela não é usada
            variavel_valor = 0.0  # PGR não usa variável no seu caso
            
            # Adicional por GES/GHE (coluna D não existe na aba tabela_1, então ignoramos)
            adicional_ges_ghe = 0.0
            
            # Calcula o preço unitário base (sem multiplicar pela quantidade aqui)
            preco_base += adicional_ges_ghe + variavel_valor
            print(f"Preço unitário calculado para PGR: {preco_base}")
            return preco_base  # Retorna apenas o preço unitário, a multiplicação será feita no front-end
        
        else:
            # Para outros serviços, usa a aba "tabela_5"
            servico_data = df_outros[df_outros['Serviço'] == nome_servico]
            if servico_data.empty:
                print(f"Serviço não encontrado nas tabelas de preços: {nome_servico}")
                return 0.0
            
            # Filtra por variável, se fornecida
            if variavel:
                servico_data = servico_data[servico_data['Variável'] == variavel]
                if servico_data.empty:
                    print(f"Variável não encontrada para o serviço {nome_servico}: {variavel}")
                    return 0.0
            
            row = servico_data.iloc[0]
            
            if regiao == "Instituto":
                # Ajuste para garantir que o valor seja convertido corretamente (ex.: "R$ 352.00" -> 352.0, não 35200.0)
                preco_base = float(str(row['Instituto']).replace('R$', '').replace('.', '').replace(',', '.')) / 100 if pd.notna(row['Instituto']) else 0.0
            else:
                # Ajuste para lidar com a coluna "Sul e Extremo Sul" na aba tabela_5
                if regiao in ["Sul", "Extremo Sul"]:
                    preco_regiao = float(str(row['Sul e Extremo Sul']).replace('R$', '').replace('.', '').replace(',', '.')) / 100 if pd.notna(row['Sul e Extremo Sul']) else 0.0
                else:
                    preco_regiao = float(str(row[regioes[regiao]]).replace('R$', '').replace('.', '').replace(',', '.')) / 100 if pd.notna(row[regioes[regiao]]) else 0.0
                preco_base = preco_regiao
            
            # Obtém o Adicional por GES/GHE (coluna D), tratando "-" como 0.0
            adicional_ges_ghe = float(str(row['Adicional por GES/GHE']).replace('R$', '').replace('.', '').replace(',', '.').replace('-', '0')) / 100 if pd.notna(row['Adicional por GES/GHE']) else 0.0
            
            # Obtém a variável (coluna B) se fornecida
            variavel_valor = 0.0
            if variavel and pd.notna(row['Variável']) and variavel in str(row['Variável']):
                variavel_valor = float(str(row['Variável']).replace('R$', '').replace('.', '').replace(',', '.')) / 100 if pd.notna(row['Variável']) else 0.0
            
            # Calcula o preço base somando os componentes
            preco_base += adicional_ges_ghe + variavel_valor
            
            # Ajustes específicos por serviço (exceto PGR)
            if nome_servico == "Coleta para Avaliação Ambiental":
                if quantidade <= 4 and variavel == "Pacote (1 a 4 avaliações)":
                    return preco_base
                elif quantidade > 4 and variavel == "Por Avaliação Adicional":
                    return preco_base + (quantidade - 4) * variavel_valor
                else:
                    return preco_base
            
            elif nome_servico == "Ruído Limítrofe (NBR 10151)":
                if quantidade <= 4 and variavel == "Pacote (1 a 4 avaliações)":
                    return preco_base
                elif quantidade > 4 and variavel == "Por Avaliação Adicional":
                    return preco_base + (quantidade - 4) * variavel_valor
                else:
                    return preco_base
            
            elif nome_servico in ["Relatório Técnico por Agente Ambiental", "Revisão de Relatório Técnico (após 90 dias)",
                                 "Laudo de Insalubridade", "Revisão de Laudo de Insalubridade (após 90 dias)",
                                 "LTCAT - Condições Ambientais de Trabalho", "Revisão de LTCAT (após 90 dias)",
                                 "Laudo de Periculosidade", "Revisão de Laudo de Periculosidade (após 90 dias)"]:
                if variavel in ["Por Relatório Unitário", "Por Laudo Técnico"]:
                    return preco_base * quantidade
                elif variavel in ["Base + Adicional por GES/GHE"]:
                    return (preco_base + adicional_ges_ghe) * quantidade  # Inclui o adicional por quantidade
                elif variavel in ["Adicional por GES/GHE Revisado"]:
                    return adicional_ges_ghe * quantidade  # Apenas o adicional revisado, multiplicado pela quantidade
                else:
                    return preco_base * quantidade
            
            print(f"Serviço não encontrado nas tabelas de preços ou variável inválida: {nome_servico}, {variavel}")
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
            nomes = request.form.getlist('servicos[][nome]')
            quantidades = request.form.getlist('servicos[][quantidade]')
            regioes = request.form.getlist('servicos[][regiao]')
            variaveis = request.form.getlist('servicos[][variavel]')  # Campo para Variável
            grau_riscos = request.form.getlist('servicos[][grau_risco]')
            num_trabalhadores = request.form.getlist('servicos[][num_trabalhadores]')
            
            print(f"Cliente email: {cliente_email}")
            print(f"Empresa do cliente: {empresa_cliente}")
            print(f"Nomes: {nomes}")
            print(f"Quantidades: {quantidades}")
            print(f"Regiões: {regioes}")
            print(f"Variáveis: {variaveis}")
            print(f"Grau de Risco: {grau_risks}")
            print(f"Número de Trabalhadores: {num_trabalhadores}")
            
            if not nomes:
                flash("Nenhum serviço foi selecionado. Por favor, selecione pelo menos um serviço.")
                return redirect(url_for('formulario'))
            
            total_orcamento = 0
            
            for i in range(len(nomes)):
                nome = nomes[i]
                quantidade = int(quantidades[i]) if i < len(quantidades) and quantidades[i].isdigit() else 1
                regiao = regioes[i] if i < len(regioes) else "Central"
                variavel = variaveis[i] if i < len(variaveis) else None
                grau_risco = grau_risks[i] if i < len(grau_risks) else None
                num_trabalhador = num_trabalhadores[i] if i < len(num_trabalhadores) else None
                
                preco_unitario = obter_preco_servico(nome, quantidade, regiao, variavel, grau_risco, num_trabalhador)
                preco_total = preco_unitario * quantidade
                
                print(f"Serviço {i+1}: {nome}, Preço unitário: {preco_unitario}, Preço total: {preco_total}, Variável: {variavel}, Grau de Risco: {grau_risco}, Número de Trabalhadores: {num_trabalhador}")
                
                total_orcamento += preco_total
                
                servicos.append({
                    'nome': nome,
                    'quantidade': quantidade,
                    'preco_unitario': preco_unitario,
                    'preco_total': preco_total,
                    'empresa': empresa_cliente,
                    'regiao': regiao,
                    'variavel': variavel,  # Mantém a variável para rastreamento
                    'grau_risco': grau_risco,
                    'num_trabalhadores': num_trabalhador
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
    # Carrega as variáveis disponíveis para cada serviço do Excel
    df_pgr, df_outros = carregar_dados_excel()
    variaveis_disponiveis = {}
    if df_pgr is not None and df_outros is not None:
        for servico in servicos:
            if servico == "Elaboração e acompanhamento do PGR":
                variaveis = df_pgr['Variável'].dropna().unique().tolist()
            else:
                # Extrai todas as variáveis únicas para o serviço na tabela_5
                variaveis = df_outros[df_outros['Serviço'] == servico]['Variável'].dropna().unique().tolist()
            # Garante que as variáveis sejam exatamente as listadas
            validas = ["Pacote (1 a 4 avaliações)", "Por Avaliação Adicional", "Por Relatório Unitário",
                      "Base + Adicional por GES/GHE", "Adicional por GES/GHE Revisado", "Por Laudo Técnico"]
            variaveis_filtradas = [v for v in variaveis if v in validas]
            print(f"Variáveis disponíveis para {servico}: {variaveis_filtradas}")
            variaveis_disponiveis[servico] = variaveis_filtradas if variaveis_filtradas else [None]
    
    return render_template('formulario.html', servicos=servicos, variaveis_disponiveis=variaveis_disponiveis)

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
            quantidade = int(request.form.get(f'servicos[{i}][quantidade]', 1) or 1)
            variavel = request.form.get(f'servicos[{i}][variavel]', '')
            preco_unitario = float(request.form.get(f'servicos[{i}][preco_unitario]', 0))
            preco_total = float(request.form.get(f'servicos[{i}][preco_total]', 0))
            grau_risco = request.form.get(f'servicos[{i}][grau_risco]', '')
            num_trabalhadores = request.form.get(f'servicos[{i}][num_trabalhadores]', '')
            
            servico = {
                'nome': nome,
                'empresa': empresa_cliente,
                'regiao': regiao,
                'quantidade': quantidade,
                'unidade': 'contrato',
                'preco_unitario': preco_unitario,
                'preco_total': preco_total,
                'variavel': variavel,
                'grau_risco': grau_risco,
                'num_trabalhadores': num_trabalhadores
            }
            
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

@app.route('/calcular_preco')
def calcular_preco():
    """Calcula o preço dinamicamente com base nos parâmetros do formulário"""
    servico = request.args.get('servico', '')
    regiao = request.args.get('regiao', 'Central')
    variavel = request.args.get('variavel', '')
    quantidade = int(request.args.get('quantidade', 1))
    grau_risco = request.args.get('grau_risco', '')
    num_trabalhadores = request.args.get('num_trabalhadores', '')
    
    print(f"Parâmetros recebidos: servico={servico}, regiao={regiao}, variavel={variavel}, quantidade={quantidade}, grau_risco={grau_risco}, num_trabalhadores={num_trabalhadores}")
    
    preco_unitario = obter_preco_servico(servico, quantidade, regiao, variavel, grau_risco, num_trabalhadores)
    
    return jsonify({"preco_unitario": preco_unitario})

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

@app.route('/obter_variaveis')
def obter_variaveis():
    servico = request.args.get('servico', '')
    
    # Carregar os dados da planilha se ainda não foram carregados
    if not hasattr(app, 'dados_excel') or app.dados_excel is None:
        carregar_dados_excel()
    
    variaveis = []
    
    # Verificar se o serviço existe na tabela_5
    if 'tabela_5' in app.dados_excel:
        tabela_5 = app.dados_excel['tabela_5']
        # Filtrar as variáveis para o serviço selecionado
        for _, row in tabela_5.iterrows():
            if row.get('Serviço') == servico and pd.notna(row.get('Variável')):
                variaveis.append(row.get('Variável'))
    
    # Remover duplicatas e ordenar
    variaveis = sorted(list(set(variaveis)))
    
    return jsonify({'variaveis': variaveis})

# Configuração para Vercel
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)