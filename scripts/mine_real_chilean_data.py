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


QUERIES_TO_MINE = [
    {"category": "leche", "query": "leche descremada"},
    {"category": "leche", "query": "leche entera"},
    {"category": "leche", "query": "leche semidescremada"},
    {"category": "leche", "query": "leche sin lactosa"},
    {"category": "carne_vacuno", "query": "lomo liso"},
    {"category": "carne_vacuno", "query": "posta negra"},
    {"category": "carne_vacuno", "query": "lomo vetado"},
    {"category": "carne_pollo", "query": "pechuga pollo"},
    {"category": "arroz", "query": "arroz grado 1"},
    {"category": "fideos", "query": "spaghetti"},
    {"category": "fideos", "query": "espirales"},
]


async def mine_live_retail():
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

        for q_item in QUERIES_TO_MINE:
            cat = q_item["category"]
            q = q_item["query"]
            print(f"\n🔍 Minando categoría '{cat}' con término: '{q}'...")

            raw_items = []
            for sc in scrapers:
                try:
                    items = await sc.search_category(category=cat, query=q, limit=4)
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
    asyncio.run(mine_live_retail())
