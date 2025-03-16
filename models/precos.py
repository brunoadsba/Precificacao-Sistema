"""
Modelo para gerenciamento de preços dos serviços.
"""
import os
import pandas as pd
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class GerenciadorPrecos:
    """Classe para gerenciar os preços dos serviços."""
    
    def __init__(self, app=None):
        """
        Inicializa o gerenciador de preços.
        
        Args:
            app (Flask, optional): Aplicação Flask
        """
        self.app = app
        self.precos_pgr = pd.DataFrame(columns=["servico", "regiao", "grau_risco", "num_trabalhadores", "preco"])
        self.precos_ambientais = pd.DataFrame(columns=["servico", "tipo_avaliacao", "adicional_ges_ghe", "regiao", "preco"])
        
        if app is not None:
            self.init_app(app)
        else:
            self.carregar_precos()
    
    def init_app(self, app):
        """
        Inicializa o gerenciador de preços com a aplicação Flask.
        
        Args:
            app: Aplicação Flask
        """
        self.app = app
        
        # Carregar preços
        self.carregar_precos_pgr(app.config['PRECOS_PGR_CSV'])
        self.carregar_precos_ambientais(app.config['PRECOS_AMBIENTAIS_CSV'])
        
        logger.info("Gerenciador de preços inicializado")
    
    def carregar_precos(self):
        """Carrega os preços dos arquivos CSV."""
        try:
            # Determinar caminhos dos arquivos CSV
            if self.app:
                pgr_path = self.app.config.get('PRECO_PGR_CSV')
                ambientais_path = self.app.config.get('PRECO_AMBIENTAIS_CSV')
            else:
                # Fallback para caminhos padrão
                csv_dir = os.path.join(os.getcwd(), 'csv')
                pgr_path = os.path.join(csv_dir, 'Precos_PGR.csv')
                ambientais_path = os.path.join(csv_dir, 'Precos_Ambientais.csv')
            
            # Carregar preços do PGR
            if os.path.exists(pgr_path):
                self.precos_pgr = pd.read_csv(pgr_path)
                logger.info(f"Preços PGR carregados: {len(self.precos_pgr)} registros")
            else:
                logger.warning(f"Arquivo de preços PGR não encontrado: {pgr_path}")
            
            # Carregar preços ambientais
            if os.path.exists(ambientais_path):
                self.precos_ambientais = pd.read_csv(ambientais_path)
                logger.info(f"Preços Ambientais carregados: {len(self.precos_ambientais)} registros")
            else:
                logger.warning(f"Arquivo de preços Ambientais não encontrado: {ambientais_path}")
        
        except Exception as e:
            logger.error(f"Erro ao carregar preços: {str(e)}")
    
    def carregar_precos_pgr(self, caminho_arquivo):
        """
        Carrega os preços dos serviços de PGR.
        
        Args:
            caminho_arquivo (str): Caminho para o arquivo CSV com os preços
        """
        try:
            if not os.path.exists(caminho_arquivo):
                logger.error(f"Arquivo de preços PGR não encontrado: {caminho_arquivo}")
                return
                
            self.precos_pgr = pd.read_csv(caminho_arquivo, encoding='utf-8')
            logger.info(f"Preços PGR carregados: {len(self.precos_pgr)} registros")
        except Exception as e:
            logger.error(f"Erro ao carregar preços PGR: {str(e)}")
            
    def carregar_precos_ambientais(self, caminho_arquivo):
        """
        Carrega os preços dos serviços ambientais.
        
        Args:
            caminho_arquivo (str): Caminho para o arquivo CSV com os preços
        """
        try:
            if not os.path.exists(caminho_arquivo):
                logger.error(f"Arquivo de preços ambientais não encontrado: {caminho_arquivo}")
                return
                
            self.precos_ambientais = pd.read_csv(caminho_arquivo, encoding='utf-8')
            logger.info(f"Preços Ambientais carregados: {len(self.precos_ambientais)} registros")
        except Exception as e:
            logger.error(f"Erro ao carregar preços ambientais: {str(e)}")
    
    def obter_servicos(self):
        """
        Obtém a lista de serviços disponíveis.
        
        Returns:
            list: Lista de serviços disponíveis
        """
        try:
            # Obter serviços únicos de ambos os DataFrames
            servicos_pgr = self.precos_pgr['servico'].unique().tolist() if 'servico' in self.precos_pgr.columns else []
            servicos_ambientais = self.precos_ambientais['servico'].unique().tolist() if 'servico' in self.precos_ambientais.columns else []
            
            # Combinar e remover duplicatas
            servicos = list(set(servicos_pgr + servicos_ambientais))
            servicos.sort()
            
            return servicos
        except Exception as e:
            logger.error(f"Erro ao obter serviços: {str(e)}")
            raise
    
    def obter_regioes_disponiveis(self, servico):
        """
        Obtém as regiões disponíveis para os serviços.
        
        Args:
            servico (str): Nome do serviço para filtrar as regiões
            
        Returns:
            list: Lista de regiões disponíveis
        """
        try:
            # Verificar se o serviço está nos preços de PGR
            if servico in self.precos_pgr['servico'].values:
                regioes = self.precos_pgr[self.precos_pgr['servico'] == servico]['regiao'].unique().tolist()
            # Verificar se o serviço está nos preços ambientais
            elif servico in self.precos_ambientais['servico'].values:
                regioes = self.precos_ambientais[self.precos_ambientais['servico'] == servico]['regiao'].unique().tolist()
            else:
                regioes = []
                
            regioes.sort()
            return regioes
        except Exception as e:
            logger.error(f"Erro ao obter regiões para o serviço {servico}: {str(e)}")
            raise
    
    def obter_variaveis_disponiveis(self, servico):
        """
        Obtém as variáveis disponíveis para um serviço específico.
        
        Args:
            servico (str): Nome do serviço
            
        Returns:
            dict: Dicionário com as variáveis disponíveis
        """
        try:
            # Verificar se o serviço está nos preços de PGR
            if servico in self.precos_pgr['servico'].values:
                # Para serviços de PGR, as variáveis são grau de risco e número de trabalhadores
                graus_risco = self.precos_pgr[self.precos_pgr['servico'] == servico]['grau_risco'].unique().tolist()
                faixas_trab = self.precos_pgr[self.precos_pgr['servico'] == servico]['num_trabalhadores'].unique().tolist()
                
                variaveis = {
                    'grau_risco': {
                        'nome': 'Grau de Risco',
                        'tipo': 'select',
                        'opcoes': sorted(graus_risco)
                    },
                    'num_trabalhadores': {
                        'nome': 'Número de Trabalhadores',
                        'tipo': 'select',
                        'opcoes': sorted(faixas_trab, key=lambda x: int(x.split('-')[0]) if '-' in x else int(x))
                    }
                }
            # Verificar se o serviço está nos preços ambientais
            elif servico in self.precos_ambientais['servico'].values:
                # Para serviços ambientais, as variáveis são tipo de avaliação e adicional GES/GHE
                tipos_avaliacao = self.precos_ambientais[self.precos_ambientais['servico'] == servico]['tipo_avaliacao'].unique().tolist()
                
                variaveis = {
                    'tipo_avaliacao': {
                        'nome': 'Tipo de Avaliação',
                        'tipo': 'select',
                        'opcoes': sorted(tipos_avaliacao)
                    },
                    'num_ges_ghe': {
                        'nome': 'Número de GES/GHE',
                        'tipo': 'numero',
                        'min': 0,
                        'max': 100
                    },
                    'num_avaliacoes_adicionais': {
                        'nome': 'Número de Avaliações Adicionais',
                        'tipo': 'numero',
                        'min': 0,
                        'max': 100
                    }
                }
            else:
                variaveis = {}
                
            return variaveis
        except Exception as e:
            logger.error(f"Erro ao obter variáveis para o serviço {servico}: {str(e)}")
            raise
    
    def obter_preco_servico(self, servico, regiao, tipo_avaliacao=None, grau_risco=None, num_trabalhadores=None, num_ges_ghe=0, num_avaliacoes_adicionais=0):
        """
        Obtém o preço de um serviço com base nos parâmetros fornecidos.
        
        Args:
            servico (str): Nome do serviço
            regiao (str): Região
            tipo_avaliacao (str, optional): Tipo de avaliação (para serviços ambientais)
            grau_risco (str, optional): Grau de risco (para serviços de PGR)
            num_trabalhadores (str, optional): Número de trabalhadores (para serviços de PGR)
            num_ges_ghe (int, optional): Número de GES/GHE (para serviços ambientais)
            num_avaliacoes_adicionais (int, optional): Número de avaliações adicionais (para serviços ambientais)
            
        Returns:
            float: Preço do serviço
        """
        try:
            # Verificar se o serviço está nos preços de PGR
            if servico in self.precos_pgr['servico'].values:
                # Filtrar por serviço, região, grau de risco e número de trabalhadores
                filtro = (
                    (self.precos_pgr['servico'] == servico) & 
                    (self.precos_pgr['regiao'] == regiao)
                )
                
                if grau_risco:
                    filtro = filtro & (self.precos_pgr['grau_risco'] == grau_risco)
                    
                if num_trabalhadores:
                    filtro = filtro & (self.precos_pgr['num_trabalhadores'] == num_trabalhadores)
                
                # Obter preço
                resultado = self.precos_pgr[filtro]
                
                if resultado.empty:
                    logger.warning(f"Nenhum preço encontrado para o serviço {servico} na região {regiao} com grau de risco {grau_risco} e {num_trabalhadores} trabalhadores")
                    return 0
                    
                preco = resultado['preco'].iloc[0]
                
            # Verificar se o serviço está nos preços ambientais
            elif servico in self.precos_ambientais['servico'].values:
                # Filtrar por serviço, região e tipo de avaliação
                filtro = (
                    (self.precos_ambientais['servico'] == servico) & 
                    (self.precos_ambientais['regiao'] == regiao)
                )
                
                if tipo_avaliacao:
                    filtro = filtro & (self.precos_ambientais['tipo_avaliacao'] == tipo_avaliacao)
                
                # Obter preço base
                resultado = self.precos_ambientais[filtro]
                
                if resultado.empty:
                    logger.warning(f"Nenhum preço encontrado para o serviço {servico} na região {regiao} com tipo de avaliação {tipo_avaliacao}")
                    return 0
                    
                preco_base = resultado['preco'].iloc[0]
                
                # Adicionar custo de GES/GHE adicionais
                adicional_ges_ghe = resultado['adicional_ges_ghe'].iloc[0] if 'adicional_ges_ghe' in resultado.columns else 0
                preco = preco_base + (adicional_ges_ghe * num_ges_ghe)
                
                # Adicionar custo de avaliações adicionais (50% do preço base por avaliação)
                preco += (preco_base * 0.5 * num_avaliacoes_adicionais)
                
            else:
                logger.warning(f"Serviço {servico} não encontrado")
                return 0
                
            return float(preco)
        except Exception as e:
            logger.error(f"Erro ao obter preço para o serviço {servico}: {str(e)}")
            raise
    
    def verificar_precos_csv(self):
        """
        Garante que todas as regiões tenham preços definidos para todos os serviços.
        """
        try:
            # Verificar preços ambientais
            if self.precos_ambientais is not None:
                servicos = self.precos_ambientais["servico"].unique()
                tipos_avaliacao = self.precos_ambientais["tipo_avaliacao"].unique()
                regioes = self.precos_ambientais["regiao"].unique()
                
                for servico in servicos:
                    for tipo in tipos_avaliacao:
                        for regiao in regioes:
                            df_filtrado = self.precos_ambientais[
                                (self.precos_ambientais["servico"] == servico) &
                                (self.precos_ambientais["tipo_avaliacao"] == tipo) &
                                (self.precos_ambientais["regiao"] == regiao)
                            ]
                            
                            if df_filtrado.empty:
                                logger.warning(f"Preço não definido para: Serviço={servico}, Tipo={tipo}, Região={regiao}")
            
            # Verificar preços PGR
            if self.precos_pgr is not None:
                servicos = self.precos_pgr["servico"].unique()
                graus_risco = self.precos_pgr["grau_risco"].unique()
                faixas_trab = self.precos_pgr["num_trabalhadores"].unique()
                regioes = self.precos_pgr["regiao"].unique()
                
                for servico in servicos:
                    for grau in graus_risco:
                        for faixa in faixas_trab:
                            for regiao in regioes:
                                df_filtrado = self.precos_pgr[
                                    (self.precos_pgr["servico"] == servico) &
                                    (self.precos_pgr["grau_risco"] == grau) &
                                    (self.precos_pgr["num_trabalhadores"] == faixa) &
                                    (self.precos_pgr["regiao"] == regiao)
                                ]
                                
                                if df_filtrado.empty:
                                    logger.warning(f"Preço não definido para: Serviço={servico}, Grau={grau}, Faixa={faixa}, Região={regiao}")
        
        except Exception as e:
            logger.error(f"Erro ao verificar preços CSV: {str(e)}")

# Instância global para uso direto
gerenciador_precos = GerenciadorPrecos() 