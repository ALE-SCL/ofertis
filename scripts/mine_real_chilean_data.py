import asyncio
import os
import sys
from decimal import Decimal

# Añadir backend al sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import AsyncSessionLocal
from app.agents.harvester_agent import HarvesterAgent
from app.agents.normalizer_agent import NormalizerAgent
from app.agents.entity_resolution_agent import EntityResolutionAgent
from app.scrapers.cencosud_scraper import CencosudScraperAdapter
from app.scrapers.unimarc_scraper import UnimarcScraperAdapter
from app.scrapers.lider_scraper import LiderScraperAdapter
from app.agents.harvester_agent import HarvesterAgent


async def mine_live_retail(targets=None, limit_per_query=3):
    queries_to_mine = targets or HarvesterAgent.get_all_catalog_targets()

    print("==================================================================")
    print("🚀 INICIANDO MINERÍA DE DATOS REAL EN VIVO (RETAIL CHILE)")
    print("Consultando APIs de catálogo de Jumbo, Santa Isabel, Unimarc y Lider...")
    print("==================================================================")

    scrapers = [
        CencosudScraperAdapter(brand_type="jumbo"),
        CencosudScraperAdapter(brand_type="santaisabel"),
        UnimarcScraperAdapter(),
        LiderScraperAdapter()
    ]

    normalizer = NormalizerAgent()

    async with AsyncSessionLocal() as session:
        resolver = EntityResolutionAgent(session)
        total_mined = 0

        for q_item in queries_to_mine:
            cat = q_item["category"]
            q = q_item["query"]
            print(f"\n🔍 Minando categoría '{cat}' con término: '{q}'...")

            raw_items = []
            for sc in scrapers:
                try:
                    items = await sc.search_category(category=cat, query=q, limit=limit_per_query)
                    print(f"   [{sc.supermarket_name}] Extraídos: {len(items)} productos reales.")
                    raw_items.extend(items)
                except Exception as ex:
                    print(f"   [{sc.supermarket_name}] Error temporal: {ex}")

            if not raw_items:
                continue

            # Normalizar unidades ($/kg, $/L)
            norm_res = await normalizer.run_once(raw_items=raw_items)
            norm_items = norm_res.get("data", {}).get("normalized_items", [])

            # Resolver entidades canónicas con pgvector
            res_result = await resolver.run_once(normalized_items=norm_items)
            affected = res_result.get("data", {}).get("canonical_products_affected", [])
            total_mined += len(norm_items)

            print(f"   ✅ {len(norm_items)} items normalizados e indexados con pgvector ({len(affected)} entidades canónicas actualizadas).")

        print("\n==================================================================")
        print(f"🎉 MINERÍA COMPLETADA: {total_mined} productos reales actualizados en PostgreSQL!")
        print("==================================================================")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ofertis Chile - Minería Multi-Categoría")
    parser.add_argument("--category", type=str, help="Categoría específica a minar (ej: frutas, verduras, bebidas, etc.)")
    parser.add_argument("--all", action="store_true", help="Minar todos los 80+ objetivos del catálogo")
    parser.add_argument("--limit", type=int, default=3, help="Límite de productos por supermercado por consulta")
    args = parser.parse_args()

    targets = None
    if args.category:
        targets = [t for t in HarvesterAgent.get_all_catalog_targets() if t["category"] == args.category]
        if not targets:
            targets = [{"category": args.category, "query": args.category}]
    elif not args.all:
        targets = HarvesterAgent.get_current_shift_batch()

    asyncio.run(mine_live_retail(targets=targets, limit_per_query=args.limit))
