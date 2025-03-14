#!/bin/bash

# Script de build para o Vercel

echo "Iniciando script de build..."

# Instalar dependências
echo "Instalando dependências..."
pip install -r vercel-requirements.txt

# Criar diretório de sessão
echo "Criando diretório de sessão..."
mkdir -p flask_session

# Verificar se os arquivos CSV existem
echo "Verificando arquivos CSV..."
if [ ! -f "Precos_PGR.csv" ]; then
    echo "Criando arquivo Precos_PGR.csv..."
    echo "Serviço,Grau_Risco,Faixa_Trab,Região,Preço" > Precos_PGR.csv
    echo "\"Elaboração e acompanhamento do PGR\",\"1 e 2\",\"Até 19 Trab.\",\"Central\",700.00" >> Precos_PGR.csv
fi

if [ ! -f "Precos_Ambientais.csv" ]; then
    echo "Criando arquivo Precos_Ambientais.csv..."
    echo "Serviço,Tipo_Avaliacao,Adicional_GES_GHE,Região,Preço" > Precos_Ambientais.csv
    echo "\"Coleta para Avaliação Ambiental\",\"Pacote (1 a 4 avaliações)\",50.00,\"Central\",300.00" >> Precos_Ambientais.csv
fi

# Listar pacotes instalados
echo "Pacotes instalados:"
pip list

echo "Build concluído com sucesso!" 