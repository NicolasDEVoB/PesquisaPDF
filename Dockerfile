# Usamos uma imagem leve do Python
FROM python:3.11-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para o PyMuPDF e outras libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o arquivo de dependências primeiro (aproveita o cache do Docker)
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto para o container
COPY . .

# Expõe a porta que o FastAPI vai usar
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "docintel.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
