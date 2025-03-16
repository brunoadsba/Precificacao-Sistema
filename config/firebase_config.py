"""
Configuração do Firebase para o sistema de precificação.
"""
import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from dotenv import load_dotenv

# Configurar logger
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

class FirebaseConfig:
    """
    Classe para configuração e gerenciamento do Firebase.
    """
    def __init__(self):
        """
        Inicializa a configuração do Firebase.
        """
        self.app = None
        self.db = None
        self.bucket = None
        self.initialized = False
    
    def init_app(self, app):
        """
        Inicializa o Firebase com a aplicação Flask.
        
        Args:
            app: Aplicação Flask
        """
        self.app = app
        
        try:
            # Verificar se as credenciais estão definidas como variável de ambiente
            firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
            
            if firebase_credentials:
                # Usar credenciais da variável de ambiente
                cred_dict = json.loads(firebase_credentials)
                cred = credentials.Certificate(cred_dict)
            else:
                # Verificar se existe um arquivo de credenciais
                cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
                
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                else:
                    logger.warning("Credenciais do Firebase não encontradas. Algumas funcionalidades podem não funcionar corretamente.")
                    return
            
            # Inicializar o Firebase
            self.firebase_app = firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'precificacao-sistema.appspot.com')
            })
            
            # Inicializar Firestore
            self.db = firestore.client()
            
            # Inicializar Storage
            self.bucket = storage.bucket()
            
            self.initialized = True
            logger.info("Firebase inicializado com sucesso.")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Firebase: {str(e)}")
    
    def verificar_token(self, token):
        """
        Verifica um token de autenticação do Firebase.
        
        Args:
            token (str): Token de autenticação
            
        Returns:
            dict: Dados do usuário se o token for válido, None caso contrário
        """
        if not self.initialized:
            logger.warning("Firebase não inicializado. Não é possível verificar o token.")
            return None
            
        try:
            return auth.verify_id_token(token)
        except Exception as e:
            logger.error(f"Erro ao verificar token: {str(e)}")
            return None
    
    def upload_arquivo(self, caminho_destino, conteudo, tipo_conteudo=None):
        """
        Faz upload de um arquivo para o Firebase Storage.
        
        Args:
            caminho_destino (str): Caminho de destino no Storage
            conteudo (bytes/str): Conteúdo do arquivo
            tipo_conteudo (str, optional): Tipo de conteúdo (MIME type)
            
        Returns:
            str: URL do arquivo no Storage, None em caso de erro
        """
        if not self.initialized:
            logger.warning("Firebase não inicializado. Não é possível fazer upload do arquivo.")
            return None
            
        try:
            blob = self.bucket.blob(caminho_destino)
            
            if isinstance(conteudo, str):
                blob.upload_from_string(conteudo, content_type=tipo_conteudo)
            else:
                blob.upload_from_file(conteudo, content_type=tipo_conteudo)
                
            # Tornar o arquivo público e obter URL
            blob.make_public()
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload do arquivo: {str(e)}")
            return None
    
    def download_arquivo(self, caminho_origem):
        """
        Faz download de um arquivo do Firebase Storage.
        
        Args:
            caminho_origem (str): Caminho do arquivo no Storage
            
        Returns:
            bytes: Conteúdo do arquivo, None em caso de erro
        """
        if not self.initialized:
            logger.warning("Firebase não inicializado. Não é possível fazer download do arquivo.")
            return None
            
        try:
            blob = self.bucket.blob(caminho_origem)
            return blob.download_as_bytes()
            
        except Exception as e:
            logger.error(f"Erro ao fazer download do arquivo: {str(e)}")
            return None

# Instância global da configuração do Firebase
firebase_config = FirebaseConfig() 