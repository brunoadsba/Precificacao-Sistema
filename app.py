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
    """Verifica se os arquivos CSV existem"""
    pgr_path = os.path.join(os.path.dirname(__file__), 'Precos_PGR.csv.txt')
    ambientais_path = os.path.join(os.path.dirname(__file__), 'Precos_Ambientais.csv.txt')
    
    if not os.path.exists(pgr_path):
        return False, f"Arquivo não encontrado: {pgr_path}"
    
    if not os.path.exists(ambientais_path):
        return False, f"Arquivo não encontrado: {ambientais_path}"
    
    return True, "Arquivos CSV encontrados"

def obter_servicos():
    """Obtém a lista de serviços disponíveis a partir dos arquivos CSV"""
    servicos = set()
    
    # Carregar serviços do arquivo PGR
    pgr_path = os.path.join(os.path.dirname(__file__), 'Precos_PGR.csv.txt')
    if os.path.exists(pgr_path):
        try:
            df_pgr = pd.read_csv(pgr_path)
            servicos.update(df_pgr['Serviço'].unique())
        except Exception as e:
            app.logger.error(f"Erro ao ler arquivo PGR: {str(e)}")
    
    # Carregar serviços do arquivo Ambientais
    ambientais_path = os.path.join(os.path.dirname(__file__), 'Precos_Ambientais.csv.txt')
    if os.path.exists(ambientais_path):
        try:
            df_ambientais = pd.read_csv(ambientais_path)
            servicos.update(df_ambientais['Serviço'].unique())
        except Exception as e:
            app.logger.error(f"Erro ao ler arquivo Ambientais: {str(e)}")
    
    return sorted(list(servicos))

def carregar_dados_excel():
    """Carrega os dados dos arquivos CSV"""
    dados = {}
    
    # Carregar dados do arquivo PGR
    pgr_path = os.path.join(os.path.dirname(__file__), 'Precos_PGR.csv.txt')
    if os.path.exists(pgr_path):
        try:
            df_pgr = pd.read_csv(pgr_path)
            dados['pgr'] = df_pgr
        except Exception as e:
            app.logger.error(f"Erro ao ler arquivo PGR: {str(e)}")
    
    # Carregar dados do arquivo Ambientais
    ambientais_path = os.path.join(os.path.dirname(__file__), 'Precos_Ambientais.csv.txt')
    if os.path.exists(ambientais_path):
        try:
            df_ambientais = pd.read_csv(ambientais_path)
            dados['ambientais'] = df_ambientais
        except Exception as e:
            app.logger.error(f"Erro ao ler arquivo Ambientais: {str(e)}")
    
    return dados

def obter_preco_servico(nome_servico, quantidade=1, regiao="Central", variavel=None, grau_risco=None, num_trabalhadores=None):
    """Obtém o preço de um serviço com base nos parâmetros fornecidos"""
    try:
        dados = carregar_dados_excel()
        
        # Verificar se o serviço é PGR
        if "PGR" in nome_servico or nome_servico == "Elaboração e acompanhamento do PGR":
            if not grau_risco or not num_trabalhadores:
                return None, "Parâmetros incompletos para PGR"
            
            df = dados.get('pgr')
            if df is None:
                return None, "Dados de PGR não encontrados"
            
            # Filtrar por serviço, grau de risco e região
            filtro = (df['Serviço'] == nome_servico) & (df['Grau_Risco'] == grau_risco) & (df['Região'] == regiao)
            
            # Filtrar por faixa de trabalhadores
            faixa_trab_map = {
                'ate19': 'Até 19 Trab.',
                '20a50': '20 a 50 Trab.',
                '51a100': '51 a 100 Trab.',
                '101a160': '101 a 160 Trab.',
                '161a250': '161 a 250 Trab.',
                '251a300': '251 a 300 Trab.',
                '301a350': '301 a 350 Trab.',
                '351a400': '351 a 400 Trab.',
                '401a450': '401 a 450 Trab.',
                '451a500': '451 a 500 Trab.',
                '501a550': '501 a 550 Trab.',
                '551a600': '551 a 600 Trab.',
                '601a650': '601 a 650 Trab.',
                '651a700': '651 a 700 Trab.',
                '701a750': '701 a 750 Trab.',
                '751a800': '751 a 800 Trab.'
            }
            
            faixa_trab = faixa_trab_map.get(num_trabalhadores)
            if not faixa_trab:
                return None, f"Faixa de trabalhadores inválida: {num_trabalhadores}"
            
            filtro = filtro & (df['Faixa_Trab'] == faixa_trab)
            
            resultado = df[filtro]
            if resultado.empty:
                return None, f"Nenhum preço encontrado para os parâmetros: {nome_servico}, {grau_risco}, {regiao}, {faixa_trab}"
            
            preco = resultado['Preço'].iloc[0]
            return preco, "Preço encontrado com sucesso"
        
        # Verificar se é um serviço ambiental
        else:
            df = dados.get('ambientais')
            if df is None:
                return None, "Dados ambientais não encontrados"
            
            # Ajustar região para Sul e Extremo Sul se necessário
            regiao_ajustada = regiao
            if regiao in ["Sul", "Extremo Sul"]:
                regiao_ajustada = "Sul e Extremo Sul"
            
            # Filtrar por serviço e região
            filtro = (df['Serviço'] == nome_servico) & (df['Região'] == regiao_ajustada)
            
            # Se tiver variável, filtrar por tipo de avaliação
            if variavel:
                filtro = filtro & (df['Tipo_Avaliacao'] == variavel)
            
            resultado = df[filtro]
            if resultado.empty:
                return None, f"Nenhum preço encontrado para os parâmetros: {nome_servico}, {regiao_ajustada}, {variavel}"
            
            preco_base = resultado['Preço'].iloc[0]
            
            # Verificar se há adicional por GES/GHE
            adicional_ges_ghe = resultado['Adicional_GES_GHE'].iloc[0]
            
            # Por enquanto, não estamos aplicando o adicional, apenas retornando o preço base
            return preco_base, "Preço encontrado com sucesso"
    
    except Exception as e:
        app.logger.error(f"Erro ao obter preço: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, f"Erro ao obter preço: {str(e)}"

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
                
                preco_unitario, resultado = obter_preco_servico(nome, quantidade, regiao, variavel, grau_risco, num_trabalhador)
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
    
    # Carregar dados dos arquivos CSV
    dados = carregar_dados_excel()
    
    # Verificar se os dados foram carregados corretamente
    if not dados or not isinstance(dados, dict):
        flash("Erro ao carregar dados dos arquivos CSV", "error")
        return render_template('formulario.html', servicos=[], variaveis_disponiveis={})
    
    # Obter serviços disponíveis
    servicos = obter_servicos()
    
    # Preparar dicionário de variáveis disponíveis para cada serviço
    variaveis_disponiveis = {}
    
    # Para serviços PGR, não há variáveis específicas
    for servico in servicos:
        if "PGR" in servico:
            variaveis_disponiveis[servico] = []
            continue
        
        # Para serviços ambientais
        df_ambientais = dados.get('ambientais')
        if df_ambientais is not None and isinstance(df_ambientais, pd.DataFrame):
            # Filtrar por serviço
            filtro = df_ambientais['Serviço'] == servico
            resultado = df_ambientais[filtro]
            
            if not resultado.empty:
                # Obter valores únicos da coluna Tipo_Avaliacao
                variaveis = resultado['Tipo_Avaliacao'].unique().tolist()
                variaveis_disponiveis[servico] = variaveis
            else:
                variaveis_disponiveis[servico] = []
    
    return render_template('formulario.html', servicos=servicos, variaveis_disponiveis=variaveis_disponiveis)

@app.route('/resumo')
def resumo():
    """Renderiza o resumo dos serviços antes de gerar o orçamento"""
    if 'servicos' not in session or 'cliente_email' not in session:
        flash("Dados de orçamento não encontrados. Por favor, preencha o formulário novamente.")
        return redirect(url_for('formulario'))
    
    cliente_email = session.get('cliente_email', '')
    empresa_cliente = session.get('empresa_cliente', '')
    telefone_cliente = session.get('telefone_cliente', '')
    servicos = session.get('servicos', [])
    
    return render_template(
        'resumo.html',
        email=cliente_email,
        empresa_cliente=empresa_cliente,
        telefone=telefone_cliente,
        servicos=servicos
    )

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
    """Função para explorar os dados dos arquivos CSV (para debug)"""
    try:
        pgr_path = os.path.join(os.path.dirname(__file__), 'Precos_PGR.csv.txt')
        ambientais_path = os.path.join(os.path.dirname(__file__), 'Precos_Ambientais.csv.txt')
        
        resultado = {}
        
        # Explorar PGR
        if os.path.exists(pgr_path):
            df_pgr = pd.read_csv(pgr_path)
            resultado['pgr'] = {
                'colunas': df_pgr.columns.tolist(),
                'servicos': df_pgr['Serviço'].unique().tolist(),
                'graus_risco': df_pgr['Grau_Risco'].unique().tolist(),
                'faixas_trab': df_pgr['Faixa_Trab'].unique().tolist(),
                'regioes': df_pgr['Região'].unique().tolist(),
                'num_registros': len(df_pgr)
            }
        
        # Explorar Ambientais
        if os.path.exists(ambientais_path):
            df_ambientais = pd.read_csv(ambientais_path)
            resultado['ambientais'] = {
                'colunas': df_ambientais.columns.tolist(),
                'servicos': df_ambientais['Serviço'].unique().tolist(),
                'tipos_avaliacao': df_ambientais['Tipo_Avaliacao'].unique().tolist(),
                'regioes': df_ambientais['Região'].unique().tolist(),
                'num_registros': len(df_ambientais)
            }
        
        return resultado
    
    except Exception as e:
        app.logger.error(f"Erro ao explorar planilha: {str(e)}")
        return {'error': str(e)}

explorar_planilha()

@app.route('/')
def index():
    """Página inicial do sistema"""
    return redirect(url_for('formulario'))

@app.route('/processar_formulario', methods=['POST'])
def processar_formulario():
    """Processa o formulário de orçamento"""
    if request.method == 'POST':
        cliente_email = request.form.get('cliente_email')
        empresa_cliente = request.form.get('empresa')
        telefone_cliente = request.form.get('telefone', '')
        
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
        session['telefone_cliente'] = telefone_cliente
        session['servicos'] = servicos_form
        session['total_orcamento'] = total_orcamento
        session['data_orcamento'] = datetime.now().strftime('%d/%m/%Y')
        
        return redirect(url_for('resumo'))
    
    return redirect(url_for('formulario'))

@app.route('/calcular_preco')
def calcular_preco():
    """Calcula o preço de um serviço com base nos parâmetros da requisição"""
    servico = request.args.get('servico')
    regiao = request.args.get('regiao')
    variavel = request.args.get('variavel')
    grau_risco = request.args.get('grau_risco')
    num_trabalhadores = request.args.get('num_trabalhadores')
    
    if not servico or not regiao:
        return jsonify({'error': 'Parâmetros incompletos'}), 400
    
    preco, mensagem = obter_preco_servico(
        nome_servico=servico,
        regiao=regiao,
        variavel=variavel,
        grau_risco=grau_risco,
        num_trabalhadores=num_trabalhadores
    )
    
    if preco is None:
        return jsonify({'error': mensagem}), 404
    
    return jsonify({'preco': preco, 'mensagem': mensagem})

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
    """Obtém as variáveis disponíveis para um serviço específico"""
    servico = request.args.get('servico')
    if not servico:
        return jsonify({'error': 'Serviço não especificado'}), 400
    
    try:
        dados = carregar_dados_excel()
        
        # Se for PGR, não tem variáveis específicas
        if "PGR" in servico:
            return jsonify({'variaveis': []})
        
        # Para serviços ambientais
        df = dados.get('ambientais')
        if df is None:
            return jsonify({'error': 'Dados ambientais não encontrados'}), 404
        
        # Filtrar por serviço
        filtro = df['Serviço'] == servico
        resultado = df[filtro]
        
        if resultado.empty:
            return jsonify({'variaveis': []})
        
        # Obter valores únicos da coluna Tipo_Avaliacao
        variaveis = resultado['Tipo_Avaliacao'].unique().tolist()
        
        return jsonify({'variaveis': variaveis})
    
    except Exception as e:
        app.logger.error(f"Erro ao obter variáveis: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Configuração para Vercel
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)