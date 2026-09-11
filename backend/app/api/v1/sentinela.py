from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from app.schemas.sentinela import SentinelaArticle, SentinelaStats
from app.services.sentinela_service import SentinelaService

router = APIRouter(prefix="/sentinela", tags=["Alza de Precios - Blog Sentinela"])


@router.get("/articles", response_model=List[SentinelaArticle])
async def get_sentinela_articles(
    category: Optional[str] = Query(None, description="Filtro por categoría afectada"),
    severity: Optional[str] = Query(None, description="Filtro por severidad: ALTA o MEDIA"),
    direction: Optional[str] = Query(None, description="Filtro por dirección: ALZA, BAJA o TENDENCIA"),
    limit: int = Query(30, ge=1, le=100)
):
    """
    Retorna los artículos publicados automáticamente por el agente Sentinela sobre
    alzas proyectadas, oportunidades de baja y temas de interés alimentario basados en fuentes oficiales.
    """
    service = SentinelaService()
    return service.get_all_articles(category=category, severity=severity, trend_direction=direction, limit=limit)


@router.get("/articles/{article_id}", response_model=SentinelaArticle)
async def get_sentinela_article_detail(article_id: str):
    """
    Obtiene el detalle completo de un artículo del Sentinela con su cadena de causalidad.
    """
    service = SentinelaService()
    articles = service.get_all_articles(limit=100)
    for art in articles:
        if art.id == article_id:
            return art
    raise HTTPException(status_code=404, detail="Artículo del Sentinela no encontrado")


@router.get("/stats", response_model=SentinelaStats)
async def get_sentinela_stats():
    """
    Retorna estadísticas del radar de alzas del Sentinela: boletines procesados, alertas críticas y fuentes.
    """
    service = SentinelaService()
    return service.get_stats()
