# Usar uma imagem base oficial do Python leve
FROM python:3.11-slim

# Definir variáveis de ambiente para evitar arquivos .pyc e logs em buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir o diretório de trabalho no container
WORKDIR /app

# Instalar dependências do sistema necessárias (opcional, mas bom pra bibliotecas como pandas/numpy se precisarem de compilação)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do projeto para o container
COPY . .

# Expor a porta que o Flask usa
EXPOSE 3001

# Comando para iniciar a aplicação
# Recomendado para produção: usar gunicorn (mas mantendo o padrão atual por enquanto)
CMD ["python", "app.py"]
