#!/bin/bash

# Script de build para ambiente local

echo "Iniciando script de build..."
echo "Diretório atual: $(pwd)"
echo "Conteúdo do diretório: $(ls -la)"

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python -m venv venv
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências principais primeiro
echo "Instalando dependências principais..."
pip install -U pip setuptools wheel

# Instalar dependências do requirements.txt
echo "Instalando dependências do requirements.txt..."
pip install -r requirements.txt

# Criar diretório de sessão
echo "Criando diretório de sessão..."
mkdir -p flask_session
chmod 777 flask_session

# Verificar se os arquivos CSV existem
echo "Verificando arquivos CSV..."
if [ ! -f "Precos_PGR.csv" ]; then
    echo "Criando arquivo Precos_PGR.csv..."
    echo "Serviço,Grau_Risco,Faixa_Trab,Região,Preço" > Precos_PGR.csv
    echo "\"Elaboração e acompanhamento do PGR\",\"1 e 2\",\"Até 19 Trab.\",\"Central\",700.00" >> Precos_PGR.csv
    chmod 666 Precos_PGR.csv
fi

if [ ! -f "Precos_Ambientais.csv" ]; then
    echo "Criando arquivo Precos_Ambientais.csv..."
    echo "Serviço,Tipo_Avaliacao,Adicional_GES_GHE,Região,Preço" > Precos_Ambientais.csv
    echo "\"Coleta para Avaliação Ambiental\",\"Pacote (1 a 4 avaliações)\",50.00,\"Central\",300.00" >> Precos_Ambientais.csv
    chmod 666 Precos_Ambientais.csv
fi

# Verificar variáveis de ambiente
echo "Verificando variáveis de ambiente..."
if [ ! -f ".env" ]; then
    echo "Criando arquivo .env..."
    echo "SECRET_KEY=chave_secreta_padrao" > .env
    echo "FLASK_ENV=production" >> .env
    echo "FLASK_APP=app.py" >> .env
    echo "SESSION_TYPE=filesystem" >> .env
    echo "SESSION_PERMANENT=False" >> .env
    echo "SESSION_FILE_DIR=./flask_session" >> .env
fi

# Listar pacotes instalados
echo "Pacotes instalados:"
pip list

# Verificar Python
echo "Versão do Python: $(python --version)"
echo "Caminho do Python: $(which python)"

echo "Build concluído com sucesso!" 