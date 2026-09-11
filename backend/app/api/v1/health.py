from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health & System"])


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check completo: verifica conectividad con PostgreSQL y la extensión pgvector.
    """
    db_status = "healthy"
    pgvector_status = "disabled"

    try:
        res = await db.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector';"))
        row = res.scalar()
        if row:
            pgvector_status = f"enabled (v{row})"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "service": "ofertis-backend",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "pgvector": pgvector_status,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "whatsapp_provider": settings.WHATSAPP_PROVIDER,
        "version": "2026.09.11-v2"
    }
