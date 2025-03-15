#!/bin/bash

# Script de build específico para o Vercel

echo "Iniciando script de build para o Vercel..."
echo "Diretório atual: $(pwd)"
echo "Conteúdo do diretório: $(ls -la)"

# Instalar dependências principais primeiro
echo "Instalando dependências principais..."
pip install -U pip setuptools wheel

# Instalar dependências diretamente
echo "Instalando dependências específicas..."
pip install Flask==2.3.3 Werkzeug==2.3.7 Flask-WTF==1.2.0 pandas==2.2.0 python-dotenv==1.0.0 Babel==2.8.0 reportlab==4.3.1 waitress==2.1.2 email-validator==2.0.0.post2 Flask-Mail==0.9.1 cachelib==0.13.0 Flask-Session==0.8.0

# Criar diretório de sessão e garantir permissões
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

# Criar um arquivo requirements.txt simplificado para o Vercel
echo "Criando requirements.txt simplificado..."
cat > requirements.txt << EOL
Flask==2.3.3
Werkzeug==2.3.7
Flask-WTF==1.2.0
pandas==2.2.0
python-dotenv==1.0.0
Babel==2.8.0
reportlab==4.3.1
waitress==2.1.2
email-validator==2.0.0.post2
Flask-Mail==0.9.1
cachelib==0.13.0
Flask-Session==0.8.0
EOL

echo "Build concluído com sucesso!" 