#!/bin/bash

# Script de build para o Vercel

echo "Iniciando script de build..."
echo "Diretório atual: $(pwd)"
echo "Conteúdo do diretório: $(ls -la)"

# Instalar dependências
echo "Instalando dependências..."
pip install -r vercel-requirements.txt

# Verificar se Flask-Session foi instalado
echo "Verificando se Flask-Session foi instalado..."
if pip show flask-session; then
    echo "Flask-Session está instalado"
else
    echo "Flask-Session NÃO está instalado, tentando instalar novamente..."
    pip install Flask-Session==0.8.0
    
    if pip show flask-session; then
        echo "Flask-Session instalado com sucesso na segunda tentativa"
    else
        echo "AVISO: Flask-Session ainda não está instalado, mas continuaremos mesmo assim"
    fi
fi

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
echo "VERCEL_DEPLOYMENT: $VERCEL_DEPLOYMENT"
echo "FLASK_ENV: $FLASK_ENV"

# Listar pacotes instalados
echo "Pacotes instalados:"
pip list

# Verificar Python
echo "Versão do Python: $(python --version)"
echo "Caminho do Python: $(which python)"

# Verificar se podemos importar flask_session
echo "Tentando importar flask_session..."
python -c "
try:
    import flask_session
    print('flask_session importado com sucesso')
except ImportError as e:
    print(f'Erro ao importar flask_session: {e}')
"

echo "Build concluído com sucesso!" 