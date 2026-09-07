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

## 🌿 Flujo de Trabajo Ágil & Gobernanza en GitHub

- **`main`:** Código estable de producción.
- **`develop`:** Rama de integración continua.
- **`feat/*`:** Ramas de características individuales por Sprint.
- **CI/CD con GitHub Actions:**
  - `.github/workflows/ci.yml`: Ejecución automática de linters (`ruff`), verificación de tipos y tests con servicio de Postgres+pgvector.
  - `.github/workflows/cd.yml`: Compilación y empaquetado de contenedores Docker con Buildx ante tags de versión `v*.*.*`.
