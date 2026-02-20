FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Instalar dependências de sistema necessárias apenas para build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e gerar wheels para evitar compilação no final
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Dependências de sistema mínimas em runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar wheels e instalar sem compilar
COPY --from=builder /wheels /wheels
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt || \
    (echo "Fallback: instalar via PyPI" && pip install --no-cache-dir -r requirements.txt)

# Copiar código da aplicação
COPY . .

# Permitir execução do entrypoint
RUN chmod +x /app/entrypoint.sh

ENV FLASK_APP=app.py
EXPOSE 5000

CMD ["/app/entrypoint.sh"]