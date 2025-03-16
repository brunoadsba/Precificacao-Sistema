"""
Rotas para gerenciamento de orçamentos.
"""
import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, current_app, send_file, send_from_directory
from io import BytesIO

from models.precos import gerenciador_precos
from services.email_sender import email_service
from utils.orcamento_utils import (
    gerar_numero_orcamento, 
    calcular_custos_logisticos,
    calcular_custos_multiplos_dias,
    calcular_custos_laboratoriais,
    gerar_pdf_orcamento,
    gerar_corpo_email_orcamento,
    formatar_moeda
)

# Configurar logger
logger = logging.getLogger(__name__)

# Criar blueprint
orcamentos_bp = Blueprint('orcamentos', __name__)

@orcamentos_bp.route('/servicos', methods=['GET'])
def servicos():
    """
    Retorna a lista de serviços disponíveis.
    
    Returns:
        JSON: Lista de serviços disponíveis
    """
    try:
        servicos = gerenciador_precos.obter_servicos()
        return jsonify({
            'success': True,
            'servicos': servicos
        })
    except Exception as e:
        logger.error(f"Erro ao obter serviços: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orcamentos_bp.route('/regioes', methods=['GET'])
def regioes():
    """
    Retorna a lista de regiões disponíveis para um serviço.
    
    Returns:
        JSON: Lista de regiões disponíveis
    """
    try:
        servico = request.args.get('servico')
        if not servico:
            return jsonify({
                'success': False,
                'error': 'Parâmetro servico é obrigatório'
            }), 400
            
        regioes = gerenciador_precos.obter_regioes_disponiveis(servico)
        return jsonify({
            'success': True,
            'regioes': regioes
        })
    except Exception as e:
        logger.error(f"Erro ao obter regiões: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orcamentos_bp.route('/variaveis/<servico>', methods=['GET'])
def variaveis(servico):
    """
    Retorna as variáveis disponíveis para um serviço.
    
    Args:
        servico (str): Nome do serviço
        
    Returns:
        JSON: Variáveis disponíveis para o serviço
    """
    try:
        variaveis = gerenciador_precos.obter_variaveis_disponiveis(servico)
        return jsonify({
            'success': True,
            'variaveis': variaveis
        })
    except Exception as e:
        logger.error(f"Erro ao obter variáveis para o serviço {servico}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orcamentos_bp.route('/calcular_preco', methods=['POST'])
def calcular_preco():
    """
    Calcula o preço de um serviço com base nos parâmetros fornecidos.
    
    Returns:
        JSON: Preço calculado
    """
    try:
        dados = request.json
        
        servico = dados.get('servico')
        regiao = dados.get('regiao')
        tipo_avaliacao = dados.get('tipo_avaliacao')
        grau_risco = dados.get('grau_risco')
        num_trabalhadores = dados.get('num_trabalhadores')
        num_ges_ghe = int(dados.get('num_ges_ghe', 0) or 0)
        num_avaliacoes_adicionais = int(dados.get('num_avaliacoes_adicionais', 0) or 0)
        
        if not servico or not regiao:
            return jsonify({
                'success': False,
                'error': 'Serviço e região são obrigatórios'
            }), 400
        
        preco = gerenciador_precos.obter_preco_servico(
            servico=servico,
            regiao=regiao,
            tipo_avaliacao=tipo_avaliacao,
            grau_risco=grau_risco,
            num_trabalhadores=num_trabalhadores,
            num_ges_ghe=num_ges_ghe,
            num_avaliacoes_adicionais=num_avaliacoes_adicionais
        )
        
        return jsonify({
            'success': True,
            'preco': preco,
            'preco_formatado': formatar_moeda(preco)
        })
    except Exception as e:
        logger.error(f"Erro ao calcular preço: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orcamentos_bp.route('/calcular_custos_logisticos', methods=['POST'])
def calcular_custos_logisticos_route():
    """
    Calcula os custos logísticos com base na região e distância.
    """
    try:
        dados = request.json
        regiao = dados.get('regiao')
        distancia_km = dados.get('distancia_km')
        
        if not regiao:
            return jsonify({"success": False, "error": "Região é obrigatória"}), 400
        
        custo = calcular_custos_logisticos(regiao, distancia_km)
        
        return jsonify({
            "success": True, 
            "custo": custo,
            "custo_formatado": f"R$ {custo:.2f}".replace('.', ',')
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular custos logísticos: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@orcamentos_bp.route('/calcular_custos_multiplos_dias', methods=['POST'])
def calcular_custos_multiplos_dias_route():
    """
    Calcula custos adicionais para coletas que duram múltiplos dias.
    """
    try:
        dados = request.json
        dias_coleta = dados.get('dias_coleta', 1)
        
        custo = calcular_custos_multiplos_dias(dias_coleta)
        
        return jsonify({
            "success": True, 
            "custo": custo,
            "custo_formatado": f"R$ {custo:.2f}".replace('.', ',')
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular custos de múltiplos dias: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@orcamentos_bp.route('/calcular_custos_laboratoriais', methods=['POST'])
def calcular_custos_laboratoriais_route():
    """
    Calcula os custos laboratoriais para análises ambientais.
    """
    try:
        dados = request.json
        tipo_amostrador = dados.get('tipo_amostrador')
        quantidade_amostras = dados.get('quantidade_amostras', 1)
        tipo_analise = dados.get('tipo_analise')
        necessita_art = dados.get('necessita_art', False)
        metodo_envio = dados.get('metodo_envio', 'Correios')
        
        if not tipo_amostrador or not tipo_analise:
            return jsonify({
                "success": False, 
                "error": "Tipo de amostrador e tipo de análise são obrigatórios"
            }), 400
        
        custo = calcular_custos_laboratoriais(
            tipo_amostrador, 
            quantidade_amostras, 
            tipo_analise, 
            necessita_art, 
            metodo_envio
        )
        
        return jsonify({
            "success": True, 
            "custo": custo,
            "custo_formatado": f"R$ {custo:.2f}".replace('.', ',')
        })
        
    except Exception as e:
        logger.error(f"Erro ao calcular custos laboratoriais: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@orcamentos_bp.route('/gerar_orcamento', methods=['POST'])
def gerar_orcamento():
    """
    Gera um orçamento com base nos dados fornecidos.
    
    Returns:
        JSON: Dados do orçamento gerado
    """
    try:
        dados = request.json
        
        # Validar dados
        if not dados.get('empresa') or not dados.get('email') or not dados.get('servicos'):
            return jsonify({
                'success': False,
                'error': 'Dados incompletos para gerar orçamento'
            }), 400
        
        # Calcular valores
        subtotal = sum(servico.get('valor', 0) for servico in dados.get('servicos', []))
        percentual_sesi = float(dados.get('percentual_sesi', current_app.config['PERCENTUAL_SESI_PADRAO']))
        valor_sesi = subtotal * (percentual_sesi / 100)
        total = subtotal + valor_sesi
        
        # Gerar número de orçamento
        numero_orcamento = gerar_numero_orcamento()
        
        # Criar dados do orçamento
        dados_orcamento = {
            'numero_orcamento': numero_orcamento,
            'empresa': dados.get('empresa'),
            'email': dados.get('email'),
            'telefone': dados.get('telefone', ''),
            'contato': dados.get('contato', ''),
            'servicos': dados.get('servicos', []),
            'subtotal': subtotal,
            'percentual_sesi': percentual_sesi,
            'valor_sesi': valor_sesi,
            'total': total
        }
        
        # Gerar PDF
        caminho_pdf = gerar_pdf_orcamento(
            dados_orcamento=dados_orcamento,
            caminho_orcamentos=current_app.config['ORCAMENTOS_FOLDER']
        )
        
        # Salvar dados do orçamento em arquivo JSON
        caminho_json = os.path.join(current_app.config['ORCAMENTOS_FOLDER'], f"orcamento_{numero_orcamento}.json")
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(dados_orcamento, f, ensure_ascii=False, indent=4)
        
        # Enviar por email se solicitado
        if dados.get('enviar_email', False):
            try:
                corpo_email = gerar_corpo_email_orcamento(dados_orcamento)
                assunto = f"Orçamento {numero_orcamento} - {dados_orcamento['empresa']}"
                
                email_service.enviar_email(
                    destinatario=dados_orcamento['email'],
                    assunto=assunto,
                    corpo=corpo_email,
                    anexos=[caminho_pdf]
                )
                
                logger.info(f"Email enviado para {dados_orcamento['email']} com o orçamento {numero_orcamento}")
            except Exception as e:
                logger.error(f"Erro ao enviar email do orçamento {numero_orcamento}: {str(e)}")
        
        return jsonify({
            'success': True,
            'numero_orcamento': numero_orcamento,
            'subtotal': subtotal,
            'percentual_sesi': percentual_sesi,
            'valor_sesi': valor_sesi,
            'total': total
        })
    except Exception as e:
        logger.error(f"Erro ao gerar orçamento: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@orcamentos_bp.route('/download_orcamento/<numero_orcamento>', methods=['GET'])
def download_orcamento(numero_orcamento):
    """
    Faz o download do PDF de um orçamento.
    
    Args:
        numero_orcamento (str): Número do orçamento
        
    Returns:
        File: Arquivo PDF do orçamento
    """
    try:
        caminho_arquivo = os.path.join('orcamentos', f"orcamento_{numero_orcamento}.pdf")
        
        if not os.path.exists(caminho_arquivo):
            logger.error(f"Arquivo de orçamento não encontrado: {caminho_arquivo}")
            return jsonify({
                'success': False,
                'error': 'Arquivo de orçamento não encontrado'
            }), 404
        
        return send_file(
            caminho_arquivo,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"orcamento_{numero_orcamento}.pdf"
        )
    except Exception as e:
        logger.error(f"Erro ao fazer download do orçamento: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Alias para compatibilidade
@orcamentos_bp.route('/gerar', methods=['POST'])
def gerar():
    """
    Alias para gerar_orcamento para compatibilidade.
    """
    return gerar_orcamento()

# Aliases para compatibilidade com versões anteriores
@orcamentos_bp.route('/obter_servicos', methods=['GET'])
def obter_servicos():
    """Alias para servicos()"""
    return servicos()

@orcamentos_bp.route('/obter_regioes', methods=['GET'])
def obter_regioes():
    """Alias para regioes()"""
    return regioes()

@orcamentos_bp.route('/obter_variaveis/<servico>', methods=['GET'])
def obter_variaveis(servico):
    """Alias para variaveis()"""
    return variaveis(servico)

def init_app(app):
    """
    Inicializa o blueprint com a aplicação Flask.
    """
    # Inicializar gerenciador de preços com a aplicação
    gerenciador_precos.init_app(app)
    
    # Registrar blueprint
    app.register_blueprint(orcamentos_bp, url_prefix='/orcamentos') 