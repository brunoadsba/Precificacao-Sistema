"""
Modelo para gerenciamento de preços dos serviços usando Firestore.
"""
import logging
from config.firebase_config import firebase_config

# Configurar logger
logger = logging.getLogger(__name__)

class GerenciadorPrecosFirestore:
    """
    Classe para gerenciar os preços dos serviços usando Firestore.
    """
    def __init__(self):
        """
        Inicializa o gerenciador de preços.
        """
        self.db = None
        self.app = None
        self.initialized = False
        
    def init_app(self, app):
        """
        Inicializa o gerenciador de preços com a aplicação Flask.
        
        Args:
            app: Aplicação Flask
        """
        self.app = app
        
        # Verificar se o Firebase está inicializado
        if not firebase_config.initialized:
            firebase_config.init_app(app)
            
        if firebase_config.initialized:
            self.db = firebase_config.db
            self.initialized = True
            logger.info("Gerenciador de preços Firestore inicializado")
            
            # Importar dados CSV para Firestore se necessário
            if app.config.get('IMPORTAR_CSV_PARA_FIRESTORE', False):
                self.importar_csv_para_firestore(
                    app.config['PRECOS_PGR_CSV'],
                    app.config['PRECOS_AMBIENTAIS_CSV']
                )
        else:
            logger.warning("Firebase não inicializado. Gerenciador de preços Firestore não funcionará corretamente.")
            
    def importar_csv_para_firestore(self, caminho_pgr, caminho_ambientais):
        """
        Importa dados de arquivos CSV para o Firestore.
        
        Args:
            caminho_pgr (str): Caminho para o arquivo CSV com os preços de PGR
            caminho_ambientais (str): Caminho para o arquivo CSV com os preços ambientais
        """
        try:
            import pandas as pd
            import os
            
            # Verificar se o Firestore está inicializado
            if not self.initialized:
                logger.warning("Firestore não inicializado. Não é possível importar dados.")
                return
                
            # Importar preços PGR
            if os.path.exists(caminho_pgr):
                df_pgr = pd.read_csv(caminho_pgr, encoding='utf-8')
                
                # Criar batch para operações em lote
                batch = self.db.batch()
                
                # Adicionar cada registro ao Firestore
                for _, row in df_pgr.iterrows():
                    doc_ref = self.db.collection('precos_pgr').document()
                    batch.set(doc_ref, row.to_dict())
                
                # Commit do batch
                batch.commit()
                logger.info(f"Preços PGR importados para o Firestore: {len(df_pgr)} registros")
                
            # Importar preços ambientais
            if os.path.exists(caminho_ambientais):
                df_ambientais = pd.read_csv(caminho_ambientais, encoding='utf-8')
                
                # Criar batch para operações em lote
                batch = self.db.batch()
                
                # Adicionar cada registro ao Firestore
                for _, row in df_ambientais.iterrows():
                    doc_ref = self.db.collection('precos_ambientais').document()
                    batch.set(doc_ref, row.to_dict())
                
                # Commit do batch
                batch.commit()
                logger.info(f"Preços Ambientais importados para o Firestore: {len(df_ambientais)} registros")
                
        except Exception as e:
            logger.error(f"Erro ao importar dados para o Firestore: {str(e)}")
            
    def obter_servicos(self):
        """
        Retorna a lista de serviços disponíveis.
        
        Returns:
            list: Lista de serviços disponíveis
        """
        try:
            if not self.initialized:
                logger.warning("Firestore não inicializado. Não é possível obter serviços.")
                return []
                
            # Obter serviços de PGR
            servicos_pgr = set()
            pgr_docs = self.db.collection('precos_pgr').stream()
            for doc in pgr_docs:
                data = doc.to_dict()
                if 'servico' in data:
                    servicos_pgr.add(data['servico'])
            
            # Obter serviços ambientais
            servicos_ambientais = set()
            ambientais_docs = self.db.collection('precos_ambientais').stream()
            for doc in ambientais_docs:
                data = doc.to_dict()
                if 'servico' in data:
                    servicos_ambientais.add(data['servico'])
            
            # Combinar e ordenar
            servicos = list(servicos_pgr.union(servicos_ambientais))
            servicos.sort()
            
            return servicos
        except Exception as e:
            logger.error(f"Erro ao obter serviços: {str(e)}")
            return []
            
    def obter_regioes_disponiveis(self, servico):
        """
        Retorna as regiões disponíveis para um serviço.
        
        Args:
            servico (str): Nome do serviço
            
        Returns:
            list: Lista de regiões disponíveis
        """
        try:
            if not self.initialized:
                logger.warning("Firestore não inicializado. Não é possível obter regiões.")
                return []
                
            # Verificar se o serviço está nos preços de PGR
            regioes = set()
            
            # Buscar em preços PGR
            pgr_docs = self.db.collection('precos_pgr').where('servico', '==', servico).stream()
            for doc in pgr_docs:
                data = doc.to_dict()
                if 'regiao' in data:
                    regioes.add(data['regiao'])
            
            # Se não encontrou em PGR, buscar em ambientais
            if not regioes:
                ambientais_docs = self.db.collection('precos_ambientais').where('servico', '==', servico).stream()
                for doc in ambientais_docs:
                    data = doc.to_dict()
                    if 'regiao' in data:
                        regioes.add(data['regiao'])
            
            # Ordenar e retornar
            return sorted(list(regioes))
        except Exception as e:
            logger.error(f"Erro ao obter regiões para o serviço {servico}: {str(e)}")
            return []
            
    def obter_variaveis_disponiveis(self, servico):
        """
        Retorna as variáveis disponíveis para um serviço.
        
        Args:
            servico (str): Nome do serviço
            
        Returns:
            dict: Dicionário com as variáveis disponíveis
        """
        try:
            if not self.initialized:
                logger.warning("Firestore não inicializado. Não é possível obter variáveis.")
                return {}
                
            # Verificar se o serviço está nos preços de PGR
            pgr_docs = list(self.db.collection('precos_pgr').where('servico', '==', servico).limit(1).stream())
            
            if pgr_docs:
                # Para serviços de PGR, as variáveis são grau de risco e número de trabalhadores
                graus_risco = set()
                faixas_trab = set()
                
                # Buscar todos os valores únicos
                pgr_all_docs = self.db.collection('precos_pgr').where('servico', '==', servico).stream()
                for doc in pgr_all_docs:
                    data = doc.to_dict()
                    if 'grau_risco' in data:
                        graus_risco.add(data['grau_risco'])
                    if 'num_trabalhadores' in data:
                        faixas_trab.add(data['num_trabalhadores'])
                
                variaveis = {
                    'grau_risco': {
                        'nome': 'Grau de Risco',
                        'tipo': 'select',
                        'opcoes': sorted(list(graus_risco))
                    },
                    'num_trabalhadores': {
                        'nome': 'Número de Trabalhadores',
                        'tipo': 'select',
                        'opcoes': sorted(list(faixas_trab), key=lambda x: int(x.split('-')[0]) if '-' in x else int(x))
                    }
                }
            else:
                # Verificar se o serviço está nos preços ambientais
                ambientais_docs = list(self.db.collection('precos_ambientais').where('servico', '==', servico).limit(1).stream())
                
                if ambientais_docs:
                    # Para serviços ambientais, as variáveis são tipo de avaliação e adicional GES/GHE
                    tipos_avaliacao = set()
                    
                    # Buscar todos os valores únicos
                    ambientais_all_docs = self.db.collection('precos_ambientais').where('servico', '==', servico).stream()
                    for doc in ambientais_all_docs:
                        data = doc.to_dict()
                        if 'tipo_avaliacao' in data:
                            tipos_avaliacao.add(data['tipo_avaliacao'])
                    
                    variaveis = {
                        'tipo_avaliacao': {
                            'nome': 'Tipo de Avaliação',
                            'tipo': 'select',
                            'opcoes': sorted(list(tipos_avaliacao))
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
            return {}
            
    def obter_preco_servico(self, servico, regiao, tipo_avaliacao=None, grau_risco=None, num_trabalhadores=None, num_ges_ghe=0, num_avaliacoes_adicionais=0):
        """
        Retorna o preço de um serviço com base nos parâmetros fornecidos.
        
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
            if not self.initialized:
                logger.warning("Firestore não inicializado. Não é possível obter preço.")
                return 0
                
            # Verificar se o serviço está nos preços de PGR
            query = self.db.collection('precos_pgr').where('servico', '==', servico).where('regiao', '==', regiao)
            
            if grau_risco:
                query = query.where('grau_risco', '==', grau_risco)
                
            if num_trabalhadores:
                query = query.where('num_trabalhadores', '==', num_trabalhadores)
            
            pgr_docs = list(query.stream())
            
            if pgr_docs:
                # Obter preço
                preco = float(pgr_docs[0].to_dict().get('preco', 0))
                return preco
            
            # Verificar se o serviço está nos preços ambientais
            query = self.db.collection('precos_ambientais').where('servico', '==', servico).where('regiao', '==', regiao)
            
            if tipo_avaliacao:
                query = query.where('tipo_avaliacao', '==', tipo_avaliacao)
            
            ambientais_docs = list(query.stream())
            
            if ambientais_docs:
                # Obter preço base
                data = ambientais_docs[0].to_dict()
                preco_base = float(data.get('preco', 0))
                
                # Adicionar custo de GES/GHE adicionais
                adicional_ges_ghe = float(data.get('adicional_ges_ghe', 0))
                preco = preco_base + (adicional_ges_ghe * num_ges_ghe)
                
                # Adicionar custo de avaliações adicionais (50% do preço base por avaliação)
                preco += (preco_base * 0.5 * num_avaliacoes_adicionais)
                
                return preco
            
            logger.warning(f"Serviço {servico} não encontrado")
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao obter preço para o serviço {servico}: {str(e)}")
            return 0

# Instância global do gerenciador de preços
gerenciador_precos_firestore = GerenciadorPrecosFirestore() 