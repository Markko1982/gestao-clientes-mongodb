# Imagem base com Python (completa, para facilitar pandas etc.)
FROM python:3.12

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia apenas o requirements primeiro (melhor para cache de build)
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Agora copia o restante do código do projeto
COPY . .

# Algumas configs úteis de runtime
ENV PYTHONUNBUFFERED=1

# Porta padrão da API FastAPI
EXPOSE 8000

# Comando para subir a API
# - src.api:app  -> módulo e objeto FastAPI
# - --host 0.0.0.0 -> expõe para fora do container
# - --port 8000    -> porta interna
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
