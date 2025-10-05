# Use Python 3.11 slim como base
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependências
COPY api/requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cria a estrutura de diretórios
RUN mkdir -p /app/data

# Copia o arquivo CSV de dados
COPY data/books_data.csv /app/data/books_data.csv

# Copia o código da aplicação
COPY api/main.py .
COPY api/models.py .
COPY api/data_service.py .
COPY api/auth_service.py .

# Cria um usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expõe a porta 8000
EXPOSE 8000

# Comando para executar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
