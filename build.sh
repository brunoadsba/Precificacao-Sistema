#!/bin/bash

# Script de configuração do ambiente para o Sistema de Precificação

echo "Iniciando configuração do ambiente..."

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não encontrado. Por favor, instale o Python 3 antes de continuar."
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
echo "Versão do Python: $PYTHON_VERSION"

# Criar ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Instalar dependências
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretórios necessários
echo "Criando diretórios necessários..."
mkdir -p csv
mkdir -p logs
mkdir -p orcamentos
mkdir -p uploads
mkdir -p templates

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "Criando arquivo .env a partir do modelo..."
    cp .env.example .env
    echo "Por favor, edite o arquivo .env com suas configurações."
fi

# Verificar se os arquivos CSV de preços existem
if [ ! -f csv/Precos_PGR.csv ]; then
    echo "Criando arquivo CSV de preços PGR de exemplo..."
    echo "Serviço,Grau_Risco,Faixa_Trab,Região,Preço" > csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,1 e 2,Até 10 Trab.,Central,500.00" >> csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,1 e 2,Até 10 Trab.,Norte,650.00" >> csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,1 e 2,Até 10 Trab.,Oeste,700.00" >> csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,1 e 2,Até 10 Trab.,Sudoeste,750.00" >> csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,1 e 2,Até 10 Trab.,Sul e Extremo Sul,800.00" >> csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,3 e 4,Até 10 Trab.,Central,600.00" >> csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,3 e 4,Até 10 Trab.,Norte,750.00" >> csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,3 e 4,Até 10 Trab.,Oeste,800.00" >> csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,3 e 4,Até 10 Trab.,Sudoeste,850.00" >> csv/Precos_PGR.csv
    echo "Elaboração e acompanhamento do PGR,3 e 4,Até 10 Trab.,Sul e Extremo Sul,900.00" >> csv/Precos_PGR.csv
fi

if [ ! -f csv/Precos_Ambientais.csv ]; then
    echo "Criando arquivo CSV de preços Ambientais de exemplo..."
    echo "Serviço,Tipo_Avaliacao,Adicional_GES_GHE,Região,Preço" > csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Pacote (1 a 4 avaliações),0,Central,300.00" >> csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Pacote (1 a 4 avaliações),0,Norte,450.00" >> csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Pacote (1 a 4 avaliações),0,Oeste,500.00" >> csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Pacote (1 a 4 avaliações),0,Sudoeste,550.00" >> csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Pacote (1 a 4 avaliações),0,Sul e Extremo Sul,600.00" >> csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Por Avaliação Adicional,0,Central,75.00" >> csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Por Avaliação Adicional,0,Norte,112.50" >> csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Por Avaliação Adicional,0,Oeste,125.00" >> csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Por Avaliação Adicional,0,Sudoeste,137.50" >> csv/Precos_Ambientais.csv
    echo "Coleta para Avaliação Ambiental,Por Avaliação Adicional,0,Sul e Extremo Sul,150.00" >> csv/Precos_Ambientais.csv
    echo "Laudo de Insalubridade,Por GES/GHE,100.00,Central,400.00" >> csv/Precos_Ambientais.csv
    echo "Laudo de Insalubridade,Por GES/GHE,150.00,Norte,550.00" >> csv/Precos_Ambientais.csv
    echo "Laudo de Insalubridade,Por GES/GHE,150.00,Oeste,600.00" >> csv/Precos_Ambientais.csv
    echo "Laudo de Insalubridade,Por GES/GHE,150.00,Sudoeste,650.00" >> csv/Precos_Ambientais.csv
    echo "Laudo de Insalubridade,Por GES/GHE,150.00,Sul e Extremo Sul,700.00" >> csv/Precos_Ambientais.csv
fi

echo "Configuração concluída com sucesso!"
echo "Para iniciar a aplicação, execute: python app.py" 