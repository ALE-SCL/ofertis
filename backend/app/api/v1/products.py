import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import (
    ProductSearchResult,
    CanonicalProductDetail,
)

router = APIRouter(prefix="/products", tags=["Products & Price Comparison"])


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna dinámicamente las categorías monitoreadas con stock real en góndola y su conteo de productos.
    """
    service = ProductService(db)
    return await service.get_categories_with_counts()


@router.get("/search", response_model=List[ProductSearchResult])
async def search_products(
    q: Optional[str] = Query(None, description="Texto de búsqueda semántica (ej: 'lomo liso', 'queso chanco', 'aceite', 'leche')"),
    category: Optional[str] = Query(None, description="Filtro opcional por categoría"),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Búsqueda híbrida y exploración del catálogo completo de retail chileno.
    Si no se especifica 'q', retorna el catálogo completo (o filtrado por categoría) ordenado por disponibilidad.
    """
    service = ProductService(db)
    return await service.search_products(query=q, category=category, limit=limit, offset=offset)


@router.get("/{canonical_id}", response_model=CanonicalProductDetail)
async def get_product_detail(
    canonical_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la ficha comparativa del producto entre Jumbo, Santa Isabel, Unimarc y Lider,
    calculando la mejor opción y precio normalizado por kg o L.
    """
    service = ProductService(db)
    detail = await service.get_product_detail(canonical_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return detail


@router.post("/refresh-live")
async def refresh_live_products(
    q: str = Query(..., min_length=2, description="Término a buscar y minar en vivo en los 4 supermercados"),
    category: Optional[str] = Query(None),
    limit: int = Query(4, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Minería Just-In-Time (On-Demand):
    Consulta en tiempo real las APIs oficiales de Jumbo, Santa Isabel, Unimarc y Lider,
    normaliza los precios ($/kg o $/L), resuelve entidades con pgvector y retorna
    los resultados frescos con los precios del minuto.
    """
    from app.scrapers.cencosud_scraper import CencosudScraperAdapter
    from app.scrapers.unimarc_scraper import UnimarcScraperAdapter
    from app.scrapers.lider_scraper import LiderScraperAdapter
    from app.agents.normalizer_agent import NormalizerAgent
    from app.agents.entity_resolution_agent import EntityResolutionAgent

    scrapers = [
        CencosudScraperAdapter(brand_type="jumbo"),
        CencosudScraperAdapter(brand_type="santaisabel"),
        UnimarcScraperAdapter(),
        LiderScraperAdapter()
    ]

    normalizer = NormalizerAgent()
    resolver = EntityResolutionAgent(db)

    cat_hint = category if (category and category != "todos") else "general"

    # 1. Extraer en vivo de las 4 tiendas concurrentemente
    tasks = [sc.search_category(category=cat_hint, query=q, limit=limit) for sc in scrapers]
    results_nested = await asyncio.gather(*tasks, return_exceptions=True)

    raw_items = []
    for res in results_nested:
        if isinstance(res, list):
            raw_items.extend(res)

    if raw_items:
        # 2. Normalizar unidades
        norm_res = await normalizer.run_once(raw_items=raw_items)
        normalized_items = norm_res.get("data", {}).get("normalized_items", [])

        # 3. Resolver entidades canónicas con pgvector
        if normalized_items:
            await resolver.run_once(normalized_items=normalized_items)

    # 4. Devolver la búsqueda vectorial actualizada
    service = ProductService(db)
    return await service.search_products(query=q, category=category, limit=20)


@router.get("/{canonical_id}/history")
async def get_product_price_history(
    canonical_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el historial cronológico de precios para graficar la evolución en el tiempo.
    """
    service = ProductService(db)
    return await service.get_price_history(canonical_id)
