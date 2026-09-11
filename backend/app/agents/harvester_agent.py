import logging
from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct
from app.scrapers.cencosud_scraper import CencosudScraperAdapter
from app.scrapers.unimarc_scraper import UnimarcScraperAdapter
from app.scrapers.lider_scraper import LiderScraperAdapter

from datetime import datetime, timezone, timedelta

logger = logging.getLogger("ofertis.agents.harvester")


class HarvesterAgent(BaseAgent):
    """
    Agente de Minería e Ingesta Continua (Data Mining Loop).
    Recorre las categorías de productos de primera necesidad en los 4 supermercados líderes
    distribuidas en 3 turnos diarios para un crecimiento orgánico sin saturación de recursos.
    """

    BATCH_1_PROTEINAS = [
        {"category": "carne_vacuno", "query": "lomo liso"},
        {"category": "carne_vacuno", "query": "lomo vetado"},
        {"category": "carne_vacuno", "query": "posta negra"},
        {"category": "carne_vacuno", "query": "asiento"},
        {"category": "carne_vacuno", "query": "huachalomo"},
        {"category": "carne_vacuno", "query": "carne molida"},
        {"category": "carne_cerdo", "query": "pulpa cerdo"},
        {"category": "carne_cerdo", "query": "costillar cerdo"},
        {"category": "carne_pollo", "query": "pechuga deshuesada"},
        {"category": "carne_pollo", "query": "trutro entero"},
    ]

    BATCH_2_DESPENSA = [
        {"category": "arroz", "query": "arroz grado 1"},
        {"category": "arroz", "query": "arroz integral"},
        {"category": "legumbres", "query": "lentejas"},
        {"category": "legumbres", "query": "porotos"},
        {"category": "legumbres", "query": "garbanzos"},
        {"category": "fideos", "query": "spaghetti 5"},
        {"category": "fideos", "query": "fideos espirales"},
        {"category": "fideos", "query": "tallarines"},
        {"category": "pastas", "query": "salsa de tomate"},
        {"category": "harinas", "query": "harina de trigo"},
        {"category": "aceites", "query": "aceite vegetal"},
    ]

    BATCH_3_LACTEOS_ASEO = [
        {"category": "leche", "query": "leche entera"},
        {"category": "leche", "query": "leche sin lactosa"},
        {"category": "lacteos", "query": "queso laminado"},
        {"category": "lacteos", "query": "mantequilla"},
        {"category": "huevos", "query": "huevos bandeja"},
        {"category": "desayuno", "query": "cafe instantaneo"},
        {"category": "desayuno", "query": "te ceylan"},
        {"category": "limpieza", "query": "detergente liquido"},
        {"category": "limpieza", "query": "cloro gel"},
        {"category": "limpieza", "query": "lavaloza liquido"},
        {"category": "limpieza", "query": "papel higienico"},
    ]

    @classmethod
    def get_current_shift_batch(cls) -> list:
        """
        Determina el lote de minería según la hora de Chile:
        - Noche / Medianoche (20:00 - 03:59 CLT): Carnes y Proteínas NCh 1424
        - Mañana (04:00 - 11:59 CLT): Despensa, Arroz, Pastas y Legumbres
        - Tarde (12:00 - 19:59 CLT): Lácteos, Huevos, Desayuno y Aseo
        """
        try:
            import zoneinfo
            chile_tz = zoneinfo.ZoneInfo("America/Santiago")
        except Exception:
            chile_tz = timezone(timedelta(hours=-3))

        hour = datetime.now(chile_tz).hour
        if 4 <= hour < 12:
            logger.info(f"🌅 Turno Mañana (08:00 CLT / {hour}:00): Minando Despensa, Abarrotes y Legumbres.")
            return cls.BATCH_2_DESPENSA
        elif 12 <= hour < 20:
            logger.info(f"🌇 Turno Tarde (16:00 CLT / {hour}:00): Minando Lácteos, Desayuno y Aseo.")
            return cls.BATCH_3_LACTEOS_ASEO
        else:
            logger.info(f"🌙 Turno Medianoche (00:00 CLT / {hour}:00): Minando Carnes NCh 1424 y Proteínas.")
            return cls.BATCH_1_PROTEINAS

    def __init__(self):
        super().__init__(name="HarvesterAgent", role="Data Mining & Catalog Harvester")
        self.adapters: List[BaseScraperAdapter] = [
            LiderScraperAdapter(),
            CencosudScraperAdapter(brand_type="jumbo"),
            CencosudScraperAdapter(brand_type="santaisabel"),
            UnimarcScraperAdapter(),
        ]

    async def step(self, limit_per_query: int = 4, target_queries: list = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Ejecuta un ciclo de extracción en todas las tiendas para las categorías del turno actual.
        """
        queries_to_run = target_queries or self.get_current_shift_batch()
        all_raw_items: List[RawScrapedProduct] = []
        stats_by_super: Dict[str, int] = {ad.supermarket_slug: 0 for ad in self.adapters}

        for target in queries_to_run:
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
