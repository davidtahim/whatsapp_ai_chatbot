# Stage de build: gera wheels das dependências
FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Dependências de sistema necessárias para build (mínimas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Gerar wheels (evita compilar durante pip install no final)
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Stage final: runtime enxuto
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Dependências de sistema necessárias em runtime (mínimas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia wheels e instala sem compilar
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir --find-links=/wheels -r requirements.txt

# Copia código da aplicação
COPY . .

# Permitir execução do entrypoint
RUN chmod +x /app/entrypoint.sh

ENV FLASK_APP=app.py
EXPOSE 5000

CMD ["/app/entrypoint.sh"]