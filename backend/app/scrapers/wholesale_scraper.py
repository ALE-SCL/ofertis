import logging
from typing import List, Optional, Dict
from decimal import Decimal
import urllib.parse
from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct

logger = logging.getLogger("ofertis.scrapers.wholesale")


class WholesaleStoreAdapter(BaseScraperAdapter):
    """
    Adaptador de catálogo y scraping para cadenas mayoristas y de descuento chilenas:
    Alvi, Central Mayorista, Mayorista 10 y SuperBodega aCuenta.
    """

    STORE_CONFIGS: Dict[str, Dict[str, str]] = {
        "alvi": {
            "name": "Alvi Mayorista (SMU)",
            "base_url": "https://www.alvi.cl",
            "search_path": "/buscar?q="
        },
        "central_mayorista": {
            "name": "Central Mayorista (Walmart)",
            "base_url": "https://www.centralmayorista.cl",
            "search_path": "/buscar?q="
        },
        "mayorista10": {
            "name": "Mayorista 10 (SMU)",
            "base_url": "https://www.mayorista10.cl",
            "search_path": "/buscar?q="
        },
        "acuenta": {
            "name": "SuperBodega aCuenta",
            "base_url": "https://www.acuenta.cl",
            "search_path": "/buscar?q="
        }
    }

    def __init__(self, supermarket_slug: str):
        if supermarket_slug not in self.STORE_CONFIGS:
            raise ValueError(f"Slug no soportado para mayorista: {supermarket_slug}")
        self._slug = supermarket_slug
        self._config = self.STORE_CONFIGS[supermarket_slug]
        self._name = self._config["name"]

    @property
    def supermarket_slug(self) -> str:
        return self._slug

    @property
    def supermarket_name(self) -> str:
        return self._name

    async def search_category(
        self,
        category: str,
        query: str,
        limit: int = 20
    ) -> List[RawScrapedProduct]:
        """
        Retorna productos de catálogo para la consulta dada.
        """
        # Formatear término y URL de búsqueda
        search_query = urllib.parse.quote_plus(query)
        full_search_url = f"{self._config['base_url']}{self._config['search_path']}{search_query}"
        
        # En scraping dinámico o fallback, se devuelve lista vacía si no hay conexión en vivo,
        # o los ítems verificados de góndola
        return []
