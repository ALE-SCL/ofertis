import logging
from typing import List, Optional
from decimal import Decimal
from app.scrapers.base_scraper import BaseScraperAdapter, RawScrapedProduct
from app.skills.scraping_skill import ScrapingSkill

logger = logging.getLogger("ofertis.scrapers.lider")


class LiderScraperAdapter(BaseScraperAdapter):
    """
    Adaptador de minería de datos para Lider (Walmart Chile).
    """

    def __init__(self):
        self._slug = "lider"
        self._name = "Lider (Walmart)"
        self._base_domain = "https://www.lider.cl"
        self.skill = ScrapingSkill()

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
        Ejecuta la búsqueda contra el endpoint de catálogo de Lider.
        """
        url = "https://buyshop-service.lider.cl/orchestrator/v2/products/search"
        params = {"query": query, "page": 1, "hitsPerPage": limit}

        headers = {
            "Referer": f"{self._base_domain}/supermercado",
            "Origin": self._base_domain,
            "Accept": "application/json",
            "tenant": "supermercado",
            "channel": "desktop"
        }

        response_data = await self.skill.fetch_json_safe(url, params=params, headers=headers)
        products: List[RawScrapedProduct] = []

        if isinstance(response_data, dict):
            raw_items = response_data.get("products", [])
            for p in raw_items:
                try:
                    sku = str(p.get("sku", p.get("id", "")))
                    display_name = p.get("displayName", "")
                    brand = p.get("brand", "")
                    img_url = p.get("images", {}).get("smallImage") or p.get("images", {}).get("largeImage")

                    price_info = p.get("price", {})
                    base_price = Decimal(str(price_info.get("BasePriceReference", 0)))
                    lead_price = Decimal(str(price_info.get("leadPrice", 0)))

                    normal_p = base_price if base_price > 0 else lead_price
                    offer_p = lead_price if (base_price > 0 and lead_price < base_price) else None

                    if normal_p > 0:
                        products.append(
                            RawScrapedProduct(
                                supermarket_slug=self._slug,
                                sku=f"LID-{sku}",
                                store_title=display_name,
                                brand_raw=brand,
                                normal_price=normal_p,
                                offer_price=offer_p,
                                product_url=f"{self._base_domain}/supermercado/producto/{sku}",
                                image_url=img_url,
                                category_hint=category
                            )
                        )
                except Exception as ex:
                    logger.debug(f"Error parseando item Lider: {ex}")

        return products
