from typing import List
from fastapi import APIRouter, HTTPException, Query

from app.services.cronista_service import (
    CronistaService,
    CronistaArticleSummary,
    CronistaArticleDetail,
)

router = APIRouter(prefix="/cronista", tags=["El Cronista Económico - Artículos Editoriales"])


@router.get("/articles", response_model=List[CronistaArticleSummary])
async def list_cronista_articles(
    limit: int = Query(20, ge=1, le=50, description="Número máximo de artículos a retornar")
):
    """
    Retorna el listado de artículos periodísticos redactados por El Cronista Económico,
    ordenados del más reciente al más antiguo, con tiempo de lectura y tags.
    """
    service = CronistaService()
    return service.list_articles(limit=limit)


@router.get("/articles/{slug}", response_model=CronistaArticleDetail)
async def get_cronista_article(slug: str):
    """
    Retorna el contenido editorial completo de un artículo en Markdown, incluyendo
    los bloques de diagramas Mermaid (flujo causal y horizonte temporal Gantt).
    """
    service = CronistaService()
    article = service.get_article(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Artículo de El Cronista no encontrado")
    return article
