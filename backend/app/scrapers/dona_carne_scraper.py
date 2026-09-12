import json
import logging
import urllib.request
import urllib.error
import urllib.parse
from decimal import Decimal
from typing import List, Optional
from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct

logger = logging.getLogger("ofertis.scrapers.dona_carne")


class DonaCarneScraperAdapter(BaseScraperAdapter):
    """
    Adaptador de precios en vivo para Doña Carne vía Shopify JSON API.
    """
    STORE_ID = "dona_carne"
    STORE_NAME = "Doña Carne"
    BASE_URL = "https://ventasonline.xn--doacarne-e3a.cl"
    PRODUCTS_API_URL = "https://ventasonline.xn--doacarne-e3a.cl/products.json?limit=50"

    def __init__(self):
        self._slug = "dona_carne"
        self._name = "Doña Carne"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        self._cached_products: Optional[List[dict]] = None

    @property
    def supermarket_slug(self) -> str:
        return self._slug

    @property
    def supermarket_name(self) -> str:
        return self._name

    def _fetch_all_products(self) -> List[dict]:
        if self._cached_products is not None:
            return self._cached_products

        try:
            req = urllib.request.Request(self.PRODUCTS_API_URL, headers=self.headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    payload = json.loads(response.read().decode("utf-8"))
                    self._cached_products = payload.get("products", [])
                    return self._cached_products
        except Exception as err:
            logger.warning(f"Error conectando a Doña Carne Shopify API: {err}")
        return []

    async def search_category(
        self,
        category: str,
        query: str,
        limit: int = 20
    ) -> List[RawScrapedProduct]:
        """
        Ejecuta la búsqueda y normalización de cortes de carne para Doña Carne.
        """
        meat_categories = {"carne_vacuno", "carne_cerdo", "carne_pollo", "carne_pavo", "embutidos", "fiambreria"}
        if category not in meat_categories and not any(k in query.lower() for k in ["lomo", "posta", "carne", "pollo", "cerdo", "asado", "costillar", "huachalomo", "sobrecostilla"]):
            return []

        products = self._fetch_all_products()
        results: List[RawScrapedProduct] = []
        q_tokens = [t.lower() for t in query.split() if len(t) > 2]

        for p in products:
            title = p.get("title", "").strip()
            title_lower = title.lower()

            # Coincidencia con tokens de búsqueda
            matches = any(token in title_lower for token in q_tokens) if q_tokens else True
            if not matches:
                continue

            handle = p.get("handle", "")
            images = p.get("images", [])
            img_url = images[0].get("src") if images else "https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80"
            variants = p.get("variants", [])

            for v in variants:
                try:
                    price = float(v.get("price", 0))
                    if price <= 0:
                        continue
                    sku = f"DC-{v.get('id', '001')}"
                    results.append(
                        RawScrapedProduct(
                            supermarket_slug=self._slug,
                            sku=sku,
                            store_title=title,
                            brand_raw="Doña Carne",
                            normal_price=Decimal(str(int(price))),
                            offer_price=None,
                            product_url=f"{self.BASE_URL}/products/{handle}",
                            image_url=img_url,
                            category_hint=category
                        )
                    )
                    if len(results) >= limit:
                        break
                except Exception as parse_err:
                    logger.debug(f"Error parseando variante de {title}: {parse_err}")

            if len(results) >= limit:
                break

        return results
