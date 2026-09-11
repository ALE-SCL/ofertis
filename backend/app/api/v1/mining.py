from typing import List, Dict, Any, Optional
from pydantic import BaseModel
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
        "items_populated_or_updated": updated_count,
        "total_canonical_products": total_canonical,
        "total_supermarket_items": total_items,
        "mining_summary": mining_summary
    }


class ImportItemPayload(BaseModel):
    supermarket_slug: str
    sku: str
    store_title: str
    brand_extracted: Optional[str] = None
    product_url: str = ""
    image_url: Optional[str] = None
    package_quantity: float = 1.0
    package_unit: str = "un"
    is_available: bool = True
    normal_price: float
    offer_price: Optional[float] = None
    unit_price_normalized: float
    is_offer: bool = False


class ImportProductPayload(BaseModel):
    name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    standard_unit: str = "kg"
    description: Optional[str] = None
    embedding: Optional[List[float]] = None
    items: List[ImportItemPayload] = []


class ImportBatchRequest(BaseModel):
    batch_index: int = 0
    total_batches: int = 1
    products: List[ImportProductPayload]


@router.post("/import-batch")
async def import_catalog_batch(
    payload: ImportBatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Importa de manera atómica, idempotente y eficiente un lote de productos canónicos
    con sus respectivas ofertas de supermercados y precios normalizados.
    Diseñado para sincronización de alto rendimiento entre entornos (Dev -> Prod).
    """
    from decimal import Decimal
    from sqlalchemy import func
    from app.models.price_record import PriceRecord
    from app.services.vector_service import VectorService

    # 1. Mapa de supermercados
    res_supers = await db.execute(select(Supermarket))
    super_map = {s.slug.lower(): s.id for s in res_supers.scalars().all()}

    canonical_created = 0
    canonical_updated = 0
    items_created = 0
    items_updated = 0

    for prod_data in payload.products:
        # Buscar entidad canónica
        stmt_c = select(CanonicalProduct).where(
            func.lower(CanonicalProduct.name) == prod_data.name.strip().lower(),
            CanonicalProduct.category == prod_data.category
        )
        canon = (await db.execute(stmt_c)).scalar_one_or_none()

        embedding = prod_data.embedding
        if not embedding:
            emb_text = f"{prod_data.name} {prod_data.category} {prod_data.brand or ''} {prod_data.description or ''}"
            embedding = VectorService.generate_embedding(emb_text)

    from decimal import Decimal
    import logging
    from sqlalchemy import func
    from fastapi import HTTPException
    from app.models.price_record import PriceRecord
    from app.services.vector_service import VectorService

    logger = logging.getLogger("ofertis.mining")

    try:
        # 1. Mapa de supermercados
        res_supers = await db.execute(select(Supermarket))
        super_map = {s.slug.lower(): s.id for s in res_supers.scalars().all()}

        canonical_created = 0
        canonical_updated = 0
        items_created = 0
        items_updated = 0

        for prod_data in payload.products:
            c_name = prod_data.name.strip()[:255]
            c_cat = prod_data.category.strip()[:50]
            c_subcat = prod_data.subcategory.strip()[:50] if prod_data.subcategory else None
            c_brand = prod_data.brand.strip()[:100] if prod_data.brand else None
            c_unit = (prod_data.standard_unit or "kg").strip()[:10]

            stmt_c = select(CanonicalProduct).where(
                func.lower(CanonicalProduct.name) == c_name.lower(),
                CanonicalProduct.category == c_cat
            )
            canon = (await db.execute(stmt_c)).scalars().first()

            embedding = prod_data.embedding
            if not embedding:
                emb_text = f"{c_name} {c_cat} {c_brand or ''} {prod_data.description or ''}"
                embedding = VectorService.generate_embedding(emb_text)

            if not canon:
                canon = CanonicalProduct(
                    name=c_name,
                    category=c_cat,
                    subcategory=c_subcat,
                    brand=c_brand,
                    standard_unit=c_unit,
                    description=prod_data.description,
                    embedding=embedding
                )
                db.add(canon)
                await db.flush()
                canonical_created += 1
            else:
                if c_subcat:
                    canon.subcategory = c_subcat
                if c_brand:
                    canon.brand = c_brand
                if prod_data.description:
                    canon.description = prod_data.description
                if embedding and not canon.embedding:
                    canon.embedding = embedding
                canonical_updated += 1

            # Procesar items asociados
            for item_data in prod_data.items:
                super_slug = item_data.supermarket_slug.lower()
                super_id = super_map.get(super_slug)
                if not super_id:
                    continue

                sku_clean = item_data.sku.strip()[:100]
                store_title_clean = item_data.store_title.strip()[:255]
                brand_ext = item_data.brand_extracted.strip()[:100] if item_data.brand_extracted else None
                unit_clean = (item_data.package_unit or "un").strip()[:10]

                stmt_i = select(SupermarketItem).where(
                    SupermarketItem.supermarket_id == super_id,
                    SupermarketItem.sku == sku_clean
                )
                item_obj = (await db.execute(stmt_i)).scalars().first()

                pkg_qty = Decimal(str(round(item_data.package_quantity, 3)))
                norm_price = Decimal(str(round(item_data.normal_price, 2)))
                off_price = Decimal(str(round(item_data.offer_price, 2))) if item_data.offer_price is not None else None
                unit_norm = Decimal(str(round(item_data.unit_price_normalized, 2)))

                if not item_obj:
                    item_obj = SupermarketItem(
                        canonical_id=canon.id,
                        supermarket_id=super_id,
                        sku=sku_clean,
                        store_title=store_title_clean,
                        brand_extracted=brand_ext,
                        product_url=item_data.product_url or "",
                        image_url=item_data.image_url,
                        package_quantity=pkg_qty,
                        package_unit=unit_clean,
                        is_available=item_data.is_available
                    )
                    db.add(item_obj)
                    await db.flush()
                    items_created += 1
                else:
                    item_obj.canonical_id = canon.id
                    item_obj.store_title = store_title_clean
                    if brand_ext:
                        item_obj.brand_extracted = brand_ext
                    if item_data.image_url:
                        item_obj.image_url = item_data.image_url
                    if item_data.product_url:
                        item_obj.product_url = item_data.product_url
                    item_obj.package_quantity = pkg_qty
                    item_obj.package_unit = unit_clean
                    item_obj.is_available = item_data.is_available
                    items_updated += 1

                # Gestionar PriceRecord
                stmt_pr = select(PriceRecord).where(
                    PriceRecord.item_id == item_obj.id
                ).order_by(PriceRecord.recorded_at.desc()).limit(1)
                latest_pr = (await db.execute(stmt_pr)).scalars().first()

                if not latest_pr:
                    pr = PriceRecord(
                        item_id=item_obj.id,
                        normal_price=norm_price,
                        offer_price=off_price,
                        unit_price_normalized=unit_norm,
                        is_offer=item_data.is_offer
                    )
                    db.add(pr)
                else:
                    latest_pr.normal_price = norm_price
                    latest_pr.offer_price = off_price
                    latest_pr.unit_price_normalized = unit_norm
                    latest_pr.is_offer = item_data.is_offer

        await db.commit()

        total_canonical = await db.scalar(select(func.count(CanonicalProduct.id)))
        total_items = await db.scalar(select(func.count(SupermarketItem.id)))

        return {
            "status": "success",
            "batch_index": payload.batch_index,
            "total_batches": payload.total_batches,
            "canonical_created": canonical_created,
            "canonical_updated": canonical_updated,
            "items_created": items_created,
            "items_updated": items_updated,
            "total_canonical_products": total_canonical,
            "total_supermarket_items": total_items
        }
    except Exception as exc:
        logger.exception(f"Error procesando lote {payload.batch_index}: {exc}")
        await db.rollback()
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"error": str(exc), "type": type(exc).__name__, "batch_index": payload.batch_index}
        )


