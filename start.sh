#!/bin/bash
# Script para iniciar o servidor RAIA em background

# Navegar para o diretório do script (garante que rode do lugar certo)
cd "$(dirname "$0")"

# Verificar se já está rodando
if lsof -i :3001 > /dev/null; then
    echo "⚠️  O servidor já parece estar rodando na porta 3001."
    echo "Use 'lsof -i :3001' para ver o processo e 'kill -9 <PID>' para parar."
    exit 1
fi

# Iniciar com nohup
echo "🚀 Iniciando servidor..."
nohup ./venv/bin/python app.py > output.log 2>&1 &

echo "✅ Servidor iniciado em background!"
echo "📄 Logs estão sendo salvos em 'output.log'"
echo "Para acompanhar os logs, use: tail -f output.log"
