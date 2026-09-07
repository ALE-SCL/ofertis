import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.products import router as products_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.mining import router as mining_router
from app.api.v1.radar import router as radar_router

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
    Inicializa conexiones y precarga modelos de IA si corresponde.
    """
    logger.info(f"Iniciando Ofertis Backend en modo [{settings.ENVIRONMENT}]...")
    logger.info(f"Base de datos configurada: {settings.POSTGRES_DB} en {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    logger.info(f"Canal de alertas WhatsApp: [{settings.WHATSAPP_PROVIDER}]")
    yield
    logger.info("Cerrando Ofertis Backend...")


app = FastAPI(
    title="Ofertis Chile - API Multi-Agente & pgvector",
    description="Sistema de búsqueda semántica, minería de datos y comparador de canasta básica chilena (Carnes NCh 1424, Lácteos, Arroz y Fideos) con alertas por WhatsApp.",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar middleware CORS para el frontend en React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else settings.cors_origins_list,
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


@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de Ofertis Chile 🇨🇱",
        "docs_url": "/docs",
        "status": "online"
    }
