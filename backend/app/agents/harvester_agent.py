import logging
from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct
from app.scrapers.cencosud_scraper import CencosudScraperAdapter
from app.scrapers.unimarc_scraper import UnimarcScraperAdapter
from app.scrapers.lider_scraper import LiderScraperAdapter
from app.scrapers.dona_carne_scraper import DonaCarneScraperAdapter
from app.scrapers.el_carnicero_scraper import ElCarniceroScraperAdapter
from app.scrapers.wholesale_scraper import WholesaleStoreAdapter

from datetime import datetime, timezone, timedelta

logger = logging.getLogger("ofertis.agents.harvester")


class HarvesterAgent(BaseAgent):
    """
    Agente de Minería e Ingesta Continua (Data Mining Loop).
    Recorre las categorías de productos de primera necesidad en los 10 supermercados y mayoristas
    distribuidas en turnos diarios para un crecimiento orgánico sin saturación de recursos.
    """

    BATCH_1_PROTEINAS = [
        {"category": "carne_vacuno", "query": "lomo liso"},
        {"category": "carne_vacuno", "query": "lomo vetado"},
        {"category": "carne_vacuno", "query": "posta negra"},
        {"category": "carne_vacuno", "query": "posta rosada"},
        {"category": "carne_vacuno", "query": "asiento"},
        {"category": "carne_vacuno", "query": "huachalomo"},
        {"category": "carne_vacuno", "query": "sobrecostilla"},
        {"category": "carne_vacuno", "query": "carne molida"},
        {"category": "carne_cerdo", "query": "pulpa cerdo"},
        {"category": "carne_cerdo", "query": "costillar cerdo"},
        {"category": "carne_cerdo", "query": "chuletas de cerdo"},
        {"category": "carne_pollo", "query": "pechuga deshuesada"},
        {"category": "carne_pollo", "query": "trutro pollo"},
        {"category": "carne_pavo", "query": "pechuga de pavo"},
        {"category": "embutidos", "query": "vienesas"},
        {"category": "embutidos", "query": "longanizas"},
    ]

    BATCH_2_DESPENSA = [
        {"category": "arroz", "query": "arroz grado 1"},
        {"category": "arroz", "query": "arroz integral"},
        {"category": "legumbres", "query": "lentejas"},
        {"category": "legumbres", "query": "porotos"},
        {"category": "legumbres", "query": "garbanzos"},
        {"category": "fideos", "query": "spaghetti"},
        {"category": "fideos", "query": "fideos espirales"},
        {"category": "fideos", "query": "tallarines"},
        {"category": "pastas", "query": "salsa de tomate"},
        {"category": "harinas", "query": "harina de trigo"},
        {"category": "aceites", "query": "aceite vegetal"},
        {"category": "aceites", "query": "aceite maravilla"},
        {"category": "aceites", "query": "aceite oliva"},
        {"category": "aderezos", "query": "mayonesa"},
        {"category": "conservas", "query": "atun lomitos"},
        {"category": "conservas", "query": "jurel natural"},
    ]

    BATCH_3_LACTEOS_HUEVOS = [
        {"category": "leche", "query": "leche entera"},
        {"category": "leche", "query": "leche descremada"},
        {"category": "leche", "query": "leche sin lactosa"},
        {"category": "lacteos", "query": "queso gauda laminado"},
        {"category": "lacteos", "query": "queso chanco"},
        {"category": "lacteos", "query": "mantequilla con sal"},
        {"category": "lacteos", "query": "crema de leche"},
        {"category": "lacteos", "query": "yogurt batido"},
        {"category": "huevos", "query": "huevos bandeja"},
        {"category": "huevos", "query": "huevos blancos"},
    ]

    BATCH_4_FRUTAS_VERDURAS = [
        {"category": "verduras", "query": "tomate larga vida"},
        {"category": "verduras", "query": "palta hass"},
        {"category": "verduras", "query": "cebolla a granel"},
        {"category": "verduras", "query": "papas a granel"},
        {"category": "verduras", "query": "zanahorias"},
        {"category": "verduras", "query": "lechuga costina"},
        {"category": "verduras", "query": "limon"},
        {"category": "frutas", "query": "platano"},
        {"category": "frutas", "query": "manzana royal gala"},
        {"category": "frutas", "query": "naranjas"},
    ]

    BATCH_5_BEBIDAS_BOTILLERIA = [
        {"category": "aguas", "query": "agua mineral sin gas"},
        {"category": "aguas", "query": "agua purificada bidon"},
        {"category": "gaseosas", "query": "coca cola original"},
        {"category": "gaseosas", "query": "coca cola zero"},
        {"category": "jugos", "query": "jugo nectar naranja"},
        {"category": "cervezas", "query": "cerveza lager"},
        {"category": "cervezas", "query": "cerveza corona"},
        {"category": "vinos", "query": "vino cabernet sauvignon"},
        {"category": "destilados", "query": "pisco mistral"},
    ]

    BATCH_6_PANADERIA_DESAYUNO = [
        {"category": "pan", "query": "pan de molde blanco"},
        {"category": "pan", "query": "pan de molde integral"},
        {"category": "pan", "query": "pan pita"},
        {"category": "pan", "query": "tortillas rapiditas"},
        {"category": "desayuno", "query": "cafe instantaneo"},
        {"category": "desayuno", "query": "te ceylan"},
        {"category": "cereales", "query": "cereal chocapic"},
        {"category": "dulces", "query": "manjar tradicional"},
        {"category": "dulces", "query": "mermelada frutilla"},
        {"category": "galletas", "query": "galletas de soda"},
        {"category": "snacks", "query": "papas fritas lays"},
    ]

    BATCH_7_LIMPIEZA_ASEO = [
        {"category": "limpieza", "query": "detergente liquido ropa"},
        {"category": "limpieza", "query": "detergente omo"},
        {"category": "limpieza", "query": "cloro tradicional"},
        {"category": "limpieza", "query": "cloro gel"},
        {"category": "limpieza", "query": "lavaloza liquido"},
        {"category": "limpieza", "query": "papel higienico doble hoja"},
        {"category": "limpieza", "query": "toalla de papel"},
        {"category": "cuidado_personal", "query": "shampoo sedal"},
        {"category": "cuidado_personal", "query": "jabon liquido"},
        {"category": "cuidado_personal", "query": "pasta dental colgate"},
        {"category": "cuidado_personal", "query": "desodorante rexona"},
        {"category": "bebe", "query": "pañales pampers"},
    ]

    BATCH_8_CONGELADOS_MASCOTAS = [
        {"category": "congelados", "query": "choclo congelado"},
        {"category": "congelados", "query": "arvejas congeladas"},
        {"category": "congelados", "query": "papas prefritas congeladas"},
        {"category": "congelados", "query": "nuggets de pollo"},
        {"category": "congelados", "query": "filete merluza congelado"},
        {"category": "mascotas", "query": "alimento perro dog chow"},
        {"category": "mascotas", "query": "alimento gato cat chow"},
        {"category": "mascotas", "query": "arena para gatos sanitaria"},
        {"category": "fiambreria", "query": "jamon pierna artesanal"},
        {"category": "fiambreria", "query": "jamon de pavo"},
    ]

    @classmethod
    def get_all_catalog_targets(cls) -> list:
        """
        Devuelve la totalidad de los objetivos de minería para todos los departamentos.
        """
        return (
            cls.BATCH_1_PROTEINAS
            + cls.BATCH_2_DESPENSA
            + cls.BATCH_3_LACTEOS_HUEVOS
            + cls.BATCH_4_FRUTAS_VERDURAS
            + cls.BATCH_5_BEBIDAS_BOTILLERIA
            + cls.BATCH_6_PANADERIA_DESAYUNO
            + cls.BATCH_7_LIMPIEZA_ASEO
            + cls.BATCH_8_CONGELADOS_MASCOTAS
        )

    @classmethod
    def get_current_shift_batch(cls) -> list:
        """
        Determina el lote de minería según la hora de Chile:
        - 00:00 - 05:59 CLT: Carnes, Proteínas NCh 1424 y Fiambrería
        - 06:00 - 08:59 CLT: Panadería, Desayuno y Galletas
        - 09:00 - 11:59 CLT: Despensa, Arroz, Pastas y Aceites
        - 12:00 - 14:59 CLT: Frutas, Verduras y Frescos
        - 15:00 - 17:59 CLT: Lácteos, Huevos y Quesos
        - 18:00 - 20:59 CLT: Bebidas, Aguas y Botillería
        - 21:00 - 23:59 CLT: Limpieza, Cuidado Personal, Congelados y Mascotas
        """
        try:
            import zoneinfo
            chile_tz = zoneinfo.ZoneInfo("America/Santiago")
        except Exception:
            chile_tz = timezone(timedelta(hours=-3))

        hour = datetime.now(chile_tz).hour
        if 0 <= hour < 6:
            return cls.BATCH_1_PROTEINAS
        elif 6 <= hour < 9:
            return cls.BATCH_6_PANADERIA_DESAYUNO
        elif 9 <= hour < 12:
            return cls.BATCH_2_DESPENSA
        elif 12 <= hour < 15:
            return cls.BATCH_4_FRUTAS_VERDURAS
        elif 15 <= hour < 18:
            return cls.BATCH_3_LACTEOS_HUEVOS
        elif 18 <= hour < 21:
            return cls.BATCH_5_BEBIDAS_BOTILLERIA
        else:
            return cls.BATCH_7_LIMPIEZA_ASEO + cls.BATCH_8_CONGELADOS_MASCOTAS

    def __init__(self):
        super().__init__(name="HarvesterAgent", role="Data Mining & Catalog Harvester")
        self.adapters: List[BaseScraperAdapter] = [
            LiderScraperAdapter(),
            CencosudScraperAdapter(brand_type="jumbo"),
            CencosudScraperAdapter(brand_type="santaisabel"),
            UnimarcScraperAdapter(),
            WholesaleStoreAdapter(supermarket_slug="alvi"),
            WholesaleStoreAdapter(supermarket_slug="central_mayorista"),
            WholesaleStoreAdapter(supermarket_slug="mayorista10"),
            WholesaleStoreAdapter(supermarket_slug="acuenta"),
            DonaCarneScraperAdapter(),
            ElCarniceroScraperAdapter(),
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
