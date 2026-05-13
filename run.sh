#!/bin/bash
# Calculadora de Valor Hora/Aula - Launcher (Linux/Mac)

echo ""
echo "===================================="
echo " Calculadora de Valor Hora/Aula"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não foi encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements if needed
pip list | grep PyQt5 > /dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependências..."
    pip install -r requirements.txt
fi

# Run the application
echo ""
echo "Iniciando aplicação..."
echo ""
python main.py

