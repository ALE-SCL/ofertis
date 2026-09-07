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
