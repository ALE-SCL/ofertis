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


@router.get("/articles/{article_id}/carousel")
async def get_article_carousel(article_id: str):
    """
    Retorna la información del carrusel de 5 diapositivas (URLs de imágenes y caption de redes sociales).
    Si aún no ha sido generado, lo genera en el acto.
    """
    service = SentinelaService()
    article = None
    for art in service.get_all_articles(limit=100):
        if art.id == article_id:
            article = art
            break

    if not article:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")

    import os
    import json
    from sentinela.sentinela.generator.carousel_generator import CarouselGenerator

    gen = CarouselGenerator()
    manifest_path = os.path.join(gen.output_base_dir, article_id, "manifest.json")

    if not os.path.exists(manifest_path):
        manifest = gen.render_carousel_for_article(article.dict())
    else:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

    # Añadir URLs públicas
    public_base = os.getenv("PUBLIC_BASE_URL", "https://ofertis-backend.onrender.com").rstrip("/")
    manifest["public_slide_urls"] = [
        f"{public_base}/static/carousels/{article_id}/{fname}"
        for fname in manifest.get("slide_filenames", [])
    ]
    return manifest


@router.post("/articles/{article_id}/publish-social")
async def publish_article_social(article_id: str, dry_run: bool = Query(False, description="Simula la publicación sin enviar a Meta")):
    """
    Publica automáticamente el carrusel de 5 diapositivas en Instagram y Facebook.
    """
    carousel_info = await get_article_carousel(article_id)
    from sentinela.sentinela.publisher.meta_publisher import MetaSocialPublisher

    publisher = MetaSocialPublisher()
    result = publisher.publish_carousel(article_id, carousel_info, dry_run=dry_run)
    return result


@router.post("/generate")
async def generate_news_pipeline(
    sample: bool = Query(False, description="Usa eventos de contingencia verificados"),
    simulate: Optional[str] = Query(None, description="Simula un escenario económico específico")
):
    """
    Ejecuta el pipeline completo bajo demanda:
    1. Sentinela (monitoreo en tiempo real o contingencia verificada, filtro anti-monotonía de 48h).
    2. El Cronista Económico (redacción de artículo editorial con diagramas Mermaid y SVG).
    3. Retorna el estado y los artículos disponibles inmediatamente.
    """
    import asyncio
    from scripts.generar_noticias import execute_full_pipeline

    result = await asyncio.to_thread(execute_full_pipeline, is_sample=sample, simulate=simulate)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Error ejecutando pipeline de noticias"))

    service = SentinelaService()
    fresh_articles = service.get_all_articles(limit=10)

    return {
        "success": True,
        "message": "Pipeline de noticias ejecutado exitosamente",
        "result": result,
        "articles": fresh_articles
    }

