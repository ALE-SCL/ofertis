from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.supermarket import Supermarket
from app.models.supermarket_item import SupermarketItem
from app.models.canonical_product import CanonicalProduct

router = APIRouter(prefix="/mining", tags=["Data Mining & Scrapers"])


@router.get("/supermarkets")
async def get_supermarkets(db: AsyncSession = Depends(get_db)):
    """
    Lista los supermercados chilenos monitoreados y su estado.
    """
    stmt = select(Supermarket).order_by(Supermarket.name.asc())
    res = await db.execute(stmt)
    supers = res.scalars().all()

    return [
        {
            "id": s.id,
            "slug": s.slug,
            "name": s.name,
            "base_url": s.base_url,
            "color_hex": s.color_hex,
            "is_active": s.is_active
        }
        for s in supers
    ]


@router.get("/stats")
async def get_mining_stats(db: AsyncSession = Depends(get_db)):
    """
    Estadísticas del pipeline de minería de datos y catálogo normalizado.
    """
    from sqlalchemy import func
    
    total_canonical = await db.scalar(select(func.count(CanonicalProduct.id)))
    total_items = await db.scalar(select(func.count(SupermarketItem.id)))
    
    return {
        "canonical_products_count": total_canonical or 0,
        "supermarket_skus_tracked": total_items or 0,
        "active_supermarkets": ["Lider", "Jumbo", "Santa Isabel", "Unimarc"],
        "commune_target": "Santiago Centro / Providencia (Región Metropolitana)"
    }


@router.post("/run-cycle")
async def trigger_multi_agent_cycle(
    limit: int = 3,
    db: AsyncSession = Depends(get_db)
):
    """
    Ejecuta bajo demanda el ciclo completo multi-agente:
    Harvester -> Normalizer -> Entity Resolution (pgvector) -> Alert Monitor (WhatsApp).
    """
    from app.agents.orchestrator import MultiAgentOrchestrator
    orchestrator = MultiAgentOrchestrator(db)
    result = await orchestrator.execute_full_cycle(limit_per_query=limit)
    return result


@router.post("/daily-sync")
async def trigger_daily_sync(
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de sincronización diaria cada 24 horas:
    1. Sincroniza y actualiza la canasta básica con precios oficiales de góndola.
    2. Ejecuta un ciclo multi-agente para minar ofertas vivas de Lider, Jumbo, Santa Isabel y Unimarc.
    3. Despacha alertas si detecta caídas de precio notables.
    """
    from datetime import datetime, timezone
    from app.services.seed_service import sync_or_update_seed_prices
    from app.agents.orchestrator import MultiAgentOrchestrator

    # Paso 1: Actualizar catálogo base verificado
    seed_updated = await sync_or_update_seed_prices(db)

    # Paso 2: Minería multi-agente en vivo
    orchestrator = MultiAgentOrchestrator(db)
    cycle_res = await orchestrator.execute_full_cycle(limit_per_query=4)

    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed_items_updated": seed_updated,
        "mining_cycle": cycle_res.get("summary", {})
    }


@router.post("/populate-expanded")
async def populate_expanded_catalog(
    mine_live: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Puebla la base de datos de producción con el catálogo expandido:
    1. Inserta o actualiza todos los productos canónicos de la canasta chilena y sus ofertas retail verificadas.
    2. Si 'mine_live' es True, ejecuta además un ciclo de recolección en vivo para expandir el inventario.
    """
    from datetime import datetime, timezone
    from sqlalchemy import func
    from app.services.seed_service import sync_or_update_seed_prices

    updated_count = await sync_or_update_seed_prices(db)

    mining_summary = None
    if mine_live:
        from app.agents.orchestrator import MultiAgentOrchestrator
        orchestrator = MultiAgentOrchestrator(db)
        cycle_res = await orchestrator.execute_full_cycle(limit_per_query=4)
        mining_summary = cycle_res.get("summary", {})

    total_canonical = await db.scalar(select(func.count(CanonicalProduct.id)))
    total_items = await db.scalar(select(func.count(SupermarketItem.id)))

    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "items_populated_or_updated": updated_count,
        "total_canonical_products": total_canonical,
        "total_supermarket_items": total_items,
        "mining_summary": mining_summary
    }

