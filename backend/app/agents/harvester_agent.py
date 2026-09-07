import logging
from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct
from app.scrapers.cencosud_scraper import CencosudScraperAdapter
from app.scrapers.unimarc_scraper import UnimarcScraperAdapter
from app.scrapers.lider_scraper import LiderScraperAdapter

logger = logging.getLogger("ofertis.agents.harvester")


class HarvesterAgent(BaseAgent):
    """
    Agente de Minería e Ingesta Continua (Data Mining Loop).
    Recorre las categorías de productos de primera necesidad en los 4 supermercados líderes.
    """

    TARGET_QUERIES = [
        {"category": "carne_vacuno", "query": "lomo liso"},
        {"category": "carne_vacuno", "query": "posta negra"},
        {"category": "carne_vacuno", "query": "lomo vetado"},
        {"category": "carne_pollo", "query": "pechuga deshuesada"},
        {"category": "leche", "query": "leche entera"},
        {"category": "leche", "query": "leche sin lactosa"},
        {"category": "arroz", "query": "arroz grado 1"},
        {"category": "fideos", "query": "spaghetti 5"},
        {"category": "fideos", "query": "fideos espirales"},
    ]

    def __init__(self):
        super().__init__(name="HarvesterAgent", role="Data Mining & Catalog Harvester")
        self.adapters: List[BaseScraperAdapter] = [
            LiderScraperAdapter(),
            CencosudScraperAdapter(brand_type="jumbo"),
            CencosudScraperAdapter(brand_type="santaisabel"),
            UnimarcScraperAdapter(),
        ]

    async def step(self, limit_per_query: int = 5, **kwargs: Any) -> Dict[str, Any]:
        """
        Ejecuta un ciclo de extracción en todas las tiendas para las categorías básicas.
        """
        all_raw_items: List[RawScrapedProduct] = []
        stats_by_super: Dict[str, int] = {ad.supermarket_slug: 0 for ad in self.adapters}

        for target in self.TARGET_QUERIES:
            cat = target["category"]
            q = target["query"]

            for adapter in self.adapters:
                try:
                    items = await adapter.search_category(category=cat, query=q, limit=limit_per_query)
                    all_raw_items.extend(items)
                    stats_by_super[adapter.supermarket_slug] += len(items)
                except Exception as e:
                    logger.warning(f"Fallo temporal extrayendo '{q}' en {adapter.supermarket_name}: {e}")

        return {
            "total_items_harvested": len(all_raw_items),
            "stats_by_supermarket": stats_by_super,
            "raw_items": all_raw_items
        }
