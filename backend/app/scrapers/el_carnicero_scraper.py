import logging
import urllib.request
import ssl
import re
from typing import List, Optional
from decimal import Decimal
from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct

logger = logging.getLogger("ofertis.scrapers.elcarnicero")


class ElCarniceroScraperAdapter(BaseScraperAdapter):
    """
    Adaptador de minería en vivo para 'El Carnicero' (Maestro en Carnes).
    Monitorea cortes de vacuno, cerdo y aves con precios por kilo.
    """

    BASE_URL = "https://elcarnicero.cl"

    def __init__(self):
        self._slug = "el_carnicero"
        self._name = "El Carnicero"
        self.ctx = ssl._create_unverified_context()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

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
        Ejecuta la extracción de productos para El Carnicero.
        """
        products: List[RawScrapedProduct] = []

        # Si la búsqueda no es de carnes ni aves, no aplica
        meat_categories = {"carne_vacuno", "carne_cerdo", "carne_pollo", "carne_pavo", "embutidos", "fiambreria"}
        if category not in meat_categories and not any(k in query.lower() for k in ["lomo", "posta", "carne", "pollo", "cerdo", "asado", "costillar", "huachalomo", "sobrecostilla"]):
            return []

        search_url = f"{self.BASE_URL}/search?q={urllib.parse.quote_plus(query)}"
        try:
            req = urllib.request.Request(search_url, headers=self.headers)
            with urllib.request.urlopen(req, context=self.ctx, timeout=10) as response:
                html = response.read().decode("utf-8", errors="ignore")

                # Extraer productos de Jumpseller
                cards = re.findall(
                    r"data-product-name=[\"'](.*?)[\"'].*?data-product-url=[\"'](.*?)[\"'].*?data-price=[\"'](.*?)[\"']",
                    html,
                    re.DOTALL
                )

                for name, prod_url, price_str in cards[:limit]:
                    try:
                        clean_name = name.strip()
                        price = float(price_str)
                        if price <= 0:
                            continue

                        full_url = f"{self.BASE_URL}{prod_url}" if not prod_url.startswith("http") else prod_url
                        sku = f"EC-{abs(hash(full_url)) % 1000000:06d}"

                        products.append(
                            RawScrapedProduct(
                                supermarket_slug=self._slug,
                                sku=sku,
                                store_title=clean_name,
                                brand_raw="El Carnicero",
                                normal_price=Decimal(str(int(price))),
                                offer_price=None,
                                product_url=full_url,
                                image_url="https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80",
                                category_hint=category
                            )
                        )
                    except Exception as p_err:
                        logger.debug(f"Error parseando item El Carnicero: {p_err}")
        except Exception as e:
            logger.warning(f"Error consultando El Carnicero en '{search_url}': {e}")

        return products
