import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager

# Resolver rutas para entornos de despliegue (Render, Docker, Local)
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_APP_DIR)
_REPO_ROOT = os.path.dirname(_BACKEND_DIR)
for _p in (_REPO_ROOT, _BACKEND_DIR, _APP_DIR):
    if _p and os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.products import router as products_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.mining import router as mining_router
from app.api.v1.radar import router as radar_router
from app.api.v1.sentinela import router as sentinela_router
from app.api.v1.cronista import router as cronista_router

# Configuración de Logging estructurado
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ofertis.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manejador del ciclo de vida de la aplicación.
    Inicializa conexiones, verifica tablas y precarga datos base si está vacía.
    """
    logger.info(f"Iniciando Ofertis Backend en modo [{settings.ENVIRONMENT}]...")
    logger.info(f"Canal de alertas WhatsApp: [{settings.WHATSAPP_PROVIDER}]")
    
    # Asegurar tablas y catálogo inicial (en Render o local)
    try:
        from app.services.seed_service import ensure_db_schema_and_seed
        await ensure_db_schema_and_seed()
    except Exception as e:
        logger.warning(f"Aviso durante la inicialización de DB en lifespan: {e}")

    # Bucle periódico de 24 horas (opcional en segundo plano)
    sync_task = None
    import os
    if os.getenv("ENABLE_DAILY_PRICE_LOOP", "false").lower() in ["true", "1", "yes"]:
        interval_secs = int(os.getenv("PRICE_SYNC_INTERVAL_SECONDS", "28800"))  # 8 horas (3 veces al día)
        async def daily_sync_background():
            while True:
                await asyncio.sleep(interval_secs)
                try:
                    logger.info("⏰ Ejecutando ciclo de minería periódica en segundo plano (3 veces al día)...")
                    from app.core.database import AsyncSessionLocal
                    from app.services.seed_service import sync_or_update_seed_prices
                    from app.agents.orchestrator import MultiAgentOrchestrator
                    async with AsyncSessionLocal() as session:
                        await sync_or_update_seed_prices(session)
                        orchestrator = MultiAgentOrchestrator(session)
                        await orchestrator.execute_full_cycle(limit_per_query=4)
                except Exception as ex:
                    logger.error(f"Aviso en ciclo periódico en segundo plano: {ex}")

        sync_task = asyncio.create_task(daily_sync_background())
        logger.info(f"Bucle de actualización periódica activado (cada {interval_secs / 3600:.1f} horas / 3 veces al día).")

    yield
    if sync_task:
        sync_task.cancel()
    logger.info("Cerrando Ofertis Backend...")



app = FastAPI(
    title="Ofertis Chile - API Multi-Agente & pgvector",
    description="Sistema de búsqueda semántica, minería de datos y comparador de canasta básica chilena (Carnes NCh 1424, Lácteos, Arroz y Fideos) con alertas por WhatsApp.",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar middleware CORS para el frontend en React (permite Vercel y localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" or "*" in settings.cors_origins_list else settings.cors_origins_list,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$" if settings.ENVIRONMENT != "development" else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers de la API v1
app.include_router(health_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(mining_router, prefix="/api/v1")
app.include_router(radar_router, prefix="/api/v1")
app.include_router(sentinela_router, prefix="/api/v1")
app.include_router(cronista_router, prefix="/api/v1")

# Montar directorio estático para servir carruseles de redes sociales e imágenes
import os
from fastapi.staticfiles import StaticFiles
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de Ofertis Chile 🇨🇱",
        "docs_url": "/docs",
        "status": "online"
    }
