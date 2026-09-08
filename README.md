# 🛒 Ofertis Chile - Comparador de Canasta Básica & Alertas WhatsApp

Sistema fullstack con arquitectura multi-agente, minería de datos y base de datos vectorial (**PostgreSQL 16 + pgvector**) para búsqueda semántica, comparativa normalizada de precios ($\$ / \text{kg}$ y $\$ / \text{L}$) y alertas en tiempo real vía WhatsApp para productos de primera necesidad en Chile (**Lider, Jumbo, Santa Isabel y Unimarc**).

---

## 🚀 Arquitectura y Componentes Clave

- **Base de Datos Vectorial & Relacional:** PostgreSQL 16 con extensión `pgvector` e índice **HNSW** (`vector_cosine_ops`) para búsqueda semántica y deduplicación de productos equivalentes.
- **Motor de Embeddings:** Modelo multilingüe de 384 dimensiones (`paraphrase-multilingual-MiniLM-L12-v2`).
- **Minería de Datos & Taxonomía Chilena:**
  - `UnitNormalizerSkill`: Normaliza envases y presentaciones chilenas (`900 ml` $\rightarrow$ `0.9 L`, `400g` $\rightarrow$ `0.4 kg`) y calcula el precio por unidad base.
  - `ChileanMeatTaxonomySkill`: Clasificación oficial de carnes según la Norma Chilena **NCh 1424** (lomo liso, lomo vetado, posta negra, etc.) y productos de despensa.
  - `ScrapingSkill`: Extractor HTTP resiliente con rate limiting adaptativo y headers optimizados para retail chileno.
- **Alertas por WhatsApp:**
  - `WhatsAppNotificationSkill`: Formateo de mensajes enriquecidos con comparativa de ahorro y enlaces directos.
  - Soporta modo simulado (*mock*) para desarrollo y *Twilio Sandbox / Meta Cloud API* para producción.
- **Frontend:** React (Vite + TypeScript + Tailwind CSS + Lucide Icons + Recharts).
- **Backend:** FastAPI (Python 3.12) + SQLAlchemy 2.0 Async (`asyncpg`) + Pydantic v2.

---

## 🛠️ Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose.
- Opcionalmente: Python 3.12+ y Node.js 22+ para ejecución nativa.

---

## 💻 Entorno de Desarrollo (Local con Hot-Reload)

### 1. Clonar el repositorio y configurar variables de entorno:
```bash
cp .env.example .env
```

### 2. Levantar la infraestructura en modo desarrollo:
```bash
docker compose -f docker-compose.dev.yml up --build -d
```

Los servicios iniciarán en:
- **Frontend React:** [http://localhost:5173](http://localhost:5173)
- **Backend FastAPI:** [http://localhost:8000](http://localhost:8000)
- **Documentación Interactiva Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL + pgvector:** Puerto `5432`

### 3. Poblar la base de datos con la Canasta Básica Chilena:
```bash
docker compose -f docker-compose.dev.yml exec backend python ../scripts/seed_chilean_data.py
```
*(O de forma local si tienes Python configurado: `python3 scripts/seed_chilean_data.py`)*

### 4. Ejecutar las Pruebas Unitarias:
```bash
docker compose -f docker-compose.dev.yml exec backend pytest -v
```

---

## 🏭 Despliegue en Producción (Hardened & Multi-Stage)

El proyecto incluye configuración de grado empresarial para producción:
- Imágenes Docker **Multi-Stage** (Backend sin compiladores ni herramientas de build; Frontend servido en **Nginx Alpine < 25MB** con compresión Gzip y headers de seguridad).
- Contenedores ejecutándose con **usuarios sin privilegios (non-root)**.
- Límites de CPU y memoria predefinidos.
- Healthchecks integrados.

### Para desplegar en producción:
```bash
# 1. Configurar archivo seguro de producción
cp .env.example .env.prod
# Editar .env.prod con credenciales reales y proveedor de WhatsApp

# 2. Levantar contenedores optimizados
docker compose -f docker-compose.prod.yml up --build -d
```

---

## 🎮 Guía Operativa: Iniciar, Monitorear y Detener Procesos

Esta guía detalla cómo gestionar la infraestructura Docker, el demonio de minería continua y los tres agentes satélites autónomos de Ofertis.

---

### 1. Infraestructura Docker (Base de Datos, Redis, Backend y Frontend)

#### Iniciar Contenedores:
```bash
# Modo Desarrollo (Hot-Reloading en puerto 5173 y 8000)
docker compose -f docker-compose.dev.yml up -d

# Modo Producción (Optimizado, Nginx < 25MB y usuarios non-root)
docker compose -f docker-compose.prod.yml up -d
```

#### Monitorear y Ver Logs:
```bash
# Ver estado de los contenedores
docker compose -f docker-compose.dev.yml ps

# Ver consumo de CPU y memoria en tiempo real
docker stats --no-stream

# Seguir logs en tiempo real (todos o uno específico)
docker compose -f docker-compose.dev.yml logs -f
docker compose -f docker-compose.dev.yml logs -f backend
docker compose -f docker-compose.dev.yml logs -f frontend
```

#### Detener Contenedores:
```bash
# Detener conservando los datos de PostgreSQL y Redis
docker compose -f docker-compose.dev.yml down

# Detener y LIMPIAR volúmenes (reset total de base de datos)
docker compose -f docker-compose.dev.yml down -v
```

---

### 2. Demonio de Minería Masiva Continua (Docker)

El barrido continuo recorre 167 categorías departamentales en Jumbo, Lider, Santa Isabel y Unimarc, con pausas térmicas adaptativas (< 5% CPU).

#### Iniciar Minería en Segundo Plano:
```bash
docker exec -d ofertis_backend_dev python scripts/overnight_mining_daemon.py
```

#### Monitorear Progreso de Minería:
```bash
# Ver log en vivo de extracciones y similitud vectorial pgvector
tail -f backend/logs/overnight_mining.log

# Consultar ciclo actual y total histórico procesado
cat backend/logs/mining_state.json

# Consultar métricas en la API REST
curl -s http://localhost:8000/api/v1/mining/stats | python3 -m json.tool
```

#### Detener Minería Continua:
```bash
docker exec ofertis_backend_dev pkill -f overnight_mining_daemon.py
```

---

### 3. Agentes Satélites Autónomos (Host Local)

Los agentes se ejecutan de forma independiente en Python 3 sin interferir con la infraestructura Docker.

#### A. Agente 'Sentinela' (Alerta Temprana de Precios de Alimentos)
Monitorea causalmente ODEPA, Banco Central (USD/CLP), DMC y FAO sin especulación.

```bash
# Ejecución única on-demand
python3 -m sentinela.sentinela.main --now

# Iniciar demonio continuo en segundo plano (cada 4 horas)
nohup python3 -m sentinela.sentinela.main --daemon --interval 4 > sentinela/logs/daemon.log 2>&1 &

# Detener demonio Sentinela
pkill -f "sentinela.sentinela.main"

# Ver reportes generados
ls -lh sentinela/reports/
```

#### B. Agente 'Radar Alternativo' (Canales No Tradicionales)
Monitorea El Carnicero, SuperBodega aCuenta y Mercado Lo Valledor (ahorros hasta 65%).

```bash
# Ejecución única on-demand
python3 -m radar_alternativo.radar_alternativo.main --now

# Iniciar demonio continuo en segundo plano (cada 6 horas)
nohup python3 -m radar_alternativo.radar_alternativo.main --daemon --interval 6 > radar_alternativo/logs/daemon.log 2>&1 &

# Detener demonio Radar Alternativo
pkill -f "radar_alternativo.radar_alternativo.main"

# Ver reportes generados
ls -lh radar_alternativo/reports/
```

#### C. Agente 'El Cronista Económico' (Redacción de Blog con Gráficos)
Redacta artículos periódicos en Markdown con gráficos Mermaid (Causal + Gantt) y SVG vectorial.

```bash
# Redactar artículo inmediatamente con los datos vigentes
python3 -m cronista.main --now

# Iniciar demonio continuo en segundo plano (cada 6 horas)
nohup python3 -m cronista.main --daemon --interval 6 > cronista/logs/cronista_daemon.out 2>&1 &

# Detener demonio El Cronista
pkill -f "cronista.main"

# Ver artículos y gráficos generados
ls -lh cronista/articles/
ls -lh cronista/articles/assets/
```

---

### 4. Comandos de Control Global Rápido

```bash
# Verificar qué agentes satélites están corriendo en el host
ps aux | grep -E "sentinela|radar_alternativo|cronista" | grep -v grep

# Detener TODOS los agentes satélites simultáneamente
pkill -f "sentinela.sentinela.main"
pkill -f "radar_alternativo.radar_alternativo.main"
pkill -f "cronista.main"

# Reiniciar backend de Ofertis tras cambios de código
docker compose -f docker-compose.dev.yml restart backend
```

---

## 🌿 Flujo de Trabajo Ágil & Gobernanza en GitHub

- **`main`:** Código estable de producción.
- **`develop`:** Rama de integración continua.
- **`feat/*`:** Ramas de características individuales por Sprint.
- **CI/CD con GitHub Actions:**
  - `.github/workflows/ci.yml`: Ejecución automática de linters (`ruff`), verificación de tipos y tests con servicio de Postgres+pgvector.
  - `.github/workflows/cd.yml`: Compilación y empaquetado de contenedores Docker con Buildx ante tags de versión `v*.*.*`.
