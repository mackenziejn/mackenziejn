#!/bin/bash

# Caminho para o venv
VENV_DIR="venv"

# Verifica se o venv existe
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️ Ambiente virtual não encontrado. Criando..."
    python3 -m venv "$VENV_DIR"
fi

# Ativa o venv
source "$VENV_DIR/bin/activate"

# Instala dependências se necessário
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Roda o bot
if [ -f "src/bot_main.py" ]; then
    echo "🚀 Iniciando JacarHair Bot..."
    python -m src.bot_main
else
    echo "❌ Arquivo src/bot_main.py não encontrado!"
fi
