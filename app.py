from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import pandas as pd
import os
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import pathlib
import re
from dotenv import load_dotenv
from config import Config
from services.email_sender import init_mail, enviar_email_orcamento, enviar_email_orcamento_pdf
from babel.numbers import format_currency
import json
import logging
from flask_session import Session  # Importar Flask-Session

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicialização do aplicativo Flask
app = Flask(__name__)
app.config.from_object(Config)
# Não precisamos sobrescrever a configuração da sessão, pois já está em Config
csrf = CSRFProtect(app)

# Inicializar a sessão do Flask
Session(app)

# Adicionar suporte a CORS
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

# Criar diretório para sessões se não existir e se estiver usando filesystem
if app.config['SESSION_TYPE'] == 'filesystem' and 'SESSION_FILE_DIR' in app.config:
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])

# Configurar logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Caminho para o arquivo Excel usando caminhos relativos
BASE_DIR = pathlib.Path(__file__).parent
EXCEL_PATH = BASE_DIR / 'dados_precificacao_teste.xlsx'

# Inicializar Flask-Mail
mail = init_mail(app)

# Função para verificar a estrutura da planilha
def verificar_planilha():
    """Verifica se os arquivos CSV existem"""
    pgr_path = os.path.join(os.path.dirname(__file__), 'Precos_PGR.csv')
    ambientais_path = os.path.join(os.path.dirname(__file__), 'Precos_Ambientais.csv')
    
    if not os.path.exists(pgr_path):
        return False, f"Arquivo não encontrado: {pgr_path}"
    
    if not os.path.exists(ambientais_path):
        return False, f"Arquivo não encontrado: {ambientais_path}"
    
    return True, "Arquivos CSV encontrados"

def obter_servicos():
    """Obtém a lista de serviços disponíveis a partir dos arquivos CSV"""
    servicos = set()
    
    # Carregar serviços do arquivo PGR
    pgr_path = os.path.join(os.path.dirname(__file__), 'Precos_PGR.csv')
    if os.path.exists(pgr_path):
        try:
            df_pgr = pd.read_csv(pgr_path)
            servicos.update(df_pgr['Serviço'].unique())
        except Exception as e:
            app.logger.error(f"Erro ao ler arquivo PGR: {str(e)}")
    
    # Carregar serviços do arquivo Ambientais
    ambientais_path = os.path.join(os.path.dirname(__file__), 'Precos_Ambientais.csv')
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
    pgr_path = os.path.join(os.path.dirname(__file__), 'Precos_PGR.csv')
    if os.path.exists(pgr_path):
        try:
            df_pgr = pd.read_csv(pgr_path)
            dados['pgr'] = df_pgr
        except Exception as e:
            app.logger.error(f"Erro ao ler arquivo PGR: {str(e)}")
    
    # Carregar dados do arquivo Ambientais
    ambientais_path = os.path.join(os.path.dirname(__file__), 'Precos_Ambientais.csv')
    if os.path.exists(ambientais_path):
        try:
            df_ambientais = pd.read_csv(ambientais_path)
            dados['ambientais'] = df_ambientais
        except Exception as e:
            app.logger.error(f"Erro ao ler arquivo Ambientais: {str(e)}")
    
    return dados

def obter_preco_servico(nome_servico, regiao=None, variavel=None, grau_risco=None, num_trabalhadores=None, num_ges_ghe=None, num_avaliacoes_adicionais=None):
    """Obtém o preço de um serviço com base nos parâmetros fornecidos"""
    try:
        app.logger.info(f"Buscando preço para: {nome_servico}, {regiao}, {variavel}, {grau_risco}, {num_trabalhadores}")
        
        # Verificar qual arquivo CSV usar
        if "PGR" in nome_servico:
            # Lógica para serviços PGR
            df = pd.read_csv('Precos_PGR.csv')
            
            # Filtrar por serviço, região e grau de risco
            # Verificar se o nome do serviço contém "Elaboração e acompanhamento do PGR"
            
            # Para serviços PGR, o nome no CSV é "Elaboração e acompanhamento do PGR"
            nome_servico_csv = "Elaboração e acompanhamento do PGR"
            
            # Verificar se o dataframe está vazio
            if df.empty:
                app.logger.error("Arquivo Precos_PGR.csv está vazio ou não foi carregado corretamente")
                return 0
                
            # Verificar se as colunas necessárias existem
            colunas_necessarias = ['Serviço', 'Região', 'Grau_Risco', 'Faixa_Trab', 'Preço']
            for coluna in colunas_necessarias:
                if coluna not in df.columns:
                    app.logger.error(f"Coluna {coluna} não encontrada no arquivo Precos_PGR.csv")
                    return 0
            
            # Verificar se o serviço existe no CSV
            if nome_servico_csv not in df['Serviço'].values:
                app.logger.error(f"Serviço '{nome_servico_csv}' não encontrado no arquivo Precos_PGR.csv")
                return 0
                
            # Verificar se a região existe no CSV
            if regiao and regiao not in df['Região'].values:
                app.logger.warning(f"Região '{regiao}' não encontrada no arquivo Precos_PGR.csv, tentando região Central")
                regiao = 'Central'
                
            # Verificar se o grau de risco existe no CSV
            if grau_risco and grau_risco not in df['Grau_Risco'].values:
                app.logger.warning(f"Grau de risco '{grau_risco}' não encontrado no arquivo Precos_PGR.csv")
                # Tentar converter o formato do grau de risco
                if grau_risco == "1e2":
                    grau_risco = "1 e 2"
                elif grau_risco == "3e4":
                    grau_risco = "3 e 4"
                
                if grau_risco not in df['Grau_Risco'].values:
                    app.logger.error(f"Grau de risco '{grau_risco}' não encontrado mesmo após conversão")
                    return 0
            
            # Iniciar o filtro com o serviço
            filtro = (df['Serviço'] == nome_servico_csv)
            
            # Adicionar filtro de região se fornecido
            if regiao:
                filtro = filtro & (df['Região'] == regiao)
            
            # Adicionar filtro de grau de risco se fornecido
            if grau_risco:
                # Converter o formato do grau de risco se necessário
                if grau_risco == "1e2":
                    grau_risco = "1 e 2"
                elif grau_risco == "3e4":
                    grau_risco = "3 e 4"
                
                filtro = filtro & (df['Grau_Risco'] == grau_risco)
            
            # Converter num_trabalhadores para o formato da coluna Faixa_Trab
            faixa_trab = None
            if num_trabalhadores:
                # Mapeamento de valores do formulário para valores do CSV
                mapeamento = {
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
                
                faixa_trab = mapeamento.get(num_trabalhadores)
                if not faixa_trab:
                    app.logger.warning(f"Faixa de trabalhadores não mapeada: {num_trabalhadores}")
                    if num_trabalhadores.startswith('Acima'):
                        faixa_trab = 'Acima de 101 Trab.'
            
            if faixa_trab:
                app.logger.info(f"Faixa de trabalhadores mapeada: {num_trabalhadores} -> {faixa_trab}")
                
                # Verificar se a faixa de trabalhadores existe no CSV
                if faixa_trab not in df['Faixa_Trab'].values:
                    app.logger.warning(f"Faixa de trabalhadores '{faixa_trab}' não encontrada no arquivo Precos_PGR.csv")
                    # Tentar encontrar uma faixa similar
                    faixas_disponiveis = df['Faixa_Trab'].unique()
                    app.logger.info(f"Faixas disponíveis: {faixas_disponiveis}")
                    
                    # Usar a primeira faixa disponível como fallback
                    if len(faixas_disponiveis) > 0:
                        faixa_trab = faixas_disponiveis[0]
                        app.logger.info(f"Usando faixa de trabalhadores '{faixa_trab}' como fallback")
                
                filtro = filtro & (df['Faixa_Trab'] == faixa_trab)
            
            # Aplicar filtro
            resultado = df[filtro]
            
            # Imprimir o resultado para debug
            app.logger.info(f"Resultado da busca: {len(resultado)} registros encontrados")
            if not resultado.empty:
                app.logger.info(f"Primeiro resultado: {resultado.iloc[0].to_dict()}")
            
            if resultado.empty:
                app.logger.warning(f"Nenhum resultado encontrado para PGR com filtros: {nome_servico_csv}, {regiao}, {grau_risco}, {faixa_trab}")
                
                # Tentar buscar na região Central como fallback
                filtro_central = (df['Serviço'] == nome_servico_csv)
                if regiao != 'Central':
                    filtro_central = filtro_central & (df['Região'] == 'Central')
                if grau_risco:
                    filtro_central = filtro_central & (df['Grau_Risco'] == grau_risco)
                if faixa_trab:
                    filtro_central = filtro_central & (df['Faixa_Trab'] == faixa_trab)
                
                resultado_central = df[filtro_central]
                if not resultado_central.empty:
                    app.logger.info(f"Usando preço da região Central como fallback")
                    resultado = resultado_central
                else:
                    # Se ainda não encontrar, tentar com qualquer faixa de trabalhadores
                    app.logger.warning(f"Tentando encontrar preço com qualquer faixa de trabalhadores")
                    filtro_qualquer_faixa = (df['Serviço'] == nome_servico_csv)
                    if regiao != 'Central':
                        filtro_qualquer_faixa = filtro_qualquer_faixa & (df['Região'] == regiao)
                    if grau_risco:
                        filtro_qualquer_faixa = filtro_qualquer_faixa & (df['Grau_Risco'] == grau_risco)
                    
                    resultado_qualquer_faixa = df[filtro_qualquer_faixa]
                    if not resultado_qualquer_faixa.empty:
                        app.logger.info(f"Usando primeira faixa de trabalhadores disponível")
                        resultado = resultado_qualquer_faixa.iloc[[0]]
                    else:
                        # Tentar com qualquer região e qualquer faixa
                        app.logger.warning(f"Tentando encontrar preço com qualquer região e qualquer faixa")
                        filtro_qualquer = (df['Serviço'] == nome_servico_csv)
                        if grau_risco:
                            filtro_qualquer = filtro_qualquer & (df['Grau_Risco'] == grau_risco)
                        
                        resultado_qualquer = df[filtro_qualquer]
                        if not resultado_qualquer.empty:
                            app.logger.info(f"Usando primeiro preço disponível")
                            resultado = resultado_qualquer.iloc[[0]]
                        else:
                            # Último recurso: usar qualquer preço disponível
                            app.logger.warning("Tentando usar qualquer preço disponível como último recurso")
                            if not df.empty:
                                resultado = df.iloc[[0]]
            
            if resultado.empty:
                app.logger.error(f"Nenhum preço encontrado para PGR: {nome_servico_csv}, {regiao}, {grau_risco}, {faixa_trab}")
                # Retornar um valor padrão para não quebrar a aplicação
                return 700.0
            
            # Obter o preço
            preco = resultado['Preço'].iloc[0]
            app.logger.info(f"Preço encontrado: {preco}")
            
            return preco
        else:
            # Lógica para serviços ambientais
            df = pd.read_csv('Precos_Ambientais.csv')
            
            # Filtrar por serviço e região
            filtro_regiao = (df['Serviço'] == nome_servico) & (df['Região'] == regiao)
            
            # Verificar se há resultados para a região
            if df[filtro_regiao].empty:
                app.logger.warning(f"Nenhum resultado para {nome_servico} na região {regiao}")
                
                # Tentar região Central como fallback
                filtro_regiao = (df['Serviço'] == nome_servico) & (df['Região'] == 'Central')
                
                if df[filtro_regiao].empty:
                    app.logger.error(f"Nenhum resultado para {nome_servico} na região Central (fallback)")
                    return 0
            
            # Filtrar por variável
            resultado = pd.DataFrame()
            if variavel:
                filtro_completo = filtro_regiao & (df['Tipo_Avaliacao'] == variavel)
                resultado = df[filtro_completo]
                
                # Se não encontrar com a variável específica, tentar outras variáveis
                if resultado.empty:
                    app.logger.warning(f"Nenhum resultado para variável {variavel}, tentando outras variáveis")
                    
                    # Listar todas as variáveis disponíveis para este serviço e região
                    variaveis_disponiveis = df[filtro_regiao]['Tipo_Avaliacao'].unique()
                    app.logger.info(f"Variáveis disponíveis: {variaveis_disponiveis}")
                    
                    # Tentar encontrar uma variável similar
                    variavel_encontrada = None
                    for var_disp in variaveis_disponiveis:
                        if variavel in var_disp or var_disp in variavel:
                            variavel_encontrada = var_disp
                            break
                    
                    if variavel_encontrada:
                        app.logger.info(f"Usando variável similar: {variavel_encontrada}")
                        filtro_completo = filtro_regiao & (df['Tipo_Avaliacao'] == variavel_encontrada)
                        resultado = df[filtro_completo]
                    else:
                        # Se não encontrar variável similar, usar a primeira disponível
                        if len(variaveis_disponiveis) > 0:
                            app.logger.info(f"Usando primeira variável disponível: {variaveis_disponiveis[0]}")
                            filtro_completo = filtro_regiao & (df['Tipo_Avaliacao'] == variaveis_disponiveis[0])
                            resultado = df[filtro_completo]
            else:
                # Se não especificar variável, usar a primeira disponível
                variaveis_disponiveis = df[filtro_regiao]['Tipo_Avaliacao'].unique()
                if len(variaveis_disponiveis) > 0:
                    app.logger.info(f"Nenhuma variável especificada, usando primeira disponível: {variaveis_disponiveis[0]}")
                    filtro_completo = filtro_regiao & (df['Tipo_Avaliacao'] == variaveis_disponiveis[0])
                    resultado = df[filtro_completo]
                else:
                    resultado = pd.DataFrame()
            
            if resultado.empty:
                app.logger.warning(f"Nenhum resultado encontrado após todas as tentativas")
                return 0
            
            # Obter o preço base
            preco = resultado['Preço'].iloc[0]
            app.logger.info(f"Preço base encontrado: {preco}")
            
            # Verificar se há custo adicional por GES/GHE
            adicional_ges_ghe = 0
            if 'Adicional_GES_GHE' in resultado.columns and num_ges_ghe and num_ges_ghe > 1:
                try:
                    valor_adicional = resultado['Adicional_GES_GHE'].iloc[0]
                    if pd.notna(valor_adicional) and valor_adicional > 0:
                        adicional_ges_ghe = valor_adicional * (num_ges_ghe - 1)
                        app.logger.info(f"Adicional GES/GHE: {adicional_ges_ghe} para {num_ges_ghe} GES/GHE")
                except:
                    app.logger.warning(f"Erro ao calcular adicional GES/GHE")
            
            # Verificar se há custo adicional por avaliações adicionais
            adicional_avaliacoes = 0
            if num_avaliacoes_adicionais and num_avaliacoes_adicionais > 0:
                # Verificar se há preço para avaliação adicional
                filtro_avaliacao_adicional = filtro_regiao & (df['Tipo_Avaliacao'] == 'Por Avaliação Adicional')
                resultado_avaliacao_adicional = df[filtro_avaliacao_adicional]
                
                if not resultado_avaliacao_adicional.empty:
                    preco_avaliacao_adicional = resultado_avaliacao_adicional['Preço'].iloc[0]
                    adicional_avaliacoes = preco_avaliacao_adicional * num_avaliacoes_adicionais
                    app.logger.info(f"Adicionando {num_avaliacoes_adicionais} avaliações adicionais ao pacote: R$ {adicional_avaliacoes}")
            
            # Calcular preço final
            preco_final = preco + adicional_ges_ghe + adicional_avaliacoes
            app.logger.info(f"Preço encontrado: {preco}, Adicional GES/GHE: {adicional_ges_ghe}, Preço Final: {preco_final}")
            
            return preco_final
    
    except Exception as e:
        app.logger.error(f"Erro ao obter preço do serviço: {str(e)}")
        import traceback
        traceback.print_exc()
        # Retornar um valor padrão para não quebrar a aplicação
        if "PGR" in nome_servico:
            return 700.0
        else:
            return 300.0

verificar_planilha()
# A função verificar_precos_csv() será chamada apenas no bloco if __name__ == "__main__"

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
            print(f"Grau de Risco: {grau_riscos}")
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
                grau_risco = grau_riscos[i] if i < len(grau_riscos) else None
                num_trabalhador = num_trabalhadores[i] if i < len(num_trabalhadores) else None
                
                # Obter os valores de GES/GHE e avaliações adicionais
                num_ges_ghe = request.form.getlist('servicos[][num_ges_ghe]')[i] if i < len(request.form.getlist('servicos[][num_ges_ghe]')) else None
                num_avaliacoes_adicionais = request.form.getlist('servicos[][quantidade_avaliacoes]')[i] if i < len(request.form.getlist('servicos[][quantidade_avaliacoes]')) else None
                
                preco_unitario = obter_preco_servico(nome, regiao=regiao, variavel=variavel, grau_risco=grau_risco, num_trabalhadores=num_trabalhador, num_ges_ghe=num_ges_ghe, num_avaliacoes_adicionais=num_avaliacoes_adicionais)
                preco_total = preco_unitario * quantidade if preco_unitario else 0
                
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
            
            return redirect(url_for('resumo_view'))
            
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
    
    # Definir uma região padrão para buscar variáveis iniciais
    regiao_padrao = "Central"
    
    # Para serviços PGR, não há variáveis específicas
    for servico in servicos:
        if "PGR" in servico:
            variaveis_disponiveis[servico] = []
            continue
        
        # Para serviços ambientais
        df_ambientais = dados.get('ambientais')
        if df_ambientais is not None and isinstance(df_ambientais, pd.DataFrame):
            # Filtrar por serviço e região padrão
            filtro = (df_ambientais['Serviço'] == servico) & (df_ambientais['Região'] == regiao_padrao)
            resultado = df_ambientais[filtro]
            
            if not resultado.empty:
                # Obter valores únicos da coluna Tipo_Avaliacao
                variaveis = resultado['Tipo_Avaliacao'].unique().tolist()
                variaveis_disponiveis[servico] = variaveis
            else:
                variaveis_disponiveis[servico] = []
    
    return render_template('formulario.html', servicos=servicos, variaveis_disponiveis=variaveis_disponiveis)

def gerar_numero_orcamento():
    """
    Gera um número de orçamento baseado na data atual e um contador sequencial.
    Formato: DD-MM-AAAA-XXXX (onde XXXX é um número sequencial)
    """
    from datetime import datetime
    import os
    import json
    
    # Obter a data atual
    data_atual = datetime.now()
    data_formatada = data_atual.strftime("%d-%m-%Y")
    
    # Caminho para o arquivo de contagem
    contador_path = os.path.join(app.config['SESSION_FILE_DIR'], 'contador_orcamento.json')
    
    # Verificar se o arquivo existe e carregar o contador
    contador = 1
    data_anterior = ""
    
    if os.path.exists(contador_path):
        try:
            with open(contador_path, 'r') as f:
                dados = json.load(f)
                data_anterior = dados.get('data', '')
                contador = dados.get('contador', 1)
                
                # Se a data mudou, reiniciar o contador
                if data_anterior != data_formatada:
                    contador = 1
                else:
                    contador += 1
        except:
            # Em caso de erro, usar valores padrão
            contador = 1
    
    # Salvar o novo contador
    try:
        with open(contador_path, 'w') as f:
            json.dump({
                'data': data_formatada,
                'contador': contador
            }, f)
    except:
        app.logger.error("Erro ao salvar contador de orçamento")
    
    # Formatar o número do orçamento: DD-MM-AAAA-XXXX
    numero_orcamento = f"{data_formatada}-{contador:04d}"
    
    return numero_orcamento

@app.route('/resumo')
@app.route('/resumo_view')
def resumo_view():
    try:
        # Verificar se há dados na sessão
        if 'servicos' not in session or not session['servicos']:
            app.logger.error("Dados de serviços não encontrados na sessão")
            flash("Não há dados de orçamento disponíveis. Por favor, preencha o formulário novamente.")
            return redirect(url_for('formulario'))
        
        # Obter dados da sessão
        servicos = session.get('servicos', [])
        email = session.get('cliente_email', '')  # Alterado para 'cliente_email' para consistência
        telefone = session.get('telefone', '')
        empresa_cliente = session.get('empresa_cliente', '')
        subtotal_orcamento = session.get('subtotal_orcamento', 0)
        valor_sesi = session.get('valor_sesi', 0)
        total_orcamento = session.get('total_orcamento', 0)
        percentual_sesi = session.get('percentual_sesi', 30)
        
        app.logger.info(f"Exibindo resumo para {empresa_cliente} com {len(servicos)} serviços")
        
        # Formatar valores monetários
        subtotal_formatado = f"R$ {subtotal_orcamento:.2f}".replace('.', ',')
        valor_sesi_formatado = f"R$ {valor_sesi:.2f}".replace('.', ',')
        total_formatado = f"R$ {total_orcamento:.2f}".replace('.', ',')
        
        # Gerar número do orçamento
        numero_orcamento = gerar_numero_orcamento()
        
        # Armazenar número do orçamento na sessão
        session['numero_orcamento'] = numero_orcamento
        session.modified = True
        
        return render_template(
            'resumo.html',
            servicos=servicos,
            email=email,
            telefone=telefone,
            empresa_cliente=empresa_cliente,
            subtotal=subtotal_formatado,
            valor_sesi=valor_sesi_formatado,
            total=total_formatado,
            percentual_sesi=percentual_sesi,
            numero_orcamento=numero_orcamento
        )
    except Exception as e:
        app.logger.error(f"Erro ao exibir resumo: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Erro ao exibir resumo: {str(e)}")
        return redirect(url_for('formulario'))

def gerar_pdf_orcamento(dados):
    """
    Gera um PDF com os dados do orçamento.
    
    Args:
        dados: Dicionário com os dados do orçamento
        
    Returns:
        Tupla com (BytesIO contendo o PDF, nome do arquivo)
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        import os
        from io import BytesIO
        
        # Criar um buffer de memória para o PDF
        buffer = BytesIO()
        
        # Nome do arquivo para download
        filename = f"orcamento_{dados['numero_orcamento']}.pdf"
        
        # Criar documento no buffer de memória
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        # Em vez de adicionar um novo estilo 'Normal', vamos criar estilos com nomes diferentes
        styles.add(ParagraphStyle(name='Titulo', fontSize=16, alignment=1, spaceAfter=12))
        styles.add(ParagraphStyle(name='Subtitulo', fontSize=14, alignment=0, spaceAfter=10))
        styles.add(ParagraphStyle(name='TextoNormal', fontSize=12, alignment=0, spaceAfter=8))
        styles.add(ParagraphStyle(name='Destaque', fontSize=12, alignment=0, spaceAfter=8, textColor=colors.blue))
        styles.add(ParagraphStyle(name='DetalheServico', fontSize=11, alignment=0, spaceAfter=8, leftIndent=20))
        styles.add(ParagraphStyle(name='AssinaturaLinha', fontSize=12, alignment=1, spaceAfter=0))
        
        # Título
        elements.append(Paragraph(f"ORÇAMENTO Nº {dados['numero_orcamento']}", styles['Titulo']))
        elements.append(Paragraph(f"Data: {dados['data']}", styles['TextoNormal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Dados do cliente
        elements.append(Paragraph("DADOS DO CLIENTE", styles['Subtitulo']))
        elements.append(Paragraph(f"<b>Empresa:</b> {dados['empresa_cliente']}", styles['TextoNormal']))
        
        # Garantir que o e-mail seja exibido mesmo se estiver vazio
        email_cliente = dados['email'] if dados['email'] else "Não informado"
        elements.append(Paragraph(f"<b>E-mail:</b> {email_cliente}", styles['TextoNormal']))
        
        if dados['telefone']:
            elements.append(Paragraph(f"<b>Telefone:</b> {dados['telefone']}", styles['TextoNormal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Serviços
        elements.append(Paragraph("SERVIÇOS", styles['Subtitulo']))
        
        for i, servico in enumerate(dados['servicos']):
            elements.append(Paragraph(f"<b>Serviço {i+1}:</b> {servico['nome']}", styles['Destaque']))
            
            # Melhorar a formatação dos detalhes do serviço
            if servico.get('detalhes'):
                # Dividir os detalhes em linhas para melhor formatação
                detalhes_texto = servico['detalhes']
                
                # Formatar o texto dos detalhes para adicionar espaço entre "1" e "2" e complementar "Até 19" com "trabalhadores"
                detalhes_texto = detalhes_texto.replace("1e2", "1 e 2")
                detalhes_texto = detalhes_texto.replace("Até 19", "Até 19 trabalhadores")
                
                # Verificar se há custos adicionais nos detalhes
                if "Custos adicionais" in detalhes_texto:
                    # Separar os custos adicionais para formatação especial
                    partes = detalhes_texto.split("Custos adicionais:")
                    detalhes_principais = partes[0].strip()
                    custos_adicionais = partes[1].strip() if len(partes) > 1 else ""
                    
                    # Formatar os detalhes principais
                    elements.append(Paragraph(f"<b>Detalhes:</b>", styles['TextoNormal']))
                    for linha in detalhes_principais.split('. '):
                        if linha.strip():
                            elements.append(Paragraph(f"• {linha.strip()}", styles['DetalheServico']))
                    
                    # Formatar os custos adicionais
                    if custos_adicionais:
                        elements.append(Paragraph(f"<b>Custos adicionais:</b>", styles['TextoNormal']))
                        for linha in custos_adicionais.split(','):
                            if linha.strip():
                                elements.append(Paragraph(f"• {linha.strip()}", styles['DetalheServico']))
                else:
                    # Se não houver custos adicionais, formatar normalmente
                    elements.append(Paragraph(f"<b>Detalhes:</b>", styles['TextoNormal']))
                    for linha in detalhes_texto.split('. '):
                        if linha.strip():
                            elements.append(Paragraph(f"• {linha.strip()}", styles['DetalheServico']))
            
            # Tabela com informações do serviço
            data = [
                ["Quantidade", "Unidade", "Preço Unitário", "Preço Total"],
                [
                    str(servico['quantidade']), 
                    servico['unidade'], 
                    servico['preco_unitario_formatado'], 
                    servico['preco_total_formatado']
                ]
            ]
            
            t = Table(data, colWidths=[1.2*inch, 1.2*inch, 1.5*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (3, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (3, 0), colors.black),
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (3, 0), 12),
                ('BOTTOMPADDING', (0, 0), (3, 0), 12),
                ('BACKGROUND', (0, 1), (3, 1), colors.white),
                ('TEXTCOLOR', (0, 1), (3, 1), colors.black),
                ('ALIGN', (0, 1), (3, 1), 'CENTER'),
                ('FONTNAME', (0, 1), (3, 1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (3, 1), 10),
                ('GRID', (0, 0), (3, 1), 1, colors.black)
            ]))
            
            elements.append(t)
            elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Resumo financeiro
        elements.append(Paragraph("RESUMO FINANCEIRO", styles['Subtitulo']))
        
        # Tabela com resumo financeiro
        subtotal_formatado = f"R$ {dados['subtotal']:.2f}".replace('.', ',')
        valor_sesi_formatado = f"R$ {dados['valor_sesi']:.2f}".replace('.', ',')
        total_formatado = f"R$ {dados['total']:.2f}".replace('.', ',')
        
        data = [
            ["Descrição", "Valor"],
            ["Subtotal", subtotal_formatado],
            [f"Percentual Indireto SESI ({dados['percentual_sesi']}%)", valor_sesi_formatado],
            ["TOTAL", total_formatado]
        ]
        
        t = Table(data, colWidths=[4*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, 2), colors.white),
            ('TEXTCOLOR', (0, 1), (1, 2), colors.black),
            ('ALIGN', (0, 1), (0, 3), 'LEFT'),
            ('ALIGN', (1, 1), (1, 3), 'RIGHT'),
            ('FONTNAME', (0, 1), (1, 2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (1, 2), 10),
            ('BACKGROUND', (0, 3), (1, 3), colors.lightblue),
            ('TEXTCOLOR', (0, 3), (1, 3), colors.black),
            ('FONTNAME', (0, 3), (1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (1, 3), 12),
            ('GRID', (0, 0), (1, 3), 1, colors.black)
        ]))
        
        elements.append(t)
        
        # Observações
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("OBSERVAÇÕES", styles['Subtitulo']))
        elements.append(Paragraph("1. Este orçamento tem validade de 30 dias.", styles['TextoNormal']))
        elements.append(Paragraph("2. O pagamento deve ser realizado conforme condições acordadas.", styles['TextoNormal']))
        elements.append(Paragraph("3. Os serviços serão agendados após a confirmação do orçamento.", styles['TextoNormal']))
        
        # Adicionar espaço antes da linha de assinatura
        elements.append(Spacer(1, 1*inch))
        
        # Adicionar linha para assinatura
        elements.append(HRFlowable(width="60%", thickness=1, lineCap='round', color=colors.black, spaceBefore=0, spaceAfter=1, hAlign='CENTER'))
        elements.append(Paragraph("Responsável Técnico", styles['AssinaturaLinha']))
        
        # Construir o documento
        doc.build(elements)
        
        # Retornar ao início do buffer
        buffer.seek(0)
        
        app.logger.info(f"PDF gerado com sucesso em memória para orçamento {dados['numero_orcamento']}")
        return buffer, filename
        
    except Exception as e:
        app.logger.error(f"Erro ao gerar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None

@app.route('/gerar_orcamento', methods=['POST'])
def gerar_orcamento():
    try:
        app.logger.info("Iniciando função gerar_orcamento")
        
        # Verificar se há dados na sessão
        if 'servicos' not in session or not session['servicos']:
            app.logger.error("Dados de serviços não encontrados na sessão")
            flash("Não há dados de orçamento disponíveis. Por favor, preencha o formulário novamente.")
            return redirect(url_for('formulario'))
        
        # Obter dados da sessão
        servicos = session.get('servicos', [])
        email = session.get('cliente_email', '')  # Alterado para 'cliente_email' para consistência
        telefone = session.get('telefone', '')
        empresa_cliente = session.get('empresa_cliente', '')
        subtotal_orcamento = session.get('subtotal_orcamento', 0)
        valor_sesi = session.get('valor_sesi', 0)
        total_orcamento = session.get('total_orcamento', 0)
        percentual_sesi = session.get('percentual_sesi', 30)
        numero_orcamento = session.get('numero_orcamento', gerar_numero_orcamento())
        
        app.logger.info(f"Gerando orçamento {numero_orcamento} para {empresa_cliente}")
        app.logger.info(f"Email: {email}, Telefone: {telefone}")
        app.logger.info(f"Serviços: {len(servicos)}, Total: {total_orcamento}")
        
        # Criar dados para o PDF
        dados_orcamento = {
            'numero_orcamento': numero_orcamento,
            'data': datetime.now().strftime("%d/%m/%Y"),
            'empresa_cliente': empresa_cliente,
            'email': email,
            'telefone': telefone,
            'servicos': servicos,
            'subtotal': subtotal_orcamento,
            'percentual_sesi': percentual_sesi,
            'valor_sesi': valor_sesi,
            'total': total_orcamento
        }
        
        app.logger.info("Chamando função gerar_pdf_orcamento")
        # Gerar o PDF em memória
        pdf_buffer, filename = gerar_pdf_orcamento(dados_orcamento)
        
        if not pdf_buffer:
            app.logger.error(f"Falha ao gerar PDF do orçamento {numero_orcamento}")
            flash("Erro ao gerar o PDF do orçamento. Por favor, tente novamente.")
            return redirect(url_for('resumo_view'))
        
        app.logger.info(f"PDF gerado com sucesso em memória")
        
        # Verificar se estamos em ambiente de produção (Vercel)
        is_vercel = os.environ.get('VERCEL', False)
        
        # Enviar e-mail com o orçamento, se o e-mail estiver disponível
        if email:
            try:
                # Usar a função enviar_email_orcamento_pdf com todos os dados do orçamento
                app.logger.info(f"Enviando e-mail para {email}")
                
                # Verificar se as credenciais de e-mail estão configuradas
                email_remetente = os.environ.get('EMAIL_REMETENTE')
                email_senha = os.environ.get('EMAIL_SENHA')
                
                if not email_remetente or not email_senha:
                    app.logger.error("Credenciais de e-mail não configuradas")
                    session['email_enviado'] = False
                    session['erro_email'] = "Credenciais de e-mail não configuradas"
                else:
                    # Modificar a função enviar_email_orcamento_pdf para aceitar BytesIO em vez de caminho de arquivo
                    try:
                        from services.email_sender import enviar_email_orcamento_pdf_buffer
                        
                        # Tentar usar a nova função se existir
                        sucesso, mensagem = enviar_email_orcamento_pdf_buffer(
                            email, 
                            pdf_buffer, 
                            filename,
                            numero_orcamento, 
                            empresa_cliente,
                            servicos=servicos,
                            subtotal=subtotal_orcamento,
                            valor_sesi=valor_sesi,
                            total=total_orcamento,
                            percentual_sesi=percentual_sesi
                        )
                    except (ImportError, AttributeError):
                        # Fallback: salvar temporariamente o arquivo
                        import tempfile
                        
                        # Criar diretório temporário se não existir
                        temp_dir = os.path.join(tempfile.gettempdir(), 'orcamentos_pdf')
                        os.makedirs(temp_dir, exist_ok=True)
                        
                        # Salvar o PDF temporariamente
                        temp_pdf_path = os.path.join(temp_dir, filename)
                        with open(temp_pdf_path, 'wb') as f:
                            f.write(pdf_buffer.getvalue())
                        
                        # Usar a função existente com o caminho do arquivo
                        from services.email_sender import enviar_email_orcamento_pdf
                        sucesso, mensagem = enviar_email_orcamento_pdf(
                            email, 
                            temp_pdf_path, 
                            numero_orcamento, 
                            empresa_cliente,
                            servicos=servicos,
                            subtotal=subtotal_orcamento,
                            valor_sesi=valor_sesi,
                            total=total_orcamento,
                            percentual_sesi=percentual_sesi
                        )
                        
                        # Remover o arquivo temporário após o envio
                        try:
                            os.remove(temp_pdf_path)
                        except:
                            pass
                    
                    if sucesso:
                        app.logger.info(f"E-mail enviado para {email} com o orçamento {numero_orcamento}")
                        # Salvar na sessão que o e-mail foi enviado com sucesso
                        session['email_enviado'] = True
                    else:
                        app.logger.error(f"Erro ao enviar e-mail: {mensagem}")
                        session['email_enviado'] = False
                        session['erro_email'] = mensagem
            except Exception as e:
                app.logger.error(f"Erro ao enviar e-mail: {str(e)}")
                session['email_enviado'] = False
                session['erro_email'] = str(e)
        
        # Salvar na sessão que o orçamento foi gerado com sucesso
        session['orcamento_gerado'] = True
        session['numero_orcamento'] = numero_orcamento
        
        # Retornar o PDF para download a partir do buffer de memória
        pdf_buffer.seek(0)  # Garantir que estamos no início do buffer
        
        # Configurar o cabeçalho para redirecionar após o download
        response = send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"Orcamento_{numero_orcamento}_{empresa_cliente.replace(' ', '_')}.pdf",
            mimetype='application/pdf'
        )
        
        # Adicionar um script JavaScript para redirecionar após o download
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Definir um cookie para indicar que o download foi iniciado
        response.set_cookie('download_iniciado', 'true')
        
        return response
        
    except Exception as e:
        app.logger.error(f"Erro ao gerar orçamento: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Erro ao gerar orçamento: {str(e)}")
        return redirect(url_for('resumo_view'))

@app.route('/confirmacao')
def confirmacao():
    """Renderiza a página de confirmação após o envio do orçamento"""
    # Obter informações da sessão para exibir na página de confirmação, se disponíveis
    email_enviado = session.get('email_enviado', None)
    erro_email = session.get('erro_email', None)
    numero_orcamento = session.get('numero_orcamento', '')
    
    # Mesmo que não tenhamos informações na sessão, ainda exibimos a página de confirmação
    return render_template('confirmacao.html', 
                          email_enviado=email_enviado, 
                          erro_email=erro_email,
                          numero_orcamento=numero_orcamento)

def explorar_planilha():
    """Função para explorar os dados dos arquivos CSV (para debug)"""
    try:
        pgr_path = os.path.join(os.path.dirname(__file__), 'Precos_PGR.csv')
        ambientais_path = os.path.join(os.path.dirname(__file__), 'Precos_Ambientais.csv')
        
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

@app.route('/processar_formulario', methods=['POST'])
def processar_formulario():
    try:
        # Obter dados do formulário
        empresa_cliente = request.form.get('empresa', '').strip()
        cliente_email = request.form.get('cliente_email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        
        # Validar dados básicos
        erros = []
        if not empresa_cliente:
            erros.append("O campo Empresa é obrigatório.")
        if not cliente_email:
            erros.append("O campo E-mail é obrigatório.")
        
        # Validar formato do e-mail
        if cliente_email and '@' not in cliente_email:
            erros.append("O E-mail fornecido não é válido.")
            
        if erros:
            for erro in erros:
                flash(erro)
            app.logger.error(f"Dados básicos do cliente não fornecidos: {', '.join(erros)}")
            return redirect(url_for('formulario'))
        
        # Processar serviços
        servicos_form = []
        
        # Verificar se há serviços no formulário
        for key in request.form:
            if key.startswith('servicos[') and key.endswith('][nome]'):
                index = key.split('[')[1].split(']')[0]
                servicos_form.append(index)
        
        if not servicos_form:
            app.logger.error("Nenhum serviço encontrado no formulário")
            flash("Por favor, adicione pelo menos um serviço ao orçamento.")
            return redirect(url_for('formulario'))
        
        app.logger.info(f"Processando {len(servicos_form)} serviços para {empresa_cliente} ({cliente_email})")
        
        servicos = []
        erros_servicos = []
        
        for i in servicos_form:
            try:
                nome_servico = request.form.get(f'servicos[{i}][nome]', '')
                if not nome_servico:
                    continue
                
                regiao = request.form.get(f'servicos[{i}][regiao]', '')
                if not regiao:
                    erros_servicos.append(f"Região não selecionada para o serviço {nome_servico}")
                    continue
                
                variavel = request.form.get(f'servicos[{i}][variavel]', '')
                grau_risco = request.form.get(f'servicos[{i}][grau_risco]', '')
                num_trabalhadores = request.form.get(f'servicos[{i}][num_trabalhadores]', '')
                num_ges_ghe = request.form.get(f'servicos[{i}][num_ges_ghe]', '1')
                
                # Verificar se há avaliações adicionais
                avaliacao_adicional = request.form.get(f'servicos[{i}][avaliacao_adicional]', 'nao')
                num_avaliacoes_adicionais = 0
                if avaliacao_adicional == 'sim':
                    num_avaliacoes_adicionais = int(request.form.get(f'servicos[{i}][quantidade_avaliacoes]', '0'))
                
                # Obter quantidade e preços
                quantidade = int(request.form.get(f'servicos[{i}][quantidade]', '1'))
                preco_unitario_str = request.form.get(f'servicos[{i}][preco_unitario]', '0')
                preco_total_str = request.form.get(f'servicos[{i}][preco_total]', '0')
                
                try:
                    preco_unitario = float(preco_unitario_str)
                    preco_total = float(preco_total_str)
                except ValueError:
                    app.logger.warning(f"Erro ao converter preços: unitário={preco_unitario_str}, total={preco_total_str}")
                    preco_unitario = 0
                    preco_total = 0
                    erros_servicos.append(f"Erro ao calcular preço para o serviço {nome_servico}")
                
                # Verificar se o preço foi calculado corretamente
                if preco_unitario <= 0:
                    app.logger.warning(f"Preço unitário inválido para o serviço {nome_servico}: {preco_unitario}")
                    erros_servicos.append(f"Preço não calculado para o serviço {nome_servico}")
                
                # Obter custos logísticos
                custos_logisticos_str = request.form.get(f'servicos[{i}][custos_logisticos]', '0')
                try:
                    # Remover caracteres não numéricos, exceto ponto e vírgula
                    custos_logisticos_str = re.sub(r'[^\d.,]', '', custos_logisticos_str)
                    
                    # Substituir vírgula por ponto
                    custos_logisticos_str = custos_logisticos_str.replace(',', '.')
                    
                    # Converter para float
                    custos_logisticos = float(custos_logisticos_str)
                except (ValueError, TypeError):
                    app.logger.warning(f"Erro ao converter custos logísticos: {custos_logisticos_str}")
                    custos_logisticos = 0.0
                
                # Calcular custos laboratoriais para serviços de coleta
                custos_laboratoriais = 0.0
                if nome_servico.lower().find('coleta') >= 0:
                    tipo_amostrador = request.form.get(f'servicos[{i}][tipo_amostrador]', '')
                    quantidade_amostras = int(request.form.get(f'servicos[{i}][quantidade_amostras]', '1'))
                    tipo_analise = request.form.get(f'servicos[{i}][tipo_analise]', '')
                    necessita_art = request.form.get(f'servicos[{i}][necessita_art]', '') == 'on'
                    metodo_envio = request.form.get(f'servicos[{i}][metodo_envio]', 'padrao')
                    
                    if tipo_amostrador and tipo_analise:
                        custos_laboratoriais = calcular_custos_laboratoriais(
                            tipo_amostrador, 
                            quantidade_amostras, 
                            tipo_analise, 
                            necessita_art, 
                            metodo_envio
                        )
                
                # Processar custos de múltiplos dias
                custos_multiplos_dias = 0.0
                multiplas_coletas = request.form.get(f'servicos[{i}][multiplas_coletas]', 'nao')
                if multiplas_coletas == 'sim':
                    quantidade_dias = int(request.form.get(f'servicos[{i}][quantidade_dias]', '1'))
                    dias_coleta = []
                    
                    for d in range(1, quantidade_dias + 1):
                        data = request.form.get(f'servicos[{i}][dias_coleta][{d-1}][data]', '')
                        hora = request.form.get(f'servicos[{i}][dias_coleta][{d-1}][hora]', '')
                        local = request.form.get(f'servicos[{i}][dias_coleta][{d-1}][local]', '')
                        observacoes = request.form.get(f'servicos[{i}][dias_coleta][{d-1}][observacoes]', '')
                        
                        dias_coleta.append({
                            'data': data,
                            'hora': hora,
                            'local': local,
                            'observacoes': observacoes
                        })
                    
                    if dias_coleta:
                        custos_multiplos_dias_str = request.form.get(f'servicos[{i}][custos_multiplos_dias]', '0')
                        try:
                            custos_multiplos_dias = float(custos_multiplos_dias_str)
                        except ValueError:
                            app.logger.warning(f"Erro ao converter custos de múltiplos dias: {custos_multiplos_dias_str}")
                            custos_multiplos_dias = 0.0
                
                # Recalcular o preço total considerando todos os custos adicionais
                preco_total_calculado = preco_unitario * quantidade
                preco_total = preco_total_calculado + custos_logisticos + custos_laboratoriais + custos_multiplos_dias
                
                # Construir detalhes do serviço
                detalhes = ""
                if "PGR" in nome_servico:
                    detalhes = f"Grau de Risco: {grau_risco}, Faixa: {num_trabalhadores.replace('ate', 'Até ').replace('a', ' a ')}"
                elif variavel:
                    detalhes = f"Tipo: {variavel}"
                    if num_ges_ghe and int(num_ges_ghe) > 1:
                        detalhes += f", {num_ges_ghe} GES/GHE"
                    if num_avaliacoes_adicionais > 0:
                        detalhes += f", {num_avaliacoes_adicionais} avaliações adicionais"
                
                # Adicionar detalhes de custos adicionais
                custos_adicionais = []
                if custos_logisticos > 0:
                    custos_adicionais.append(f"Logística: R$ {custos_logisticos:.2f}")
                if custos_laboratoriais > 0:
                    custos_adicionais.append(f"Laboratório: R$ {custos_laboratoriais:.2f}")
                if custos_multiplos_dias > 0:
                    custos_adicionais.append(f"Múltiplos dias: R$ {custos_multiplos_dias:.2f}")
                
                if custos_adicionais:
                    detalhes += ". Custos adicionais: " + ", ".join(custos_adicionais)
                
                # Criar objeto de serviço
                servico = {
                    'nome': nome_servico,
                    'regiao': regiao,
                    'variavel': variavel,
                    'grau_risco': grau_risco,
                    'num_trabalhadores': num_trabalhadores,
                    'num_ges_ghe': int(num_ges_ghe) if num_ges_ghe else 1,
                    'num_avaliacoes_adicionais': num_avaliacoes_adicionais,
                    'quantidade': quantidade,
                    'unidade': 'unidade',
                    'preco_unitario': preco_unitario,
                    'preco_total': preco_total,
                    'custos_logisticos': custos_logisticos,
                    'custos_laboratoriais': custos_laboratoriais,
                    'custos_multiplos_dias': custos_multiplos_dias,
                    'detalhes': detalhes,
                    'preco_unitario_formatado': f"R$ {preco_unitario:.2f}".replace('.', ','),
                    'preco_total_formatado': f"R$ {preco_total:.2f}".replace('.', ',')
                }
            
                servicos.append(servico)
                
            except Exception as e:
                app.logger.error(f"Erro ao processar serviço {i}: {str(e)}")
                erros_servicos.append(f"Erro ao processar serviço {nome_servico if 'nome_servico' in locals() else i}: {str(e)}")
                # Continuar processando outros serviços
        
        # Verificar se há erros nos serviços
        if erros_servicos:
            for erro in erros_servicos:
                flash(erro)
            return redirect(url_for('formulario'))
        
        # Verificar se há serviços processados
        if not servicos:
            app.logger.error("Nenhum serviço processado com sucesso")
            flash("Não foi possível processar nenhum serviço. Por favor, verifique os dados e tente novamente.")
            return redirect(url_for('formulario'))
        
        # Calcular o total do orçamento
        total_orcamento = sum(s['preco_total'] for s in servicos)
        
        # Aplicar percentual indireto do SESI (30%)
        percentual_sesi = 0.30
        valor_sesi = total_orcamento * percentual_sesi
        total_com_sesi = total_orcamento + valor_sesi
        
        # Armazenar na sessão
        session['servicos'] = servicos
        session['email'] = cliente_email
        session['telefone'] = telefone
        session['empresa_cliente'] = empresa_cliente
        session['subtotal_orcamento'] = total_orcamento
        session['valor_sesi'] = valor_sesi
        session['total_orcamento'] = total_com_sesi
        session['percentual_sesi'] = percentual_sesi * 100  # Para exibir como porcentagem
        
        # Forçar a sessão a ser salva
        session.modified = True
        
        app.logger.info(f"Formulário processado com sucesso. Total: {total_orcamento}, Total com SESI: {total_com_sesi}")
        
        return redirect(url_for('resumo_view'))
        
    except Exception as e:
        app.logger.error(f"Erro ao processar formulário: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Erro ao processar formulário: {str(e)}")
        return redirect(url_for('formulario'))

@app.route('/obter_variaveis')
def obter_variaveis():
    servico = request.args.get('servico', '')
    
    app.logger.info(f"Obtendo variáveis para o serviço: {servico}")
    
    if not servico:
        return jsonify({'variaveis': []})
    
    try:
        # Para serviços PGR, as variáveis são fixas
        if "PGR" in servico:
            # Para PGR, não temos variáveis específicas no CSV, então retornamos uma lista vazia
            return jsonify({'variaveis': []})
        
        # Para serviços ambientais, buscar no CSV
        df = pd.read_csv('Precos_Ambientais.csv')
        
        # Filtrar pelo serviço
        df_filtrado = df[df['Serviço'] == servico]
        
        if df_filtrado.empty:
            app.logger.warning(f"Nenhuma variável encontrada para o serviço: {servico}")
            return jsonify({'variaveis': []})
        
        # Obter variáveis únicas (coluna Tipo_Avaliacao)
        variaveis = df_filtrado['Tipo_Avaliacao'].unique().tolist()
        app.logger.info(f"Variáveis encontradas para {servico}: {variaveis}")
        
        # Verificar se o serviço requer GES/GHE
        requer_ges_ghe = False
        if 'Adicional_GES_GHE' in df_filtrado.columns:
            # Converter numpy.bool_ para bool Python nativo
            requer_ges_ghe = bool((df_filtrado['Adicional_GES_GHE'] > 0).any())
        
        return jsonify({
            'variaveis': variaveis,
            'requer_ges_ghe': requer_ges_ghe
        })
    
    except Exception as e:
        app.logger.error(f"Erro ao obter variáveis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

@app.route('/calcular_preco', methods=['GET', 'POST'])
def calcular_preco():
    """Calcula o preço de um serviço com base nos parâmetros fornecidos"""
    try:
        # Obter parâmetros da requisição
        if request.method == 'GET':
            servico = request.args.get('servico')
            regiao = request.args.get('regiao')
            grau_risco = request.args.get('grau_risco')
            num_trabalhadores = request.args.get('num_trabalhadores')
            variavel = request.args.get('variavel')
            num_ges_ghe = request.args.get('num_ges_ghe', '1')
            num_avaliacoes_adicionais = request.args.get('num_avaliacoes_adicionais', '0')
        else:  # POST
            servico = request.form.get('servico')
            regiao = request.form.get('regiao')
            grau_risco = request.form.get('grau_risco')
            num_trabalhadores = request.form.get('num_trabalhadores')
            variavel = request.form.get('variavel')
            num_ges_ghe = request.form.get('num_ges_ghe', '1')
            num_avaliacoes_adicionais = request.form.get('num_avaliacoes_adicionais', '0')
        
        if not servico:
            app.logger.error("Parâmetro 'servico' não fornecido")
            return jsonify({'success': False, 'erro': 'Serviço não especificado'}), 400
        
        if not regiao:
            app.logger.error("Parâmetro 'regiao' não fornecido")
            return jsonify({'success': False, 'erro': 'Região não especificada'}), 400
        
        # Verificar se os parâmetros necessários estão presentes
        if "PGR" in servico:
            if not grau_risco:
                app.logger.error(f"Parâmetro 'grau_risco' não fornecido para serviço PGR: {servico}")
                return jsonify({'success': False, 'erro': 'Grau de risco não especificado para serviço PGR'}), 400
            
            if not num_trabalhadores:
                app.logger.error(f"Parâmetro 'num_trabalhadores' não fornecido para serviço PGR: {servico}")
                return jsonify({'success': False, 'erro': 'Número de trabalhadores não especificado para serviço PGR'}), 400
        else:
            # Para serviços não-PGR, verificar se a variável foi fornecida
            if not variavel:
                app.logger.error(f"Parâmetro 'variavel' não fornecido para serviço não-PGR: {servico}")
                return jsonify({'success': False, 'erro': 'Variável não especificada para serviço não-PGR'}), 400
        
        # Converter valores numéricos
        try:
            num_ges_ghe = int(num_ges_ghe) if num_ges_ghe else 1
            num_avaliacoes_adicionais = int(num_avaliacoes_adicionais) if num_avaliacoes_adicionais else 0
        except ValueError:
            app.logger.error(f"Erro ao converter valores numéricos: num_ges_ghe={num_ges_ghe}, num_avaliacoes_adicionais={num_avaliacoes_adicionais}")
            return jsonify({'success': False, 'erro': 'Valores numéricos inválidos'}), 400
        
        # Calcular o preço
        app.logger.info(f"Calculando preço para: Serviço={servico}, Região={regiao}, Variável={variavel}, GR={grau_risco}, NT={num_trabalhadores}, GES={num_ges_ghe}, Aval={num_avaliacoes_adicionais}")
        
        preco = obter_preco_servico(
            servico, 
            regiao=regiao, 
            variavel=variavel, 
            grau_risco=grau_risco, 
            num_trabalhadores=num_trabalhadores,
            num_ges_ghe=num_ges_ghe,
            num_avaliacoes_adicionais=num_avaliacoes_adicionais
        )
        
        if preco <= 0:
            app.logger.warning(f"Preço calculado é zero ou negativo: {preco}")
            return jsonify({
                'success': False,
                'erro': 'Não foi possível calcular o preço para os parâmetros fornecidos',
                'servico': servico,
                'regiao': regiao,
                'grau_risco': grau_risco,
                'num_trabalhadores': num_trabalhadores,
                'variavel': variavel
            }), 404
        
        app.logger.info(f"Preço calculado: {preco}")
        
        # Retornar o preço calculado
        return jsonify({
            'success': True,
            'preco': preco,
            'preco_formatado': f"R$ {preco:.2f}".replace('.', ',')
        })
        
    except Exception as e:
        app.logger.error(f"Erro ao calcular preço: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'erro': f'Erro ao calcular preço: {str(e)}'}), 500

def calcular_custos_laboratoriais(tipo_amostrador, quantidade_amostras, tipo_analise, necessita_art, metodo_envio):
    """
    Calcula os custos laboratoriais com base nos parâmetros informados.
    
    Args:
        tipo_amostrador: Tipo de amostrador utilizado
        quantidade_amostras: Quantidade de amostras a serem analisadas
        tipo_analise: Tipo de análise a ser realizada
        necessita_art: Se necessita ART específica
        metodo_envio: Método de envio das amostras
        
    Returns:
        float: Valor total dos custos laboratoriais
    """
    try:
        # Valores base para cada tipo de amostrador
        custos_amostradores = {
            'bomba': 150.0,
            'dosimetro': 120.0,
            'cassete': 100.0,
            'impinger': 180.0,
            'outro': 130.0
        }
        
        # Valores base para cada tipo de análise
        custos_analises = {
            'quimica': 200.0,
            'biologica': 250.0,
            'fisica': 180.0
        }
        
        # Multiplicadores para métodos de envio
        multiplicadores_envio = {
            'padrao': 1.0,
            'expresso': 1.2,
            'urgente': 1.5
        }
        
        # Custo base do amostrador
        custo_amostrador = custos_amostradores.get(tipo_amostrador, 130.0)
        
        # Custo base da análise
        custo_analise = custos_analises.get(tipo_analise, 200.0)
        
        # Custo total por amostra
        custo_por_amostra = custo_amostrador + custo_analise
        
        # Custo total das amostras
        custo_total = custo_por_amostra * quantidade_amostras
        
        # Adicionar custo de ART se necessário
        if necessita_art:
            custo_total += 150.0
        
        # Aplicar multiplicador de método de envio
        multiplicador = multiplicadores_envio.get(metodo_envio, 1.0)
        custo_total *= multiplicador
        
        app.logger.info(f"Custos laboratoriais calculados: {custo_total:.2f}")
        return custo_total
        
    except Exception as e:
        app.logger.error(f"Erro ao calcular custos laboratoriais: {str(e)}")
        return 0.0

@app.route('/enviar_orcamento', methods=['POST'])
def enviar_orcamento():
    try:
        # Verificar se há dados na sessão
        if 'servicos' not in session:
            app.logger.error("Serviços não encontrados na sessão")
            flash("Dados de orçamento não encontrados. Por favor, preencha o formulário novamente.")
            return redirect(url_for('formulario'))
        
        # Obter dados da sessão
        cliente_email = session.get('cliente_email', '')  # Mantido como 'cliente_email' para consistência
        if not cliente_email:
            app.logger.error("E-mail do cliente não encontrado na sessão")
            flash("E-mail do cliente não encontrado. Por favor, preencha o formulário novamente.")
            return redirect(url_for('formulario'))
            
        empresa_cliente = session.get('empresa_cliente', '')
        servicos = session.get('servicos', [])
        total_orcamento = session.get('total_orcamento', 0)
        
        app.logger.info(f"Enviando orçamento para {cliente_email}, {len(servicos)} serviços, total: {total_orcamento}")
        
        # Formatar os serviços para o e-mail
        servicos_formatados = []
        for servico in servicos:
            servico_formatado = servico.copy()
            if 'preco_unitario_formatado' not in servico_formatado:
                servico_formatado['preco_unitario_formatado'] = f"R$ {servico['preco_unitario']:.2f}".replace('.', ',')
            if 'preco_total_formatado' not in servico_formatado:
                servico_formatado['preco_total_formatado'] = f"R$ {servico['preco_total']:.2f}".replace('.', ',')
            if 'empresa' not in servico_formatado:
                servico_formatado['empresa'] = empresa_cliente
            servicos_formatados.append(servico_formatado)
        
        # Enviar o e-mail
        sucesso, mensagem = enviar_email_orcamento(cliente_email, empresa_cliente, servicos_formatados, total_orcamento)
        
        if sucesso:
            flash("Orçamento enviado com sucesso para o seu e-mail!")
            return redirect(url_for('confirmacao'))
        else:
            app.logger.error(f"Erro ao enviar e-mail: {mensagem}")
            flash(f"Erro ao enviar o orçamento: {mensagem}")
            return redirect(url_for('formulario'))
    
    except Exception as e:
        app.logger.error(f"Erro ao enviar orçamento por e-mail: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f"Erro ao enviar orçamento por e-mail: {str(e)}")
        return redirect(url_for('formulario'))

def verificar_precos_csv():
    """
    Verifica se os arquivos CSV de preços estão completos e atualiza-os se necessário.
    Garante que todas as regiões tenham preços definidos para todos os serviços.
    """
    try:
        app.logger.info("Verificando arquivos CSV de preços...")
        
        # Verificar preços ambientais
        try:
            df_ambientais = pd.read_csv('Precos_Ambientais.csv')
            
            # Obter lista de serviços e regiões únicas
            servicos = df_ambientais['Serviço'].unique()
            regioes = df_ambientais['Região'].unique()
            variaveis = df_ambientais['Tipo_Avaliacao'].unique()
            
            # Verificar se há preços para todas as combinações de serviço, região e variável
            registros_faltantes = []
            for servico in servicos:
                for variavel in variaveis:
                    # Verificar se há pelo menos um preço para a região Central
                    filtro_central = (df_ambientais['Serviço'] == servico) & (df_ambientais['Região'] == 'Central') & (df_ambientais['Tipo_Avaliacao'] == variavel)
                    if df_ambientais[filtro_central].empty:
                        app.logger.warning(f"Preço não encontrado para {servico}, Central, {variavel}")
                    
                    # Verificar outras regiões
                    for regiao in regioes:
                        if regiao == 'Central':
                            continue
                        
                        filtro = (df_ambientais['Serviço'] == servico) & (df_ambientais['Região'] == regiao) & (df_ambientais['Tipo_Avaliacao'] == variavel)
                        if df_ambientais[filtro].empty:
                            app.logger.warning(f"Preço não encontrado para {servico}, {regiao}, {variavel}")
            
            app.logger.info("Verificação de preços ambientais concluída")
        except Exception as e:
            app.logger.error(f"Erro ao verificar preços ambientais: {str(e)}")
        
        # Verificar preços PGR
        try:
            df_pgr = pd.read_csv('Precos_PGR.csv')
            
            # Obter lista de serviços, regiões e graus de risco únicos
            servicos_pgr = df_pgr['Serviço'].unique()
            regioes_pgr = df_pgr['Região'].unique()
            graus_risco = df_pgr['Grau_Risco'].unique() if 'Grau_Risco' in df_pgr.columns else []
            faixas_trab = df_pgr['Faixa_Trab'].unique() if 'Faixa_Trab' in df_pgr.columns else []
            
            # Verificar se há preços para todas as combinações
            for servico in servicos_pgr:
                for grau_risco in graus_risco:
                    for faixa_trab in faixas_trab:
                        # Verificar se há pelo menos um preço para a região Central
                        filtro_central = (df_pgr['Serviço'] == servico) & (df_pgr['Região'] == 'Central')
                        if 'Grau_Risco' in df_pgr.columns:
                            filtro_central = filtro_central & (df_pgr['Grau_Risco'] == grau_risco)
                        if 'Faixa_Trab' in df_pgr.columns:
                            filtro_central = filtro_central & (df_pgr['Faixa_Trab'] == faixa_trab)
                        
                        if df_pgr[filtro_central].empty:
                            app.logger.warning(f"Preço não encontrado para PGR {servico}, Central, {grau_risco}, {faixa_trab}")
            
            app.logger.info("Verificação de preços PGR concluída")
        except Exception as e:
            app.logger.error(f"Erro ao verificar preços PGR: {str(e)}")
        
        app.logger.info("Verificação de preços concluída")
    except Exception as e:
        app.logger.error(f"Erro ao verificar preços CSV: {str(e)}")
        import traceback
        traceback.print_exc()

@app.route('/api/regioes_disponiveis', methods=['GET'])
def regioes_disponiveis():
    try:
        # Obter o serviço selecionado
        servico = request.args.get('servico', '')
        if not servico:
            return jsonify({'erro': 'Serviço não especificado'}), 400
        
        # Carregar dados
        dados = carregar_dados_excel()
        
        # Verificar se os dados foram carregados corretamente
        if not dados or not isinstance(dados, dict):
            return jsonify({'erro': 'Erro ao carregar dados'}), 500
        
        # Obter regiões disponíveis para o serviço
        regioes = []
        
        if "PGR" in servico:
            # Para serviços PGR, verificar no DataFrame de PGR
            df_pgr = dados.get('pgr')
            if df_pgr is not None and isinstance(df_pgr, pd.DataFrame):
                # Filtrar por serviço
                filtro = df_pgr['Serviço'] == servico
                resultado = df_pgr[filtro]
                
                if not resultado.empty:
                    # Obter valores únicos da coluna Região
                    regioes = resultado['Região'].unique().tolist()
        else:
            # Para serviços ambientais
            df_ambientais = dados.get('ambientais')
            if df_ambientais is not None and isinstance(df_ambientais, pd.DataFrame):
                # Filtrar por serviço
                filtro = df_ambientais['Serviço'] == servico
                resultado = df_ambientais[filtro]
                
                if not resultado.empty:
                    # Obter valores únicos da coluna Região
                    regioes = resultado['Região'].unique().tolist()
        
        # Ordenar regiões
        regioes.sort()
        
        app.logger.info(f"Regiões disponíveis para {servico}: {regioes}")
        return jsonify({'regioes': regioes})
    
    except Exception as e:
        app.logger.error(f"Erro ao obter regiões: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/variaveis_disponiveis', methods=['GET'])
def variaveis_disponiveis_api():
    try:
        # Obter parâmetros
        servico = request.args.get('servico', '')
        regiao = request.args.get('regiao', '')
        
        if not servico:
            return jsonify({'erro': 'Serviço não especificado'}), 400
        
        if not regiao:
            return jsonify({'erro': 'Região não especificada'}), 400
        
        # Para serviços PGR, não há variáveis
        if "PGR" in servico:
            return jsonify({'variaveis': []})
        
        # Carregar dados
        dados = carregar_dados_excel()
        
        # Verificar se os dados foram carregados corretamente
        if not dados or not isinstance(dados, dict):
            return jsonify({'erro': 'Erro ao carregar dados'}), 500
        
        # Para serviços ambientais
        df_ambientais = dados.get('ambientais')
        variaveis = []
        
        if df_ambientais is not None and isinstance(df_ambientais, pd.DataFrame):
            # Filtrar por serviço e região
            filtro = (df_ambientais['Serviço'] == servico) & (df_ambientais['Região'] == regiao)
            resultado = df_ambientais[filtro]
            
            if not resultado.empty:
                # Obter valores únicos da coluna Tipo_Avaliacao
                variaveis = resultado['Tipo_Avaliacao'].unique().tolist()
            else:
                # Se não encontrar para a região específica, tentar região Central como fallback
                filtro_fallback = (df_ambientais['Serviço'] == servico) & (df_ambientais['Região'] == 'Central')
                resultado_fallback = df_ambientais[filtro_fallback]
                
                if not resultado_fallback.empty:
                    variaveis = resultado_fallback['Tipo_Avaliacao'].unique().tolist()
        
        # Ordenar variáveis
        variaveis.sort()
        
        app.logger.info(f"Variáveis disponíveis para {servico} na região {regiao}: {variaveis}")
        return jsonify({'variaveis': variaveis})
    
    except Exception as e:
        app.logger.error(f"Erro ao obter variáveis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/servicos', methods=['GET'])
def servicos_api():
    """Retorna a lista de serviços disponíveis"""
    try:
        servicos = obter_servicos()
        return jsonify({'servicos': servicos})
    except Exception as e:
        app.logger.error(f"Erro ao obter serviços: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': str(e)}), 500

# A chamada da função será feita apenas no bloco if __name__ == "__main__"

def encontrar_porta_disponivel(porta_inicial=3000, max_tentativas=10):
    """
    Encontra uma porta disponível começando pela porta_inicial.
    Tenta até max_tentativas portas sequenciais.
    
    Args:
        porta_inicial: Porta inicial para tentar (padrão: 3000)
        max_tentativas: Número máximo de tentativas (padrão: 10)
        
    Returns:
        int: Número da porta disponível ou None se nenhuma porta estiver disponível
    """
    import socket
    
    for porta in range(porta_inicial, porta_inicial + max_tentativas):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('0.0.0.0', porta))
            sock.close()
            return porta
        except OSError:
            app.logger.warning(f"Porta {porta} já está em uso, tentando próxima...")
            continue
        finally:
            sock.close()
    
    return None

# Chamar a função verificar_precos_csv após sua definição
if __name__ == "__main__":
    verificar_precos_csv()
    
    # Tentar encontrar uma porta disponível
    porta_padrao = int(os.environ.get("PORT", 3000))
    porta = encontrar_porta_disponivel(porta_padrao)
    
    if porta is None:
        app.logger.error(f"Não foi possível encontrar uma porta disponível após {10} tentativas. Iniciando na porta padrão {porta_padrao}.")
        porta = porta_padrao
    
    app.logger.info(f"Iniciando servidor na porta {porta}")
    
    from waitress import serve
    try:
        # Em ambiente de produção (como Vercel), o host será gerenciado pelo provedor
        # Em desenvolvimento, usamos localhost ou 0.0.0.0
        if os.environ.get("VERCEL_ENV") == "production":
            # Na Vercel, o aplicativo será servido automaticamente
            pass
        else:
            serve(app, host="localhost", port=porta)
    except OSError as e:
        app.logger.error(f"Erro ao iniciar servidor na porta {porta}: {str(e)}")
        app.logger.info("Tentando iniciar na porta 8080 como última alternativa...")
        try:
            serve(app, host="localhost", port=8080)
        except Exception as e2:
            app.logger.error(f"Falha ao iniciar servidor: {str(e2)}")

def calcular_custos_logisticos(regiao, distancia_km=None):
    """
    Calcula os custos logísticos com base na região e distância.
    
    Args:
        regiao: Região onde o serviço será realizado
        distancia_km: Distância em km (opcional)
        
    Returns:
        float: Valor total dos custos logísticos
    """
    try:
        # Valores base para cada região
        custos_base = {
            'Central': 50.0,
            'Norte': 150.0,
            'Sul': 120.0,
            'Leste': 100.0,
            'Oeste': 130.0,
            'Nordeste': 200.0,
            'Sudeste': 180.0,
            'Noroeste': 220.0,
            'Sudoeste': 190.0,
            'Extremo Sul': 250.0,
            'Instituto': 0.0
        }
        
        # Custo base da região
        custo_base = custos_base.get(regiao, 100.0)
        
        # Se a distância for fornecida, adicionar custo por km
        if distancia_km:
            custo_km = float(distancia_km) * 1.5  # R$ 1,50 por km
            custo_total = custo_base + custo_km
        else:
            custo_total = custo_base
        
        app.logger.info(f"Custos logísticos calculados para {regiao}: {custo_total:.2f}")
        return custo_total
        
    except Exception as e:
        app.logger.error(f"Erro ao calcular custos logísticos: {str(e)}")
        return 0.0

def calcular_custos_multiplos_dias(dias_coleta):
    """
    Calcula os custos adicionais para coletas em múltiplos dias.
    
    Args:
        dias_coleta: Lista de dicionários com informações sobre cada dia de coleta
        
    Returns:
        float: Valor total dos custos de múltiplos dias
    """
    try:
        custo_total = 0.0
        
        # Valores base
        custo_diaria = 200.0
        custo_refeicao = 50.0
        custo_hora_adicional = 30.0
        
        for dia in dias_coleta:
            # Custo base por dia
            custo_dia = custo_diaria
            
            # Adicionar custo de hospedagem se necessário
            if dia.get('hospedagem') == 'sim':
                custo_dia += 150.0
            
            # Adicionar custo de refeições
            num_refeicoes = int(dia.get('refeicoes', 1))
            custo_dia += num_refeicoes * custo_refeicao
            
            # Adicionar custo de horas adicionais
            horas = int(dia.get('horas', 8))
            if horas > 8:
                horas_adicionais = horas - 8
                custo_dia += horas_adicionais * custo_hora_adicional
            
            custo_total += custo_dia
        
        app.logger.info(f"Custos de múltiplos dias calculados: {custo_total:.2f}")
        return custo_total
        
    except Exception as e:
        app.logger.error(f"Erro ao calcular custos de múltiplos dias: {str(e)}")
        return 0.0

def enviar_email_orcamento(email_destino, pdf_path, numero_orcamento, empresa_cliente):
    """
    Envia um e-mail com o orçamento em anexo.
    
    Args:
        email_destino: E-mail do destinatário
        pdf_path: Caminho para o arquivo PDF do orçamento
        numero_orcamento: Número do orçamento
        empresa_cliente: Nome da empresa cliente
    """
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        
        # Configurações de e-mail
        email_remetente = app.config.get('EMAIL_REMETENTE', 'sistema@exemplo.com')
        email_senha = app.config.get('EMAIL_SENHA', '')
        smtp_servidor = app.config.get('SMTP_SERVIDOR', 'smtp.gmail.com')
        smtp_porta = app.config.get('SMTP_PORTA', 587)
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = email_remetente
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
        
        # Anexar PDF
        with open(pdf_path, 'rb') as f:
            anexo = MIMEApplication(f.read(), _subtype='pdf')
            anexo.add_header('Content-Disposition', 'attachment', filename=f"Orcamento_{numero_orcamento}.pdf")
            msg.attach(anexo)
        
        # Enviar e-mail
        with smtplib.SMTP(smtp_servidor, smtp_porta) as servidor:
            servidor.starttls()
            if email_senha:  # Se tiver senha configurada
                servidor.login(email_remetente, email_senha)
            servidor.send_message(msg)
        
        app.logger.info(f"E-mail enviado com sucesso para {email_destino}")
        return True
        
    except Exception as e:
        app.logger.error(f"Erro ao enviar e-mail: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
        raise