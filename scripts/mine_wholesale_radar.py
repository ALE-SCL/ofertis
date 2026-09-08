#!/usr/bin/env python3
"""
Ofertis Chile - Ingestion and Mining Engine for Radar Alternativo & Wholesale Stores
==================================================================================
Persiste tiendas alternativas y mayoristas, ejecuta scrapers en vivo (Doña Carne Shopify,
distribuidores mayoristas, Lo Valledor ODEPA, El Carnicero), calcula spreads reales frente
al retail tradicional y almacena embeddings semánticos en PostgreSQL + pgvector.
"""

import os
import sys
import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Añadir paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.alternative_store import AlternativeStore
from app.models.alternative_item import AlternativeItem
from app.models.alternative_price_record import AlternativePriceRecord
from app.services.vector_service import VectorService

# Scrapers y adaptadores
from app.scrapers.dona_carne_scraper import DonaCarneScraperAdapter
from app.scrapers.wholesale_distributors_scraper import WholesaleDistributorsAdapter
from app.services.radar_service import ALTERNATIVE_STORES, RAW_ALTERNATIVE_ITEMS, TRADITIONAL_RETAIL_BENCHMARKS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [radar_miner] %(message)s"
)
logger = logging.getLogger("radar_miner")

# Imagenes fallback de alta calidad por categoría
CATEGORY_FALLBACK_IMAGES = {
    "carnes": "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=600&q=80",
    "frutas_verduras": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&q=80",
    "despensa": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
    "lacteos_huevos": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=600&q=80",
}


def find_benchmark_price(product_name: str, fallback_unit_price: float) -> tuple[float, str]:
    """Determina el benchmark de retail tradicional y su etiqueta descriptiva."""
    p_lower = product_name.lower()
    
    # Búsqueda por palabras clave exactas en TRADITIONAL_RETAIL_BENCHMARKS
    for key, bm_price in TRADITIONAL_RETAIL_BENCHMARKS.items():
        if key in p_lower:
            return float(bm_price), f"Promedio Retail Tradicional ({key.title()} ~${bm_price:,} CLP)".replace(",", ".")
    
    # Heurísticas por corte o producto común
    if any(w in p_lower for w in ["lomo", "bife"]):
        return 16990.0, "Promedio Retail Cortes Parrilleros (~$16.990/kg)"
    elif any(w in p_lower for w in ["posta", "asiento", "punta"]):
        return 12990.0, "Promedio Retail Vacuno Primera (~$12.990/kg)"
    elif any(w in p_lower for w in ["huachalomo", "sobrecostilla", "abastero"]):
        return 9990.0, "Promedio Retail Vacuno Guisar (~$9.990/kg)"
    elif any(w in p_lower for w in ["cerdo", "costillar", "pulpa"]):
        return 6990.0, "Promedio Retail Cortes de Cerdo (~$6.990/kg)"
    elif any(w in p_lower for w in ["pollo", "pechuga", "trutro"]):
        return 4990.0, "Promedio Retail Pollo Entero y Cortes (~$4.990/kg)"
    elif any(w in p_lower for w in ["arroz", "tucapel"]):
        return 1790.0, "Promedio Retail Arroz Grado 1 (~$1.790/kg)"
    elif any(w in p_lower for w in ["aceite", "maravilla"]):
        return 2490.0, "Promedio Retail Aceite Maravilla 900ml (~$2.490)"
    elif any(w in p_lower for w in ["leche", "colun", "soprole"]):
        return 1290.0, "Promedio Retail Leche Entera 1L (~$1.290)"
    elif any(w in p_lower for w in ["fideos", "spaghetti", "espirales"]):
        return 990.0, "Promedio Retail Fideos 400g (~$990)"
    elif any(w in p_lower for w in ["azucar", "iansa"]):
        return 1390.0, "Promedio Retail Azúcar 1kg (~$1.390)"
    elif any(w in p_lower for w in ["atun"]):
        return 1490.0, "Promedio Retail Lomitos Atún (~$1.490)"
    
    # Si no hay coincidencia, asumir spread retail estándar de 30%
    retail_est = round(fallback_unit_price * 1.30)
    return float(retail_est), f"Estimación Retail Tradicional (~${retail_est:,} CLP)".replace(",", ".")


async def seed_or_update_stores(session) -> Dict[str, int]:
    """Siembra y actualiza las tiendas y distribuidores alternativos en la base de datos."""
    logger.info("Verificando tiendas y cadenas alternativas en PostgreSQL...")
    store_id_map: Dict[str, int] = {}
    
    for s_info in ALTERNATIVE_STORES:
        slug = s_info["id"]
        stmt = select(AlternativeStore).where(AlternativeStore.slug == slug)
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()
        
        if existing:
            existing.name = s_info["name"]
            existing.store_type = s_info["type"]
            existing.type_label = s_info["type_label"]
            existing.badge_color = s_info.get("badge_color", "blue")
            existing.website = s_info["website"]
            existing.description = s_info.get("description")
            existing.coverage = s_info.get("coverage")
            existing.highlight = s_info.get("highlight")
            existing.is_active = True
            store_id_map[slug] = existing.id
        else:
            new_store = AlternativeStore(
                slug=slug,
                name=s_info["name"],
                store_type=s_info["type"],
                type_label=s_info["type_label"],
                badge_color=s_info.get("badge_color", "blue"),
                website=s_info["website"],
                description=s_info.get("description"),
                coverage=s_info.get("coverage"),
                highlight=s_info.get("highlight"),
                is_active=True
            )
            session.add(new_store)
            await session.flush()
            store_id_map[slug] = new_store.id
            logger.info(f"  [+] Tienda creada: {new_store.name} ({new_store.slug})")

    await session.commit()
    return store_id_map


async def ingest_items(session, store_id_map: Dict[str, int]):
    """Ejecuta scrapers en vivo y cataloga oportunidades en la base de datos."""
    all_raw_items: List[Dict[str, Any]] = []

    # 1. Scraper en vivo Doña Carne (Shopify API)
    logger.info("Ejecutando scraper en vivo de Doña Carne (Shopify)...")
    try:
        dc_adapter = DonaCarneScraperAdapter()
        dc_items = dc_adapter.fetch_products()
        logger.info(f"  Doña Carne en vivo: {len(dc_items)} cortes reales extraídos de Shopify.")
        for item in dc_items:
            unit_price = float(item.get("unit_price") or item.get("price"))
            bm_price, bm_label = find_benchmark_price(item["product_name"], unit_price)
            item["traditional_benchmark_unit_price"] = bm_price
            item["benchmark_label"] = bm_label
            item["advice"] = f"Corte fresco directo de carnicería Doña Carne. Precio online por kilo frente a ${bm_price:,.0f} en supermercados retail."
            all_raw_items.append(item)
    except Exception as e:
        logger.warning(f"Error en Doña Carne scraper: {e}")

    # 2. Scraper distribuidores mayoristas (Alvi, Central Mayorista, Comercial Castro, etc.)
    logger.info("Extrayendo catálogo comprobado de distribuidores mayoristas...")
    try:
        dist_adapter = WholesaleDistributorsAdapter()
        dist_items = dist_adapter.fetch_verified_opportunities()
        logger.info(f"  Distribuidores mayoristas: {len(dist_items)} ítems procesados.")
        all_raw_items.extend(dist_items)
    except Exception as e:
        logger.warning(f"Error en Wholesale Distributors scraper: {e}")

    # 3. Catálogo base verificado de Radar Alternativo (Lo Valledor ODEPA, El Carnicero, aCuenta, Mayorista 10)
    logger.info(f"Incorporando catálogo verificado de Radar Alternativo ({len(RAW_ALTERNATIVE_ITEMS)} items)...")
    all_raw_items.extend(RAW_ALTERNATIVE_ITEMS)

    # Procesar y persistir en alternative_items
    logger.info(f"Persistiendo total de {len(all_raw_items)} items en PostgreSQL...")
    inserted_count = 0
    updated_count = 0

    for itm in all_raw_items:
        slug = itm.get("store_id")
        store_db_id = store_id_map.get(slug)
        if not store_db_id:
            continue

        sku = itm.get("sku") or f"{slug.upper()}-{hash(itm['product_name']) % 100000}"
        name = itm.get("product_name", "").strip()
        category = itm.get("category", "despensa")
        unit = itm.get("unit", "kg")
        price = Decimal(str(round(float(itm.get("price", 0)), 2)))
        unit_price = Decimal(str(round(float(itm.get("unit_price", price)), 2)))
        
        trad_price_val = float(itm.get("traditional_benchmark_unit_price") or float(unit_price) * 1.30)
        trad_price = Decimal(str(round(trad_price_val, 2)))
        bm_label = itm.get("benchmark_label") or f"Retail Tradicional (~${trad_price_val:,.0f})"
        
        # Cálculo de Ahorro y Spread
        savings_clp = max(Decimal("0.0"), trad_price - unit_price)
        if trad_price > Decimal("0.0"):
            savings_pct = Decimal(str(round(float((savings_clp / trad_price) * Decimal("100.0")), 1)))
        else:
            savings_pct = Decimal("0.0")

        if savings_pct >= Decimal("25.0"):
            deal_level = "SUPER_AHORRO"
            deal_label = "🔥 Súper Ahorro (> 25%)"
        elif savings_pct >= Decimal("15.0"):
            deal_level = "AHORRO_ALTO"
            deal_label = "⭐ Ahorro Alto (15% a 25%)"
        else:
            deal_level = "AHORRO_MODERADO"
            deal_label = "🏷️ Ahorro Moderado (5% a 15%)"

        image_url = itm.get("image_url") or CATEGORY_FALLBACK_IMAGES.get(category, CATEGORY_FALLBACK_IMAGES["despensa"])
        purchase_url = itm.get("purchase_url") or "https://ofertis.cl"
        advice = itm.get("advice") or itm.get("recommendation_note") or "Oportunidad de ahorro comprobada en canal alternativo."
        is_wholesale = bool(itm.get("is_wholesale", False))

        # Generar embedding semántico
        embed_text = f"{name} {category} {itm.get('store_name', '')} {unit} ahorro {savings_pct}%"
        embedding_vec = VectorService.generate_embedding(embed_text)

        # Upsert en PostgreSQL
        stmt = select(AlternativeItem).where(
            AlternativeItem.store_id == store_db_id,
            AlternativeItem.sku == sku
        )
        res = await session.execute(stmt)
        existing_item = res.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if existing_item:
            existing_item.product_name = name
            existing_item.category = category
            existing_item.unit = unit
            existing_item.current_price = price
            existing_item.unit_price_normalized = unit_price
            existing_item.traditional_benchmark_price = trad_price
            existing_item.benchmark_label = bm_label
            existing_item.savings_clp = savings_clp
            existing_item.savings_percentage = savings_pct
            existing_item.deal_level = deal_level
            existing_item.deal_label = deal_label
            existing_item.is_wholesale = is_wholesale
            existing_item.purchase_url = purchase_url
            existing_item.recommendation_note = advice
            existing_item.image_url = image_url
            existing_item.embedding = embedding_vec
            existing_item.is_available = True
            existing_item.last_seen_at = now
            item_db_id = existing_item.id
            updated_count += 1
        else:
            new_item = AlternativeItem(
                store_id=store_db_id,
                sku=sku,
                product_name=name,
                category=category,
                unit=unit,
                current_price=price,
                unit_price_normalized=unit_price,
                traditional_benchmark_price=trad_price,
                benchmark_label=bm_label,
                savings_clp=savings_clp,
                savings_percentage=savings_pct,
                deal_level=deal_level,
                deal_label=deal_label,
                is_wholesale=is_wholesale,
                purchase_url=purchase_url,
                recommendation_note=advice,
                image_url=image_url,
                embedding=embedding_vec,
                is_available=True,
                last_seen_at=now,
                created_at=now
            )
            session.add(new_item)
            await session.flush()
            item_db_id = new_item.id
            inserted_count += 1

        # Registrar historial de precio en alternative_price_records
        price_rec = AlternativePriceRecord(
            item_id=item_db_id,
            price=price,
            unit_price_normalized=unit_price,
            traditional_benchmark_price=trad_price,
            savings_percentage=savings_pct,
            recorded_at=now
        )
        session.add(price_rec)

    await session.commit()
    logger.info(f"Minería completada: {inserted_count} nuevos items insertados, {updated_count} actualizados.")


async def main():
    logger.info("=== INICIANDO MINERÍA Y SINCRONIZACIÓN DE RADAR ALTERNATIVO ===")
    async with AsyncSessionLocal() as session:
        store_map = await seed_or_update_stores(session)
        logger.info(f"Tiendas sincronizadas: {len(store_map)} tiendas activas.")
        await ingest_items(session, store_map)
    logger.info("=== SINCRONIZACIÓN DE RADAR ALTERNATIVO FINALIZADA CON ÉXITO ===")


if __name__ == "__main__":
    asyncio.run(main())
