#!/usr/bin/env python3
"""
Ofertis Chile - Poblamiento del Catálogo Expandido
===================================================
Inserta y sincroniza el catálogo canónico completo con la base de datos de producción
y opcionalmente ejecuta minería en vivo para capturar ofertas adicionales.

Uso:
  # Vía Base de Datos directa (por ejemplo contra Render DB):
  DATABASE_URL="postgresql+asyncpg://..." python3 scripts/populate_expanded_catalog.py

  # Vía API remota (ej: backend en Render):
  python3 scripts/populate_expanded_catalog.py --api https://ofertis-backend.onrender.com

  # Con minería en vivo adicional:
  python3 scripts/populate_expanded_catalog.py --mine
"""

import os
import sys
import argparse
import asyncio
import urllib.request
import json
import logging

# Configurar path al backend
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ofertis.populate")


async def populate_via_db(mine_live: bool = False):
    """
    Pobla la base de datos conectada en DATABASE_URL directamente.
    """
    from sqlalchemy import select, func
    from app.core.database import AsyncSessionLocal
    from app.services.seed_service import sync_or_update_seed_prices, PRODUCTS_SEED
    from app.models.canonical_product import CanonicalProduct
    from app.models.supermarket_item import SupermarketItem

    logger.info("==================================================================")
    logger.info("📦 INICIANDO POBLAMIENTO DEL CATÁLOGO EXPANDIDO (VÍA DB)")
    logger.info("==================================================================")
    logger.info(f"Catálogo canónico disponible en memoria: {len(PRODUCTS_SEED)} familias de productos")

    async with AsyncSessionLocal() as session:
        # 1. Contar estado actual
        before_canonical = await session.scalar(select(func.count(CanonicalProduct.id)))
        before_items = await session.scalar(select(func.count(SupermarketItem.id)))
        logger.info(f"Estado inicial en DB: {before_canonical} productos canónicos, {before_items} ofertas de supermercado.")

        # 2. Sincronizar / Insertar catálogo
        logger.info("Insertando/actualizando productos y ofertas con embeddings...")
        updated = await sync_or_update_seed_prices(session)
        logger.info(f"✅ Procesados {updated} productos del catálogo semilla.")

        # 3. Minería en vivo si fue solicitada
        if mine_live:
            logger.info("🌐 Ejecutando ciclo de minería en vivo en supermercados chilenos...")
            from app.agents.orchestrator import MultiAgentOrchestrator
            orchestrator = MultiAgentOrchestrator(session)
            cycle_res = await orchestrator.execute_full_cycle(limit_per_query=4)
            summary = cycle_res.get("summary", {})
            logger.info(f"   -> Minería: {summary.get('items_harvested', 0)} recolectados, {summary.get('items_normalized', 0)} normalizados.")

        # 4. Estado final
        after_canonical = await session.scalar(select(func.count(CanonicalProduct.id)))
        after_items = await session.scalar(select(func.count(SupermarketItem.id)))
        logger.info("==================================================================")
        logger.info("🎉 POBLAMIENTO COMPLETADO EXITOSAMENTE")
        logger.info(f"   • Productos Canónicos: {before_canonical} -> {after_canonical} (+{after_canonical - before_canonical})")
        logger.info(f"   • Ofertas Supermercado: {before_items} -> {after_items} (+{after_items - before_items})")
        logger.info("==================================================================")


def populate_via_api(api_url: str, mine_live: bool = False):
    """
    Invoca el endpoint /api/v1/mining/populate-expanded en el backend remoto.
    """
    clean_url = api_url.rstrip("/")
    endpoint = f"{clean_url}/api/v1/mining/populate-expanded?mine_live={'true' if mine_live else 'false'}"

    logger.info("==================================================================")
    logger.info(f"🚀 INICIANDO POBLAMIENTO VÍA API: {endpoint}")
    logger.info("==================================================================")

    req = urllib.request.Request(
        endpoint,
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            status = response.status
            body = response.read().decode("utf-8")
            data = json.loads(body)
            logger.info(f"Código HTTP: {status}")
            logger.info(f"Respuesta del servidor:")
            logger.info(json.dumps(data, indent=2, ensure_ascii=False))
            logger.info("==================================================================")
            logger.info("🎉 POBLAMIENTO REMOTO COMPLETADO EXITOSAMENTE")
            logger.info("==================================================================")
    except Exception as e:
        logger.error(f"❌ Error al conectar con la API ({endpoint}): {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Ofertis Chile - Poblar Catálogo Expandido")
    parser.add_argument(
        "--api",
        type=str,
        help="URL base del backend de producción (ej: https://ofertis-backend.onrender.com). Si no se especifica, usa la conexión directa a base de datos."
    )
    parser.add_argument(
        "--mine",
        action="store_true",
        help="Ejecutar además un ciclo de recolección en vivo en los supermercados"
    )

    args = parser.parse_args()

    if args.api:
        populate_via_api(args.api, mine_live=args.mine)
    else:
        asyncio.run(populate_via_db(mine_live=args.mine))


if __name__ == "__main__":
    main()
