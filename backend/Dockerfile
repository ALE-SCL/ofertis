# ===========================================================
# STAGE 1: Build & Dependency Resolution
# ===========================================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /install

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ===========================================================
# STAGE 2: Production Minimal Runtime (Non-Root User)
# ===========================================================
FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

WORKDIR /app

# Instalar sólo las librerías dinámicas compartidas de PostgreSQL (sin compilador)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario sin privilegios root por seguridad
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/sh appuser

# Copiar dependencias de Python precompiladas desde builder
COPY --from=builder /install /usr/local

# Copiar código fuente
COPY app /app/app

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Healthcheck interno para verificar que FastAPI responda
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
